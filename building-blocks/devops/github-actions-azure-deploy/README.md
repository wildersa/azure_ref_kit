# GitHub Actions Azure Deployment Reference

Secure GitHub Actions deployment pattern for publishing the [Static Status Portal](../../portals/static-status-portal/) to Azure Static Web Apps.

## Purpose

This building block defines secure reference patterns for deploying to Azure using GitHub Actions. It prioritizes identity-based authentication (OIDC) to minimize the use of long-lived secrets.

## When to Use These Patterns

- **Use when**: Deploying frontend applications to Azure Static Web Apps or infrastructure via Terraform/OpenTofu from a GitHub repository.
- **Use when**: You want to eliminate long-lived Service Principal secrets in GitHub using OpenID Connect (OIDC).
- **Do not use when**: Deploying to non-Azure targets or using legacy credential-based authentication as the primary method.

## Deployment Architecture

The following diagram illustrates the secure deployment boundary:

```mermaid
graph TD
    Developer[Developer] -->|Push Code| GitHub[GitHub Repository]
    GitHub -->|Trigger| GHA[GitHub Actions Workflow]

    subgraph "Azure Auth & Deploy Boundary"
        GHA -->|OIDC Auth| Entra[Microsoft Entra ID]
        Entra -->|Short-lived Token| SWADeploy[Azure Static Web Apps Deploy Action]
    end

    subgraph "Hosting & Outcome"
        SWADeploy -->|Upload Artifacts| SWAHost[Azure Static Web Apps Hosting]
        SWAHost -->|Serves| Portal[Customer-Safe Portal]
    end
```

## Configuration and Secrets

To implement this pattern securely, configure the following GitHub Repository Secrets. **Never commit these values to the repository.**

| Name | Type | Description |
|------|------|-------------|
| `AZURE_CLIENT_ID` | Secret | The Application (client) ID of the Entra ID app or Managed Identity configured for OIDC. |
| `AZURE_TENANT_ID` | Secret | The Directory (tenant) ID of your Azure tenant. |
| `AZURE_SUBSCRIPTION_ID` | Secret | The ID of the Azure Subscription. |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Secret | (Optional) The SWA deployment token. Required if not using the full OIDC integration for the upload action. |
| `BACKEND_RESOURCE_GROUP_NAME` | Secret | The resource group name for the Terraform remote backend. |
| `BACKEND_STORAGE_ACCOUNT_NAME` | Secret | The storage account name for the Terraform remote backend. |
| `BACKEND_CONTAINER_NAME` | Secret | The container name for the Terraform remote backend. |
| `BACKEND_KEY` | Secret | The state file key for the Terraform remote backend. |

### Configuration Variables

| Name | Type | Description |
|------|------|-------------|
| `ENVIRONMENT_NAME` | Variable | The name of the GitHub Environment used for deployment gating (e.g., `durable-pipeline-deploy`). |

### OIDC Configuration Prerequisites
1. Create a Microsoft Entra application or User-Assigned Managed Identity.
2. Configure **Federated Identity Credentials** in Azure to trust your GitHub repository, branch, or environment.
3. Assign the `Contributor` role (or a custom role with SWA deployment permissions) to the identity at the target resource or resource group scope.

## Reference Workflow: Deploy Static Status Portal

The following YAML demonstrates a secure deployment for the `static-status-portal`.

```yaml
name: Deploy Static Status Portal

on:
  push:
    branches: [ main ]
    paths:
      - 'building-blocks/portals/static-status-portal/**'
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches: [ main ]
    paths:
      - 'building-blocks/portals/static-status-portal/**'

jobs:
  build_and_deploy:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.action != 'closed')
    runs-on: ubuntu-latest
    permissions:
      id-token: write # Mandatory for OIDC
      contents: read  # Mandatory for checkout

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: 'Az CLI Login'
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: 'Get ID Token for SWA'
        uses: actions/github-script@v7
        id: idtoken
        with:
          script: |
            const id_token = await core.getIDToken();
            core.setOutput('token', id_token);

      - name: Build And Deploy
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          # Use github_id_token for OIDC-native deployment to SWA
          github_id_token: ${{ steps.idtoken.outputs.token }}
          action: "upload"
          app_location: "building-blocks/portals/static-status-portal/src"
          api_location: "" # Linked API is handled separately or via portal-api-functions
          output_location: "dist" # Folder where the build output is generated
```

