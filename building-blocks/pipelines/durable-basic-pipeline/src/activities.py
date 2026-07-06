import logging
from datetime import datetime, timezone


def update_pipeline_run_status(status_data: dict):
    """
    Activity to update the overall pipeline run status.
    In a real implementation, this would write to a database (e.g., Cosmos DB).
    Follows shared/contracts/pipeline-run.schema.json
    """
    run_id = status_data.get("id")
    status = status_data.get("status")
    logging.info(f"Activity: Updating PipelineRun {run_id} to {status}")

    # Safety check: Ensure no internal Azure IDs or secrets are in the business_summary or friendly_error
    # This is a reference implementation, so we assume the input is already sanitized
    # or the activity itself handles it.

    return True


def ocr_document_intelligence(input_data: dict):
    """
    Mock OCR activity.
    Follows shared/contracts/pipeline-step.schema.json behavior.
    """
    run_id = input_data.get("run_id")
    logging.info(f"Activity: Starting OCR for RunID: {run_id}")

    # Mock success
    return {
        "run_id": run_id,
        "name": "ocr-document-intelligence",
        "status": "completed",
        "output_summary": "OCR extraction completed successfully.",
        "artifacts": ["ocr-result-artifact-id"],
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


def field_validation_worker(input_data: dict):
    """
    Mock field validation activity.
    Follows shared/contracts/pipeline-step.schema.json behavior.
    """
    run_id = input_data.get("run_id")
    logging.info(f"Activity: Starting Field Validation for RunID: {run_id}")

    # Mock success
    return {
        "run_id": run_id,
        "name": "field-validation-worker",
        "status": "completed",
        "validation_status": "valid",
        "output_summary": "All mandatory fields validated.",
        "artifacts": ["validation-report-id"],
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


def final_result_publisher(input_data: dict):
    """
    Mock final result publisher activity.
    """
    run_id = input_data.get("run_id")
    logging.info(f"Activity: Finalizing publication for RunID: {run_id}")

    # Mock success
    return {
        "run_id": run_id,
        "status": "completed",
        "publication_status": "published",
        "friendly_summary": "Results are now visible in the portal.",
    }
