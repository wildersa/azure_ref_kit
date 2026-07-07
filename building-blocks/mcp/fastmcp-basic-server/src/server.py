from fastmcp import FastMCP

# Initialize FastMCP server
# This server provides a reference implementation of the Model Context Protocol (MCP)
# for local tool integration. It demonstrates safe, read-only tool exposure.
mcp = FastMCP("fastmcp-basic-server")


@mcp.tool()
def get_service_health(service_name: str) -> str:
    """
    Check the health status of a mock internal service.

    Args:
        service_name: The name of the service to check (e.g., 'database', 'auth', 'storage').
    """
    # Define a safe subset of allowed services to prevent arbitrary probing
    # In a production scenario, this would interface with a real monitoring system.
    health_data = {
        "database": "Healthy - All clusters operational",
        "auth": "Healthy - Token service response time 45ms",
        "storage": "Degraded - Increased latency in Blob Storage (Region: US-East)",
        "search": "Healthy - Indexing up to date",
    }

    normalized_name = service_name.lower().strip()
    return health_data.get(
        normalized_name,
        f"Unknown service: '{service_name}'. Supported: {', '.join(health_data.keys())}",
    )


@mcp.tool()
def get_system_status() -> str:
    """
    Returns the general operational status of the MCP server.
    """
    return "Status: Operational. FastMCP Basic Server is ready to handle tool requests via stdio."


if __name__ == "__main__":
    # Running the server will start the MCP transport (default is stdio)
    mcp.run()
