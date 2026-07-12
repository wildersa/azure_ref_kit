import pytest
import sys
import os
import json
from fastmcp.exceptions import ValidationError

# Add src to path to ensure local imports work during test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from server import mcp, get_synthetic_resource


@pytest.mark.asyncio
async def test_tool_registration():
    """Verify that the tool is correctly registered with the FastMCP instance."""
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}
    assert "get_synthetic_resource" in tool_names


@pytest.mark.asyncio
async def test_get_synthetic_resource_valid():
    """Verify valid resource retrieval."""
    # Test compute
    result = await mcp.call_tool("get_synthetic_resource", arguments={"resource_type": "compute"})
    assert len(result.content) > 0
    data = json.loads(result.content[0].text)
    assert data["id"] == "comp-001"
    assert data["status"] == "running"

    # Test storage
    result = await mcp.call_tool("get_synthetic_resource", arguments={"resource_type": "storage"})
    assert len(result.content) > 0
    data = json.loads(result.content[0].text)
    assert data["id"] == "stg-001"
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_get_synthetic_resource_invalid():
    """Verify handling of unsupported resource types (fail-closed)."""
    # FastMCP uses Pydantic to validate Literals and raises ValidationError for invalid inputs
    with pytest.raises(ValidationError) as excinfo:
        await mcp.call_tool("get_synthetic_resource", arguments={"resource_type": "invalid"})

    assert "resource_type" in str(excinfo.value)
    assert "Input should be 'compute' or 'storage'" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_synthetic_resource_no_args():
    """Verify behavior when arguments are missing."""
    # FastMCP raises ValidationError when required arguments are missing
    with pytest.raises(ValidationError):
        await mcp.call_tool("get_synthetic_resource", arguments={})


def test_get_synthetic_resource_internal_logic():
    """Verify the internal logic of the tool function directly."""
    # Valid input
    assert get_synthetic_resource("compute")["id"] == "comp-001"

    # Invalid input (simulating bypass of Pydantic validation if called directly)
    result = get_synthetic_resource("unknown")
    assert "error" in result
    assert result["error"] == "Unsupported resource type"
    assert "supported_types" in result

    # Verify no leakage of internal paths/secrets even in manual call
    result_str = str(result)
    assert "src/" not in result_str
    assert "Traceback" not in result_str
