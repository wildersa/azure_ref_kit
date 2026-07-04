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
        logging.info("Received tool call: %s", json.dumps(message_payload))

        # Extract arguments and CorrelationId
        function_args = message_payload.get("function_args", {})
        correlation_id = message_payload.get("CorrelationId")

        if not correlation_id:
            logging.error("Message missing CorrelationId.")
            return

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

        logging.info("Sending result: %s", json.dumps(response_message))
        outputQueue.set(json.dumps(response_message))

    except Exception as e:
        # Avoid returning raw stack traces to the agent for security reasons.
        logging.error("Error processing tool call: %s", str(e))
        # Optional: Return a safe error envelope if the agent expects it.
