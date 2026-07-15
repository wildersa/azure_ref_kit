# Infrastructure: Application Insights Observability

This directory contains the Terraform configuration to provision a Log Analytics Workspace and a workspace-based Application Insights resource.

## Resources

- `azurerm_log_analytics_workspace`: Provides the storage backend for telemetry.
- `azurerm_application_insights`: Provides the observability platform for technical telemetry.

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Plan the deployment:
   ```bash
   terraform plan -var-file=your.tfvars
   ```

3. Apply the changes:
   ```bash
   terraform apply -var-file=your.tfvars
   ```

## Outputs

- `application_insights_connection_string`: (Sensitive) Used by applications to send telemetry.
- `application_insights_instrumentation_key`: (Sensitive) Legacy key, use connection string where possible.
- `log_analytics_workspace_id`: ID for the workspace backend.
