import azure.functions as func
import logging
import json

app = func.FunctionApp()


@app.queue_trigger(
    arg_name="msg",
    queue_name="agent-tool-input-queue",
    connection="STORAGE_CONNECTION",
)
@app.queue_output(
    arg_name="outputQueue",
    queue_name="agent-tool-output-queue",
    connection="STORAGE_CONNECTION",
)
def queue_trigger(msg: func.QueueMessage, outputQueue: func.Out[str]):
    """
    Queue-triggered function that serves as an async agent tool.
    Processes the message and returns the result with the mandatory CorrelationId.
    """
    try:
        # Parse the incoming message from the agent
        # Expected schema: {"function_args": {...}, "CorrelationId": "..."}
        message_payload = json.loads(msg.get_body().decode("utf-8"))
        correlation_id = message_payload.get("CorrelationId")

        if not correlation_id:
            logging.error("Received tool call missing CorrelationId.")
            return

        logging.info("Processing tool call with CorrelationId: %s", correlation_id)

        # Extract arguments
        function_args = message_payload.get("function_args", {})

        # --- Tool Logic Starts ---
        # Replace this with actual long-running business logic.
        # This example just performs a simple calculation.
        input_value = function_args.get("input_data", "default")
        result_value = f"Processed: {input_value}"
        # --- Tool Logic Ends ---

        # Return the result with the original CorrelationId
        # The agent uses CorrelationId to match this response to its request.
        response_message = {
            "Value": result_value,
            "CorrelationId": correlation_id,
        }

        logging.info("Sending result for CorrelationId: %s", correlation_id)
        outputQueue.set(json.dumps(response_message))

    except Exception:
        # Avoid returning raw stack traces or internal errors to the agent or logs.
        logging.error("Error processing tool call.")

        # Return a safe error envelope to the agent
        try:
            error_message = {
                "Error": "An error occurred while processing the tool call.",
                "CorrelationId": correlation_id
                if "correlation_id" in locals()
                else "unknown",
            }
            outputQueue.set(json.dumps(error_message))
        except Exception:
            logging.error("Failed to send error response.")
