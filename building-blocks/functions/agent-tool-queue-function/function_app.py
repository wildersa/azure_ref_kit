import azure.functions as func
import logging
import json
import uuid
from datetime import datetime, timezone

try:
    from .src.tool import process_queue_job_safe, StatusStore
    from .src.models import SubmitRequest, SubmitResponse, JobStatus, JobInput
except ImportError:
    from src.tool import process_queue_job_safe, StatusStore
    from src.models import SubmitRequest, SubmitResponse, JobStatus, JobInput

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="submit", methods=["POST"])
@app.queue_output(
    arg_name="outputQueue",
    queue_name="agent-tool-input",
    connection="AzureWebJobsStorage",
)
def submit_job(req: func.HttpRequest, outputQueue: func.Out[str]) -> func.HttpResponse:
    """
    HTTP POST endpoint to submit a new asynchronous job.
    Validates the request, generates a correlation ID, enqueues the job,
    and persists the initial PENDING status.
    """
    logging.info("Submit job request received.")

    try:
        # 1. Parse and validate request
        try:
            req_body = req.get_json()
            submit_req = SubmitRequest(**req_body)
        except (ValueError, Exception) as e:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid request: {str(e)}"}),
                status_code=400,
                mimetype="application/json",
            )

        # 2. Generate opaque correlation ID
        correlation_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # 3. Persist PENDING status
        store = StatusStore()
        store.update_status(
            correlation_id,
            JobStatus.PENDING,
            business_summary="Job enqueued, awaiting processing.",
            created_at=created_at,
        )

        # 4. Enqueue the job message
        job_input = JobInput(
            correlation_id=correlation_id,
            operation_type=submit_req.operation_type,
            parameters=submit_req.parameters,
        )
        outputQueue.set(job_input.model_dump_json())

        # 5. Return success response
        response = SubmitResponse(correlation_id=correlation_id, status=JobStatus.PENDING)
        return func.HttpResponse(
            response.model_dump_json(), status_code=202, mimetype="application/json"
        )

    except Exception:
        logging.error("Unhandled exception in submit_job boundary.")
        return func.HttpResponse(
            json.dumps({"error": "An internal error occurred."}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="status/{correlation_id}", methods=["GET"])
def get_job_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP GET endpoint to retrieve the status and result of a job.
    """
    correlation_id = req.route_params.get("correlation_id")
    logging.info("Status request received for correlation_id: %s", correlation_id)

    if not correlation_id:
        return func.HttpResponse(
            json.dumps({"error": "Correlation ID is required."}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        store = StatusStore()
        status_res = store.get_status(correlation_id)

        if not status_res:
            return func.HttpResponse(
                json.dumps({"error": "Job not found."}),
                status_code=404,
                mimetype="application/json",
            )

        return func.HttpResponse(
            status_res.model_dump_json(), status_code=200, mimetype="application/json"
        )

    except Exception:
        logging.error("Unhandled exception in get_job_status boundary.")
        return func.HttpResponse(
            json.dumps({"error": "An internal error occurred."}),
            status_code=500,
            mimetype="application/json",
        )


@app.queue_trigger(
    arg_name="msg",
    queue_name="agent-tool-input",
    connection="AzureWebJobsStorage",
)
@app.queue_output(
    arg_name="outputQueue",
    queue_name="agent-tool-output",
    connection="AzureWebJobsStorage",
)
def agent_tool_queue_trigger(msg: func.QueueMessage, outputQueue: func.Out[str]) -> None:
    """
    Azure Function triggered by a Storage Queue message.
    Executes tool logic, updates the status table, and emits result to output queue.
    """
    logging.info("Queue trigger function processing a message.")

    try:
        # 1. Parse message body
        try:
            body = msg.get_body().decode("utf-8")
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            logging.error("Failed to decode or parse queue message as JSON.")
            return

        # 2. Execute tool logic safely (includes status updates)
        store = StatusStore()
        result = process_queue_job_safe(payload, store=store)

        # 3. Emit result to output queue for the agent to consume
        outputQueue.set(json.dumps(result))
        logging.info(
            "Successfully processed job. CorrelationId: %s",
            result.get("correlation_id"),
        )

    except Exception:
        logging.error("Unexpected error in the Function queue trigger.")
