# Infrastructure for Web App Hosted Agent API

This folder contains the Terraform/OpenTofu configuration to deploy an Azure Linux Web App for Containers to host an agent-facing API.

## Resources Created

- **Resource Group:** A new resource group for all hosting resources.
- **App Service Plan:** A Linux App Service plan (defaulting to B1 SKU).
- **Linux Web App:** Configured for custom containers with HTTPS-only and system-assigned managed identity.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) or [OpenTofu](https://opentofu.org/docs/intro/install/) installed.
- Azure CLI authenticated (`az login`).
- A container image ready in a registry (e.g., Azure Container Registry or Docker Hub).

## Usage

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Plan the deployment:**
   ```bash
   terraform plan -var="container_image=<your-registry>.azurecr.io/agent-api:latest"
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply -var="container_image=<your-registry>.azurecr.io/agent-api:latest"
   ```

## Variables

| Name | Type | Description | Default |
|------|------|-------------|---------|
| `prefix` | `string` | Prefix for resource names. | `webappapi` |
| `location` | `string` | Azure region for deployment. | `eastus` |
| `container_image` | `string` | The container image URI to deploy. | (Required) |
| `listen_port` | `number` | The port the container listens on. | `8080` |
| `sku_name` | `string` | The SKU name for the App Service Plan. | `B1` |
| `tags` | `map(string)` | Tags for resources. | See `variables.tf` |

## Outputs

| Name | Description |
|------|-------------|
| `webapp_name` | The name of the deployed web app. |
| `api_endpoint` | The public URL of the hosted API. |
| `resource_group_name` | The name of the resource group. |
| `principal_id` | The principal ID of the system-assigned managed identity. |
