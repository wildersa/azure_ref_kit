# DevOps MCP Tool Contract

## Purpose
This building block defines the safe, read-only [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) tool contracts for querying Azure DevOps status. It establishes a security boundary that allows AI agents to answer questions about build and pipeline health without exposing sensitive internals or allowing mutations.

## Architecture

```mermaid
sequenceDiagram
    participant A as Foundry/Agent Consumer
    participant MCP as MCP Tool Boundary
    participant C as Safe DevOps Status Contract
    participant D as Azure DevOps API

    A->>MCP: Request Status (pipeline_id, run_id)
    MCP->>C: Validate Input (Safe Identifiers Only)
    C->>D: Sanitized Request (GET /_apis/...)
    D-->>C: Raw Response (Logs, Secrets, Internals)
    C->>C: Sanitize & Filter to Contract
    C-->>MCP: Sanitized Response (Safe Fields Only)
    MCP-->>A: Business Status Outcome
```

## Security Boundary

To protect the integrity and confidentiality of the DevOps environment, the following constraints are enforced by this contract:

### Allowed (Safe Fields)
- **Status**: Current state of a run (e.g., `inProgress`, `completed`).
- **Result**: Outcome of a completed run (e.g., `succeeded`, `failed`, `canceled`).
- **Metadata**: Pipeline name, run ID (surrogate or real depending on implementation), branch name, and commit short SHA.
- **Timing**: Start time, end time, and duration.
- **Summaries**: Friendly business-level summaries of successes or failures.
- **Placeholders**: URLs to the Azure DevOps portal (customer-facing links).

### Forbidden
- **Mutations**: No tools for triggering builds, canceling runs, or changing configurations.
- **Sensitive Data**: No access to secrets, variables marked as secret, tokens, or credentials.
- **Technical Internals**: No raw logs, full stack traces, or detailed model/tool payloads.
- **Broad Access**: No unbounded organization or project discovery; tools should be scoped to specific projects.
- **Arbitrary Queries**: No passthrough of raw OData or SQL-like queries to DevOps APIs.

## Tool Contracts

The following MCP tools are defined in this contract. Implementation should follow the provided JSON schemas and Pydantic models.

### 1. `get_pipeline_run_status`
Returns the status and summary of a specific Azure DevOps pipeline run.

**Inputs:**
- `pipeline_id` (string): The ID or name of the pipeline.
- `run_id` (string): The specific run ID to query.

**Output Example:**
```json
{
  "pipeline_name": "Main CI",
  "run_id": "20240101.5",
  "status": "completed",
  "result": "failed",
  "branch": "main",
  "commit_sha": "a1b2c3d",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:05:00Z",
  "summary": "Step 'Unit Tests' failed on agent 'Linux-01'.",
  "portal_url": "https://dev.azure.com/org/proj/_build/results?buildId=12345"
}
```

### 2. `get_latest_build_summary`
Returns the summary of the most recent build for a specified pipeline or branch.

**Inputs:**
- `pipeline_id` (string): The ID or name of the pipeline.
- `branch` (string, optional): Filter by branch name (defaults to default branch).

**Output Example:**
```json
{
  "pipeline_name": "Main CI",
  "build_number": "20240102.1",
  "status": "completed",
  "result": "succeeded",
  "branch": "main",
  "finish_time": "2024-01-02T12:00:00Z",
  "summary": "Build succeeded. All 150 tests passed.",
  "portal_url": "https://dev.azure.com/org/proj/_build/results?buildId=12346"
}
```

## Deployment / IaC Decision
**No-IaC Decision**: This building block defines a contract and local validation logic. It does not introduce deployable Azure resources. Future implementations (e.g., an MCP server hosted on Azure Functions) will include their own infrastructure definitions.

## Local Validation
Validation includes JSON schema checks and Pydantic model verification.

```bash
python --version
ruff check .
ruff format --check .
pytest tests/
```

## References
- [Azure DevOps Pipelines REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/get?view=azure-devops-rest-7.1)
- [Azure DevOps Build REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/build/builds/get?view=azure-devops-rest-7.1)
- [Foundry Agent Tool Catalog](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
