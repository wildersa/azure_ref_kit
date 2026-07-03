# AGENTS.md

This repository is an Azure AI reference kit for modular, reusable architecture examples.

Agents should keep examples small, explicit, Azure-ready, locally understandable, and easy to compose into customer solutions.

## Operating model

- Read this file before changing the repository.
- Read `README.md` and the closest module or solution documentation before editing.
- Prefer small, coherent changes that deliver the requested outcome end to end.
- Do not create broad scaffolding, placeholder modules, or speculative abstractions without a concrete use case.
- Keep each example or module independently understandable and runnable when possible.
- Preserve repository clarity over cleverness: simple folders, clear names, short READMEs, explicit contracts, and explicit commands.
- If a task is ambiguous, make the safest minimal implementation and document the assumption in the PR body.

## Repository structure expectations

The repository grows as a catalog of building blocks plus composed reference solutions.

Use this structure for reusable modules:

```text
building-blocks/<category>/<module>/
  README.md
  module.yaml
  src/      # only when code exists
  tests/    # only when behavior exists
  infra/    # only when Azure resources are required
  examples/ # only when useful
```

Use this structure for composed solutions:

```text
solutions/<solution>/
  README.md
  solution.yaml
  docs/     # only when solution-specific notes are needed
  infra/    # only when deployment is solution-specific
```

Use only the folders that are needed. Do not create empty folder trees just to match a template.

Each module README should include:

- what the module demonstrates;
- local run commands;
- Azure deployment notes when applicable;
- required environment variables;
- test or validation commands;
- known limits or trade-offs.

Each solution README should include:

- customer/process scenario;
- composed building blocks;
- entrypoints and trigger model;
- customer-facing outcome;
- deployment assumptions;
- local/demo flow when available.

For monorepo-style growth, add nested `AGENTS.md` files only when a subfolder needs different commands, contracts, or conventions. The closest `AGENTS.md` to the changed files is the most specific instruction source.

## Microsoft/Azure documentation rule

For any task involving Azure, Microsoft services, Microsoft SDKs, cloud architecture, identity, security, deployment, IaC, CI/CD, networking, pricing-related assumptions, quotas, service limits, supported regions, or preview features, check current official Microsoft documentation before implementing.

Use Microsoft Learn as the primary source of truth.

When available, use the Microsoft Learn CLI:

```bash
npx @microsoft/learn-cli search "<query>" --json
npx @microsoft/learn-cli fetch "<learn-url>" --max-chars 3000
npx @microsoft/learn-cli code-search "<query>" --language <language> --json
```

Implementation expectations:

- Do not rely only on memory for Azure/Microsoft behavior.
- Prefer official Microsoft Learn, Azure docs, SDK docs, and official Microsoft samples.
- Read `docs/microsoft-reference-map.md` when the task touches Foundry, agents, tools, Functions, DevOps, CI/CD, observability, or deployment.
- Record consulted Microsoft Learn URLs in the PR body when they materially influenced the implementation.
- If official docs are missing, unclear, or contradictory, state the uncertainty in the PR body and choose the safest minimal implementation.
- Do not introduce Azure-specific defaults, limits, regions, SKUs, permissions, networking behavior, identity behavior, preview assumptions, or security assumptions without checking current documentation.

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
- split complex branching into named steps or helpers;
- avoid generic frameworks inside a reference module unless the solution already proves the need;
- do not add broad configuration surfaces before at least one concrete solution uses them;
- if complexity increases, explain why in the module README, solution README, or PR body.

Future code-bearing modules should add objective complexity checks where applicable:

- Python: Ruff McCabe complexity (`C901`) with a tolerant initial limit;
- TypeScript/React: ESLint complexity or cognitive-complexity rule;
- pipelines/agents: step count, tool count, and branching should stay explicit and bounded.

Do not block useful reference delivery only because old/example code is imperfect. Prefer a baseline/ratchet approach: report first, then block only new or worsened complexity.

See `docs/minimalism-and-complexity.md` for the project-level review rule.

## Code and architecture standards

- Prefer boring, maintainable implementations over framework-heavy solutions.
- Keep modules loosely coupled. Shared utilities are allowed only when at least two real modules need them.
- Prefer explicit contracts in YAML or JSON schemas over implicit behavior.
- Avoid hidden global state, implicit environment assumptions, and hardcoded cloud resources.
- Use environment variables for configurable values, but document every variable near the module that uses it.
- Never commit secrets, tokens, connection strings, private keys, `.env` files, or generated credentials.
- Prefer managed identity, least privilege, private networking, and explicit RBAC when designing Azure examples.
- Keep local development paths viable when the module is meant to support both local and Azure execution.
- Do not expose Azure Portal internals, raw logs, prompts, credentials, or unrestricted cloud resource access to customer-facing examples.

## Infrastructure standards

- Prefer Terraform/OpenTofu-style IaC for reusable Azure examples unless the task explicitly asks for another tool.
- Use `azd`/Bicep when following or adapting an official Microsoft sample that is designed around that flow.
- Keep infrastructure examples minimal and reviewable.
- Do not create production-grade complexity unless the module explicitly demonstrates that concern.
- Document estimated cost drivers when adding Azure resources that may create meaningful spend.
- Prefer secure defaults: no public admin endpoints, no broad wildcard permissions, no unauthenticated write APIs, and no public storage unless the example is explicitly about public static content.

## Testing and validation

There is no single repository-wide test command yet. For each module, add or update the smallest meaningful validation path.

Before finishing a PR:

- run the relevant formatter, linter, test, or build commands for the files changed;
- add or update tests when behavior changes;
- avoid weakening, deleting, skipping, or broadly mocking tests to get green results;
- document exact commands and results in the PR body;
- if a command cannot run in the agent environment, explain why and provide the closest available validation.

## Documentation standards

- Follow the [README Standard](docs/readme-standard.md) for all building blocks and solutions.
- Use the [Roadmap](docs/roadmap.md) to prioritize new contributions.
- Keep documentation short and directly useful.
- Prefer diagrams, commands, and concrete examples over long conceptual explanations.
- State assumptions, prerequisites, limits, and trade-offs explicitly.
- Do not duplicate official Microsoft documentation; link to it and explain only the repository-specific decision.

## PR expectations

Every PR should include:

- summary of the change;
- files/modules touched;
- Microsoft Learn URLs consulted when relevant;
- complexity/minimalism notes when adding meaningful code or architecture;
- test/validation commands and results;
- risks, assumptions, and genuine follow-ups.

Avoid noisy or unrelated formatting changes. Do not mix unrelated modules in the same PR unless the task explicitly requires it.
