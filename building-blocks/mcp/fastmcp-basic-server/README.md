# FastMCP Basic Server Reference

## Purpose
This building block provides a minimal reference implementation of a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server using the [FastMCP](https://github.com/jlowin/fastmcp) framework.

MCP allows AI agents to interact with external tools and data through a standardized protocol. This reference is designed to be small, independent, and locally runnable.

## Architecture

```mermaid
flowchart LR
    User --> Agent
    Agent -- MCP Protocol (stdio) --> MCP_Server[FastMCP Basic Server]
    MCP_Server --> Tool[get_system_status]
    Tool --> SystemStatus[Static Status Response]
```

## When to use MCP
- When you want to provide a standardized interface for AI agents to call your tools.
- When you need to separate tool execution from the agent's core reasoning logic.
- When you want to reuse tools across different agent frameworks (e.g., Azure Foundry, Claude, etc.).

## When NOT to use MCP
- For simple internal function calls where a protocol overhead is not justified.
- When the tool requires complex streaming or proprietary transport not yet supported by MCP.
- If the agent framework you are using does not support MCP yet.

## Local run
The server uses `stdio` as the default transport. You can run it locally using Python:

```bash
python3 src/server.py
```

## Validation
To verify the server starts and exposes the tool, you can check the help command:

```bash
python3 src/server.py --help
```

For full protocol validation, use the `mcp inspector` or a compatible MCP client.

## Environment variables
No environment variables are required for this basic reference.

## Known limits
- **Local-first**: This block is designed for local execution. For Azure hosting patterns, see [MCP on Azure Functions Reference Pattern](../azure-functions-mcp-endpoint/README.md).
- **Single Tool**: Only one read-only tool is implemented to maintain minimalism.
- **Transport**: Defaulted to `stdio`.

## Contracts
Declared in `module.yaml`.
- **Tools**: `get_system_status` (read-only).
