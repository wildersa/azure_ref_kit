import azure.functions as func
import logging
import json

app = func.FunctionApp()

# Tool properties definitions
get_service_info_properties = json.dumps(
    {"type": "object", "properties": {}, "required": []}
)

get_resource_health_properties = json.dumps(
    {
        "type": "object",
        "properties": {
            "resource_id": {
                "type": "string",
                "description": "Optional identifier for the resource to check health for.",
            }
        },
        "required": [],
    }
)


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_service_info",
    description="Returns basic information about the MCP service.",
    tool_properties=get_service_info_properties,
)
def get_service_info(context: str) -> str:
    """
    MCP tool trigger function that returns service information.

    Args:
        context (str): The JSON string representation of the tool invocation context.

    Returns:
        str: A JSON-formatted string containing service information.
    """
    logging.info("MCP tool 'get_service_info' invoked.")

    service_info = {
        "service_name": "Azure Functions MCP Reference",
        "status": "operational",
        "version": "1.0.0",
    }

    return json.dumps(service_info)


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_resource_health",
    description="Returns a mock health status for a given resource or the overall system.",
    tool_properties=get_resource_health_properties,
)
def get_resource_health(context: str) -> str:
    """
    MCP tool trigger function that returns resource health information.
    """
    logging.info("MCP tool 'get_resource_health' invoked.")

    # Parse arguments if any
    try:
        content = json.loads(context)
        args = content.get("arguments", {})
        resource_id = args.get("resource_id", "system")
    except (json.JSONDecodeError, AttributeError):
        resource_id = "system"

    health_status = {
        "resource": resource_id,
        "health": "Healthy",
        "last_check": "2024-05-20T10:00:00Z",
        "message": "All systems operational.",
    }

    return json.dumps(health_status)
