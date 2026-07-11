import os
import re
import datetime
import logging
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from .models import Artifact

logger = logging.getLogger(__name__)

# Standard security validation for DevOps identifiers
SAFE_ID_PATTERN = r"^[a-zA-Z0-9_\-\. ]+$"
SAFE_ID_REGEX = re.compile(SAFE_ID_PATTERN)

# https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers-blobs-and-metadata
CONTAINER_NAME_PATTERN = r"^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9]$"
CONTAINER_NAME_REGEX = re.compile(CONTAINER_NAME_PATTERN)

# Storage account names: 3-24 chars, lowercase and numbers
ACCOUNT_URL_PATTERN = r"^https://[a-z0-9]{3,24}\.blob\.[a-z0-9\.]+$"
ACCOUNT_URL_REGEX = re.compile(ACCOUNT_URL_PATTERN)


class BlobArtifactStore:
    """
    Minimal Blob artifact store runtime for writing artifact content/metadata
    and returning customer-safe artifact references.
    """

    def __init__(
        self,
        account_url: str = None,
        container_name: str = None,
        credential: Any = None,
        sas_max_lifetime_hours: int = 24,
    ):
        self.account_url = account_url or os.environ.get("ARTIFACT_STORE_BLOB_ENDPOINT")
        self.container_name = container_name or os.environ.get(
            "ARTIFACT_CONTAINER_NAME", "artifacts"
        )

        if not isinstance(sas_max_lifetime_hours, int) or not (
            1 <= sas_max_lifetime_hours <= 48
        ):
            raise ValueError("sas_max_lifetime_hours must be an integer between 1 and 48.")
        self.sas_max_lifetime_hours = sas_max_lifetime_hours

        if not self.account_url or not ACCOUNT_URL_REGEX.match(self.account_url):
            raise ValueError(
                "account_url is required and must be a valid https Azure Blob Storage endpoint."
            )

        if not self.container_name or not CONTAINER_NAME_REGEX.match(self.container_name):
            raise ValueError(
                f"Invalid container name: {self.container_name}. Must follow Azure naming rules."
            )

        self.credential = credential or DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient(
            account_url=self.account_url, credential=self.credential
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        # Extract account name for SAS generation
        # account_url is usually https://<account_name>.blob.core.windows.net
        self.account_name = self.account_url.split("//")[-1].split(".")[0]

    def _validate_id(self, identifier: str, name: str):
        if not identifier or not isinstance(identifier, str):
            raise ValueError(f"{name} must be a non-empty string.")
        # Prevent path traversal before regex check
        if ".." in identifier or "/" in identifier or "\\" in identifier:
            raise ValueError(f"{name} cannot contain path traversal characters.")
        if not SAFE_ID_REGEX.match(identifier):
            raise ValueError(
                f"{name} contains invalid characters. Pattern: {SAFE_ID_PATTERN}"
            )

    def store_artifact(
        self, run_id: str, artifact_id: str, content: bytes, metadata: Dict[str, Any]
    ) -> Artifact:
        """
        Validates inputs, uploads content to Blob Storage with metadata,
        and returns a customer-safe Artifact reference.
        """
        # Validate Inputs
        self._validate_id(run_id, "run_id")
        self._validate_id(artifact_id, "artifact_id")

        if not isinstance(content, bytes):
            raise ValueError("Artifact content must be bytes.")

        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary.")

        # Content boundary check (minimal example: 100MB)
        max_size = int(os.environ.get("ARTIFACT_MAX_SIZE_BYTES", 104857600))
        if len(content) > max_size:
            raise ValueError(
                f"Artifact content exceeds maximum size of {max_size} bytes."
            )

        # Validate metadata fields
        kind = metadata.get("kind")
        if kind and (not isinstance(kind, str) or not SAFE_ID_REGEX.match(kind)):
            raise ValueError("metadata['kind'] must be a safe alphanumeric string.")

        safe_name = metadata.get("safe_name")
        if safe_name and (not isinstance(safe_name, str) or not SAFE_ID_REGEX.match(safe_name)):
            raise ValueError("metadata['safe_name'] must be a safe alphanumeric string.")

        content_type = metadata.get("content_type")
        if content_type and (not isinstance(content_type, str) or "/" not in content_type):
            raise ValueError("metadata['content_type'] must be a valid MIME type string.")

        # Prepare blob path and metadata
        blob_name = f"{run_id}/{artifact_id}"

        # Map metadata to blob metadata (must be strings)
        blob_metadata = {
            "run_id": run_id,
            "id": artifact_id,
            "kind": str(kind or "generic"),
            "safe_name": str(safe_name or artifact_id),
            "is_customer_visible": str(
                metadata.get("is_customer_visible", False)
            ).lower(),
        }
        if metadata.get("step_name"):
            step_name = metadata["step_name"]
            if not isinstance(step_name, str) or not SAFE_ID_REGEX.match(step_name):
                 raise ValueError("metadata['step_name'] must be a safe alphanumeric string.")
            blob_metadata["step_name"] = step_name

        # Upload
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                content,
                overwrite=True,
                metadata=blob_metadata,
                content_settings=metadata.get("content_settings"),
            )

            # Return Artifact model
            return Artifact(
                id=artifact_id,
                run_id=run_id,
                step_name=metadata.get("step_name"),
                kind=blob_metadata["kind"],
                safe_name=blob_metadata["safe_name"],
                storage_ref=blob_name,
                content_type=metadata.get("content_type"),
                size_bytes=len(content),
                is_customer_visible=metadata.get("is_customer_visible", False),
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
        except Exception:
            logger.error("Failed to store artifact. Redacting internal details.")
            # Do not leak raw exception to customer-facing caller if used in API
            raise RuntimeError("Internal storage error occurred.") from None

    def get_safe_read_url(self, artifact: Artifact, expires_in_hours: int = 1) -> str:
        """
        Generates a short-lived, read-only, user-delegation SAS URL.
        """
        if not isinstance(artifact, Artifact):
            raise ValueError("artifact must be an instance of Artifact.")

        if not artifact.storage_ref or not isinstance(artifact.storage_ref, str):
            raise ValueError("Artifact storage_ref must be a non-empty string.")

        # Ensure storage_ref doesn't contain path traversal
        if ".." in artifact.storage_ref or artifact.storage_ref.startswith("/"):
            raise ValueError("Invalid Artifact storage_ref.")

        if expires_in_hours <= 0 or expires_in_hours > self.sas_max_lifetime_hours:
            raise ValueError(
                f"expires_in_hours must be between 1 and {self.sas_max_lifetime_hours}."
            )

        try:
            # 1. Get user delegation key
            now = datetime.datetime.now(datetime.timezone.utc)
            expiry = now + datetime.timedelta(hours=expires_in_hours)

            user_delegation_key = self.blob_service_client.get_user_delegation_key(
                key_start_time=now, key_expiry_time=expiry
            )

            # 2. Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=artifact.storage_ref,
                user_delegation_key=user_delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=expiry,
                start=now,
            )

            base_url = self.account_url.rstrip("/")
            return (
                f"{base_url}/{self.container_name}/{artifact.storage_ref}?{sas_token}"
            )

        except Exception:
            logger.error("Failed to generate SAS. Redacting internal details.")
            raise RuntimeError("Internal security error occurred.") from None
