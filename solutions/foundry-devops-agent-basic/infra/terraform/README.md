# Infrastructure for Foundry DevOps Status Agent

This directory contains the minimal Terraform configuration required to provision the Azure resources for the Foundry DevOps Status Agent solution.

## Resources Provisioned

- **Azure Resource Group**: Container for all resources.
- **Azure AI Foundry Hub (AIServices)**: The top-level resource for AI Foundry.
- **Azure AI Foundry Project**: The project where the agent will be configured.
- **Cognitive Deployment**: A deployment of `gpt-4o-mini` (or your preferred model) for the agent's brain.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) installed.
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated.

## Deployment

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Plan the deployment:
   ```bash
   terraform plan -out=tfplan
   ```

3. Apply the deployment:
   ```bash
   terraform apply tfplan
   ```

## Inputs

| Name | Description | Default |
|------|-------------|---------|
| `location` | The Azure region for resources. | `eastus2` |
| `prefix` | A prefix for resource naming. | `devops-agent` |
| `gpt_model_name` | The name of the GPT model. | `gpt-4o-mini` |
| `gpt_model_version` | The version of the model. | `2024-07-18` |

## Outputs

| Name | Description |
|------|-------------|
| `project_endpoint` | The endpoint for the AI Project (used in `AZURE_AI_PROJECT_ENDPOINT`). |
| `project_name` | The name of the AI Project. |
| `model_deployment_name` | The name of the model deployment (used in `AZURE_AI_MODEL_NAME`). |

## Identity and Access

This configuration uses System-Assigned Managed Identities for the Hub and Project. To use the agent, the calling user or service principal needs the **Foundry User** role on the AI Project.

## Security and Cost

- **Security**: No secrets or PATs are managed via this Terraform. They must be provided via environment variables to the Python runtime.
- **Cost**: The AIServices S0 tier and GPT deployment incur costs based on usage. Standard scale is 10k TPM.
- **Rollback**: Manual `terraform destroy` is required to clean up resources.
