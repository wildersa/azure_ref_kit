# How to Compose a Solution

1. Start with the customer outcome.
2. Pick the minimum building blocks needed.
3. Declare them in `solution.yaml`.
4. Define the entrypoints: manual, upload, schedule, webhook, queue.
5. Wire contracts before writing implementation.
6. Keep reusable logic in `building-blocks/` or `shared/`.
7. Keep customer-specific glue inside `solutions/`.

## Example

```text
Document AI Portal
  -> static-status-portal
  -> portal-api-functions
  -> blob-trigger-start-pipeline
  -> durable-basic-pipeline
  -> ocr-document-intelligence
  -> pipeline-assistant-foundry
```
