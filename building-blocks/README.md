# Building Blocks

Reusable Azure modules live here.

A building block is a small, bounded reference component that can be copied, deployed, tested, and composed into solutions.

## Categories

```text
agents/          Azure AI Foundry agents and assistant patterns
functions/       Azure Functions APIs, triggers, integrations, and workers
gateways/        AI gateways for model access, token governance, and security
observability/   Application Insights, Azure Monitor, dashboards, workbooks
pipelines/       Durable Functions and orchestration references
portals/         Static Web Apps and customer-facing UI references
security/        Identity, auth, tenant, network, and access patterns
storage/         Blob, status store, artifact store, and data contracts
```

## Minimum module contract

Each module should declare:

- purpose;
- Azure resources;
- inputs;
- outputs;
- dependencies;
- local run instructions;
- deployment notes;
- tests/proof.
