import sys
import os
from unittest.mock import patch

# Add solution root to sys.path to support relative imports in src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapter import FoundryAgentAdapter
from src.config import Settings
from src.mock_sdk import AIProjectClient


def test_adapter_initialization():
    settings = Settings(project_endpoint="https://mock.endpoint")
    adapter = FoundryAgentAdapter(settings)

    # Use mock client for initialization
    mock_client = AIProjectClient(endpoint=settings.project_endpoint, credential=None)
    adapter._project_client = mock_client

    adapter.initialize_client()
    assert adapter._project_client is not None


@patch("src.adapter.submit_task")
def test_get_chat_response_submit(mock_submit):
    mock_submit.return_value = {"correlation_id": "mock-id", "status": "pending"}

    settings = Settings(project_endpoint="https://mock.endpoint")
    # Inject the mock AIProjectClient
    mock_project_client = AIProjectClient(
        endpoint=settings.project_endpoint, credential=None
    )
    adapter = FoundryAgentAdapter(settings, project_client=mock_project_client)

    response = adapter.get_chat_response("Please submit a ping task")

    assert "mock-id" in response
    mock_submit.assert_called_once()


@patch("src.adapter.get_task_status")
def test_get_chat_response_status(mock_status):
    mock_status.return_value = {
        "id": "mock-id",
        "status": "completed",
        "result_data": {"val": 42},
    }

    settings = Settings(project_endpoint="https://mock.endpoint")

    # Mock the response sequence for the status check
    from src.mock_sdk import Response, OutputItem, OpenAIClient, ResponseClient

    class MockStatusOpenAIClient(OpenAIClient):
        def __init__(self):
            super().__init__()
            self.responses = ResponseClient(self.create_response)

        def create_response(self, input, **kwargs):
            if isinstance(input, str) and "status" in input.lower():
                return Response(
                    "res-1",
                    [
                        OutputItem(
                            "function_call",
                            name="get_task_status",
                            arguments='{"correlation_id": "mock-id"}',
                            call_id="call-1",
                        )
                    ],
                )
            elif isinstance(input, list):
                return Response("res-2", [], "The task is completed with result 42.")
            return Response("res-def", [], "I am a mock agent.")

    mock_project_client = AIProjectClient(
        endpoint=settings.project_endpoint, credential=None
    )
    mock_project_client.get_openai_client = lambda: MockStatusOpenAIClient()

    adapter = FoundryAgentAdapter(settings, project_client=mock_project_client)

    response = adapter.get_chat_response("What is the status of task mock-id?")

    assert "completed" in response or "42" in response
    mock_status.assert_called_once_with(correlation_id="mock-id", settings=settings)
