# Portal API Functions

API layer for the customer portal.

## Purpose

Expose stable, customer-safe endpoints for pipeline status, artifacts, costs, and assistant interactions.

## Candidate endpoints

```text
GET  /runs
GET  /runs/{runId}
POST /runs/start
GET  /runs/{runId}/artifacts
GET  /runs/{runId}/cost
POST /runs/{runId}/chat
```

## Rule

This API owns the customer-facing contract. It should not leak raw Function logs, internal exception payloads, storage keys, model prompts, or Azure resource identifiers unless explicitly safe.
