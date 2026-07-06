import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from typing import Any, Dict


class StorageAdapter:
    def __init__(self, connection_string: str = None):
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        else:
            account_url = os.environ.get("STORAGE_ACCOUNT_URL")
            if not account_url:
                raise ValueError(
                    "STORAGE_ACCOUNT_URL or BlobStorageConnectionString must be set."
                )
            self.blob_service_client = BlobServiceClient(
                account_url, credential=DefaultAzureCredential()
            )

    def read_artifact(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Reads a JSON artifact from blob storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        stream = blob_client.download_blob()
        return json.loads(stream.readall())

    def write_artifact(
        self, container_name: str, blob_name: str, content: Dict[str, Any]
    ):
        """Writes a JSON artifact to blob storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        blob_client.upload_blob(json.dumps(content), overwrite=True)
