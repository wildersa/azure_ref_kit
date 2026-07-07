# Infrastructure for Web App Hosted Agent API

Minimal Terraform to deploy an Azure App Service (Web App) with Python runtime for hosting an agent API.

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
- Azure Service Plan (Linux)
- Azure Linux Web App (Python runtime)
- System-Assigned Managed Identity

## Security Defaults

- **Managed Identity:** Uses System-Assigned identity for least-privilege access to other Azure services.
- **HTTPS Only:** Enforced at the platform level.
- **Minimal SKU:** Defaults to B1, which is the entry-level production SKU supporting custom domains and SSL.

## Cost Drivers

- **App Service Plan:** B1 and higher tiers have a fixed monthly cost.
- **Outbound Data:** Standard Azure data egress charges apply.

## Module Contract Alignment

- **Inputs:** Variables `python_version` and `startup_command` align with the `module.yaml` definition.
- **Outputs:** `app_service_url` aligns with the `module.yaml` output contract.
