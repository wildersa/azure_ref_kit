from typing import Protocol, BinaryIO
from azure.identity import DefaultAzureCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.storage.blob import BlobServiceClient


class DocumentIntelligenceAdapter(Protocol):
    def analyze_document(self, model_id: str, document: BinaryIO) -> AnalyzeResult: ...


class StorageAdapter(Protocol):
    def download_blob(self, blob_url: str) -> bytes: ...
    def upload_blob(
        self, container: str, blob_name: str, data: bytes, content_type: str
    ) -> str: ...


class AzureDocumentIntelligenceAdapter:
    def __init__(self, endpoint: str):
        self.client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=DefaultAzureCredential()
        )

    def analyze_document(self, model_id: str, document: BinaryIO) -> AnalyzeResult:
        poller = self.client.begin_analyze_document(
            model_id=model_id,
            analyze_request=document,
            content_type="application/octet-stream",
        )
        return poller.result()


class AzureStorageAdapter:
    def __init__(self, account_url: str):
        self.client = BlobServiceClient(
            account_url=account_url, credential=DefaultAzureCredential()
        )

    def download_blob(self, blob_url: str) -> bytes:
        # Assumes blob_url is a full URL or a path within the account
        # In a real implementation, we'd parse the URL or use a client for the specific container/blob
        # For simplicity in this reference, we assume blob_url is "container/blob_name"
        container_name, blob_name = blob_url.split("/", 1)
        blob_client = self.client.get_blob_client(
            container=container_name, blob=blob_name
        )
        return blob_client.download_blob().readall()

    def upload_blob(
        self, container: str, blob_name: str, data: bytes, content_type: str
    ) -> str:
        container_client = self.client.get_container_client(container)
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True, content_type=content_type)
        return blob_client.url
