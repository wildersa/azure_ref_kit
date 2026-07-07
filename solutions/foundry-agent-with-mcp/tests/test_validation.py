from src.agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions


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
    tools = get_tool_definitions()
    assert len(tools) == 1
    mcp_tool = tools[0]

    # Verify attributes (matches mock_sdk or real SDK MCPTool)
    assert mcp_tool.type == "mcp"
    assert mcp_tool.server_label == "system-status-server"
    assert mcp_tool.require_approval == "always"
    assert mcp_tool.server_url is not None


def test_no_secrets_in_instructions():
    """Verify no real secrets or IDs are in the system instructions."""
    import re

    # Pattern for UUID (Subscription/Tenant IDs)
    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    )
    assert not uuid_pattern.search(SYSTEM_INSTRUCTIONS)
