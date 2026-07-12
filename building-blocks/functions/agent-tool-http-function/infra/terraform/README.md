# Infrastructure for Agent Tool HTTP Function

This directory contains minimal Terraform to deploy the Agent Tool HTTP Function and its required Azure resources.

## Resources Created

- **Resource Group**: Container for all resources.
- **Storage Account**: Required by Azure Functions for state and code management.
- **App Service Plan**: Consumption (serverless) plan.
- **Linux Function App**: Hosts the Python function.
- **Application Insights**: Provides observability and logs.

## Deployment

1. **Login to Azure**:
   ```bash
   az login
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Plan and Apply**:
   ```bash
   terraform apply
   ```

## Configuration

The following variables can be customized in `variables.tf` or via a `.tfvars` file:

- `name_prefix`: Prefix for resource names.
- `location`: Azure region (default: `eastus`).
- `environment`: Environment name (default: `dev`).

## Security Note

This deployment uses **Function Key** authorization by default. The function key must be provided in the `x-functions-key` header or as a `code` query parameter when calling the deployed endpoint.
