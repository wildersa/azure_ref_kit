from src.agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions
from src.config import Settings


def test_system_instructions_safety_keywords():
    """Verify system instructions contain safety-related keywords."""
    keywords = [
        "safety",
        "privacy",
        "do not expose",
        "technical details",
        "internal",
        "friendly",
        "non-technical",
        "mcp",
    ]

    instructions_lower = SYSTEM_INSTRUCTIONS.lower()
    for keyword in keywords:
        assert keyword in instructions_lower


def test_mcp_tool_configuration():
    """Verify the MCP tool is configured correctly in the definition."""
    settings = Settings(
        project_endpoint="https://res.ai.azure.com/api/projects/proj-123",
        agent_name="my-agent",
        model_name="gpt-4o",
        mcp_server_url="https://mcp.com/api",
        mcp_server_label="test-mcp",
        allowed_tool_names=["get_status"],
    )
    tools = get_tool_definitions(settings)
    assert len(tools) == 1
    mcp_tool = tools[0]

    # Verify attributes (matches mock_sdk or real SDK MCPTool)
    assert mcp_tool.type == "mcp"
    assert mcp_tool.server_label == "test-mcp"
    assert mcp_tool.require_approval == "always"
    assert mcp_tool.server_url == "https://mcp.com/api"
    assert mcp_tool.allowed_tools == ["get_status"]


def test_no_secrets_in_instructions():
    """Verify no real secrets or IDs are in the system instructions."""
    import re

    # Pattern for UUID (Subscription/Tenant IDs)
    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    )
    assert not uuid_pattern.search(SYSTEM_INSTRUCTIONS)
