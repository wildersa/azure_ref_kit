from fastmcp import FastMCP

# Initialize FastMCP server
# This server demonstrates a minimal implementation of the Model Context Protocol (MCP)
# using the FastMCP framework.
mcp = FastMCP("fastmcp-basic-server")


@mcp.tool()
def get_system_status() -> str:
    """
    Returns the current status of the basic MCP server.
    This is a safe, read-only tool for reference and validation.
    """
    return "Status: Operational. Source: FastMCP Basic Server Reference."


if __name__ == "__main__":
    # Running the server will start the MCP transport (default is stdio)
    mcp.run()
