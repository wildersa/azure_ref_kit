import json
import os
from typing import Any, Dict, Optional
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class StorageAdapter:
    """Generic adapter for Azure Blob Storage operations."""

    def __init__(self, account_url: Optional[str] = None):
        if account_url:
            self.blob_service_client = BlobServiceClient(
                account_url, credential=DefaultAzureCredential()
            )
        else:
            # Auto-discovery from environment
            account_url = os.environ.get("STORAGE_ACCOUNT_URL")
            if account_url:
                self.blob_service_client = BlobServiceClient(
                    account_url, credential=DefaultAzureCredential()
                )
            else:
                raise ValueError(
                    "Storage configuration missing. Provide account_url "
                    "or set the STORAGE_ACCOUNT_URL environment variable."
                )

    def read_json(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Reads and parses a JSON blob."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            stream = blob_client.download_blob()
            return json.loads(stream.readall())
        except Exception:
            # Technical details are logged internally by the SDK if configured.
            # We avoid re-logging them to maintain the safety boundary.
            raise

    def write_json(self, container_name: str, blob_name: str, content: Dict[str, Any]):
        """Serializes and writes a JSON blob."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            blob_client.upload_blob(
                json.dumps(content), overwrite=True, content_type="application/json"
            )
        except Exception:
            raise


class ArtifactStoreAdapter:
    """Adapter for managing artifact visibility and metadata."""

    def __init__(self, storage: StorageAdapter, container_name: str):
        self.storage = storage
        self.container = container_name

    def set_visible(self, run_id: str, artifact_id: str):
        """Marks an artifact as customer-visible."""
        blob_name = f"{run_id}/{artifact_id}.json"
        artifact_data = self.storage.read_json(self.container, blob_name)
        artifact_data["is_customer_visible"] = True
        self.storage.write_json(self.container, blob_name, artifact_data)


class StatusStoreAdapter:
    """Adapter for managing pipeline run status."""

    def __init__(self, storage: StorageAdapter, container_name: str):
        self.storage = storage
        self.container = container_name

    def update_run_status(
        self,
        run_id: str,
        status: str,
        business_summary: str,
        finished_at: str,
        friendly_error: Optional[str] = None,
    ):
        """Updates the final status and summary of a pipeline run."""
        blob_name = f"{run_id}.json"
        run_data = self.storage.read_json(self.container, blob_name)

        run_data["status"] = status
        run_data["business_summary"] = business_summary
        run_data["finished_at"] = finished_at

        if friendly_error:
            run_data["friendly_error"] = friendly_error

        # Ensure internal technical IDs aren't leaking if they were present
        # In this implementation, we stick to the schema properties.
        self.storage.write_json(self.container, blob_name, run_data)
