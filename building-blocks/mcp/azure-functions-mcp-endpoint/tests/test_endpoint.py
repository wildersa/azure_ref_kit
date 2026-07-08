import json
import os
import sys

# Add src to path if needed for static analysis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


def test_tool_definition_static():
    """
    Statically verify the tool definition in function_app.py
    Since we might not have the latest azure-functions SDK in the environment,
    we perform a basic content check.
    """
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/function_app.py")
    )
    with open(src_path, "r") as f:
        content = f.read()

    assert "@app.mcp_tool_trigger" in content
    assert 'tool_name="get_service_info"' in content
    assert 'tool_name="get_resource_health"' in content
    assert "def get_service_info(context: str) -> str:" in content
    assert "def get_resource_health(context: str) -> str:" in content


def test_host_json_valid():
    """
    Verify host.json has the required MCP extension configuration.
    """
    host_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/host.json")
    )
    with open(host_path, "r") as f:
        data = json.load(f)

    assert "extensions" in data
    assert "mcp" in data["extensions"]
    assert data["extensions"]["mcp"]["serverName"] == "ReferenceMcpServer"
    assert "extensionBundle" in data
    assert data["extensionBundle"]["version"] == "[4.0.0, 5.0.0)"


def test_requirements_file():
    """
    Verify requirements.txt specifies the correct SDK version.
    """
    req_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/requirements.txt")
    )
    with open(req_path, "r") as f:
        content = f.read()

    assert "azure-functions>=1.24.0" in content
