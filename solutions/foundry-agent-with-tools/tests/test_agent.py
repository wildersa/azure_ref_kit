import json
import os
import re
from src.agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions


def test_tool_definitions_present():
    """Verify get_system_status tool is present."""
    tools = get_tool_definitions()
    tool_names = [t["function"]["name"] for t in tools]

    assert "get_system_status" in tool_names


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
    ]

    instructions_lower = SYSTEM_INSTRUCTIONS.lower()
    for keyword in keywords:
        assert keyword in instructions_lower


def test_tool_contract_json_exists_and_valid():
    """Verify tool-definitions.json exists and matches the code definitions."""
    contract_path = os.path.join(
        os.path.dirname(__file__), "../contracts/tool-definitions.json"
    )
    assert os.path.exists(contract_path)

    with open(contract_path, "r") as f:
        contract_data = json.load(f)

    contract_tools = contract_data.get("tools", [])
    contract_names = [t["name"] for t in contract_tools]

    tools = get_tool_definitions()
    code_names = [t["function"]["name"] for t in tools]

    assert set(contract_names) == set(code_names)

    # Verify each tool in contract has a response schema
    for tool in contract_tools:
        assert "response" in tool, f"Tool {tool['name']} is missing a response schema"


def test_forbidden_terms_not_in_instructions():
    """Verify system instructions do not contain examples of real secrets or IDs."""
    # Pattern for UUID (Subscription/Tenant IDs)
    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    )
    assert not uuid_pattern.search(SYSTEM_INSTRUCTIONS)


def test_no_technical_fields_in_response_schemas():
    """Verify forbidden fields are not in the contract response schemas."""
    contract_path = os.path.join(
        os.path.dirname(__file__), "../contracts/tool-definitions.json"
    )
    with open(contract_path, "r") as f:
        contract_data = json.load(f)

    forbidden_fields = [
        "storage_ref",
        "storage_account",
        "sas_token",
        "key",
        "subscription_id",
        "tenant_id",
        "resource_id",
        "traceback",
        "stack_trace",
    ]

    def check_schema(schema):
        if not isinstance(schema, dict):
            return

        properties = schema.get("properties", {})
        for field in forbidden_fields:
            assert field not in properties, f"Forbidden field '{field}' found in schema"

        # Recursive check for objects or arrays
        if schema.get("type") == "object":
            for val in properties.values():
                check_schema(val)
        elif schema.get("type") == "array":
            check_schema(schema.get("items"))

    for tool in contract_data.get("tools", []):
        check_schema(tool.get("response"))
