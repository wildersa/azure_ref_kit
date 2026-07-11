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
def test_get_chat_response_empty_agent_output(mock_client_class, mock_settings):
    """Verify sanitized error when agent returns empty response."""
    adapter = FoundryAgentAdapter(mock_settings)
    mock_client = MagicMock()
    adapter._project_client = mock_client

    mock_agent = MagicMock()
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_openai_cm = MagicMock()
    mock_openai_cm.__enter__.return_value = mock_openai
    mock_client.get_openai_client.return_value = mock_openai_cm

    # Mock response with empty output
    mock_response = MagicMock()
    mock_response.output = []
    mock_response.output_text = ""
    mock_openai.responses.create.return_value = mock_response

    # Mock conversation
    mock_conv = MagicMock()
    mock_conv.id = "conv_1"
    mock_openai.conversations.create.return_value = mock_conv

    with pytest.raises(
        RuntimeError, match="The agent was unable to provide a response"
    ):
        adapter.get_chat_response("Hello")


@patch("src.adapter.AIProjectClient")
def test_get_chat_response_tool_call_loop(mock_client_class, mock_settings):
    """Verify tool call handling loop."""
    adapter = FoundryAgentAdapter(mock_settings)
    mock_client = MagicMock()
    adapter._project_client = mock_client

    mock_agent = MagicMock()
    mock_client.agents.create_version.return_value = mock_agent

    mock_openai = MagicMock()
    mock_openai_cm = MagicMock()
    mock_openai_cm.__enter__.return_value = mock_openai
    mock_client.get_openai_client.return_value = mock_openai_cm

    # First response asks for a tool call
    mock_tool_call = MagicMock()
    mock_tool_call.type = "function_call"
    mock_tool_call.name = "get_system_status"
    mock_tool_call.arguments = "{}"
    mock_tool_call.call_id = "call_1"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_tool_call]
    mock_response_1.output_text = ""

    # Second response gives the final text
    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "The system is operational."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    # Mock conversation
    mock_conv = MagicMock()
    mock_conv.id = "conv_1"
    mock_openai.conversations.create.return_value = mock_conv

    response = adapter.get_chat_response("How is the system?")
    assert response == "The system is operational."
    assert mock_openai.responses.create.call_count == 2


@patch("src.adapter.AIProjectClient")
def test_get_chat_response_unknown_tool_sanitized(
    mock_client_class, mock_settings, caplog
):
    """Verify sanitized handling of unknown tool request."""
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
    mock_tool_call = MagicMock()
    mock_tool_call.type = "function_call"
    mock_tool_call.name = "secret_internal_tool"
    mock_tool_call.arguments = "{}"
    mock_tool_call.call_id = "call_1"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_tool_call]
    mock_response_1.output_text = ""

    mock_response_2 = MagicMock()
    mock_response_2.output = []
    mock_response_2.output_text = "Sorry, I can't do that."

    mock_openai.responses.create.side_effect = [mock_response_1, mock_response_2]

    # Mock conversation
    mock_conv = MagicMock()
    mock_conv.id = "conv_1"
    mock_openai.conversations.create.return_value = mock_conv

    adapter.get_chat_response("Run secret tool")

    assert "secret_internal_tool" not in caplog.text
    assert "Agent requested unknown tool." in caplog.text

    # Check response sent to agent
    second_call_input = mock_openai.responses.create.call_args_list[1][1]["input"]
    assert "secret_internal_tool" not in str(second_call_input)
    assert "The tool requested is unavailable." in str(second_call_input)
