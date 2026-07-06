import azure.durable_functions as df
import logging
from datetime import timezone


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

    try:
        # 2. OCR Step
        ocr_result = yield context.call_activity(
            "ocr_document_intelligence",
            {
                "run_id": run_id,
                "artifact_id": "source-document",
                "document_type": pipeline_type,
                "storage_ref": source_blob,
            },
        )

        if ocr_result.get("status") == "failed":
            raise Exception(ocr_result.get("friendly_error") or "OCR step failed.")

        # 3. Field Validation Step
        validation_result = yield context.call_activity(
            "field_validation_worker",
            {
                "run_id": run_id,
                "artifact_id": "ocr-result",  # Assumption: OCR produces this artifact
                "ruleset_id": "default-ruleset",
            },
        )

        if validation_result.get("status") == "failed":
            raise Exception(
                validation_result.get("friendly_error") or "Field validation failed."
            )

        # 4. Final Result Publishing
        publish_result = yield context.call_activity(
            "final_result_publisher",
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
            raise Exception(
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

    except Exception as e:
        # Safely capture failure without leaking internals
        error_msg = str(e)
        # Check if error_msg looks like a technical traceback or contains secrets
        # (Though in this implementation we control the exceptions raised above)

        logging.error(f"Pipeline {run_id} failed: {error_msg}")
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
