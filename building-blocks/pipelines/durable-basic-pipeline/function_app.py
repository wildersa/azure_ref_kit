import azure.functions as func
import azure.durable_functions as df
import logging

try:
    from .src.orchestrator import pipeline_orchestrator
    from .src.activities import (
        update_pipeline_run_status,
        ocr_document_intelligence,
        field_validation_worker,
        final_result_publisher,
    )
except ImportError:
    from src.orchestrator import pipeline_orchestrator
    from src.activities import (
        update_pipeline_run_status,
        ocr_document_intelligence,
        field_validation_worker,
        final_result_publisher,
    )

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    """
    HTTP trigger to start an orchestration.
    Used primarily for local testing.
    """
    function_name = req.route_params.get("functionName")
    try:
        input_data = req.get_json()
    except ValueError:
        input_data = None

    instance_id = await client.start_new(function_name, client_input=input_data)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)


# Register Orchestrator
app.orchestration_trigger(context_name="context")(pipeline_orchestrator)

# Register Activities
app.activity_trigger(input_name="status_data")(update_pipeline_run_status)
app.activity_trigger(input_name="input_data")(ocr_document_intelligence)
app.activity_trigger(input_name="input_data")(field_validation_worker)
app.activity_trigger(input_name="input_data")(final_result_publisher)
