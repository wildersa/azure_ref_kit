from fastmcp import FastMCP

# Initialize FastMCP server
# This server provides a minimal reference implementation of the Model Context Protocol (MCP)
# for local tool integration. It demonstrates safe, read-only tool exposure.
mcp = FastMCP("fastmcp-basic-server")


@mcp.tool()
def get_system_status() -> str:
    """
    Returns the general operational status of the MCP server.

    This is a safe, read-only tool that returns static demo data only.
    It does not accept any inputs and does not access any system resources.
    """
    return "Status: Operational. FastMCP Basic Server is ready to handle tool requests via stdio."


if __name__ == "__main__":
    # Running the server will start the MCP transport (default is stdio)
    mcp.run()
