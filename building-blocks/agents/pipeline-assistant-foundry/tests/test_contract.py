import json
import os
from src.agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions


def test_tool_definitions_match_p0():
    """Verify all 6 required tools are present in the definitions."""
    tools = get_tool_definitions()
    tool_names = [t["function"]["name"] for t in tools]

    expected_tools = [
        "get_pipeline_status",
        "get_pipeline_steps",
        "get_artifacts",
        "explain_error",
        "estimate_cost",
        "request_human_review",
    ]

    for tool in expected_tools:
        assert tool in tool_names


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


def test_forbidden_terms_not_in_instructions():
    """Verify system instructions do not contain examples of real secrets or IDs."""
    # We check if specific hardcoded values like '1234-5678' or real-looking IDs are present.
    # The instructions explicitly mention NOT to expose IDs, which is good.
    # This test ensures we didn't put a REAL id in as an example.
    import re

    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    )
    assert not uuid_pattern.search(SYSTEM_INSTRUCTIONS)
