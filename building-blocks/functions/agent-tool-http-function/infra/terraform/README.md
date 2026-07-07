# Infrastructure for HTTP Function Agent Tool

Minimal Terraform to deploy a Flex Consumption Function App for the HTTP status tool.

## Deployment

1. Initialize:
   ```bash
   terraform init
   ```

2. Validate:
   ```bash
   terraform validate
   ```

3. Deploy:
   ```bash
   terraform apply
   ```

## Resources

- Azure Resource Group
- Azure Storage Account (for Function state and deployment)
- Azure Service Plan (Flex Consumption FC1)
- Azure Function App (Flex Consumption)
- Managed Identity with Storage Blob Data Owner role
