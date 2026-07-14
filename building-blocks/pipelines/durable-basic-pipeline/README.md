# Durable Basic Pipeline

## Purpose

This building block demonstrates a minimal Durable Functions orchestration pattern for tracking customer-visible pipeline status. It provides a structured way to manage long-running AI workflows, expose business-level progress, and keep technical internals out of customer-facing state.

## Pattern logic

```mermaid
flowchart TD
    Trigger[Blob Trigger] --> Orchestrator[Pipeline Orchestrator]
    Orchestrator --> Init[Activity: Update Run Status 'running']

    Init --> Step1Start[Activity: Update Step Status 'ocr/running']
    Step1Start --> OCR[Activity: OCR Document Intelligence]
    OCR --> Step1End[Activity: Update Step Status 'ocr/completed']

    Step1End --> Step2Start[Activity: Update Step Status 'val/running']
    Step2Start --> Val[Activity: Field Validation Worker]
    Val --> Step2End[Activity: Update Step Status 'val/completed']

    Step2End --> Step3Start[Activity: Update Step Status 'pub/running']
    Step3Start --> Pub[Activity: Final Result Publisher]
    Pub --> Step3End[Activity: Update Step Status 'pub/completed']

    Step3End --> Final[Activity: Update Run Status 'completed']

    subgraph Error Handling
        OCR -.->|Failure| StepFail[Activity: Update Step Status 'failed']
        Val -.->|Failure| StepFail
        Pub -.->|Failure| StepFail
        StepFail --> Fail[Activity: Update Run Status 'failed']
    end
```

## Contracts

This module adheres to the following shared contracts:

- `shared/contracts/pipeline-run.schema.json`: Overall run status.
- `shared/contracts/pipeline-step.schema.json`: Individual step status.

## Customer-safe status boundary

To maintain security and clarity, the following rules apply to status updates:

- **Allowed**: Business status (e.g., "Processing document"), friendly step names, safe summaries, artifact metadata, estimated costs, and correlation IDs.
- **Forbidden**: Raw logs, prompts, model/tool payloads, stack traces, secrets, internal tenant details, and raw identifiers (e.g., `run_id`, `instance_id`) in runtime logs.

## Local run

1. Install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the functions:
   ```bash
   func start
   ```

## Deploy

- **Hosting**: Azure Functions (Linux, Flex Consumption recommended).
- **Storage**: Azure Storage Account (required for Durable Functions state).
- **Observability**: Application Insights.

### IaC Decision

This building block is primarily a **runtime reference implementation**. While a minimal Terraform example is provided for completeness, the focus is on the orchestration logic and status contracts. Per repository standards, this module does not mandate a specific IaC provider for adoption, but the provided reference follows the [docs/terraform-deployment-requirement.md](../../docs/terraform-deployment-requirement.md) for validation.

### Terraform Deployment

A minimal Terraform deployment reference is provided in the [infra/terraform/](infra/terraform/) directory. It provisions the necessary Resource Group, Storage Account, Application Insights, and the Flex Consumption Function App.

**Required Configuration (Identity-First):**

This module enforces an **identity-first security boundary**. Shared access keys are disabled on the storage account (`shared_access_key_enabled = false`), and all communication is authorized via Microsoft Entra ID (Managed Identity).

- `AzureWebJobsStorage__accountName`: The name of the storage account.
- `AzureWebJobsStorage__credential`: Set to `managedidentity`.
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: The connection string for Application Insights.

## Failure and Retry Behavior

- **Bounded Retries**: Potentially transient steps (OCR, Publication) use a `RetryOptions` policy with a 5-second initial interval and a maximum of 3 attempts. This handles temporary Azure service unavailability or network blips.
- **Retryable Exception Pattern**: Only specific categories of failures (e.g., HTTP 429/5xx) should be retried. In this reference, `call_activity_with_retry` is used for steps interfacing with external services.
- **Non-Retryable Failures**: Validation failures (e.g., missing mandatory fields) are treated as deterministic and non-retryable; the pipeline fails immediately to avoid redundant processing and cost.
- **Customer-Safe Redaction**: All failures (including retry exhaustion and unhandled exceptions) are caught by the orchestrator. It then updates the `PipelineRun` and `PipelineStep` status with a generic friendly error, preventing leakage of internal technical details, stack traces, or secrets to the customer-facing interface.

## Microsoft Learn References

- [Durable Functions Overview](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [Durable Functions Python Programming Model](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview?tabs=python-v2)
- [Orchestrator Code Constraints](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-code-constraints)
- [Error Handling in Durable Functions](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-error-handling)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)

## Known limits

- Orchestrator functions must be deterministic.
- Status updates are eventually consistent if stored in an external database.
