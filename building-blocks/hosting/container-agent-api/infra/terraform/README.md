# Infrastructure as Code: Azure Container Apps

This directory contains the Terraform configuration to deploy the `container-agent-api` to Azure Container Apps.

## Resources Created

- **Resource Group:** Logical container for all resources.
- **Log Analytics Workspace:** Stores application and system logs.
- **Container App Environment:** The hosting environment for the container app.
- **Container App:** The serverless container hosting the agent API.
- **Managed Identity:** A system-assigned managed identity for the Container App to securely access other Azure resources.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- An existing container image in a registry (e.g., Azure Container Registry).

## Deployment

1.  **Initialize Terraform:**
    ```bash
    terraform init
    ```

2.  **Create a Plan:**
    ```bash
    terraform plan -var="container_image=<your-registry>.azurecr.io/agent-api:v1" -out=tfplan
    ```

3.  **Apply the Configuration:**
    ```bash
    terraform apply tfplan
    ```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `prefix` | Prefix for resource names. | `agent-api` |
| `location` | Azure region for deployment. | `East US` |
| `container_image` | The full URI of the container image to deploy. | **Required** |
| `tags` | Tags to apply to all resources. | See `variables.tf` |

## Outputs

| Name | Description |
|------|-------------|
| `api_endpoint` | The public FQDN of the deployed Container App. |
| `resource_group_name` | The name of the created Resource Group. |

## Security Best Practices

- **Identity-First:** This deployment uses a System-Assigned Managed Identity. Downstream resources should grant RBAC permissions to this identity instead of using connection strings or keys.
- **Ingress:** External ingress is enabled on port 8080. In production, consider restricting ingress to a Virtual Network or using an API Gateway.
- **Secrets:** Do not hardcode secrets in Terraform variables. Use Azure Key Vault and reference secrets in the Container App environment variables if needed.
