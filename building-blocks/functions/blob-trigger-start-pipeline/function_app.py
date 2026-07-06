import azure.functions as func
import azure.durable_functions as df
import logging
import uuid
import os
import json
import jsonschema
from datetime import datetime, timezone
from pathlib import Path

app = df.DFApp()

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
    run_id = str(uuid.uuid4())
    logging.info(f"Processing new pipeline request. RunID: {run_id}")

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
            f"Missing mandatory metadata for run {run_id}. Pipeline start aborted."
        )
        return

    # 3. Normalize PipelineRun Payload
    pipeline_run = {
        "id": run_id,
        "customer_id": customer_id,
        "pipeline_type": document_type,
        "status": "pending",
        "correlation_id": correlation_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "business_summary": "Pipeline triggered by document upload.",
    }

    orchestration_input = {
        "pipeline_run": pipeline_run,
        "source_blob": myblob.name,  # Safe internal path reference
    }

    # 4. Contract Validation
    try:
        jsonschema.validate(instance=pipeline_run, schema=PIPELINE_RUN_SCHEMA)
    except jsonschema.ValidationError:
        logging.error(
            f"PipelineRun payload failed contract validation for run {run_id}. "
            "Please check the data format against the shared schema."
        )
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
            f"Successfully started orchestration for run {run_id} with instance ID {instance_id}."
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
