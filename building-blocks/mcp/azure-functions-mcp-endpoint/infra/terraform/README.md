# Terraform Deployment: Azure Functions MCP Endpoint

This directory contains Terraform/OpenTofu code to deploy the Azure resources required to host the Azure Functions MCP Endpoint.

## Architecture

The deployment follows the **Azure Functions Flex Consumption** pattern with **Identity-First** security:
- **Azure Function App (Flex Consumption)**: Hosts the MCP tools.
- **Azure Storage Account**: Used by the Function App for internal state and the MCP extension.
- **User-Assigned Managed Identity**: Provides the Function App with secure, keyless access to storage.
- **Application Insights & Log Analytics**: Provides observability and telemetry.

## Prerequisites
- [Terraform](https://www.terraform.io/downloads.html) or [OpenTofu](https://opentofu.org/docs/intro/install/) (>= 1.0)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Authenticated to Azure: `az login`

## Deployment Steps

1. **Initialize Terraform**:
   ```bash
   terraform init -backend-config="resource_group_name=<backend_rg>" \
                  -backend-config="storage_account_name=<backend_storage>" \
                  -backend-config="container_name=<backend_container>" \
                  -backend-config="key=mcp-endpoint.tfstate"
   ```

2. **Customize Variables**:
   Create a `terraform.tfvars` file or pass variables via the command line:
   - `prefix`: Prefix for resource names (default: `mcp-af`).
   - `location`: Azure region (default: `East US`).
   - `resource_group_name`: Optional name of an existing resource group.

3. **Plan & Apply**:
   ```bash
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

## Variables

| Name | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `prefix` | `string` | `"mcp-af"` | Prefix for all resources. |
| `location` | `string` | `"East US"` | Azure region for deployment. |
| `resource_group_name` | `string` | `""` | Optional: Existing resource group name. |

## Outputs

| Name | Description |
| :--- | :--- |
| `function_app_name` | The name of the deployed Function App. |
| `function_app_default_hostname` | The default hostname of the Function App. |
| `mcp_endpoint_url` | The full URL for the MCP Streamable HTTP endpoint. |
| `resource_group_name` | The name of the resource group used. |

## Security and Identity
This module enforces an **identity-first** posture:
- `shared_access_key_enabled = false` on the storage account.
- The Function App uses a **User-Assigned Managed Identity**.
- Role-based access control (RBAC) is granted for Blob, Queue, and Table data.
