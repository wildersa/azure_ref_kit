# Terraform Deployment for Foundry Agent Basic

This directory contains the Terraform/OpenTofu configuration to deploy the infrastructure prerequisites for the Foundry Agent Basic solution.

## Resources Provisioned

- **Resource Group**: Container for all resources.
- **Azure AI Foundry Hub**: The central management resource (using `azurerm_cognitive_account` with `AIServices` kind).
- **Azure AI Foundry Project**: The workspace for the agent (using `azurerm_cognitive_account_project`).
- **Model Deployment**: GPT-4o-mini deployment for the agent's reasoning.

## Deployment / IaC Decision

**Platform via Terraform, Agent via SDK.**

We use Terraform to manage the stable infrastructure "platform" (Hub, Project, Model). We deliberately leave the **Prompt Agent** definition and versioning to the Python SDK/code-first approach.

This decision is based on:
1. **Developer Experience**: Prompt agents are often iterated on quickly by developers or authors; managing every version in Terraform can be cumbersome.
2. **Foundry Native Flow**: Azure AI Foundry emphasizes a "code-first" deployment for agent versions via the `project.agents.create_version` API.
3. **Microsoft Guidance**: Follows the AzureRM resource pattern documented in [Microsoft Learn](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-resource-terraform?tabs=azurerm).

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) logged in: `az login`
- An active Azure Subscription.

## Deployment Steps

1. **Initialize**:
   ```bash
   terraform init
   ```

2. **Plan**:
   ```bash
   terraform plan -out=tfplan
   ```

3. **Apply**:
   ```bash
   terraform apply tfplan
   ```

## Using the Outputs

After a successful apply, Terraform will output the `AZURE_AI_PROJECT_ENDPOINT`. Use this value to set your environment variable for the solution:

```bash
export AZURE_AI_PROJECT_ENDPOINT=$(terraform output -raw AZURE_AI_PROJECT_ENDPOINT)
```

Then you can run the solution as described in the root [README.md](../README.md).
