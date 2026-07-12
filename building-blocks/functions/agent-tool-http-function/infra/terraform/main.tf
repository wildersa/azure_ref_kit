resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  resource_group_name    = "${var.name_prefix}-${var.environment}-rg"
  storage_account_name   = "${var.name_prefix}${var.environment}st${random_string.suffix.result}"
  app_service_plan_name  = "${var.name_prefix}-${var.environment}-asp"
  function_app_name      = "${var.name_prefix}-${var.environment}-func-${random_string.suffix.result}"
  application_insights_name = "${var.name_prefix}-${var.environment}-ai"
}

resource "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "st" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Security hardening
  min_tls_version          = "TLS1_2"
  # Keep keys enabled for standard Function App consumption plan state storage
  shared_access_key_enabled = true
  public_network_access_enabled = true

  tags = var.tags
}

resource "azurerm_service_plan" "asp" {
  name                = local.app_service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption plan
  tags                = var.tags
}

resource "azurerm_application_insights" "ai" {
  name                = local.application_insights_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  tags                = var.tags
}

resource "azurerm_linux_function_app" "func" {
  name                = local.function_app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.st.name
  storage_account_access_key = azurerm_storage_account.st.primary_access_key
  service_plan_id            = azurerm_service_plan.asp.id

  site_config {
    application_insights_connection_string = azurerm_application_insights.ai.connection_string

    application_stack {
      python_version = "3.11"
    }

    # Secure non-anonymous defaults
    http2_enabled = true
  }

  tags = var.tags
}
