import azure.functions as func
import logging
import json

app = func.FunctionApp()

# Minimal tool properties for get_service_info
tool_properties_json = json.dumps({"type": "object", "properties": {}, "required": []})


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_service_info",
    description="Returns basic information about the MCP service.",
    tool_properties=tool_properties_json,
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

    # In a real scenario, you might parse the context to see tool arguments
    # content = json.loads(context)
    # args = content.get("arguments", {})

    service_info = {
        "service_name": "Azure Functions MCP Reference",
        "status": "operational",
        "version": "1.0.0",
    }

    return json.dumps(service_info)
