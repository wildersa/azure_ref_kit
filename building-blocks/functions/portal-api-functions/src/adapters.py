import os
import logging
from typing import List, Optional, Dict, Any
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableClient
from azure.storage.blob import ContainerClient


class StorageAdapter:
    def __init__(self):
        self.credential = DefaultAzureCredential()

        # Table Storage for Runs and Steps
        self.table_service_endpoint = os.environ.get("STATUS_STORE_TABLE_ENDPOINT")
        self.status_table_name = os.environ.get("STATUS_TABLE_NAME", "PipelineStatus")
        self.steps_table_name = os.environ.get("STEPS_TABLE_NAME", "PipelineSteps")
        self.cost_table_name = os.environ.get("COST_TABLE_NAME", "CostLedger")

        # Blob Storage for Artifacts
        self.blob_service_endpoint = os.environ.get("ARTIFACT_STORE_BLOB_ENDPOINT")
        self.artifact_container_name = os.environ.get(
            "ARTIFACT_CONTAINER_NAME", "artifacts"
        )

    def _get_table_client(self, table_name: str) -> TableClient:
        if self.table_service_endpoint:
            return TableClient(
                endpoint=self.table_service_endpoint,
                table_name=table_name,
                credential=self.credential,
            )
        else:
            # Fallback for local development if endpoint is not provided (using connection string or similar)
            conn_str = os.environ.get("AzureWebJobsStorage")
            return TableClient.from_connection_string(conn_str, table_name=table_name)

    def _get_container_client(self) -> ContainerClient:
        if self.blob_service_endpoint:
            return ContainerClient(
                account_url=self.blob_service_endpoint,
                container_name=self.artifact_container_name,
                credential=self.credential,
            )
        else:
            conn_str = os.environ.get("AzureWebJobsStorage")
            return ContainerClient.from_connection_string(
                conn_str, container_name=self.artifact_container_name
            )

    def get_runs(self, customer_id: str) -> List[Dict[str, Any]]:
        try:
            client = self._get_table_client(self.status_table_name)
            query = f"PartitionKey eq '{customer_id}'"
            return list(client.query_entities(query))
        except Exception as e:
            logging.error(f"Error fetching runs for customer {customer_id}: {str(e)}")
            return []

    def get_run(self, customer_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        try:
            client = self._get_table_client(self.status_table_name)
            return client.get_entity(partition_key=customer_id, row_key=run_id)
        except Exception:
            return None

    def get_steps(self, run_id: str) -> List[Dict[str, Any]]:
        try:
            client = self._get_table_client(self.steps_table_name)
            query = f"PartitionKey eq '{run_id}'"
            return list(client.query_entities(query))
        except Exception as e:
            logging.error(f"Error fetching steps for run {run_id}: {str(e)}")
            return []

    def get_artifacts(self, run_id: str) -> List[Dict[str, Any]]:
        try:
            # Assuming artifact metadata is stored in a table for easier querying
            # or we list blobs with metadata. Usually a table is better.
            # README says "Blob Storage (Artifact Metadata)".
            # If it's just blobs, we can list them and filter by run_id in metadata.
            container_client = self._get_container_client()
            artifacts = []
            blobs = container_client.list_blobs(include=["metadata"])
            for blob in blobs:
                if blob.metadata and blob.metadata.get("run_id") == run_id:
                    if blob.metadata.get("is_customer_visible") == "true":
                        artifacts.append(
                            {
                                "id": blob.metadata.get("id"),
                                "run_id": run_id,
                                "kind": blob.metadata.get("kind"),
                                "safe_name": blob.metadata.get("safe_name"),
                                "storage_ref": blob.name,
                                "content_type": blob.content_settings.content_type
                                if blob.content_settings
                                else None,
                                "size_bytes": blob.size,
                                "is_customer_visible": True,
                                "created_at": blob.creation_time.isoformat()
                                if blob.creation_time
                                else None,
                            }
                        )
            return artifacts
        except Exception as e:
            logging.error(f"Error fetching artifacts for run {run_id}: {str(e)}")
            return []

    def get_costs(self, run_id: str) -> List[Dict[str, Any]]:
        try:
            client = self._get_table_client(self.cost_table_name)
            query = f"PartitionKey eq '{run_id}'"
            return list(client.query_entities(query))
        except Exception as e:
            logging.error(f"Error fetching costs for run {run_id}: {str(e)}")
            return []
