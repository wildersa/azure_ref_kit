# Azure Reference Kit

Azure Reference Kit is a modular reference repository for building Azure-native AI automation solutions.

The goal is to avoid starting every customer project from zero. Each folder should be usable as a small independent reference module, while complete examples under `solutions/` show how multiple modules can be composed into a real customer-facing solution.

## What this repository is for

Use this repository to collect and evolve reusable Azure building blocks for:

- customer-facing pipeline monitoring portals;
- Azure Functions and Durable Functions orchestration;
- Azure AI Foundry agents and tools;
- document/OCR pipelines with Azure AI services;
- artifact storage, status tracking, cost tracking, and observability;
- secure, repeatable solution compositions for customer scenarios.

## Core idea

```text
building-blocks = independent reusable Azure modules
solutions       = complete examples composed from multiple modules
shared          = common contracts, schemas, libraries, and prompts
templates       = scaffolds for new modules, agents, pipelines, and solutions
docs            = architecture and guidance for humans and LLM agents
infra           = reusable infrastructure patterns
```

A building block should be able to run and be understood by itself. A solution should explain which blocks it uses and how they are wired together.

## Initial structure

```text
azure_ref_kit/
├─ building-blocks/
│  ├─ agents/
│  ├─ functions/
│  ├─ observability/
│  ├─ pipelines/
│  ├─ portals/
│  ├─ security/
│  └─ storage/
├─ solutions/
├─ shared/
│  └─ contracts/
├─ templates/
├─ docs/
└─ infra/
```

## Default reference architecture

```text
Customer
  ↓
Static Web Apps customer portal
  ↓
Azure Functions portal API
  ↓
Durable Functions pipeline orchestrator
  ↓
Pipeline steps
  ├─ Blob Storage triggers/artifacts
  ├─ Azure AI Document Intelligence
  ├─ Azure AI Foundry agents/tools
  ├─ validation and integration functions
  └─ status/cost/event updates
  ↓
Status store + artifact store + cost ledger + Application Insights
```

## Repository rules

Every building block should include:

- `README.md` explaining purpose, local run, Azure deployment, inputs, outputs, and dependencies;
- `module.yaml` declaring the module contract;
- `src/` when code exists;
- `tests/` when behavior exists;
- `infra/` when Azure resources are required;
- `examples/` when useful.

Every solution should include:

- `README.md` explaining the customer scenario;
- `solution.yaml` declaring which blocks are composed;
- architecture notes;
- deployment assumptions;
- local/demo flow.

## First target solution

The first complete example should be:

```text
solutions/document-ai-portal/
```

It should combine:

- Static Web Apps portal;
- Functions API;
- Durable Functions pipeline;
- Blob Storage artifacts;
- Azure AI Document Intelligence OCR;
- Azure AI Foundry pipeline assistant;
- Application Insights observability;
- estimated cost ledger.

## Design principles

- Keep modules small and composable.
- Prefer explicit contracts over hidden conventions.
- Make each module readable by humans and LLM agents.
- Separate customer-facing business status from technical logs.
- Do not expose Azure Portal, raw Function logs, or Foundry internals to customers.
- Prefer Azure-native services, but keep business contracts portable.
- Add one clear example before adding too many abstractions.
