import logging
from datetime import datetime, timezone
from typing import Any, Dict
from .models import JobInput, JobResult, JobStatus, is_valid_correlation_id

logger = logging.getLogger(__name__)


def process_queue_job(payload: Dict[str, Any]) -> JobResult:
    """
    Core deterministic logic for processing a queue-based tool job.
    Validates input, performs a read-only operation, and returns a safe result.
    """
    try:
        # 1. Validate input schema
        try:
            job_input = JobInput(**payload)
        except Exception:
            logger.warning("Invalid job input received.")
            raise ValueError("Invalid job payload or schema.")

        # 2. Deterministic read-only operation
        # In this reference, we mock an "analysis" operation.
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
            return JobResult(
                correlation_id=job_input.correlation_id,
                status=JobStatus.FAILED,
                error_message=f"Unsupported operation type: {operation}",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # 3. Return successful result
        return JobResult(
            correlation_id=job_input.correlation_id,
            status=JobStatus.SUCCEEDED,
            result_data=result_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except ValueError as e:
        # Validation errors return a safe failure record if correlation_id is available
        cid = payload.get("correlation_id") if payload else None
        if not is_valid_correlation_id(cid):
            cid = "invalid-id-format"

        return JobResult(
            correlation_id=cid,
            status=JobStatus.FAILED,
            error_message=str(e),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception:
        # P0: Redact internal technical details in logs and output
        logger.error("An unhandled exception occurred during job processing.")
        cid = payload.get("correlation_id") if payload else None
        if not is_valid_correlation_id(cid):
            cid = "invalid-id-format"

        return JobResult(
            correlation_id=cid,
            status=JobStatus.FAILED,
            error_message="An internal error occurred while processing the request.",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


def process_queue_job_safe(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safe entrypoint that returns a dictionary for queue output.
    """
    result = process_queue_job(payload)
    return result.model_dump(mode="json")
