# LLM Guide

This repository should be easy for LLM agents to navigate and modify safely.

## Before editing

Read:

1. `README.md`;
2. `AGENTS.md`;
3. target module `README.md`;
4. target `module.yaml` or `solution.yaml`;
5. relevant schemas in `shared/contracts/`.

## Working rules

- Preserve module independence.
- Keep new behavior documented near the module.
- Add contracts before cross-module coupling.
- Prefer small examples that run over abstract architecture only.
- Use official Microsoft/Azure sources for Azure-specific guidance.
- Do not claim deployed behavior unless code, infra, and instructions exist.
