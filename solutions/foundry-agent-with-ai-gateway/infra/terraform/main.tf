# Foundry Agent with APIM AI Gateway
# This Terraform configuration composes the APIM AI Gateway building block
# and configures a Microsoft Foundry connection to use it for model access.

# 1. AI Gateway Building Block
module "ai_gateway" {
  source = "../../../building-blocks/gateways/apim-ai-gateway/infra/terraform"

  resource_group_name    = var.resource_group_name
  location               = var.location
  apim_name              = var.apim_name
  publisher_name         = var.publisher_name
  publisher_email        = var.publisher_email
  model_endpoint         = var.model_endpoint
  model_id               = var.model_id
  model_resource_id      = var.model_resource_id
  token_limit_per_minute = var.token_limit_per_minute
  tenant_id              = var.tenant_id
  audience               = var.audience
}

# 2. Get the Primary Key for the APIM Subscription (needed for the Foundry Connection)
# The building block requires subscriptions. We use the default 'master' or a new one.
resource "azurerm_api_management_subscription" "foundry_sub" {
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  display_name        = "Foundry Agent Subscription"
  state               = "active"
  # Optional: Link to a specific API if needed, but the gateway module uses a single API.
  # api_id is not strictly needed if the gateway only has one API, but good for least-privilege.
}

# 3. Create the Foundry Connection using APIM as the Model Gateway
# We use azapi as the current azurerm provider might have limitations with the latest
# Foundry (Cognitive Services) connection properties for ApiManagement category.

resource "azapi_resource" "foundry_apim_connection" {
  type      = "Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview"
  name      = "ai-gateway-connection"
  parent_id = var.foundry_hub_id

  body = {
    properties = {
      category      = "ApiManagement"
      authType      = "ApiKey"
      target        = "${module.ai_gateway.gateway_url}/openai"
      isSharedToAll = true
      credentials = {
        key = azurerm_api_management_subscription.foundry_sub.primary_key
      }
      metadata = {
        ApiType             = "Azure"
        inferenceAPIVersion = "2024-12-01-preview"
        # Location and models are useful for the Foundry UI/SDK to know what's behind the gateway
        Location         = var.location
        deploymentInPath = "true"
        # We pass a minimal model list to satisfy the UI/SDK
        models = jsonencode([
          {
            name = var.model_id
            properties = {
              model = {
                name   = var.model_id
                format = "OpenAI"
              }
            }
          }
        ])
      }
    }
  }
}
