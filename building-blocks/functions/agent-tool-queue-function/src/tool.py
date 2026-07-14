import logging
import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableClient
from .models import (
    JobInput,
    JobResult,
    JobStatus,
    JobStatusResponse,
    is_valid_correlation_id,
)

logger = logging.getLogger(__name__)

# Constants
TABLE_NAME = "jobstatus"
PARTITION_KEY = "jobs"


class StatusStore:
    """
    Minimal adapter for Azure Table Storage to persist job status.
    """

    def __init__(self, table_client: Optional[TableClient] = None):
        if table_client:
            self.table_client = table_client
        else:
            account_name = os.environ.get("AzureWebJobsStorage__accountName")
            if account_name:
                endpoint = f"https://{account_name}.table.core.windows.net"
                self.table_client = TableClient(
                    endpoint,
                    TABLE_NAME,
                    credential=DefaultAzureCredential(),
                )
            else:
                self.table_client = None

    def update_status(
        self,
        correlation_id: str,
        status: JobStatus,
        business_summary: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        created_at: Optional[str] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
    ):
        if not self.table_client:
            logger.warning("StatusStore table client not configured. Skipping update.")
            return

        entity = {
            "PartitionKey": PARTITION_KEY,
            "RowKey": correlation_id,
            "status": status.value,
        }

        if business_summary:
            entity["business_summary"] = business_summary
        if result_data:
            entity["result_data"] = json.dumps(result_data)
        if error_message:
            entity["error_message"] = error_message
        if created_at:
            entity["created_at"] = created_at
        if started_at:
            entity["started_at"] = started_at
        if finished_at:
            entity["finished_at"] = finished_at

        self.table_client.upsert_entity(entity)

    def get_status(self, correlation_id: str) -> Optional[JobStatusResponse]:
        if not self.table_client:
            logger.warning("StatusStore table client not configured. Returning None.")
            return None

        try:
            entity = self.table_client.get_entity(PARTITION_KEY, correlation_id)

            result_data = None
            if "result_data" in entity:
                result_data = json.loads(entity["result_data"])

            return JobStatusResponse(
                id=entity["RowKey"],
                status=JobStatus(entity["status"]),
                business_summary=entity.get("business_summary"),
                created_at=entity.get("created_at", datetime.now(timezone.utc).isoformat()),
                started_at=entity.get("started_at"),
                finished_at=entity.get("finished_at"),
                result_data=result_data,
                error_message=entity.get("error_message"),
            )
        except Exception:
            return None


def process_queue_job(payload: Any, store: Optional[StatusStore] = None) -> JobResult:
    """
    Core deterministic logic for processing a queue-based tool job.
    Validates input, performs a read-only operation, and returns a safe result.
    """
    start_time = datetime.now(timezone.utc).isoformat()
    cid = payload.get("correlation_id") if isinstance(payload, dict) else None

    if not is_valid_correlation_id(cid):
        cid = "invalid-id-format"

    try:
        # 1. Validate input schema
        try:
            if not isinstance(payload, dict):
                 raise ValueError("Payload must be a dictionary.")
            job_input = JobInput(**payload)
        except Exception as e:
            logger.warning("Invalid job input received.")
            raise ValueError(f"Invalid job payload or schema: {str(e)}")

        # 2. Update status to RUNNING
        if store:
            store.update_status(
                cid,
                JobStatus.RUNNING,
                business_summary="Processing job...",
                started_at=start_time
            )

        # 3. Deterministic operation (mock)
        operation = job_input.operation_type.lower()
        params = job_input.parameters

        if operation == "ping":
            result_data = {"message": "pong", "echo": params.get("text", "")}
        elif operation == "analyze_text":
            text = params.get("text", "")
            result_data = {
                "length": len(text),
                "word_count": len(text.split()) if text else 0,
                "is_upper": text.isupper() if text else False,
            }
        else:
            logger.warning("Unsupported operation: %s", operation)
            error_res = JobResult(
                correlation_id=job_input.correlation_id,
                status=JobStatus.FAILED,
                error_message="Unsupported operation type requested.",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            if store:
                store.update_status(
                    cid,
                    JobStatus.FAILED,
                    error_message=error_res.error_message,
                    finished_at=error_res.timestamp
                )
            return error_res

        # 4. Return successful result
        success_res = JobResult(
            correlation_id=job_input.correlation_id,
            status=JobStatus.COMPLETED,
            result_data=result_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if store:
            store.update_status(
                cid,
                JobStatus.COMPLETED,
                business_summary="Job completed successfully.",
                result_data=result_data,
                finished_at=success_res.timestamp
            )
        return success_res

    except ValueError:
        # P0: Do not echo str(e) back to caller as it may contain rejected input values.
        error_res = JobResult(
            correlation_id=cid,
            status=JobStatus.FAILED,
            error_message="Invalid job payload or schema.",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if store:
            store.update_status(
                cid,
                JobStatus.FAILED,
                error_message=error_res.error_message,
                finished_at=error_res.timestamp
            )
        return error_res
    except Exception:
        logger.error("An unhandled exception occurred during job processing.")
        error_res = JobResult(
            correlation_id=cid,
            status=JobStatus.FAILED,
            error_message="An internal error occurred while processing the request.",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if store:
            store.update_status(
                cid,
                JobStatus.FAILED,
                error_message=error_res.error_message,
                finished_at=error_res.timestamp
            )
        return error_res


def process_queue_job_safe(payload: Dict[str, Any], store: Optional[StatusStore] = None) -> Dict[str, Any]:
    """
    Safe entrypoint that returns a dictionary for queue output.
    """
    result = process_queue_job(payload, store)
    return result.model_dump(mode="json")
