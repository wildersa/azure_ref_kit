# Minimalism and Complexity Guardrails

## Intent

This repository should stay modular, composable, and easy for humans and LLM agents to modify.

Use Ponytail-style minimalism as a project principle: prefer less code, fewer abstractions, fewer branches, and clearer module boundaries.

Cyclomatic and cognitive complexity are objective signals that help enforce this principle when modules start gaining real code.

## Design rule

Before adding a new abstraction, dependency, module, agent, tool, framework layer, or configuration surface, answer:

```text
Can existing code solve this?
Can Azure-native behavior solve this?
Can the language or framework solve this?
Is this needed by a concrete current solution?
Is this smaller than the problem?
Will this make the next LLM edit easier or harder?
```

If the answer is unclear, choose the simpler option.

## Review rule

A change is suspicious when it:

- adds generic framework code before one working example exists;
- creates tools with no immediate agent use;
- creates agents with too many tools or vague scope;
- adds flags, modes, or fallback paths instead of one clear path;
- turns one module into a hidden platform;
- increases branching without named steps or contracts;
- makes a solution harder to copy into a customer project.

## Complexity guardrails for future code

### Python

Use Ruff McCabe complexity when Python modules appear:

```toml
[tool.ruff.lint]
extend-select = ["C901"]

[tool.ruff.lint.mccabe]
max-complexity = 15
```

Start tolerant. Lower the limit later only after real modules stabilize.

### TypeScript / React

Use ESLint complexity or cognitive-complexity checks when frontend code appears.

Recommended starting posture:

```text
report first
block only new extreme complexity
ratchet limits down later
```

### Agents and tools

Agent complexity is not only code complexity. Watch:

- number of tools per agent;
- vague tool names;
- overlapping tool responsibilities;
- broad system instructions;
- unrestricted access to technical internals;
- branching flows not represented in pipeline contracts.

Prefer small, single-purpose tools with explicit input and output contracts.

### Pipelines

Pipeline steps should be explicit and bounded.

Prefer:

```text
receive document
extract text
classify document
validate fields
generate result
publish status
```

Avoid:

```text
process everything
smart handler
universal pipeline executor
magic decision node
```

## Baseline strategy

Do not block early progress because reference code is imperfect.

Use this progression:

1. Document the rule.
2. Add report-only metrics.
3. Block new or worsened complexity.
4. Ratchet limits down as modules stabilize.

## PR / issue note

When a change adds meaningful code or architecture, include a short note:

```text
Complexity / minimalism notes:
- Reused existing pattern: yes/no
- New abstraction added: yes/no, why
- Complexity risk: low/medium/high
- Follow-up needed: yes/no
```
