"""
Foundry Agent with Queue Tool - Agent Definition.
Defines the customer-safe boundary and tool definitions for the asynchronous agent.
"""

from typing import List
from azure.ai.projects.models import FunctionTool, Tool

# System instructions that enforce the customer-safe boundary and async workflow.
SYSTEM_INSTRUCTIONS = """
You are a helpful Asynchronous Task Assistant.
Your goal is to help users submit long-running tasks and check their status.

### Safety and Privacy Rules:
- ONLY use the provided tools to submit tasks or check their status.
- DO NOT expose internal technical details such as:
    - Raw Azure Function logs or stack traces.
    - Storage account names, keys, or connection strings.
    - Raw queue message payloads.
    - Internal Azure Resource IDs.
- If a task fails, provide a friendly, non-technical explanation based on the `error_message` returned by the status tool.
- Never make up a correlation ID. Only use IDs returned by the `submit_task` tool.

### Task Workflow:
1. When a user wants to perform an operation (like 'ping' or 'analyze_text'), use `submit_task`.
2. Tell the user that the task has been accepted and provide them with the `correlation_id`.
3. Inform the user that they can check the status later using this ID.
4. If a user provides a `correlation_id` and asks for status, use `get_task_status`.
5. Report the status (pending, running, completed, or failed) and the results if available.
"""


def get_tool_definitions() -> List[Tool]:
    """
    Returns the list of tool definitions for the asynchronous agent.
    """
    return [
        FunctionTool(
            name="submit_task",
            description="Submit a new long-running task for asynchronous processing. Returns a correlation_id.",
            parameters={
                "type": "object",
                "properties": {
                    "operation_type": {
                        "type": "string",
                        "description": "The type of operation to perform (e.g., 'ping', 'analyze_text').",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Operation-specific parameters.",
                        "additionalProperties": True,
                    },
                },
                "required": ["operation_type"],
            },
        ),
        FunctionTool(
            name="get_task_status",
            description="Check the status and results of a previously submitted task using its correlation_id.",
            parameters={
                "type": "object",
                "properties": {
                    "correlation_id": {
                        "type": "string",
                        "description": "The opaque correlation ID returned by submit_task.",
                    }
                },
                "required": ["correlation_id"],
            },
        ),
    ]
