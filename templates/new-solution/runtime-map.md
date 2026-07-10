# Runtime Map

This document describes how the building blocks in this solution are mapped to Azure runtimes and how they interact.

## Azure Runtime Targets

| Target Name | Type | Description |
|-------------|------|-------------|
| `api_function_app` | Azure Function (Flex) | Primary API for the agent. |
| `pipeline_function_app` | Azure Function (Flex) | Backend processing and long-running tasks. |
| `portal` | Static Web App | Frontend user interface. |

## Building Block Assignment

| Building Block | Runtime Target | Role | Status |
|----------------|----------------|------|--------|
| `example-block` | `api_function_app` | `worker` | `implemented` |

## Entrypoints

- **api_function_app**: `function_app.py`
- **pipeline_function_app**: `function_app.py`
- **portal**: `index.html`

## Block Contracts

Describe how blocks communicate (e.g., via HTTP, Service Bus, Storage Queues).

## Local Run Flow

1. Step 1...
2. Step 2...

## Package/Deploy Flow

Describe how the artifacts are built and deployed.

## Blockers for `executable` Status

- [ ] Task 1
- [ ] Task 2
