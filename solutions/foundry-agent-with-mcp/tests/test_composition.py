import pytest
from src.config import Settings
from src.agent_definition import get_tool_definitions

def test_azure_functions_mcp_composition_contract(monkeypatch):
    """
    Verify that the solution correctly composes with the Azure Functions MCP endpoint
    using the expected contract values from the README and building block.
    """
    # Use the specific values defined in the solution's README/Contract
    expected_url = "https://your-functions-app.azurewebsites.net/runtime/webhooks/mcp"
    expected_label = "azure-functions-mcp"
    expected_tool = "get_synthetic_resource"

    monkeypatch.setenv("AZURE_AI_PROJECT_ENDPOINT", "https://res.ai.azure.com/api/projects/proj-123")
    monkeypatch.setenv("AZURE_AI_AGENT_NAME", "mcp-status-assistant")
    monkeypatch.setenv("AZURE_AI_MODEL_NAME", "gpt-4o")
    monkeypatch.setenv("MCP_SERVER_URL", expected_url)
    monkeypatch.setenv("MCP_SERVER_LABEL", expected_label)
    monkeypatch.setenv("ALLOWED_TOOL_NAMES", expected_tool)

    settings = Settings.from_env()

    # Assert settings are loaded correctly
    assert settings.mcp_server_url == expected_url
    assert settings.mcp_server_label == expected_label
    assert expected_tool in settings.allowed_tool_names

    # Assert tool definitions match the contract
    tools = get_tool_definitions(settings)
    assert len(tools) == 1
    mcp_tool = tools[0]

    # We are using mock_sdk.py during tests
    assert mcp_tool.type == "mcp"
    assert mcp_tool.server_url == expected_url
    assert mcp_tool.server_label == expected_label
    assert mcp_tool.allowed_tools == [expected_tool]
    assert mcp_tool.require_approval == "always"
