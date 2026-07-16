import azure.durable_functions as df
import logging
import json
import jsonschema
from datetime import timezone
from pathlib import Path

# Load schemas once
# Path: building-blocks/pipelines/durable-basic-pipeline/src/orchestrator.py
# 1: src, 2: durable-basic-pipeline, 3: pipelines, 4: building-blocks, 5: root
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
PIPELINE_RUN_SCHEMA_PATH = (
    BASE_DIR / "shared" / "contracts" / "pipeline-run.schema.json"
)
PIPELINE_STEP_SCHEMA_PATH = (
    BASE_DIR / "shared" / "contracts" / "pipeline-step.schema.json"
)

# Local schemas
MODULE_DIR = Path(__file__).parent.parent
PIPELINE_INPUT_SCHEMA_PATH = MODULE_DIR / "schemas" / "pipeline_input.schema.json"
PIPELINE_SUCCESS_SCHEMA_PATH = MODULE_DIR / "schemas" / "pipeline_success.schema.json"
FRIENDLY_FAILURE_SCHEMA_PATH = MODULE_DIR / "schemas" / "friendly_failure.schema.json"


def _load_schema(path):
    with open(path, "r") as f:
        return json.load(f)


# P0: Load schemas outside the orchestrator execution path to maintain determinism.
# Durable Functions orchestrators must be free of filesystem-dependent side effects.
try:
    PIPELINE_RUN_SCHEMA = _load_schema(PIPELINE_RUN_SCHEMA_PATH)
    PIPELINE_STEP_SCHEMA = _load_schema(PIPELINE_STEP_SCHEMA_PATH)
    PIPELINE_INPUT_SCHEMA = _load_schema(PIPELINE_INPUT_SCHEMA_PATH)
    PIPELINE_SUCCESS_SCHEMA = _load_schema(PIPELINE_SUCCESS_SCHEMA_PATH)
    FRIENDLY_FAILURE_SCHEMA = _load_schema(FRIENDLY_FAILURE_SCHEMA_PATH)
except Exception as e:
    logging.error(f"Failed to load pipeline schemas: {e}")
    PIPELINE_RUN_SCHEMA = None
    PIPELINE_STEP_SCHEMA = None
    PIPELINE_INPUT_SCHEMA = None
    PIPELINE_SUCCESS_SCHEMA = None
    FRIENDLY_FAILURE_SCHEMA = None


