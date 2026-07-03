# AGENTS.md

This repository is an Azure reference kit for modular, reusable architecture examples.
Agents should keep examples small, explicit, and easy to reuse across local and Azure deployments.

## Operating model

- Read this file before changing the repository.
- Prefer small, coherent changes that deliver the requested outcome end to end.
- Do not create broad scaffolding, placeholder modules, or speculative abstractions without a concrete use case.
- Keep each example or module independently understandable and runnable when possible.
- Preserve repository clarity over cleverness: simple folders, clear names, short READMEs, and explicit commands.
- If a task is ambiguous, make the safest minimal implementation and document the assumption in the PR body.

## Repository structure expectations

The repository may grow as a collection of independent Azure-ready examples.

Recommended structure for new modules:

```text
/<domain-or-solution>/
  README.md
  infra/
  src/
  tests/
  docs/
```

Use only the folders that are needed. Do not create empty folder trees just to match the template.

Each module README should include:

- what the module demonstrates;
- local run commands;
- Azure deployment notes when applicable;
- required environment variables;
- test/validation commands;
- known limits or trade-offs.

For monorepo-style growth, add nested `AGENTS.md` files only when a subfolder needs different commands, contracts, or conventions. The closest `AGENTS.md` to the changed files should be treated as the most specific instruction source.

## Microsoft/Azure documentation rule

For any task involving Azure, Microsoft services, Microsoft SDKs, cloud architecture, identity, security, deployment, IaC, CI/CD, networking, pricing-related assumptions, quotas, service limits, or supported regions, check current official Microsoft documentation before implementing.

Use Microsoft Learn as the primary source of truth.

When available, use the Microsoft Learn CLI:

```bash
npx @microsoft/learn-cli search "<query>" --json
npx @microsoft/learn-cli fetch "<learn-url>" --max-chars 3000
npx @microsoft/learn-cli code-search "<query>" --language <language> --json
```

Implementation expectations:

- Do not rely only on memory for Azure/Microsoft behavior.
- Prefer official Microsoft Learn, Azure docs, SDK docs, and official samples.
- Record consulted Microsoft Learn URLs in the PR body when they materially influenced the implementation.
- If official docs are missing, unclear, or contradictory, state the uncertainty in the PR body and choose the safest minimal implementation.
- Do not introduce Azure-specific defaults, limits, regions, SKUs, permissions, networking behavior, identity behavior, or security assumptions without checking current documentation.

## Code and architecture standards

- Prefer boring, maintainable implementations over framework-heavy solutions.
- Keep modules loosely coupled. Shared utilities are allowed only when at least two real modules need them.
- Avoid hidden global state, implicit environment assumptions, and hardcoded cloud resources.
- Use environment variables for configurable values, but document every variable near the module that uses it.
- Never commit secrets, tokens, connection strings, private keys, `.env` files, or generated credentials.
- Prefer managed identity, least privilege, private networking, and explicit RBAC when designing Azure examples.
- Keep local development paths viable when the module is meant to support both local and Azure execution.

## Infrastructure standards

- Prefer Terraform/OpenTofu-style IaC for Azure examples unless the task explicitly asks for another tool.
- Keep infrastructure examples minimal and reviewable.
- Do not create production-grade complexity unless the module explicitly demonstrates that concern.
- Document estimated cost drivers when adding Azure resources that may create meaningful spend.
- Prefer secure defaults: no public admin endpoints, no broad wildcard permissions, no unauthenticated write APIs, and no public storage unless the example is explicitly about public static content.

## Testing and validation

There is no single repository-wide test command yet. For each module, add or update the smallest meaningful validation path.

Before finishing a PR:

- run the relevant formatter/linter/test/build commands for the files changed;
- add or update tests when behavior changes;
- avoid weakening, deleting, skipping, or broadly mocking tests to get green results;
- document exact commands and results in the PR body;
- if a command cannot run in the agent environment, explain why and provide the closest available validation.

## Documentation standards

- Keep documentation short and directly useful.
- Prefer diagrams, commands, and concrete examples over long conceptual explanations.
- State assumptions, prerequisites, limits, and trade-offs explicitly.
- Do not duplicate official Microsoft documentation; link to it and explain only the repository-specific decision.

## PR expectations

Every PR should include:

- summary of the change;
- files/modules touched;
- Microsoft Learn URLs consulted when relevant;
- test/validation commands and results;
- risks, assumptions, and genuine follow-ups.

Avoid noisy or unrelated formatting changes. Do not mix unrelated modules in the same PR unless the task explicitly requires it.
Guidance for agents working in this repository.

## Project intent

This repository is an Azure AI reference kit. It should collect modular, reusable, Azure-native building blocks and complete solution compositions.

Do not treat this as a single application. Treat it as a catalog of independent modules plus composed reference solutions.

## Required behavior

- Read `README.md` before editing.
- Read the closest `README.md`, `module.yaml`, or `solution.yaml` before changing a module or solution.
- Keep each building block independently understandable and runnable.
- Prefer explicit contracts in YAML/JSON schemas over implicit behavior.
- Do not add hidden coupling between modules.
- Do not create broad scaffolding without a useful reference example.
- Prefer official Microsoft documentation, Azure samples, and Microsoft Learn references for Azure guidance.
- If a Microsoft Docs MCP or equivalent documentation source is available in the execution environment, consult it before adding Azure-specific claims or patterns.
- If no documentation MCP is available, use official Microsoft documentation as the source of truth.

## Minimalism and complexity guardrails

Use Ponytail-style minimalism as a design rule: solve the problem with the smallest safe change that preserves clarity, contracts, and future composition.

Before adding code, modules, abstractions, dependencies, agents, or tools, verify:

- existing repository code cannot be reused cleanly;
- native Azure, browser, framework, or language behavior is not enough;
- the new abstraction has at least one clear current use, not only a hypothetical future use;
- the diff is smaller than the problem it solves;
- added branches, modes, flags, and fallback paths are necessary;
- a simpler module boundary would not solve the same need.

When implementing code in this repository:

- keep functions, components, and pipeline steps small;
- split complex branching into named steps/helpers;
- avoid generic frameworks inside a reference module unless the solution already proves the need;
- do not add broad configuration surfaces before at least one concrete solution uses them;
- if complexity increases, explain why in the module README, solution README, or PR body.

Future code-bearing modules should add objective complexity checks where applicable:

- Python: Ruff McCabe complexity (`C901`) with a tolerant initial limit;
- TypeScript/React: ESLint complexity or cognitive-complexity rule;
- pipelines/agents: step count, tool count, and branching should stay explicit and bounded.

Do not block useful reference delivery only because old/example code is imperfect. Prefer a baseline/ratchet approach: report first, then block only new or worsened complexity.

## Repository boundaries

- `building-blocks/` contains reusable modules.
- `solutions/` contains composed customer-like examples.
- `shared/` contains contracts and reusable helpers.
- `templates/` contains scaffolds for future modules.
- `docs/` contains architecture and contribution guidance.
- `infra/` contains reusable infrastructure patterns.

## Module expectations

Each building block should include:

- `README.md`;
- `module.yaml`;
- `src/` when code exists;
- `tests/` when behavior exists;
- `infra/` when Azure resources are required;
- `examples/` when useful.

Each solution should include:

- `README.md`;
- `solution.yaml`;
- a clear list of referenced building blocks;
- deployment assumptions;
- local/demo flow;
- customer-facing behavior.

## Style

- Keep documentation concise and operational.
- Use short sections and clear contracts.
- Prefer small, reviewable changes.
- Preserve modularity over clever abstractions.
