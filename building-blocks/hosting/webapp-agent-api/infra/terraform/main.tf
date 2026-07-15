resource "random_string" "unique" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.prefix}-${random_string.unique.result}"
  location = var.location
  tags     = var.tags
}

resource "azurerm_service_plan" "plan" {
  name                = "asp-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1" # Basic tier for reference, scalable.
}

resource "azurerm_linux_web_app" "agent_api" {
  name                = "app-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      docker_image_name   = var.container_image
      docker_registry_url = "https://${var.container_registry_server}"
    }
    container_registry_use_managed_identity = true
  }

  app_settings = {
    "WEBSITES_PORT" = "8080"
  }

  # Secure inbound default: Enable EasyAuth
  auth_settings_v2 {
    auth_enabled           = true
    default_provider       = "azuread"
    unauthenticated_action = "Return401"

    login {
      token_store_enabled = true
    }

    active_directory_v2 {
      client_id            = var.client_id
      tenant_auth_endpoint = "https://sts.windows.net/${var.tenant_id}/v2.0"
    }
  }

  https_only = true

  tags = var.tags
}

resource "azurerm_role_assignment" "acr_pull" {
  count                = var.container_registry_id != null ? 1 : 0
  scope                = var.container_registry_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_web_app.agent_api.identity[0].principal_id
}
