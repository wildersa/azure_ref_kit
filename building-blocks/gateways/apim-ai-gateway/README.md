# APIM AI Gateway Model-Access Building Block

This module implements a minimal, reusable **AI Gateway** using **Azure API Management (APIM)** for controlled access to a single generative-AI model backend.

## Purpose

The AI Gateway provides a governance and security layer between your callers (e.g., agents, applications) and your AI model deployments (e.g., Azure OpenAI, Microsoft Foundry).

## When to Use

- **Recommended**: When you need to centralize token governance, audit usage, redact technical headers, and authenticate callers via Entra ID instead of static backend API keys.
- **Optional**: For simple development scenarios where direct model access is sufficient and governance is not a requirement.

## Supported Topology (v1)

- One Gateway instance governs **one** existing Azure OpenAI or Microsoft Foundry model backend.
- Managed Identity is used for backend authentication; static API keys are forbidden.

## Architecture

The AI Gateway acts as a secure proxy between clients and the model backend. It enforces authentication, applies governance policies, and ensures that telemetry remains customer-safe by redacting technical identifiers and provider-specific headers.

### Mermaid Diagram

```mermaid
flowchart TD
    Caller[Caller or Agent Runtime]
    APIM[APIM AI Gateway]
    Model[Existing Model Backend: Azure OpenAI or Foundry]
    AppInsights[Application Insights / Metrics Boundary]

    Caller -- "1. Authenticated Request" --> APIM
    subgraph APIM_Policies [Policy Enforcement]
        Auth[Authenticated Caller Boundary]
        TPM[Token-per-Minute Governance]
        Telemetry[Safe Token Metrics]
        BackendAuth[Managed Identity Auth]
    end
    APIM -- "2. Authenticated Managed Identity access" --> Model
    Model -- "3. Prompt Result" --> APIM
    APIM -- "4. Redacted Response" --> Caller
    APIM -- "5. Safe Telemetry" --> AppInsights
```

## Prerequisites

- An existing Azure Resource Group.
- An existing Azure OpenAI or Microsoft Foundry model deployment.
- Azure CLI and Terraform for deployment.

## Deployment Inputs

| Input | Type | Description |
|---|---|---|
| `apim_name` | `string` | Name of the API Management instance. |
| `location` | `string` | Azure region for the deployment. |
| `model_endpoint` | `string` | The target model endpoint URL. |
| `model_resource_id` | `string` | The Azure Resource ID of the model for RBAC assignment. |
| `model_id` | `string` | Friendly identifier (e.g., 'gpt-4o') for metrics. |
| `token_limit_per_minute` | `number` | The TPM limit to enforce. |

## Local Validation

Since this is an infrastructure module, local validation focus is on static analysis of policy XML and Terraform HCL.

```bash
# Verify XML syntax
python -m pytest building-blocks/gateways/apim-ai-gateway/tests/
```

## Azure Deployment

Deploy the module using Terraform:

```bash
cd building-blocks/gateways/apim-ai-gateway/infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

## Cost/Operations

### Cost Drivers
- **API Management (APIM)**: Costs depend on the selected SKU (e.g., Standard v2). For GenAI capabilities, v2 tiers are recommended.
- **Application Insights**: Storage costs for emitted metrics and traces.
- **Model Consumption**: The underlying model backend continues to charge based on its own pricing model.

### Operations
- **Monitoring**: Use the emitted `llm-token-metric` in Application Insights to build usage dashboards.
- **Governance**: TPM limits are enforced at the gateway level. If a limit is reached, the gateway returns a `429 Too Many Requests` response.
- **Security**: Regularly rotate calling application identities and audit RBAC assignments for the APIM Managed Identity.

## Security Assumptions

- The Gateway is the only authorized way to access the backend model for the intended workload.
- Callers must provide a valid authentication mechanism recognized by the Gateway.
- Backend access is granted via **least-privilege RBAC** (Cognitive Services User role).

## Limitations

- First version governs exactly one model backend.
- No semantic caching, multi-backend routing, or circuit breakers in this version.
- Requires an APIM SKU that supports GenAI policies (Standard v2 or equivalent).

## Usage

### Caller Authentication

The AI Gateway requires **Microsoft Entra ID (Azure AD)** authentication for all callers.

1.  Obtain an Entra ID token for the audience defined in your deployment (default: `https://cognitiveservices.azure.com`).
2.  Include the token in the `Authorization` header: `Bearer <token>`.

### APIM Subscription

By default, this gateway requires a valid **APIM Subscription Key**.

-   The subscription key must be passed in the `Ocp-Apim-Subscription-Key` header.
-   Token governance (`llm-token-limit`) is enforced per subscription ID.

### Example Usage (Placeholder)

```bash
# Example call to the gateway (Chat Completions)
# Replace <gateway-url> with your deployed APIM gateway URL
# Replace <subscription-key> with a valid APIM subscription key
# Replace <entra-token> with a valid Entra ID access token

curl -X POST "https://<gateway-url>/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "Ocp-Apim-Subscription-Key: <subscription-key>" \
     -H "Authorization: Bearer <entra-token>" \
     -d '{
       "messages": [
         {"role": "user", "content": "Hello, AI Gateway!"}
       ]
     }'
```

## Security & State

### Terraform State Security

**Warning**: Terraform state files and plans for this module contain sensitive infrastructure identifiers.

-   **Do not commit** `terraform.tfstate`, `terraform.tfstate.backup`, or `.tfplan` files to version control.
-   **Do not commit** generated credentials, keys, or tokens.
-   Use a secure remote backend (e.g., Azure Blob Storage with encryption) for production state management.

### Safe Telemetry

The gateway emits safe telemetry only:
-   **Trace**: Logs `RequestId` and `DurationMs`.
-   **Metrics**: Emits token usage counts (TPM) per Subscription ID and Model ID.
-   **Forbidden**: The gateway **never** logs prompts, completions, request/response bodies, authorization headers, subscription keys, or internal resource IDs.

## Cleanup

```bash
terraform destroy
```
