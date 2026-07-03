# Document AI Portal

First target solution: customer-facing portal for tracking a document AI pipeline.

## Scenario

A customer uploads a document or starts a process. The system runs OCR/extraction, validates data, generates artifacts, estimates cost, and exposes friendly status through a portal and optional agent.

## Composed blocks

- `building-blocks/portals/static-status-portal`
- `building-blocks/functions/portal-api-functions`
- `building-blocks/functions/blob-trigger-start-pipeline`
- `building-blocks/functions/ocr-document-intelligence`
- `building-blocks/pipelines/durable-basic-pipeline`
- `building-blocks/agents/pipeline-assistant-foundry`
- `building-blocks/storage/blob-artifact-store`
- `building-blocks/observability/appinsights-observability`
- `building-blocks/security/entra-external-id-auth`

## Customer-facing outcome

The customer can see:

- whether the process started;
- which step is running;
- whether action is required;
- friendly failure reason;
- generated artifacts;
- estimated cost;
- assistant answers about the execution.
