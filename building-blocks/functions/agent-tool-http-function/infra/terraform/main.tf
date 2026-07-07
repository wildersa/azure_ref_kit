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

resource "azurerm_storage_account" "storage" {
  name                            = replace("st${var.prefix}${random_string.unique.result}", "-", "")
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  tags                            = var.tags
}

resource "azurerm_storage_container" "deploy" {
  name                  = "deploymentpackage"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

resource "azurerm_service_plan" "plan" {
  name                = "plan-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "FC1"
  tags                = var.tags
}

resource "azurerm_function_app_flex_consumption" "function" {
  name                = "func-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  runtime_name    = "python"
  runtime_version = "3.11"

  storage_container_type      = "blobContainer"
  storage_container_endpoint  = "${azurerm_storage_account.storage.primary_blob_endpoint}deploymentpackage"
  storage_authentication_type = "SystemAssignedIdentity"

  identity {
    type = "SystemAssigned"
  }

  site_config {}

  app_settings = {
    "AzureWebJobsStorage__accountName" = azurerm_storage_account.storage.name
    "AzureWebJobsStorage__credential"  = "managedidentity"
  }

  tags = var.tags
}

resource "azurerm_role_assignment" "storage_owner" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_function_app_flex_consumption.function.identity[0].principal_id
}
