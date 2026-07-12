# Infrastructure for Agent Tool Queue Function

This directory contains the Terraform configuration to deploy the required Azure resources for the Queue-based Agent Tool.

## Resources Created

- **Resource Group**: Container for all resources.
- **Storage Account**: Used for Function App state and hosting the queues.
- **Storage Queues**:
    - `agent-tool-input`: Receives tool call requests from the agent.
    - `agent-tool-output`: Receives processed results from the function.
- **Service Plan**: Flex Consumption plan for the Function App.
- **Linux Function App**: Python 3.11 environment running the tool logic.
- **Role Assignments**: System-assigned identity for the Function App with least-privilege access to the storage account (Queues and Blobs).

## Deployment

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Validate configuration:
   ```bash
   terraform validate
   ```

3. Deploy:
   ```bash
   terraform apply
   ```

## Variables

| Name | Description | Default |
|------|-------------|---------|
| `name_prefix` | Prefix for resource naming (3-12 alphanumeric). | (Required) |
| `location` | Azure region. | `eastus` |
| `environment` | Environment name. | `dev` |
