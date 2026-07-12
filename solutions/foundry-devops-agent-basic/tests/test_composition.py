import json
from unittest.mock import MagicMock, patch
import pytest
from src.adapter import FoundryDevOpsAgentAdapter
from src.config import Settings


@pytest.fixture
def mock_settings():
    return Settings(
        project_endpoint="https://test.ai.azure.com/api/projects/123",
        agent_name="test-agent",
        model_name="gpt-4o",
        devops_pat="test-pat",
        organization_url="https://dev.azure.com/test-org",
        project="test-project",
        build_id=456,
    )


@patch("src.adapter.AIProjectClient")
@patch("src.adapter.DefaultAzureCredential")
@patch("src.adapter.tool.get_build_status_safe")
def test_adapter_chat_response_with_tool_call(
    mock_get_status, mock_credential, mock_client_class, mock_settings
):
    """
    Proves successful tool composition:
    1. Agent requests get_build_status.
    2. Adapter routes to tool.get_build_status_safe.
    3. Result is returned to the agent.
    """
    # Mock AIProjectClient and its sub-objects
    mock_client = mock_client_class.return_value
    mock_agent = MagicMock()
    mock_agent.name = "resolved-agent"
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_client.get_openai_client.return_value.__enter__.return_value = mock_openai

    # Mock Conversation and Responses
    mock_conv = MagicMock()
    mock_conv.id = "conv-123"
    mock_openai.conversations.create.return_value = mock_conv

    # First response contains a function call
    mock_call = MagicMock()
    mock_call.type = "function_call"
    mock_call.name = "get_build_status"
    mock_call.arguments = json.dumps({
        "organization_url": "https://dev.azure.com/test-org",
        "project": "test-project",
        "build_id": 456
    })
    mock_call.call_id = "call-789"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_call]

    # Second response contains final text
    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "The build succeeded."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    # Mock the tool implementation result
    mock_get_status.return_value = {
        "status": "completed",
        "result": "succeeded",
        "summary": "Build succeeded.",
        "portal_url": "https://dev.azure.com/test-org/test-project/_build/results?buildId=456"
    }

    # Execute
    adapter = FoundryDevOpsAgentAdapter(mock_settings)
    response = adapter.get_chat_response("What is my build status?")

    # Assertions
    assert response == "The build succeeded."
    mock_get_status.assert_called_once()

    # Verify the tool was called with the correct arguments from the agent
    args = mock_get_status.call_args[0][0]
    assert args["build_id"] == 456
    assert args["project"] == "test-project"


@patch("src.adapter.AIProjectClient")
@patch("src.adapter.tool.get_build_status_safe")
def test_adapter_handles_tool_failure_sanitized(
    mock_get_status, mock_client_class, mock_settings
):
    """
    Verifies that tool failures are caught and a sanitized error is returned to the agent.
    """
    mock_client = mock_client_class.return_value
    mock_openai = MagicMock()
    mock_client.get_openai_client.return_value.__enter__.return_value = mock_openai
    mock_openai.conversations.create.return_value.id = "conv-123"
    mock_client.agents.create_version.return_value.name = "agent-123"

    # Agent calls the tool
    mock_call = MagicMock()
    mock_call.type = "function_call"
    mock_call.name = "get_build_status"
    mock_call.arguments = json.dumps({
        "organization_url": "https://dev.azure.com/test-org",
        "project": "test-project",
        "build_id": 456
    })

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_call]

    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "Sorry, I couldn't get the status."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    # Tool raises an exception (e.g. connection error)
    mock_get_status.side_effect = Exception("Internal technical error")

    adapter = FoundryDevOpsAgentAdapter(mock_settings)
    adapter.get_chat_response("status?")

    # Verify the second create call received a sanitized error
    second_call_input = mock_openai.responses.create.call_args_list[1][1]["input"]
    assert len(second_call_input) == 1
    output_json = json.loads(second_call_input[0]["output"])
    assert output_json["error"] == "The status tool encountered an error."
    # Ensure raw exception didn't leak
    assert "Internal technical error" not in second_call_input[0]["output"]


@patch("src.adapter.AIProjectClient")
@patch("src.adapter.tool.get_build_status_safe")
def test_adapter_rejects_out_of_scope_build(
    mock_get_status, mock_client_class, mock_settings
):
    """
    Verifies that the adapter rejects tool calls for organizations, projects, or builds
    not explicitly defined in the solution settings.
    """
    mock_client = mock_client_class.return_value
    mock_openai = MagicMock()
    mock_client.get_openai_client.return_value.__enter__.return_value = mock_openai
    mock_openai.conversations.create.return_value.id = "conv-123"
    mock_client.agents.create_version.return_value.name = "agent-123"

    # Agent attempts to query a DIFFERENT organization or build
    mock_call = MagicMock()
    mock_call.type = "function_call"
    mock_call.name = "get_build_status"
    mock_call.arguments = json.dumps({
        "organization_url": "https://dev.azure.com/DIFFERENT-ORG",
        "project": "test-project",
        "build_id": 456
    })
    mock_call.call_id = "call-wrong"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_call]

    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "I cannot access that."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    adapter = FoundryDevOpsAgentAdapter(mock_settings)
    adapter.get_chat_response("status of DIFFERENT-ORG?")

    # Verify the tool implementation was NEVER called
    mock_get_status.assert_not_called()

    # Verify the error returned to the agent is sanitized and explains the scope limit
    second_call_input = mock_openai.responses.create.call_args_list[1][1]["input"]
    output_json = json.loads(second_call_input[0]["output"])
    assert output_json["error"] == "The tool requested is unavailable for the specified scope."
