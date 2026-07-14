import json
import sys
import os
import re

# Ensure the 'src' directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from function_app import get_synthetic_resource


def test_get_synthetic_resource_compute_valid():
    """Test valid request for compute resource."""
    context = json.dumps({"arguments": {"resource_type": "compute"}})
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    assert response["id"] == "comp-001"
    assert response["status"] == "running"
    assert "error" not in response


def test_get_synthetic_resource_storage_valid():
    """Test valid request for storage resource."""
    context = json.dumps({"arguments": {"resource_type": "storage"}})
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    assert response["id"] == "stg-001"
    assert response["status"] == "available"
    assert "error" not in response


def test_get_synthetic_resource_invalid_type():
    """Test request with unsupported resource type."""
    context = json.dumps({"arguments": {"resource_type": "database"}})
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    assert "error" in response
    assert "Unsupported resource type" in response["error"]


def test_get_synthetic_resource_missing_arg():
    """Test request with missing resource_type argument."""
    context = json.dumps({"arguments": {}})
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    assert "error" in response
    assert "Missing required argument" in response["error"]


def test_get_synthetic_resource_malformed_json():
    """Test request with malformed JSON context."""
    context = "{ malformed json }"
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    assert "error" in response
    assert "Invalid tool invocation context" in response["error"]


def test_get_synthetic_resource_no_internal_leakage():
    """Test that no internal or secret fields are leaked."""
    context = json.dumps({"arguments": {"resource_type": "compute"}})
    response_str = get_synthetic_resource(context)
    response = json.loads(response_str)

    # Expected fields
    allowed_fields = {"id", "type", "status", "region"}
    actual_fields = set(response.keys())

    assert actual_fields.issubset(allowed_fields)
    assert "connection_string" not in response
    assert "secret" not in response
    assert "key" not in response


def test_no_mutation_operations_exposed():
    """Verify that only the read-only tool is present in function_app.py and no mutation triggers exist."""
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/function_app.py")
    )
    with open(src_path, "r") as f:
        content = f.read()

    # We only expect exactly one mcp_tool_trigger decorator
    triggers = re.findall(r"@app\.mcp_tool_trigger", content)
    assert len(triggers) == 1, (
        f"Expected exactly 1 MCP tool trigger, found {len(triggers)}"
    )

    # Ensure the single tool name is the read-only one
    assert 'tool_name="get_synthetic_resource"' in content

    # Check for keywords that might indicate hidden mutation triggers
    # We look for other trigger types that might be misused or added by mistake
    mutation_triggers = [
        "@app.route",
        "@app.blob_trigger",
        "@app.queue_trigger",
        "@app.timer_trigger",
    ]
    for trigger in mutation_triggers:
        assert trigger not in content, (
            f"Prohibited trigger {trigger} found in read-only reference."
        )
