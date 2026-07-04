import azure.functions as func
import azure.durable_functions as df
import logging
from datetime import datetime, timezone

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    function_name = req.route_params.get("functionName")
    instance_id = await client.start_new(function_name)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

def pipeline_orchestrator(context: df.DurableOrchestrationContext):
    """
    Main orchestrator logic for the pipeline.
    Initializes the PipelineRun and coordinates steps.

    NOTE: Orchestrators must be deterministic. We use context.current_utc_datetime
    instead of datetime.now() to ensure replays are consistent.
    """
    run_id = context.instance_id
    # In real scenarios, this would come from context.get_input()
    customer_id = "default-customer"

    current_time = context.current_utc_datetime.isoformat()

    # 1. Initialize Pipeline Run (Customer-safe status)
    yield context.call_activity("update_pipeline_run_status", {
        "id": run_id,
        "customer_id": customer_id,
        "pipeline_type": "basic-reference-pipeline",
        "status": "running",
        "created_at": current_time,
        "started_at": current_time,
        "business_summary": "Pipeline started."
    })

    try:
        # 2. Execute Step 1
        yield context.call_activity("pipeline_step_activity", {
            "run_id": run_id,
            "name": "data_validation",
            "input_summary": "Checking input data integrity."
        })

        # 3. Execute Step 2
        yield context.call_activity("pipeline_step_activity", {
            "run_id": run_id,
            "name": "ai_processing",
            "input_summary": "Running AI model inference."
        })

        # 4. Finalize Pipeline Run
        finish_time = context.current_utc_datetime.isoformat()
        yield context.call_activity("update_pipeline_run_status", {
            "id": run_id,
            "customer_id": customer_id,
            "pipeline_type": "basic-reference-pipeline",
            "status": "completed",
            "created_at": current_time,
            "finished_at": finish_time,
            "business_summary": "Pipeline completed successfully."
        })

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        error_time = context.current_utc_datetime.isoformat()
        yield context.call_activity("update_pipeline_run_status", {
            "id": run_id,
            "customer_id": customer_id,
            "pipeline_type": "basic-reference-pipeline",
            "status": "failed",
            "created_at": current_time,
            "finished_at": error_time,
            "friendly_error": "An error occurred during pipeline execution. Please contact support."
        })
        raise

# Register the orchestrator with the App
app.orchestration_trigger(context_name="context")(pipeline_orchestrator)

@app.activity_trigger(input_name="statusData")
def update_pipeline_run_status(statusData: dict):
    """
    Activity to update the overall pipeline run status.
    In a real implementation, this would write to a database (e.g., Cosmos DB).
    """
    logging.info(f"Updating PipelineRun {statusData.get('id')} to {statusData.get('status')}")
    # Contract validation would happen here
    return True

@app.activity_trigger(input_name="stepData")
def pipeline_step_activity(stepData: dict):
    """
    Demonstrates a pipeline step activity that updates its own status.
    """
    run_id = stepData.get("run_id")
    step_name = stepData.get("name")

    logging.info(f"Starting step {step_name} for run {run_id}")

    # Simulate work
    logging.info(f"Step {step_name} completed.")

    # Update step to completed
    return {
        "run_id": run_id,
        "name": step_name,
        "status": "completed",
        "output_summary": f"Step {step_name} finished successfully."
    }
