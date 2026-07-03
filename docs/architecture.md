# Architecture

## Goal

Provide reusable Azure building blocks for AI-enabled customer processes and pipeline monitoring.

## Default layers

```text
Experience layer
  Static Web Apps portal
  optional customer assistant

API layer
  Azure Functions customer-safe API
  optional API Management

Orchestration layer
  Durable Functions pipeline orchestrator
  triggers via portal, blob, schedule, webhook, or queue

AI layer
  Azure AI Foundry agents/tools
  Azure AI Document Intelligence
  optional Azure AI Search

Data layer
  Blob artifacts
  status store
  cost ledger

Operations layer
  Application Insights
  Azure Monitor
  alerts/workbooks
```

## Key decision

Customer-facing status is not raw Azure telemetry. The system should write business events and friendly summaries into a status store.
