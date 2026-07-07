resource "azurerm_resource_group" "example" {
  name     = "${var.prefix}-rg"
  location = var.location
}

resource "azurerm_storage_account" "example" {
  name                            = "${replace(var.prefix, "-", "")}sa"
  resource_group_name             = azurerm_resource_group.example.name
  location                        = azurerm_resource_group.example.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
}

resource "azurerm_log_analytics_workspace" "example" {
  name                = "${var.prefix}-law"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "example" {
  name                = "${var.prefix}-ai"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  workspace_id        = azurerm_log_analytics_workspace.example.id
  application_type    = "web"
}

resource "azurerm_service_plan" "example" {
  name                = "${var.prefix}-asp"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  os_type             = "Linux"
  sku_name            = "FC1"
}

resource "azurerm_user_assigned_identity" "example" {
  name                = "${var.prefix}-id"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_function_app_flex_consumption" "example" {
  name                = "${var.prefix}-func"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  storage_account_type = "AzureWebJobsStorage"
  storage_account_id   = azurerm_storage_account.example.id

  service_plan_id = azurerm_service_plan.example.id

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.example.id]
  }

  site_config {
    application_insights_connection_string = azurerm_application_insights.example.connection_string
    application_insights_key               = azurerm_application_insights.example.instrumentation_key

    app_service_logs {
      disk_quota_mb         = 35
      retention_period_days = 7
    }
  }

  app_settings = {
    "AzureWebJobsStorage__accountName" = azurerm_storage_account.example.name
    "AzureWebJobsStorage__credential"  = "managedidentity"
    "AzureWebJobsStorage__clientId"    = azurerm_user_assigned_identity.example.client_id
  }

  instance_memory_mb = 2048
}

resource "azurerm_role_assignment" "storage_blob_owner" {
  scope                = azurerm_storage_account.example.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}

resource "azurerm_role_assignment" "storage_queue_contributor" {
  scope                = azurerm_storage_account.example.id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}

resource "azurerm_role_assignment" "storage_table_contributor" {
  scope                = azurerm_storage_account.example.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}
