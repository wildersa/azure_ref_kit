# Terraform Deployment for Queue Function Agent Tool

This directory contains the Terraform configuration to deploy the Queue-triggered Azure Function as an agent tool.

## Resources Provisioned

- **Azure Resource Group**: Container for all resources.
- **Azure Storage Account**: Used for the Function's internal state and the input/output queues.
- **Azure Storage Queues**:
  - `agent-tool-input-queue`: The queue where the agent sends requests.
  - `agent-tool-output-queue`: The queue where the function sends results.
- **Azure Service Plan**: Configured with the **Flex Consumption (FC1)** SKU.
- **Azure Linux Function App**: The host for the Python function code.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
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

The Function App is configured with two key application settings:
- `AzureWebJobsStorage`: Connection string for internal function management.
- `STORAGE_CONNECTION`: Connection string used by the queue triggers and outputs.

By default, both point to the same Storage Account provisioned by this module.
