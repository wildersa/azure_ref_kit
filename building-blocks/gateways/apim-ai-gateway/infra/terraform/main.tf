# APIM AI Gateway: Model Access Module
# - Deploys APIM with Managed Identity
# - Registers Model Backend
# - Sets up API and Policy
# - Grants APIM Backend Access via RBAC

data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# 1. Managed Identity for APIM
resource "azurerm_user_assigned_identity" "apim_identity" {
  name                = "id-${var.apim_name}"
  location            = var.location
  resource_group_name = data.azurerm_resource_group.rg.name
}

# 2. Azure API Management (Standard v2 recommended for GenAI)
resource "azurerm_api_management" "apim" {
  name                = var.apim_name
  location            = var.location
  resource_group_name = data.azurerm_resource_group.rg.name
  publisher_name      = var.publisher_name
  publisher_email     = var.publisher_email

  sku_name = var.apim_sku

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.apim_identity.id]
  }
}

# 3. Backend Model Registration
resource "azurerm_api_management_backend" "model_backend" {
  name                = "model-backend"
  resource_group_name = data.azurerm_resource_group.rg.name
  api_management_name = azurerm_api_management.apim.name
  protocol            = "http"
  url                 = var.model_endpoint

  description = "Backend for AI Model access via Gateway."
}

# 4. API Definition (Simplified Proxy)
resource "azurerm_api_management_api" "model_api" {
  name                = "model-api"
  resource_group_name = data.azurerm_resource_group.rg.name
  api_management_name = azurerm_api_management.apim.name
  revision            = "1"
  display_name        = "AI Model Gateway API"
  path                = "v1"
  protocols           = ["https"]

  import {
    content_format = "openapi"
    content_value  = <<-EOT
      openapi: 3.0.1
      info:
        title: AI Model Gateway API
        version: v1
      paths:
        /chat/completions:
          post:
            summary: Chat completions
            responses:
              200:
                description: Successful response
    EOT
  }
}

# 5. Policy Attachment
resource "azurerm_api_management_api_policy" "model_policy" {
  api_name            = azurerm_api_management_api.model_api.name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = data.azurerm_resource_group.rg.name

  xml_content = replace(
    replace(
      file("${path.module}/policies/model-access.xml"),
      "{{TOKEN_LIMIT_PER_MINUTE}}", var.token_limit_per_minute
    ),
    "{{MODEL_ID}}", var.model_id
  )
}

# 6. Least-Privilege RBAC for APIM to Model Backend
resource "azurerm_role_assignment" "apim_backend_access" {
  scope                = var.model_resource_id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_user_assigned_identity.apim_identity.principal_id
}

# 7. (Optional) Application Insights integration
resource "azurerm_api_management_logger" "apim_logger" {
  count               = var.app_insights_resource_id != "" ? 1 : 0
  name                = "apim-logger"
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = data.azurerm_resource_group.rg.name
  resource_id         = var.app_insights_resource_id

  application_insights {
    instrumentation_key = var.app_insights_instrumentation_key
  }
}
