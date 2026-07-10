# Runtime Map - Document AI Portal

This document describes how the building blocks of the Document AI Portal solution are mapped to Azure runtime targets, their entrypoints, and their operational requirements.

## Overview

The solution is composed of two Function Apps (one for orchestration/workers, one for the customer-facing API) and a Static Web App for the frontend.

| Runtime Target | Technology | Description |
|----------------|------------|-------------|
| `pipeline_function_app` | Azure Functions (Durable) | Orchestration, triggers, and processing workers. |
| `api_function_app` | Azure Functions | Customer-safe API for the portal and agent tools. |
| `portal_static_web_app` | Azure Static Web Apps | React-based frontend monitoring portal. |
| `agent` | Azure AI Foundry | AI Assistant for customer interaction (external/managed). |

---

## 1. Pipeline Function App (`pipeline_function_app`)

This app handles the asynchronous processing of documents.

### Included Building Blocks
- `building-blocks/pipelines/durable-basic-pipeline/`
- `building-blocks/functions/blob-trigger-start-pipeline/`
- `building-blocks/functions/ocr-document-intelligence/`
- `building-blocks/functions/field-validation-worker/`
- `building-blocks/functions/final-result-publisher/`

### Entrypoints
- **Blob Trigger**: `blob_trigger_start_pipeline` (Starts the orchestrator on upload).
- **Durable Orchestrator**: `pipeline_orchestrator` (Manages the workflow).
- **Durable Activities**:
    - `ocr_document_intelligence`: Extracts text via Azure AI Document Intelligence.
    - `field_validation_worker`: Validates extracted fields against business rules.
    - `final_result_publisher`: Finalizes data and makes it available to the portal.
    - `update_pipeline_run_status`: Internal helper for status transitions.

### Implementation Status
- **Orchestration**: Implemented.
- **OCR**: Implemented (Real integration with AI Document Intelligence).
- **Validation**: Implemented (Business logic).
- **Publisher**: Implemented.

### Shared Contracts
- `shared/contracts/pipeline-run.schema.json`
- `shared/contracts/pipeline-step.schema.json`
- `shared/contracts/artifact.schema.json`

### Required App Settings
| Setting | Description |
|---------|-------------|
| `AzureWebJobsStorage` | Connection for Durable Functions state and triggers. |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Endpoint for the OCR service. |
| `AZURE_STORAGE_ACCOUNT_URL` | Base URL for artifact storage access. |

---

## 2. Portal API Function App (`api_function_app`)

This app provides a secure, filtered view of the pipeline data for the frontend and AI agent.

### Included Building Blocks
- `building-blocks/functions/portal-api-functions/`

### Entrypoints (HTTP)
- `GET /api/runs`: List recent runs for the authenticated customer.
- `GET /api/runs/{id}`: Get detailed status and timeline.
- `GET /api/runs/{id}/artifacts`: List customer-safe artifacts.
- `GET /api/artifacts/{id}/download`: Secure download proxy.
- `GET /api/runs/{id}/cost`: Get aggregated run cost.
- `POST /api/runs/start`: Manually trigger a run.

### Customer-Safe Boundary
The API acts as the primary enforcement point. It reads raw technical data from internal stores and filters it through the shared schemas before returning it to the client. It strictly forbids exposure of internal IDs, raw logs, and provider payloads.

### Required App Settings
| Setting | Description |
|---------|-------------|
| `AZURE_STORAGE_ACCOUNT_URL` | Access to status tables and artifact blobs. |

---

## 3. Portal Static Web App (`portal_static_web_app`)

The frontend UI for end-users.

### Included Building Blocks
- `building-blocks/portals/static-status-portal/`

### Configuration
- **Source Path**: `building-blocks/portals/static-status-portal/`
- **API Integration**: Assumes `/api` route is proxied to `api_function_app`.
- **Status**: **Scaffold**. The UI shell and contract are defined, but the React implementation is a placeholder.

### Local Run Flow
```bash
# From the portal directory
swa start http://localhost:5173 --api-location http://localhost:7071
```

---

## 4. AI Assistant Agent (`agent`)

The agent provides natural language interaction over the pipeline data.

### Included Building Blocks
- `building-blocks/agents/pipeline-assistant-foundry/`

### Configuration
- **Deployment**: Managed as an Azure AI Foundry Agent.
- **Interaction**: The Portal API or a dedicated Agent endpoint interacts with the Foundry runtime.
- **Status**: Implemented. The agent is configured to use tools that call the `api_function_app` endpoints.

---

## Shared Contracts & Data Flow

All components communicate using the following schema-validated contracts:
1. `pipeline-run`: Overall state of a document processing request.
2. `pipeline-step`: Granular status and output for a specific worker (e.g., OCR).
3. `artifact`: Metadata for files produced during the run.
4. `cost-ledger`: Internal records for estimating processing costs.

## Blockers for 'Executable' Status
1. **SWA Frontend Implementation**: The `static-status-portal` is currently a scaffold.
2. **End-to-End Test Suite**: Need automated tests that verify the flow from Blob Trigger -> Durable Pipeline -> API -> Portal.
3. **Infrastructure Wiring**: Ensure all RBAC roles for Managed Identity are fully defined in the solution Terraform.
