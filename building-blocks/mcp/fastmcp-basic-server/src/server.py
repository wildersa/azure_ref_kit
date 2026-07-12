from typing import Literal
from fastmcp import FastMCP

# Initialize FastMCP server
# This server provides a minimal reference implementation of the Model Context Protocol (MCP)
# for local tool integration. It demonstrates safe, read-only tool exposure.
mcp = FastMCP("fastmcp-basic-server")

# Synthetic data for demonstration purposes
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


@mcp.tool()
def get_synthetic_resource(
    resource_type: Literal["compute", "storage"],
) -> dict:
    """
    Returns synthetic metadata for a requested resource type.

    This is a safe, read-only tool that returns static demo data only.
    It rejects any unsupported resource types and does not access real Azure APIs.

    Args:
        resource_type: The type of resource to retrieve ('compute' or 'storage').
    """
    # Note: Literal at the type level provides hint to the agent,
    # but we still validate to ensure fail-closed behavior for the implementation.
    if resource_type not in SYNTHETIC_DATA:
        # We return a generic error message to the agent, avoiding raw exceptions or stack traces.
        return {
            "error": "Unsupported resource type",
            "supported_types": list(SYNTHETIC_DATA.keys()),
        }

    return SYNTHETIC_DATA[resource_type]


if __name__ == "__main__":
    # Running the server will start the MCP transport (default is stdio)
    mcp.run()
