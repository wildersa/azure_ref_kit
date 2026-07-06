# Document AI Portal Foundation Infrastructure

This directory contains the Terraform configuration for the core infrastructure of the Document AI Portal solution.

## Resources Provisioned

- **Resource Group**: Logical container for all solution resources.
- **Storage Account**: Centralized storage for:
  - `input` container: For document uploads.
  - `artifacts` container: For processed results.
  - `deployment` container: For function app code packages.
  - `pipelinestatus` table: For tracking pipeline execution.
  - `costledger` table: For capturing estimated processing costs.
- **Observability**:
  - **Log Analytics Workspace**: For log aggregation.
  - **Application Insights**: For application performance monitoring and distributed tracing.
- **Hosting Foundation**:
  - **App Service Plan**: Configured for **Flex Consumption** (FC1) to support serverless functions.
  - **Function Apps**:
    - `api`: Hosts the `portal-api-functions` module.
    - `pipeline`: Hosts the worker and orchestration modules (`ocr-document-intelligence`, `field-validation-worker`, `final-result-publisher`, `durable-basic-pipeline`).
- **Portal Hosting**:
  - **Static Web App**: Host for the React-based customer portal.
- **Identity & Security**:
  - **User-Assigned Managed Identity**: Used by the solution components for secure service-to-service access.
  - **RBAC Assignments**: Least-privilege access for the identity (Storage Blob Data Contributor, Storage Table Data Contributor).
  - **Identity-First Storage**: Shared Key access is explicitly disabled (`shared_access_key_enabled = false`), enforcing Microsoft Entra authorization for all data operations.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- An active Azure subscription with permissions to create the resources listed above.

## Usage

### 1. Initialize

```bash
terraform init -backend=false solutions/document-ai-portal/infra/terraform
```

### 2. Validate

```bash
terraform validate solutions/document-ai-portal/infra/terraform
```

### 3. Format Check

```bash
terraform fmt -check -recursive solutions/document-ai-portal/infra/terraform
```

### 4. Plan

```bash
terraform plan -out=tfplan
```

### 5. Apply

```bash
terraform apply tfplan
```

## Intentionally Not Deployed Yet

- **Networking**: Production-grade networking (Private Endpoints, VNets) is excluded from this foundation to keep the initial reference simple.
- **Authentication**: External authentication providers for the Static Web App are not configured in this basic foundation.
