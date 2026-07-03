# AGENTS.md

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
