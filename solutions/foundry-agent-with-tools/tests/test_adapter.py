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
def test_initialize_client_failure(mock_cred, mock_client, mock_settings):
    """Verify sanitized error when client initialization fails."""
    mock_client.side_effect = Exception("Internal connection error")
    adapter = FoundryAgentAdapter(mock_settings)
    with pytest.raises(RuntimeError, match="Could not connect to the Azure AI service"):
        adapter.initialize_client()


@patch("src.adapter.AIProjectClient")
def test_create_or_resolve_agent_failure(mock_client, mock_settings):
    """Verify sanitized error when agent resolution fails."""
    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = MagicMock()
    adapter._project_client.agents.create_version.side_effect = Exception("SDK error")
    with pytest.raises(RuntimeError, match="The agent service encountered an error"):
        adapter.create_or_resolve_agent()


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
