# Durable Basic Pipeline

Reference Durable Functions orchestration for long-running AI pipelines.

## Purpose

Provide the base pattern for pipeline runs, steps, retries, friendly status, and external status lookup.

## Flow

```text
start request
  -> create PipelineRun
  -> execute ordered steps
  -> write PipelineStep status
  -> store artifacts
  -> estimate cost
  -> complete/fail with friendly summary
```

## Rule

The orchestrator owns process state. Individual workers own step-specific behavior.