## Reference Workflow: Deploy Durable Basic Pipeline Infrastructure

The following YAML demonstrates a secure Terraform deployment for the [Durable Basic Pipeline](../../pipelines/durable-basic-pipeline/infra/terraform/). It includes static validation, planning, and deployment stages with environment-based gating.

```yaml
name: Deploy Durable Basic Pipeline

on:
  push:
    branches: [ main ]
    paths:
      - 'building-blocks/pipelines/durable-basic-pipeline/infra/terraform/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'building-blocks/pipelines/durable-basic-pipeline/infra/terraform/**'

permissions:
  id-token: write
  contents: read

env:
  TF_WORKING_DIR: 'building-blocks/pipelines/durable-basic-pipeline/infra/terraform'
  # Terraform OIDC environment variables
  ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  ARM_USE_OIDC: true

jobs:
  static_validation:
    name: 'Static Validation'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        working-directory: ${{ env.TF_WORKING_DIR }}
      - name: Terraform Init & Validate
        run: |
          terraform init -backend=false
          terraform validate
        working-directory: ${{ env.TF_WORKING_DIR }}

  plan:
    name: 'Infrastructure Plan'
    needs: static_validation
    runs-on: ubuntu-latest
    environment: durable-pipeline-deploy
    steps:
      - uses: actions/checkout@v4
      - name: 'Az CLI Login'
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      - name: Terraform Plan
        run: |
          terraform init \
            -backend-config="resource_group_name=${{ secrets.BACKEND_RESOURCE_GROUP_NAME }}" \
            -backend-config="storage_account_name=${{ secrets.BACKEND_STORAGE_ACCOUNT_NAME }}" \
            -backend-config="container_name=${{ secrets.BACKEND_CONTAINER_NAME }}" \
            -backend-config="key=${{ secrets.BACKEND_KEY }}"
          terraform plan -input=false
        working-directory: ${{ env.TF_WORKING_DIR }}

  deploy:
    name: 'Infrastructure Deploy'
    needs: plan
    runs-on: ubuntu-latest
    environment: durable-pipeline-deploy
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: 'Az CLI Login'
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      - name: Terraform Apply
        run: |
          terraform init \
            -backend-config="resource_group_name=${{ secrets.BACKEND_RESOURCE_GROUP_NAME }}" \
            -backend-config="storage_account_name=${{ secrets.BACKEND_STORAGE_ACCOUNT_NAME }}" \
            -backend-config="container_name=${{ secrets.BACKEND_CONTAINER_NAME }}" \
            -backend-config="key=${{ secrets.BACKEND_KEY }}"
          terraform apply -auto-approve -input=false
        working-directory: ${{ env.TF_WORKING_DIR }}
```

## Security & Customer-Safe Boundary

This pattern enforces strict boundaries to prevent leakage of technical internals:

- **Forbidden in Repository**: Never commit `.env`, `.publishsettings`, `.json` credentials, or hardcoded IDs.
- **Identity First**: Prefer OIDC over long-lived secrets.
- **Least Privilege**: The deployment identity should only have permissions to deploy to the specific SWA resource.
- **Log Masking**: GitHub Actions automatically masks secrets, but avoid printing technical identifiers (Tenant ID, Subscription ID) in non-secret variables if they might appear in customer-facing logs.

## Deployment/IaC Decision

- **Pattern-Only**: This building block defines the *workflow* contract. It does not include Terraform/OpenTofu files because it focuses on the GitHub Actions orchestration.
- **Prerequisites**: It assumes the Azure Static Web App resource has been provisioned (e.g., via a separate infra module or manually for initial setup).

## References
- [GitHub Actions for Azure Overview](https://learn.microsoft.com/en-us/azure/developer/github/github-actions)
- [Deploy to Azure Static Web Apps with GitHub Actions](https://learn.microsoft.com/en-us/azure/static-web-apps/build-configuration)
- [Azure Login action / OpenID Connect guidance](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
