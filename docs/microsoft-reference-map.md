# Microsoft Reference Map

Last reviewed: 2026-07-03

This document is the repository-local map of official Microsoft references for Azure AI Foundry, agents, tools, Azure Functions, DevOps, deployment, and observability.

It is not a replacement for Microsoft Learn. Every implementation issue must re-check the current official documentation before coding.

## How agents should use this map

For Azure, Foundry, DevOps, SDK, IaC, CI/CD, identity, networking, pricing, quota, region, or preview-related work:

1. Start from the relevant links in this file.
2. Re-check current Microsoft Learn pages before implementing.
3. Record the materially used Microsoft Learn URLs in the PR body.
4. Prefer official Microsoft samples when code structure is unclear.
5. State uncertainty when docs are missing, gated, contradictory, preview-only, or region/model dependent.

When available, use:

```bash
npx @microsoft/learn-cli search "<query>" --json
npx @microsoft/learn-cli fetch "<learn-url>" --max-chars 3000
npx @microsoft/learn-cli code-search "<query>" --language <language> --json
```

## Core Foundry references

### Microsoft Foundry Agent Service

URL: https://learn.microsoft.com/en-us/azure/foundry/agents/overview

Use for:

- agent service concepts;
- prompt agents vs hosted agents;
- Responses API positioning;
- agent runtime, tools, identity, security, observability, publishing;
- current development lifecycle: create, test, trace, evaluate, optimize, publish, monitor.

Repository implication:

- Start with prompt agents for simple references.
- Use hosted agents only when custom runtime/orchestration is actually needed.
- Treat Responses API as the common model/tool access path.
- Do not assume older Azure AI Studio behavior; verify current Foundry names and SDKs.

### Foundry Agent tool catalog

URL: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog

Use for:

- built-in tools;
- MCP tools;
- OpenAPI tools;
- Azure Functions tools;
- Azure AI Search/file search/code interpreter;
- Toolbox/private tool catalog concepts;
- authentication options and tool governance.

Repository implication:

- Prefer small, explicit tool contracts.
- Prefer Microsoft Entra authentication when supported.
- Avoid broad agent access to technical internals.
- Do not expose secrets in prompts, logs, tool headers, or examples.

### Azure Functions as Foundry tools

URL: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/azure-functions

Use for:

- queue-based Azure Functions tools;
- AzureFunctionsTool setup;
- asynchronous function execution;
- CorrelationId behavior;
- Functions vs in-process function calling;
- MCP vs queue-based Functions integration;
- current SDK/package requirements.

Repository implication:

- Use Functions tools when the agent needs enterprise integration, isolation, dependencies, long-running work, or retryable background processing.
- Keep agent tools customer-safe and business-level.
- Treat queue-based tools and MCP-hosted tools as separate patterns.

## Pipeline and serverless references

### Azure Functions overview

URL: https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview

Use for:

- serverless API/trigger patterns;
- triggers and bindings;
- file upload processing;
- scalable web APIs;
- AI inference from queues;
- monitoring with Azure Monitor/Application Insights;
- hosting options, especially Flex Consumption for new serverless examples.

Repository implication:

- Use Functions for portal APIs, triggers, and small custom tools.
- Document hosting choice and cost drivers.
- Prefer local development support when a module is intended to run locally and in Azure.

### Durable Functions overview

URL: https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview

Use for:

- stateful serverless workflows;
- orchestrator/activity/entity functions;
- checkpoints, retries, recovery;
- long-running pipeline orchestration;
- local testing with Azure Functions Core Tools.

Repository implication:

- Use Durable Functions for customer-visible pipeline runs and steps.
- Keep the orchestrator responsible for process state.
- Keep individual workers responsible for step behavior.
- Store customer-facing status separately from raw telemetry.

## DevOps and deployment references

### Azure Pipelines documentation

URL: https://learn.microsoft.com/en-us/azure/devops/pipelines/?view=azure-devops

Use for:

- Azure Pipelines concepts;
- YAML schema;
- jobs, stages, tasks, templates, triggers;
- GitHub/Azure Repos integration;
- deployment to Azure;
- service connections and troubleshooting.

Repository implication:

- When adding Azure DevOps examples, specify whether the module targets Azure Pipelines, GitHub Actions, or both.
- Keep CI/CD examples minimal and tied to a concrete module.
- Avoid pipeline templates without a working module that uses them.

### Azure Developer CLI overview

URL: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview

Use for:

- azd template structure;
- `azd init`, `azd up`, `azd deploy`, `azd provision`;
- app + infrastructure deployment flow;
- GitHub Actions or Azure Pipelines integration from templates.

Repository implication:

- Use `azd` when adapting official Microsoft samples or when a reference solution benefits from quick end-to-end provisioning.
- Terraform/OpenTofu remains preferred for reusable IaC unless the task or official sample is explicitly azd/Bicep-based.

## First reference solution focus

Initial solution candidate:

```text
solutions/foundry-devops-agent-basic/
```

Purpose:

```text
A minimal Foundry agent that answers questions about a pipeline/build through a controlled tool boundary.
```

Suggested building blocks:

```text
building-blocks/agents/pipeline-assistant-foundry
building-blocks/functions/portal-api-functions
building-blocks/functions/devops-status-tool
building-blocks/observability/appinsights-observability
```

Suggested P0:

- document the current official Foundry agent/tool pattern;
- define the tool contract for pipeline status;
- expose only safe pipeline/build status fields;
- include local/demo validation path;
- include PR proof with Microsoft Learn URLs consulted.

## Issue authoring rule for Jules

Every Jules issue touching Foundry or DevOps must include:

```text
Repository sources:
- AGENTS.md
- docs/microsoft-reference-map.md
- relevant module README/module.yaml/solution.yaml

Documentation requirement:
- Re-check current Microsoft Learn docs before implementing.
- Record consulted Microsoft Learn URLs in the PR body.
- Do not rely only on model cutoff knowledge for Azure/Foundry behavior.
```

## Watcher/scheduler rule

When there are no open implementation issues:

1. Read `docs/roadmap.md` if present.
2. Pick the next smallest reference solution or missing building block.
3. Open one compact Jules issue using current repository specs and this reference map.
4. The new issue must name the Microsoft Learn docs that Jules must check.
5. Prefer one coherent outcome over many tiny parallel issues.
