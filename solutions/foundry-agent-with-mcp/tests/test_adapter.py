import pytest
from unittest.mock import MagicMock, patch
from src.adapter import FoundryAgentAdapter
from src.config import Settings


@pytest.fixture
def mock_settings():
    return Settings(
        project_endpoint="https://test.ai.azure.com/api/projects/123",
        agent_name="test-agent",
        model_name="gpt-4o",
        mcp_server_url="https://your-functions-app.azurewebsites.net/runtime/webhooks/mcp",
        mcp_server_label="azure-functions-mcp",
        allowed_tool_names=["get_synthetic_resource"],
    )


@patch("src.adapter.AIProjectClient")
@patch("src.adapter.DefaultAzureCredential")
def test_initialize_client_failure_sanitized(
    mock_cred, mock_client, mock_settings, caplog
):
    """Verify sanitized error when client initialization fails."""
    mock_client.side_effect = Exception("Internal connection error")
    adapter = FoundryAgentAdapter(mock_settings)
    with pytest.raises(RuntimeError, match="Could not connect to the Azure AI service"):
        adapter.initialize_client()
    assert "Internal connection error" not in caplog.text
    assert "Failed to initialize AI Project Client." in caplog.text


@patch("src.adapter.AIProjectClient")
def test_create_or_resolve_agent_failure_sanitized(mock_client, mock_settings, caplog):
    """Verify sanitized error when agent resolution fails."""
    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = MagicMock()
    adapter._project_client.agents.create_version.side_effect = Exception("SDK error")
    with pytest.raises(RuntimeError, match="The agent service encountered an error"):
        adapter.create_or_resolve_agent()
    assert "SDK error" not in caplog.text
    assert "Failed to resolve agent." in caplog.text


@patch("src.adapter.AIProjectClient")
def test_get_chat_response_mcp_approval_loop(mock_client_class, mock_settings):
    """Verify MCP approval handling loop."""
    adapter = FoundryAgentAdapter(mock_settings)
    mock_client = MagicMock()
    adapter._project_client = mock_client

    mock_agent = MagicMock()
    mock_agent.name = "test-agent"
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_openai_cm = MagicMock()
    mock_openai_cm.__enter__.return_value = mock_openai
    mock_client.get_openai_client.return_value = mock_openai_cm

    # First response asks for MCP approval
    mock_req = MagicMock()
    mock_req.type = "mcp_approval_request"
    mock_req.server_label = "azure-functions-mcp"
    mock_req.name = "get_synthetic_resource"
    mock_req.id = "req_1"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_req]
    mock_response_1.output_text = ""
    mock_response_1.id = "resp_1"

    # Second response gives the final text
    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "The system is operational."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    response = adapter.get_chat_response("How is the system?")
    assert response == "The system is operational."
    assert mock_openai.responses.create.call_count == 2

    # Verify approval response
    second_call_args = mock_openai.responses.create.call_args_list[1]
    input_list = second_call_args[1]["input"]
    assert len(input_list) == 1
    assert input_list[0]["type"] == "mcp_approval_response"
    assert input_list[0]["approve"] is True
    assert input_list[0]["approval_request_id"] == "req_1"
    assert second_call_args[1]["previous_response_id"] == "resp_1"


@patch("src.adapter.AIProjectClient")
def test_get_chat_response_unknown_mcp_tool_sanitized(
    mock_client_class, mock_settings, caplog
):
    """Verify sanitized handling of unknown MCP tool request."""
    adapter = FoundryAgentAdapter(mock_settings)
    mock_client = MagicMock()
    adapter._project_client = mock_client

    mock_agent = MagicMock()
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_openai_cm = MagicMock()
    mock_openai_cm.__enter__.return_value = mock_openai
    mock_client.get_openai_client.return_value = mock_openai_cm

    # Agent requests unknown tool
    mock_req = MagicMock()
    mock_req.type = "mcp_approval_request"
    mock_req.server_label = "unknown-server"
    mock_req.name = "secret_tool"
    mock_req.id = "req_1"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_req]
    mock_response_1.output_text = ""
    mock_response_1.id = "resp_1"

    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "Sorry, I can't do that."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    adapter.get_chat_response("Run secret tool")

    assert "secret_tool" not in caplog.text
    assert "Agent requested unauthorized MCP tool." in caplog.text

    # Check approval sent to agent (should be False)
    second_call_input = mock_openai.responses.create.call_args_list[1][1]["input"]
    assert second_call_input[0]["approve"] is False


@patch("src.adapter.AIProjectClient")
def test_get_chat_response_loop_exhaustion_fail_closed(
    mock_client_class, mock_settings
):
    """Verify fail-closed on loop exhaustion with pending approvals."""
    adapter = FoundryAgentAdapter(mock_settings)
    mock_client = MagicMock()
    adapter._project_client = mock_client

    mock_agent = MagicMock()
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_openai_cm = MagicMock()
    mock_openai_cm.__enter__.return_value = mock_openai
    mock_client.get_openai_client.return_value = mock_openai_cm

    # Mock response that ALWAYS asks for approval
    mock_req = MagicMock()
    mock_req.type = "mcp_approval_request"
    mock_req.server_label = "azure-functions-mcp"
    mock_req.name = "get_synthetic_resource"
    mock_req.id = "req_1"

    mock_response = MagicMock()
    mock_response.output = [mock_req]
    mock_response.output_text = "Progressing..."
    mock_response.id = "resp_1"

    mock_openai.responses.create.return_value = mock_response

    with pytest.raises(RuntimeError, match="The agent exceeded the tool call limit"):
        adapter.get_chat_response("Infinite tool calls")
