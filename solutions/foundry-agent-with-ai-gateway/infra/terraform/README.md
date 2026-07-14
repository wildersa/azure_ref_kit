# Infrastructure for Foundry Agent with AI Gateway

This Terraform configuration deploys the necessary infrastructure to route a Microsoft Foundry agent's model access through an APIM AI Gateway.

## Resources Created

- **APIM AI Gateway**: Composed from the `apim-ai-gateway` building block.
- **APIM Subscription**: A dedicated subscription for the Foundry Agent.
- **Foundry Connection**: A connection in the Azure AI Foundry Hub that targets the APIM Gateway using the `ApiManagement` category.

## Deployment

1. Initialize Terraform:
   ```bash
   terraform init
   ```
2. Plan the deployment:
   ```bash
   terraform plan -var-file=yourvalues.tfvars
   ```
3. Apply the changes:
   ```bash
   terraform apply
   ```

## Sensitive Information

- `apim_subscription_key`: This output contains the APIM subscription key used by the Foundry connection. It is marked as sensitive and will not be displayed in the terminal. Use `terraform output -json` to retrieve it if necessary.
- **Warning**: Do not commit your Terraform state files or any files containing real secrets.
