from typing import Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP

# Initialize FastMCP server
# This server provides a minimal reference implementation of the Model Context Protocol (MCP)
# for local tool integration. It demonstrates safe, read-only tool exposure.
mcp = FastMCP("fastmcp-basic-server")


class SyntheticResource(BaseModel):
    """Synthetic metadata for a resource."""

    id: str = Field(description="Unique identifier for the synthetic resource")
    type: str = Field(description="Resource type specification")
    status: str = Field(description="Current operational status")
    region: str = Field(description="Deployment region for the resource")


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
) -> SyntheticResource:
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
        # If this were a production tool, we might raise a custom error
        # that FastMCP handles. For this reference, Pydantic validation
        # usually catches this before we reach here if called via MCP.
        # If called directly, we return a default object or raise.
        raise ValueError(f"Unsupported resource type: {resource_type}")

    return SyntheticResource(**SYNTHETIC_DATA[resource_type])


if __name__ == "__main__":
    # Running the server will start the MCP transport (default is stdio)
    mcp.run()
