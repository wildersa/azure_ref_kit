data "azurerm_resource_group" "existing" {
  count = var.resource_group_name != "" ? 1 : 0
  name  = var.resource_group_name
}

resource "azurerm_resource_group" "new" {
  count    = var.resource_group_name == "" ? 1 : 0
  name     = "${var.prefix}-rg"
  location = var.location
}

locals {
  resource_group_name = var.resource_group_name != "" ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.new[0].name
  location            = var.resource_group_name != "" ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.new[0].location
}

resource "azurerm_storage_account" "example" {
  name                            = "${replace(lower(var.prefix), "-", "")}sa"
  resource_group_name             = local.resource_group_name
  location                        = local.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
}

resource "azurerm_storage_container" "deploy" {
  name                  = "deploymentpackage"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

resource "azurerm_log_analytics_workspace" "example" {
  name                = "${var.prefix}-law"
  location            = local.location
  resource_group_name = local.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "example" {
  name                = "${var.prefix}-ai"
  location            = local.location
  resource_group_name = local.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.example.id
  application_type    = "web"
}

resource "azurerm_service_plan" "example" {
  name                = "${var.prefix}-asp"
  location            = local.location
  resource_group_name = local.resource_group_name
  os_type             = "Linux"
  sku_name            = "FC1"
}

resource "azurerm_user_assigned_identity" "example" {
  name                = "${var.prefix}-id"
  location            = local.location
  resource_group_name = local.resource_group_name
}

resource "azurerm_function_app_flex_consumption" "example" {
  name                = "${var.prefix}-func"
  resource_group_name = local.resource_group_name
  location            = local.location

  service_plan_id = azurerm_service_plan.example.id

  runtime_name    = "python"
  runtime_version = "3.10"

  instance_memory_in_mb = 2048

  storage_container_type      = "blobContainer"
  storage_container_endpoint  = "${azurerm_storage_account.example.primary_blob_endpoint}deploymentpackage"
  storage_authentication_type = "UserAssignedIdentity"
  storage_user_assigned_identity_id = azurerm_user_assigned_identity.example.id

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
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.example.connection_string
  }
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

resource "azurerm_role_assignment" "storage_queue_message_processor" {
  scope                = azurerm_storage_account.example.id
  role_definition_name = "Storage Queue Data Message Processor"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}

resource "azurerm_role_assignment" "storage_table_contributor" {
  scope                = azurerm_storage_account.example.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}
