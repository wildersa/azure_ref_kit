import azure.functions as func
import logging
import json

app = func.FunctionApp()

# Synthetic data for demonstration purposes, matching fastmcp-basic-server
SYNTHETIC_DATA = {
    "compute": {
        "id": "comp-001",
        "type": "Standard_DS1_v2",
        "status": "running",
        "region": "local-synth-1",
    },
    "storage": {
        "id": "stg-001",
        "type": "Locally-redundant",
        "status": "available",
        "region": "local-synth-1",
    },
}

get_synthetic_resource_properties = json.dumps(
    {
        "type": "object",
        "properties": {
            "resource_type": {
                "type": "string",
                "enum": ["compute", "storage"],
                "description": "The type of resource to retrieve ('compute' or 'storage').",
            }
        },
        "required": ["resource_type"],
    }
)


@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="get_synthetic_resource",
    description="Returns synthetic metadata for a requested resource type. This is a safe, read-only tool.",
    tool_properties=get_synthetic_resource_properties,
)
def get_synthetic_resource(context: str) -> str:
    """
    MCP tool trigger function that returns synthetic resource metadata.

    Args:
        context (str): The JSON string representation of the tool invocation context.

    Returns:
        str: A JSON-formatted string containing synthetic resource metadata or an error message.
    """
    logging.info("MCP tool 'get_synthetic_resource' invoked.")

    try:
        # Parse the execution context
        content = json.loads(context)
        arguments = content.get("arguments", {})
        resource_type = arguments.get("resource_type")

        # Fail-closed: Validate input
        if not resource_type:
            return json.dumps({"error": "Missing required argument: resource_type"})

        if resource_type not in SYNTHETIC_DATA:
            return json.dumps({"error": f"Unsupported resource type: {resource_type}"})

        # Return safe, synthetic data
        return json.dumps(SYNTHETIC_DATA[resource_type])

    except json.JSONDecodeError:
        logging.error("Failed to parse MCP tool invocation context.")
        return json.dumps({"error": "Invalid tool invocation context."})
    except Exception:
        # Logging redacted error summary to prevent leakage
        logging.error("Unexpected error in MCP tool execution.")
        # Fail-closed: return a generic error message, no internal details
        return json.dumps({"error": "An internal error occurred."})
