resource "azurerm_resource_group" "main" {
  name     = "${var.name_prefix}-rg"
  location = var.location
}

resource "azurerm_storage_account" "main" {
  name                     = lower(replace("${var.name_prefix}sa", "-", ""))
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Identity-based access is preferred. Disabling shared keys for security.
  shared_access_key_enabled = false
}

resource "azurerm_storage_queue" "input" {
  name                 = "agent-tool-input"
  storage_account_name = azurerm_storage_account.main.name
}

resource "azurerm_storage_queue" "output" {
  name                 = "agent-tool-output"
  storage_account_name = azurerm_storage_account.main.name
}

resource "azurerm_service_plan" "main" {
  name                = "${var.name_prefix}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "FC1" # Flex Consumption
}

resource "azurerm_function_app_flex_consumption" "main" {
  name                = "${var.name_prefix}-func"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  storage_account_name       = azurerm_storage_account.main.name
  service_plan_id            = azurerm_service_plan.main.id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "AzureWebJobsStorage__accountName" = azurerm_storage_account.main.name
  }
}

# RBAC for the Function App to access queues
resource "azurerm_role_assignment" "queue_processor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Queue Data Message Processor"
  principal_id         = azurerm_function_app_flex_consumption.main.identity[0].principal_id
}

resource "azurerm_role_assignment" "queue_contributor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = azurerm_function_app_flex_consumption.main.identity[0].principal_id
}

# Required for Flex Consumption host operations
resource "azurerm_role_assignment" "blob_owner" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_function_app_flex_consumption.main.identity[0].principal_id
}
