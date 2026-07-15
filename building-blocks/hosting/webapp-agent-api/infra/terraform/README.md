# Terraform Deployment: Web App-hosted Agent API

This directory contains the Terraform configuration to deploy the Web App-hosted Agent API.

## Resources

- `azurerm_resource_group`: Container for all resources.
- `azurerm_service_plan`: App Service Plan (Linux, Basic tier).
- `azurerm_linux_web_app`: The Web App for Containers hosting the agent API.
- `azurerm_role_assignment`: (Optional) Grants `AcrPull` permissions to the Web App's Managed Identity.

## Prerequisites

- An Azure Container Registry (ACR) containing the `container-agent-api` image.
- A Microsoft Entra ID App Registration for EasyAuth.

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Create a `terraform.tfvars` file with required variables:
   ```hcl
   container_image           = "myregistry.azurecr.io/container-agent-api:latest"
   container_registry_server = "myregistry.azurecr.io"
   client_id                 = "00000000-0000-0000-0000-000000000000"
   tenant_id                 = "00000000-0000-0000-0000-000000000000"
   ```

3. Deploy:
   ```bash
   terraform apply
   ```
