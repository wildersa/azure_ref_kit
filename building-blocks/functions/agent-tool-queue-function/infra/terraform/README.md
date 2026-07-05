# Terraform Deployment for Queue Function Agent Tool

This directory contains the Terraform configuration to deploy the Queue-triggered Azure Function as an agent tool using the specialized **Flex Consumption** model.

## Resources Provisioned

- **Azure Resource Group**: Container for all resources.
- **Azure Storage Account**: Used for the Function's internal state and the input/output queues.
- **Azure Storage Container**: `deploymentpackage` container for hosting the function zip.
- **Azure Storage Queues**:
  - `agent-tool-input-queue`: The queue where the agent sends requests.
  - `agent-tool-output-queue`: The queue where the function sends results.
- **Azure Service Plan**: Configured with the **Flex Consumption (FC1)** SKU.
- **Azure Flex Consumption Function App**: The specialized host for Python 3.11 serverless functions.
- **Role Assignment**: Assigns `Storage Blob Data Owner` to the Function App's System-Assigned Managed Identity for secure access to the deployment container.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest) >= 4.0.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- An active Azure Subscription

## Deployment Steps

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Customize Variables (Optional)**:
   Create a `terraform.tfvars` file or pass variables via the command line to customize `location`, `prefix`, and `tags`.

3. **Plan Deployment**:
   ```bash
   terraform plan
   ```

4. **Apply Changes**:
   ```bash
   terraform apply
   ```

## Configuration Note

The Function App uses the specialized `azurerm_function_app_flex_consumption` resource. It is configured with identity-based storage access for the deployment package and a connection string for the queue interactions (`STORAGE_CONNECTION`).
