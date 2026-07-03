# Blob Trigger Start Pipeline

Reference trigger for starting a pipeline when a customer uploads a file.

## Purpose

Convert a Blob Storage upload into a normalized pipeline start event.

## Flow

```text
Blob uploaded
  -> Event Grid or Blob trigger
  -> validate metadata
  -> create PipelineRun
  -> start Durable Functions orchestration
```

## Rule

The trigger should only start the process. Business orchestration belongs to the pipeline module.
