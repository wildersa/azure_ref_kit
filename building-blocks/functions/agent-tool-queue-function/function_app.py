import azure.functions as func
import logging
import json

try:
    from .src.tool import process_queue_job_safe
except ImportError:
    from src.tool import process_queue_job_safe

app = func.FunctionApp()


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
def agent_tool_queue_trigger(
    msg: func.QueueMessage, outputQueue: func.Out[str]
) -> None:
    """
    Azure Function triggered by a Storage Queue message.
    Executes a deterministic tool operation and emits the result to an output queue.
    """
    logging.info("Python Queue trigger function processed a message.")

    try:
        # 1. Parse message body
        try:
            body = msg.get_body().decode("utf-8")
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            logging.error("Failed to decode or parse queue message as JSON.")
            # We cannot easily return a result without a correlation_id if parsing fails
            return

        # 2. Execute tool logic safely
        # The tool handles its own internal validation and error redaction.
        result = process_queue_job_safe(payload)

        # 3. Emit result to output queue
        outputQueue.set(json.dumps(result))
        logging.info(
            "Successfully processed job. CorrelationId: %s",
            result.get("correlation_id"),
        )

    except Exception:
        # P0: Do not log stack traces or leak internals
        logging.error("An unexpected error occurred in the Function trigger.")
        # If we reach here, something went wrong outside the safe tool boundary.
        # We don't have a reliable correlation_id here if it failed early.
