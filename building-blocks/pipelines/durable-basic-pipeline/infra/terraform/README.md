# Durable Basic Pipeline Infrastructure

This directory contains the Terraform configuration to deploy the Durable Basic Pipeline on Azure.

## Resources Provisioned

- **Resource Group**: Logical container for all resources.
- **Azure Storage Account**: Used for Durable Functions state, orchestration history, and deployment artifacts.
- **Log Analytics Workspace & Application Insights**: For observability and monitoring.
- **App Service Plan (Flex Consumption)**: Serverless hosting for Azure Functions.
- **Azure Function App**: Hosts the Durable Functions (Orchestrator and Activities).

## Deployment Assumptions

- The deployment uses **Azure Functions Flex Consumption (FC1)**.
- **System-Assigned Managed Identity** is used for the Function App to access the Storage Account.
- **Identity-first configuration** is used for `AzureWebJobsStorage`, avoiding the use of storage connection strings.

## Cost Drivers

- **Azure Functions Flex Consumption**: Billed based on execution count and resource consumption (memory/time).
- **Azure Storage**: Costs for data storage (especially orchestration history), transactions, and bandwidth.
- **Application Insights**: Billed based on the amount of telemetry data ingested.

## App Settings

- `AzureWebJobsStorage__accountName`: Name of the storage account.
- `AzureWebJobsStorage__credential`: Set to `managedidentity` for identity-based connection.
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Connection string for Application Insights.

## Identity and Storage Decisions

- **Shared Access Key access is disabled** on the storage account (`shared_access_key_enabled = false`) to enforce Microsoft Entra authorization.
- The Function App is granted the following roles on the storage account:
  - `Storage Blob Data Owner` (required for AzureWebJobsStorage when keys are disabled)
  - `Storage Queue Data Contributor` (for Durable Functions orchestration queues)
  - `Storage Table Data Contributor` (for Durable Functions orchestration history/tracking)

## Durable Functions Limits

- Orchestrator functions must be **deterministic**. Do not use random numbers, GUIDs, or current date/time directly in the orchestrator logic (use `context.current_utc_datetime` instead).
- Avoid long-running tasks in orchestrators; use Activity functions for such tasks.
- For more details, see [Durable Functions limits and constraints](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-orchestrations?tabs=python#reliability).
