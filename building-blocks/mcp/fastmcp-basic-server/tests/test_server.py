import pytest
import sys
import os

# Add src to path to ensure local imports work during test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from server import mcp


@pytest.mark.asyncio
async def test_tool_registration():
    """Verify that the tool is correctly registered with the FastMCP instance."""
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}
    assert "get_system_status" in tool_names


@pytest.mark.asyncio
async def test_get_system_status():
    """Verify general system status tool response."""
    result = await mcp.call_tool("get_system_status")
    assert "Operational" in result.content[0].text
