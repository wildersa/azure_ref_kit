"""
Static validation tests for the DevOps Status Agent.
Verifies safety instructions and tool definitions.
"""

from src.agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions
from azure.ai.projects.models import FunctionTool

def test_system_instructions_safety_keywords():
    """
    Verifies that the system instructions contain essential safety and privacy keywords.
    """
    required_keywords = [
        "Safety and Privacy Rules",
        "DO NOT expose",
        "logs",
        "stack traces",
        "Personal Access Tokens",
        "secrets",
        "mutation",
        "read-only",
    ]

    for keyword in required_keywords:
        assert keyword.lower() in SYSTEM_INSTRUCTIONS.lower(), f"Missing safety keyword: {keyword}"

def test_system_instructions_prohibits_mutations():
    """
    Verifies that the system instructions explicitly prohibit mutation actions.
    """
    prohibited_actions = ["trigger", "cancel", "approve"]
    for action in prohibited_actions:
        assert action in SYSTEM_INSTRUCTIONS.lower(), f"Instruction should mention prohibiting '{action}'"
    assert "NEVER perform any mutation actions" in SYSTEM_INSTRUCTIONS

def test_tool_definitions_structure():
    """
    Verifies that the tool definitions follow the expected structure for the SDK.
    """
    tools = get_tool_definitions()
    assert len(tools) == 3

    tool_names = [t.name for t in tools]
    assert "get_pipeline_run_status" in tool_names
    assert "get_latest_build_summary" in tool_names
    assert "list_recent_pipeline_runs" in tool_names

    for tool in tools:
        assert isinstance(tool, FunctionTool)
        assert tool.description is not None
        assert tool.parameters is not None
        assert tool.parameters["type"] == "object"

def test_get_pipeline_run_status_parameters():
    """
    Verifies parameters for get_pipeline_run_status.
    """
    tools = get_tool_definitions()
    tool = next(t for t in tools if t.name == "get_pipeline_run_status")
    params = tool.parameters["properties"]

    assert "pipeline_id" in params
    assert "run_id" in params
    assert "pipeline_id" in tool.parameters["required"]
    assert "run_id" in tool.parameters["required"]
