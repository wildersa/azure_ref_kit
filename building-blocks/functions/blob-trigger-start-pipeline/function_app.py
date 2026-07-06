import azure.functions as func
import azure.durable_functions as df
import logging
import uuid
import os
import json
import jsonschema
from datetime import datetime, timezone
from pathlib import Path

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

# Load schema once
SCHEMA_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "shared"
    / "contracts"
    / "pipeline-run.schema.json"
)
with open(SCHEMA_PATH, "r") as f:
    PIPELINE_RUN_SCHEMA = json.load(f)


async def main_logic(myblob: func.InputStream, client: df.DurableOrchestrationClient):
    """
    Core logic extracted from the trigger to facilitate unit testing.
    """
    logging.info(f"Processing blob: {myblob.name} ({myblob.length} bytes)")

    # 1. Extract Metadata
    blob_name_parts = myblob.name.split("/")
    path_customer_id = blob_name_parts[1] if len(blob_name_parts) >= 2 else None

    metadata = myblob.metadata or {}
    customer_id = metadata.get("customer_id") or path_customer_id
    document_type = metadata.get("document_type")
    correlation_id = metadata.get("correlation_id")

    # 2. Validation
    if not customer_id or not document_type:
        logging.error(
            f"Missing mandatory metadata for blob {myblob.name}. "
            f"customer_id: {customer_id}, document_type: {document_type}. "
            "Pipeline start aborted."
        )
        return

    # 3. Normalize PipelineRun Payload
    run_id = str(uuid.uuid4())
    pipeline_run = {
        "id": run_id,
        "customer_id": customer_id,
        "pipeline_type": document_type,
        "status": "pending",
        "correlation_id": correlation_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "business_summary": f"Triggered by upload of {myblob.name}",
    }

    # Add source blob reference (safe path only)
    # The schema might need to be extended or we use business_summary/metadata for it if strict.
    # However, for the orchestrator to work, it needs this reference.
    # We'll pass it as part of a safe metadata extension if allowed or just include it.
    # pipeline-run.schema.json has additionalProperties: false, so we must be careful.

    # Let's check the schema again.
    # id, customer_id, pipeline_type, status, current_step, progress_percent, business_summary,
    # friendly_error, correlation_id, estimated_cost, created_at, started_at, finished_at.
    # No source_blob field. I should probably use business_summary or just pass it in start_new
    # alongside the run, or better: the orchestrator should get it from a specific field.
    # If I can't change the schema, I'll put it in business_summary or a separate input.

    # Actually, the orchestrator call 'client.start_new' takes 'client_input'.
    # If the orchestrator expects more than just the PipelineRun object, I can wrap it.

    orchestration_input = {
        "pipeline_run": pipeline_run,
        "source_blob": myblob.name,  # Safe path reference
    }

    # 4. Contract Validation
    try:
        jsonschema.validate(instance=pipeline_run, schema=PIPELINE_RUN_SCHEMA)
    except jsonschema.ValidationError as e:
        logging.error(f"PipelineRun payload failed contract validation: {e.message}")
        return

    # 5. Durable Orchestration Hand-off
    orchestrator_name = os.environ.get(
        "TARGET_ORCHESTRATOR_NAME", "pipeline_orchestrator"
    )

    try:
        instance_id = await client.start_new(
            orchestrator_name, instance_id=run_id, client_input=orchestration_input
        )
        logging.info(
            f"Successfully started orchestration '{orchestrator_name}' with ID '{instance_id}'."
        )
    except Exception:
        logging.error(
            f"Failed to start orchestration for run {run_id}. The process will be retried by the trigger."
        )
        raise


@app.blob_trigger(
    arg_name="myblob",
    path="uploads/{customer_id}/{name}",
    connection="BlobStorageConnectionString",
    source="EventGrid",
)
@app.durable_client_input(client_name="client")
async def blob_trigger_start_pipeline(
    myblob: func.InputStream, client: df.DurableOrchestrationClient
):
    """
    Blob trigger function that starts a Document AI pipeline.
    """
    await main_logic(myblob, client)
