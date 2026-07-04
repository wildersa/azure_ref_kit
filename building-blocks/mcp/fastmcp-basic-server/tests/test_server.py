import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from server import mcp

@pytest.mark.asyncio
async def test_tool_registration():
    """Verify that the get_system_status tool is correctly registered."""
    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    assert "get_system_status" in tool_names

@pytest.mark.asyncio
async def test_get_system_status_content():
    """Verify that the get_system_status tool returns the expected static status."""
    # Find the tool function
    tools = await mcp.list_tools()
    target_tool = next((t for t in tools if t.name == "get_system_status"), None)
    assert target_tool is not None

    # FastMCP tools can be called directly or via mcp.call_tool
    result = await mcp.call_tool("get_system_status")

    # result is a ToolResult object, we need to check its content
    assert hasattr(result, "content")
    text_content = result.content[0].text
    assert "Status: Operational" in text_content
    assert "FastMCP Basic Server Reference" in text_content
