# HTTP Function as Agent Tool

## Purpose

This building block demonstrates a minimal HTTP-triggered Azure Function designed to serve as a **safe read-only tool boundary** for AI agents.

It provides a concrete reference for exposing enterprise data to agents without allowing arbitrary API passthrough or mutation operations.

## Architecture

```mermaid
flowchart LR
    Agent[AI Agent] -->|GET /api/system_status| Tool[HTTP Function Agent Tool]
    Tool -->|Controlled Tool Response| Agent
    subgraph "Safe Boundary"
        Tool
    end
    Tool -.->|Internal Query| Azure[Azure Resources]
```

## Tool Contract

### GET `/api/system_status`

Returns a high-level summary of the system status.

**Inputs:**
- None (GET request with no parameters).

**Outputs:**
- `business_status` (string): Friendly operational status (e.g., "operational").
- `service_health` (string): Technical health indicator.
- `active_regions` (array of strings): List of regions currently serving traffic.
- `last_updated` (string): ISO8601 timestamp of the last status update.
- `environment` (string): Name of the environment.

## Security and Boundaries

- **Read-Only:** This tool does not accept parameters that modify state.
- **Data Redaction:** The implementation explicitly filters internal metadata, raw logs, and stack traces.
- **Authentication:** In Azure, this function should be protected via Function Keys or Microsoft Entra ID.
- **No Passthrough:** This is not a generic proxy to other Azure APIs; it returns a specific, pre-defined contract.

## Known Limits

- This reference uses a synchronous HTTP trigger. For long-running tasks (>230 seconds), use the [Queue Function Tool](../agent-tool-queue-function/README.md) pattern.
- This is a reference implementation; real-world status checks should be backed by actual resource monitoring or a status database.

## Local Run

Prerequisites:
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- Python 3.11+

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the function locally:
   ```bash
   func start
   ```

3. Test the endpoint:
   ```bash
   curl http://localhost:7071/api/system_status
   ```

## Local Validation

Run tests to verify the tool logic and boundary:

```bash
# From the module root
PYTHONPATH=. pytest tests/test_function.py
```

## Dependencies

- `azure-functions`: Python SDK for Azure Functions.
- `pytest`: For running unit tests.

## Azure Deployment

This module can be deployed to an Azure Function App.

**Recommended SKU:** Flex Consumption (for scale-to-zero and managed identity support).

**Environment Variables:**
- `AzureWebJobsStorage`: Connection string for the storage account (required by Functions).
