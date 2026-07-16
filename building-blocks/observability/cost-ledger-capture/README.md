# Cost Ledger Capture

Reference building block for capturing estimated internal cost entries for pipeline steps.

## Purpose

Capture and store estimated costs associated with different steps of a Document AI pipeline. This allows for internal tracking and reporting of resource consumption without exposing sensitive Azure billing internals to customers.

## Contract vs Authoritative Billing

- **Estimate Only**: This module captures **estimated** costs based on usage metrics (e.g., tokens, pages, execution time) and pre-defined rates.
- **Not Authoritative**: This is NOT a replacement for official Azure billing, invoices, or Cost Management reconciliation. **Do not use this for customer invoicing without independent validation.**
- **Internal Focus**: The primary goal is internal observability and optional high-level customer-facing cost summaries.

## Input Fields

This module expects data aligned with the `shared/contracts/cost-ledger.schema.json` contract:

- **`run_id`** (Required): Unique identifier for the pipeline run.
- **`category`** (Required): Category of the cost (`ai_tokens`, `document_ai`, `storage`, `function_execution`, `integration`, `other`).
- **`estimated_amount`** (Required): The calculated estimate for the step.
- **`step_name`**: Name of the pipeline step that incurred the cost.
- **`provider`**: Service provider (e.g., `Azure`, `OpenAI`).
- **`model_or_service`**: Specific model or service used (e.g., `gpt-4o`, `prebuilt-invoice`).
- **`input_units`**: Number of input units (e.g., tokens, pages).
- **`output_units`**: Number of output units (e.g., tokens).
- **`unit_name`**: Name of the unit (e.g., `token`, `page`, `second`).
- **`currency`**: Currency code (Currently supported: `USD`).
- **`created_at`**: Timestamp of the cost event (ISO-8601).

## Service-Level Diagram

The following diagram shows how pipeline steps interact with the cost ledger capture boundary.

```mermaid
graph TD
    subgraph "Pipeline Execution"
        OCR[OCR Step] -->|Metrics| Capture[Cost Ledger Capture]
        Val[Validation Step] -->|Metrics| Capture
        Pub[Publishing Step] -->|Metrics| Capture
    end

    subgraph "Internal Storage"
        Capture -->|Entry| Ledger[(Internal Cost Ledger)]
    end

    subgraph "Customer-Safe Boundary"
        Ledger -->|Aggregate| Summary[Safe Cost Summary]
        Summary -->|Safe Schema| Portal[Customer Portal]
    end
```

## Customer-Safe Boundary

Strict adherence to the [Customer-Safe Status Boundary](../../security/customer-safe-status-boundary/) is required to prevent leaking technical or sensitive billing data.

### Allowed
- **Estimated Total Cost**: Aggregated cost for a run or a customer.
- **Cost Categories**: High-level grouping (e.g., "AI Processing", "Storage").
- **Currency**: The currency used for the estimates.
- **Timestamps**: When the estimate was recorded.

### Forbidden
- **Raw Billing Records**: Actual Azure billing line items or invoices.
- **Subscription & Tenant IDs**: Azure environment identifiers.
- **Resource Group Names**: Internal infrastructure organization.
- **Provider Payloads**: Raw JSON responses from Azure Cost Management or Billing APIs.
- **Technical Logs**: Internal trace IDs or execution logs associated with cost calculation.
- **Secrets & Tokens**: Any credentials used to access pricing or billing APIs.
- **SKU Details**: Specific Azure SKU IDs or internal pricing tier names.

## Local / Demo Flow

You can create a validated cost ledger entry locally using the provided Python implementation.

### Python Import

```python
from capture import capture_cost_entry

entry = capture_cost_entry(
    run_id="run-123",
    category="ai_tokens",
    estimated_amount=0.0045,
    provider="Azure",
    model_or_service="gpt-4o",
    input_units=1000,
    unit_name="token"
)

print(entry)
```

### Validation Failure (Security Boundary)

```python
# This will raise a ValueError due to the forbidden Subscription ID
capture_cost_entry(
    run_id="550e8400-e29b-41d4-a716-446655440000",
    category="ai_tokens",
    estimated_amount=1.0
)
```

## Deployment / IaC decision

This building block is currently a **logic-only reference** for validating and formatting cost entries. It does not introduce any new Azure resources at this stage.

- **Infrastructure**: No new Terraform is added.
- **Assumption**: The calling service (e.g., an Azure Function) will use this module to format data before writing it to a shared storage resource (e.g., Azure Table Storage) defined in the solution's central infrastructure.

## Known Limits

- Does not include real-time pricing lookups from the Azure Retail Prices API.
- Does not handle currency conversion or complex tax calculations.
- Aggregation logic for the customer-safe summary is implemented in the Portal API, not in the capture block.
- String fields are limited to 128 characters to prevent excessive telemetry storage.
