import json
import sys
import os
from unittest.mock import MagicMock
import azure.functions as func

# Add parent directory to sys.path so we can import function_app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from function_app import queue_trigger


def test_queue_trigger_success():
    # Mock input message
    input_payload = {
        "function_args": {"input_data": "test-data"},
        "CorrelationId": "test-correlation-id",
    }
    mock_msg = MagicMock(spec=func.QueueMessage)
    mock_msg.get_body.return_value = json.dumps(input_payload).encode("utf-8")

    # Mock output queue
    mock_output_queue = MagicMock(spec=func.Out)

    # Call the function
    queue_trigger(mock_msg, mock_output_queue)

    # Verify the output
    mock_output_queue.set.assert_called_once()
    output_message = json.loads(mock_output_queue.set.call_args[0][0])

    assert output_message["Value"] == "Processed: test-data"
    assert output_message["CorrelationId"] == "test-correlation-id"


def test_queue_trigger_missing_correlation_id():
    # Mock input message without CorrelationId
    input_payload = {"function_args": {"input_data": "test-data"}}
    mock_msg = MagicMock(spec=func.QueueMessage)
    mock_msg.get_body.return_value = json.dumps(input_payload).encode("utf-8")

    # Mock output queue
    mock_output_queue = MagicMock(spec=func.Out)

    # Call the function
    queue_trigger(mock_msg, mock_output_queue)

    # Verify no output was set
    mock_output_queue.set.assert_not_called()
