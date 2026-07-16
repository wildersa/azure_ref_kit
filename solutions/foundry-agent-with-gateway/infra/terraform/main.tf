# Foundry Agent with APIM AI Gateway
# This Terraform configuration configures a Microsoft Foundry connection
# to use an EXISTING APIM AI Gateway for model access.

# 1. Scoped APIM Subscription for the Foundry Connection
resource "azurerm_api_management_subscription" "foundry_sub" {
  api_management_name = var.apim_name
  resource_group_name = var.apim_resource_group_name
  display_name        = "Foundry Agent Subscription"
  state               = "active"

  # Least-privilege: scope the subscription to the specific model gateway API
  api_id = var.gateway_api_id
}

# 2. Create the Foundry Connection using APIM as the Model Gateway
# We scope this to the PROJECT (foundry_project_id) instead of the Hub
# and ensure it is NOT shared globally (isSharedToAll = false).

resource "azapi_resource" "foundry_apim_connection" {
  type      = "Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview"
  name      = "ai-gateway-connection"
  parent_id = var.foundry_project_id

  body = {
    properties = {
      category      = "ApiManagement"
      authType      = "ApiKey"
      target        = "${var.gateway_url}/openai"
      isSharedToAll = false
      credentials = {
        key = azurerm_api_management_subscription.foundry_sub.primary_key
      }
      metadata = {
        ApiType             = "Azure"
        inferenceAPIVersion = "2024-12-01-preview"
        Location            = var.location
        deploymentInPath    = "true"
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
