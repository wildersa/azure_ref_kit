import azure.durable_functions as df
import logging
import os

try:
    from .src.worker import publish_final_result
    from .src.adapters import StorageAdapter, ArtifactStoreAdapter, StatusStoreAdapter
except ImportError:
    from src.worker import publish_final_result
    from src.adapters import StorageAdapter, ArtifactStoreAdapter, StatusStoreAdapter

app = df.DFApp()


@app.activity_trigger(input_name="input")
async def final_result_publisher(input: dict):
    """
    Durable Functions Activity that finalizes the pipeline run.
    """
    run_id = input.get("run_id")
    correlation_id = input.get("correlation_id")
    validation_status = input.get("validation_status")
    artifact_ids = input.get("artifact_ids", [])

    logging.info(f"Final result publisher started for RunID: {run_id}")

    if not run_id:
        error_msg = "Missing mandatory input: run_id is required."
        logging.error(error_msg)
        return {
            "publication_status": "failed",
            "friendly_error": error_msg,
        }

    try:
        # 1. Initialize Adapters
        storage = StorageAdapter()

        artifact_container = os.environ.get("ARTIFACT_CONTAINER_NAME", "artifacts")
        status_container = os.environ.get("STATUS_CONTAINER_NAME", "status")

        artifact_adapter = ArtifactStoreAdapter(storage, artifact_container)
        status_adapter = StatusStoreAdapter(storage, status_container)

        # 2. Execute core logic
        result = publish_final_result(
            run_id=run_id,
            validation_status=validation_status,
            artifact_ids=artifact_ids,
            artifact_adapter=artifact_adapter,
            status_adapter=status_adapter,
            correlation_id=correlation_id,
        )

        return result

    except Exception:
        logging.error(f"Unexpected error in final-result-publisher for RunID: {run_id}")
        return {
            "publication_status": "failed",
            "run_id": run_id,
            "friendly_error": "An internal error occurred while finalizing results.",
        }