def pipeline_orchestrator(context: df.DurableOrchestrationContext):
    """
    Main orchestrator logic for the Document AI pipeline.
    Coordinates OCR, validation, and publication while maintaining
    customer-safe status transitions.
    """
    input_data = context.get_input()

    # Contract validation must fail closed if the schemas could not be loaded.
    if (
        not PIPELINE_RUN_SCHEMA
        or not PIPELINE_STEP_SCHEMA
        or not PIPELINE_INPUT_SCHEMA
        or not PIPELINE_SUCCESS_SCHEMA
        or not FRIENDLY_FAILURE_SCHEMA
    ):
        logging.error(
            "Pipeline schemas are unavailable; refusing unvalidated execution."
        )
        return {
            "status": "failed",
            "error": "Contract validation failed",
            "friendly_message": "Internal configuration error. Schemas not loaded.",
        }

    try:
        jsonschema.validate(instance=input_data, schema=PIPELINE_INPUT_SCHEMA)
    except Exception:
        logging.error("Input payload failed contract validation.")
        return {
            "status": "failed",
            "error": "Contract validation failed",
            "friendly_message": "Invalid pipeline input request.",
        }

    pipeline_run = input_data["pipeline_run"]
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
            "correlation_id": context.instance_id,
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

    current_step_name = None
    accumulated_artifacts = []

    def _update_step(
        name, status, summary=None, artifacts=None, error=None, start=None, finish=None
    ):
        step_data = {
            "run_id": run_id,
            "name": name,
            "status": status,
        }
        if summary:
            step_data["output_summary"] = summary
        if artifacts:
            step_data["artifacts"] = artifacts
        if error:
            step_data["friendly_error"] = error
        if start:
            step_data["started_at"] = start
        if finish:
            step_data["finished_at"] = finish

        # Deterministic validation
        jsonschema.validate(instance=step_data, schema=PIPELINE_STEP_SCHEMA)
        return context.call_activity("update_pipeline_step_status", step_data)

    try:
        # 2. OCR Step (Retryable)
        current_step_name = "ocr-document-intelligence"
        yield _update_step(
            current_step_name,
            "running",
            start=context.current_utc_datetime.replace(tzinfo=timezone.utc).isoformat(),
        )

        ocr_result = yield context.call_activity_with_retry(
            "ocr_document_intelligence",
            retry_options,
            {
                "run_id": run_id,
                "artifact_id": "source-document",
                "document_type": pipeline_type,
                "source_blob": source_blob,
            },
        )

        if ocr_result.get("status") == "failed":
            # Business failure (e.g. invalid document) should not be retried by Durable Functions
            # because the same input will likely fail again.
            raise ValueError(ocr_result.get("friendly_error") or "OCR step failed.")

        step_artifacts = ocr_result.get("artifacts", [])
        accumulated_artifacts.extend(step_artifacts)

        yield _update_step(
            current_step_name,
            "completed",
            summary="OCR extraction completed.",
            artifacts=step_artifacts,
            finish=context.current_utc_datetime.replace(
                tzinfo=timezone.utc
            ).isoformat(),
        )

        # 3. Field Validation Step (Non-retryable)
        # Validation is deterministic based on input; retrying won't change the outcome.
        current_step_name = "field-validation-worker"
        yield _update_step(
            current_step_name,
            "running",
            start=context.current_utc_datetime.replace(tzinfo=timezone.utc).isoformat(),
        )

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

        step_artifacts = validation_result.get("artifacts", [])
        accumulated_artifacts.extend(step_artifacts)

        yield _update_step(
            current_step_name,
            "completed",
            summary="Field validation completed.",
            artifacts=step_artifacts,
            finish=context.current_utc_datetime.replace(
                tzinfo=timezone.utc
            ).isoformat(),
        )

        # 4. Final Result Publishing (Retryable)
        current_step_name = "final-result-publisher"
        yield _update_step(
            current_step_name,
            "running",
            start=context.current_utc_datetime.replace(tzinfo=timezone.utc).isoformat(),
        )

        publish_result = yield context.call_activity_with_retry(
            "final_result_publisher",
            retry_options,
            {
                "run_id": run_id,
                "validation_status": validation_result.get(
                    "validation_status", "valid"
                ),
                "artifact_ids": accumulated_artifacts,
            },
        )

        if publish_result.get("status") == "failed":
            raise ValueError(
                publish_result.get("friendly_error") or "Final publication failed."
            )

        yield _update_step(
            current_step_name,
            "completed",
            summary="Final results published.",
            finish=context.current_utc_datetime.replace(
                tzinfo=timezone.utc
            ).isoformat(),
        )

        # 5. Finalize Pipeline Run
        finish_time = context.current_utc_datetime.replace(
            tzinfo=timezone.utc
        ).isoformat()
        business_summary = "Pipeline completed successfully. Results are now available."
        yield context.call_activity(
            "update_pipeline_run_status",
            {
                "id": run_id,
                "customer_id": customer_id,
                "pipeline_type": pipeline_type,
                "status": "completed",
                "correlation_id": context.instance_id,
                "created_at": pipeline_run["created_at"],
                "started_at": start_time,
                "finished_at": finish_time,
                "business_summary": business_summary,
            },
        )

        success_result = {
            "status": "completed",
            "artifacts": accumulated_artifacts,
            "business_summary": business_summary,
        }
        jsonschema.validate(instance=success_result, schema=PIPELINE_SUCCESS_SCHEMA)
        return success_result

    except Exception:
        # Safely capture failure without leaking internals in technical logs.
        # Avoid logging the exception object directly as it may contain SAS tokens or other secrets.
        logging.error("Pipeline execution failed.")
        error_time = context.current_utc_datetime.replace(
            tzinfo=timezone.utc
        ).isoformat()
        friendly_message = (
            "An error occurred during document processing. "
            "The error has been logged and the support team has been notified."
        )

        if current_step_name:
            yield _update_step(
                current_step_name,
                "failed",
                error="Step failed. Technical details redacted.",
                finish=error_time,
            )

        yield context.call_activity(
            "update_pipeline_run_status",
            {
                "id": run_id,
                "customer_id": customer_id,
                "pipeline_type": pipeline_type,
                "status": "failed",
                "correlation_id": context.instance_id,
                "created_at": pipeline_run["created_at"],
                "started_at": start_time,
                "finished_at": error_time,
                "friendly_error": friendly_message,
            },
        )

        failure_result = {
            "status": "failed",
            "error": "Pipeline execution failed",
            "friendly_message": friendly_message,
        }
        jsonschema.validate(instance=failure_result, schema=FRIENDLY_FAILURE_SCHEMA)
        return failure_result
