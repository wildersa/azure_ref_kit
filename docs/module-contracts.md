# Module Contracts

Every module should be explicit enough for a human or LLM agent to understand without hidden context.

## `module.yaml`

Recommended fields:

```yaml
name: example-module
type: azure-function-worker
category: document-ai
status: scaffold | experimental | stable
purpose: Short operational purpose.
inputs: []
outputs: []
azure_resources: []
contracts:
  reads: []
  writes: []
  emits: []
```

## `solution.yaml`

Recommended fields:

```yaml
name: example-solution
status: scaffold | experimental | stable
purpose: Customer scenario.
entrypoints: {}
building_blocks: []
contracts: []
```

## Rule

If two modules integrate, the integration should be visible in a contract, YAML file, README, or schema.
