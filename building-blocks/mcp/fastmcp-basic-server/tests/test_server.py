import pytest
import sys
import os

# Add src to path to ensure local imports work during test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from server import mcp


@pytest.mark.asyncio
async def test_tool_registration():
    """Verify that all tools are correctly registered with the FastMCP instance."""
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}
    assert "get_system_status" in tool_names
    assert "get_service_health" in tool_names


@pytest.mark.asyncio
async def test_get_service_health_valid():
    """Verify health check for a known valid service."""
    result = await mcp.call_tool(
        "get_service_health", arguments={"service_name": "database"}
    )
    assert "Healthy" in result.content[0].text
    assert "clusters operational" in result.content[0].text


@pytest.mark.asyncio
async def test_get_service_health_invalid():
    """Verify handling of an unknown service name."""
    result = await mcp.call_tool(
        "get_service_health", arguments={"service_name": "unknown-service"}
    )
    assert "Unknown service" in result.content[0].text
    assert "unknown-service" in result.content[0].text


@pytest.mark.asyncio
async def test_get_system_status():
    """Verify general system status tool response."""
    result = await mcp.call_tool("get_system_status")
    assert "Operational" in result.content[0].text
