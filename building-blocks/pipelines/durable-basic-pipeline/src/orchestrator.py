import azure.durable_functions as df
import logging
import json
import jsonschema
from datetime import timezone
from pathlib import Path

# Load schemas once
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
PIPELINE_RUN_SCHEMA_PATH = (
    BASE_DIR / "shared" / "contracts" / "pipeline-run.schema.json"
)


def _load_schema(path):
    with open(path, "r") as f:
        return json.load(f)


# P0: Load schema outside the orchestrator execution path to maintain determinism.
# Durable Functions orchestrators must be free of filesystem-dependent side effects.
try:
    PIPELINE_RUN_SCHEMA = _load_schema(PIPELINE_RUN_SCHEMA_PATH)
except Exception as e:
    logging.error(f"Failed to load pipeline-run schema: {e}")
    PIPELINE_RUN_SCHEMA = None


def pipeline_orchestrator(context: df.DurableOrchestrationContext):
    """
    Main orchestrator logic for the Document AI pipeline.
    Coordinates OCR, validation, and publication while maintaining
    customer-safe status transitions.
    """
    input_data = context.get_input()
    if not input_data or "pipeline_run" not in input_data:
        logging.error("Orchestrator received invalid input. Missing 'pipeline_run'.")
        return "invalid_input"

    pipeline_run = input_data["pipeline_run"]

    # Contract Validation
    if not PIPELINE_RUN_SCHEMA:
        logging.error("Schema not loaded; skipping contract validation.")
    else:
        try:
            jsonschema.validate(instance=pipeline_run, schema=PIPELINE_RUN_SCHEMA)
        except Exception:
            logging.error("PipelineRun payload failed contract validation.")
            return "invalid_contract"

    run_id = pipeline_run["id"]
    customer_id = pipeline_run["customer_id"]
    pipeline_type = pipeline_run["pipeline_type"]
    source_blob = input_data.get("source_blob")

    # Use context.current_utc_datetime for determinism
    start_time = context.current_utc_datetime.replace(tzinfo=timezone.utc).isoformat()

    # 1. Update status to 'running'
    yield context.call_activity(
        "update_pipeline_run_status",
        {
            "id": run_id,
            "customer_id": customer_id,
            "pipeline_type": pipeline_type,
            "status": "running",
            "created_at": pipeline_run["created_at"],
            "started_at": start_time,
            "business_summary": "Pipeline processing started.",
        },
    )

    # Retry policy for retryable activities (OCR, Publication)
    # We use a bounded retry policy to avoid infinite loops and excessive costs.
    retry_options = df.RetryOptions(
        first_retry_interval_in_milliseconds=5000, max_number_of_attempts=3
    )

    try:
        # 2. OCR Step (Retryable)
        ocr_result = yield context.call_activity_with_retry(
            "ocr_document_intelligence",
            retry_options,
            {
                "run_id": run_id,
                "artifact_id": "source-document",
                "document_type": pipeline_type,
                "storage_ref": source_blob,
            },
        )

        if ocr_result.get("status") == "failed":
            # Business failure (e.g. invalid document) should not be retried by Durable Functions
            # because the same input will likely fail again.
            raise ValueError(ocr_result.get("friendly_error") or "OCR step failed.")

        # 3. Field Validation Step (Non-retryable)
        # Validation is deterministic based on input; retrying won't change the outcome.
        validation_result = yield context.call_activity(
            "field_validation_worker",
            {
                "run_id": run_id,
                "artifact_id": "ocr-result",
                "ruleset_id": "default-ruleset",
            },
        )

        if validation_result.get("status") == "failed":
            raise ValueError(
                validation_result.get("friendly_error") or "Field validation failed."
            )

        # 4. Final Result Publishing (Retryable)
        publish_result = yield context.call_activity_with_retry(
            "final_result_publisher",
            retry_options,
            {
                "run_id": run_id,
                "validation_status": validation_result.get(
                    "validation_status", "valid"
                ),
                "artifact_ids": ocr_result.get("artifacts", [])
                + validation_result.get("artifacts", []),
            },
        )

        if publish_result.get("status") == "failed":
            raise ValueError(
                publish_result.get("friendly_error") or "Final publication failed."
            )

        # 5. Finalize Pipeline Run
        finish_time = context.current_utc_datetime.replace(
            tzinfo=timezone.utc
        ).isoformat()
        yield context.call_activity(
            "update_pipeline_run_status",
            {
                "id": run_id,
                "customer_id": customer_id,
                "pipeline_type": pipeline_type,
                "status": "completed",
                "created_at": pipeline_run["created_at"],
                "started_at": start_time,
                "finished_at": finish_time,
                "business_summary": "Pipeline completed successfully. Results are now available.",
            },
        )

        return "completed"

    except Exception:
        # Safely capture failure without leaking internals in technical logs.
        # Avoid logging the exception object directly as it may contain SAS tokens or other secrets.
        logging.error("Pipeline execution failed.")
        error_time = context.current_utc_datetime.replace(
            tzinfo=timezone.utc
        ).isoformat()

        yield context.call_activity(
            "update_pipeline_run_status",
            {
                "id": run_id,
                "customer_id": customer_id,
                "pipeline_type": pipeline_type,
                "status": "failed",
                "created_at": pipeline_run["created_at"],
                "started_at": start_time,
                "finished_at": error_time,
                "friendly_error": "An error occurred during document processing. "
                "The error has been logged and the support team has been notified.",
            },
        )
        # We don't re-raise here to allow the orchestration to finish cleanly
        # with the failed status in the status store.
        return "failed"
