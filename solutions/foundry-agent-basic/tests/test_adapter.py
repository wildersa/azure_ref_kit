from unittest.mock import MagicMock, patch
import pytest
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
def test_initialize_client_success(mock_credential, mock_project_client, mock_settings):
    """Test that initialize_client creates an AIProjectClient."""
    adapter = FoundryAgentAdapter(mock_settings)
    adapter.initialize_client()

    mock_project_client.assert_called_once_with(
        endpoint=mock_settings.project_endpoint,
        credential=mock_credential.return_value,
    )
    assert adapter._project_client is not None


@patch("src.adapter.AIProjectClient")
def test_initialize_client_failure(mock_project_client, mock_settings):
    """Test that initialize_client raises a sanitized RuntimeError on failure."""
    mock_project_client.side_effect = Exception("Internal SDK Error")
    adapter = FoundryAgentAdapter(mock_settings)

    with pytest.raises(RuntimeError, match="Could not connect to the Azure AI service"):
        adapter.initialize_client()


def test_create_or_resolve_agent_success(mock_settings):
    """Test that create_or_resolve_agent calls the SDK and returns an agent."""
    mock_client = MagicMock()
    mock_agent = MagicMock()
    mock_agent.name = "test-agent-name"
    mock_client.agents.create_version.return_value = mock_agent

    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = mock_client

    agent = adapter.create_or_resolve_agent()

    assert agent.name == "test-agent-name"
    mock_client.agents.create_version.assert_called_once()


def test_get_chat_response_success(mock_settings):
    """Test that get_chat_response returns the output text from the SDK."""
    mock_client = MagicMock()
    mock_agent = MagicMock()
    mock_agent.name = "test-agent-name"
    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = "Expected response text"

    mock_client.agents.create_version.return_value = mock_agent
    mock_client.get_openai_client.return_value = mock_openai
    mock_openai.responses.create.return_value = mock_response

    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = mock_client

    response = adapter.get_chat_response("Hello")

    assert response == "Expected response text"
    mock_openai.responses.create.assert_called_once()


@pytest.mark.parametrize("empty_response", ["", None, "   "])
def test_get_chat_response_empty_output(mock_settings, empty_response):
    """Test that get_chat_response raises a sanitized RuntimeError for empty response."""
    mock_client = MagicMock()
    mock_agent = MagicMock()
    mock_agent.name = "test-agent-name"
    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = empty_response

    mock_client.agents.create_version.return_value = mock_agent
    mock_client.get_openai_client.return_value = mock_openai
    mock_openai.responses.create.return_value = mock_response

    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = mock_client

    with pytest.raises(
        RuntimeError, match="The agent was unable to provide a response"
    ):
        adapter.get_chat_response("Hello")


def test_get_chat_response_failure(mock_settings):
    """Test that get_chat_response raises a sanitized RuntimeError on failure."""
    mock_client = MagicMock()
    mock_client.agents.create_version.side_effect = Exception("Internal SDK Error")

    adapter = FoundryAgentAdapter(mock_settings)
    adapter._project_client = mock_client

    with pytest.raises(RuntimeError, match="The agent service encountered an error"):
        adapter.get_chat_response("Hello")
