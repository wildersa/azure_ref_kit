# MCP on Azure Functions Reference Pattern

## Purpose
This building block documents the supported architectural pattern for hosting Model Context Protocol (MCP) servers behind an Azure Functions boundary.

By hosting MCP tools on Azure Functions, agents can access enterprise systems and complex business logic with scale-to-zero pricing, managed identity security, and standardized tool discovery.

## Supported Pattern: Remote MCP Server
The primary supported pattern for cloud-hosted MCP is the **Remote MCP Server**. In this configuration, Azure Functions serves as the hosting runtime, exposing MCP tools via a streamable HTTP transport (typically SSE - Server-Sent Events).

### Architecture

```mermaid
flowchart LR
    User --> Agent
    Agent --> Foundry[Azure AI Foundry Agent Service]
    Foundry -- MCP Protocol (HTTP/SSE) --> Functions[Azure Functions MCP Endpoint]
    Functions --> ToolLogic[Tool Implementation]
    ToolLogic --> Enterprise[Enterprise Systems/Data]
```

## Prerequisites
- **Azure AI Foundry Project**: To register and consume the MCP tool.
- **Azure Functions (Flex Consumption)**: Recommended for optimal serverless scaling and identity-based access.
- **Python 3.10+**: Standard runtime for FastMCP and Azure AI SDKs.
- **Managed Identity**: Enabled on the Function App for secure access to Azure resources without secrets.

## Implementation Details

### 1. Transport Choice
- **SSE (Standard)**: Use for synchronous, real-time tool interactions. This is the industry standard for Remote MCP servers.
- **Queue-based (Alternative)**: For long-running or asynchronous work, use the specialized `AzureFunctionsTool` with Storage Queues instead of a raw MCP endpoint.

### 2. Authentication and Security
- **Entra ID / Managed Identity**: The Function App should use Managed Identity to authenticate with other Azure services.
- **Foundry Connection**: Store any required third-party API keys in Azure AI Foundry Project Connections rather than in the Function App code.
- **Network Boundary**: Use Private Endpoints to restrict access to the MCP endpoint within a Virtual Network.

### 3. Local vs Azure
- **Local**: Development typically uses `stdio` transport with the MCP Inspector for rapid testing.
- **Azure**: Deployment requires switching to a network-based transport like `SSE` (HTTP) to allow the Foundry Agent Service to reach the endpoint.

## Limitations and Trade-offs
- **Documentation-Only**: This reference currently focuses on the architectural pattern. Implementation depends on the evolving `mcp` and `azure-functions` Python library support for SSE transport.
- **Cold Start**: While Flex Consumption minimizes cold starts, the first tool call after a period of inactivity may experience slight latency.
- **Streaming**: Verify that the chosen hosting plan and networking configuration (e.g., Azure Front Door, Application Gateway) support long-lived HTTP connections required for SSE.

## When to use this pattern
- When you need a centralized, reusable tool catalog shared across multiple agents.
- When tool logic requires specific Python dependencies or environment configurations not available in-process.
- When you want to leverage Azure Functions' built-in triggers, bindings, and scaling.

## Microsoft Learn References
- [Agent tools overview for Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)
- [Use Azure Functions with Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/azure-functions)
- [Use AI tools and models in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-ai-enabled-apps)
