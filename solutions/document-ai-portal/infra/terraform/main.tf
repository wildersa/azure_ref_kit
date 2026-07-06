resource "random_string" "unique" {
  length  = 6
  special = false
  upper   = false
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.prefix}-${random_string.unique.result}"
  location = var.location
  tags     = var.tags
}

# Storage Account for artifacts, status, and cost
resource "azurerm_storage_account" "st" {
  name                            = replace("st${var.prefix}${random_string.unique.result}", "-", "")
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  tags                            = var.tags
}

# Storage Containers for Documents and Artifacts
resource "azurerm_storage_container" "input" {
  name                  = "input"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "artifacts" {
  name                  = "artifacts"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "deployment" {
  name                  = "deployment"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}

# Storage Tables for Status and Cost Ledger
resource "azurerm_storage_table" "pipeline_status" {
  name                 = "pipelinestatus"
  storage_account_name = azurerm_storage_account.st.name
}

resource "azurerm_storage_table" "cost_ledger" {
  name                 = "costledger"
  storage_account_name = azurerm_storage_account.st.name
}

# Observability
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_application_insights" "ai" {
  name                = "ai-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  workspace_id        = azurerm_log_analytics_workspace.law.id
  application_type    = "web"
  tags                = var.tags
}

# Hosting Foundation (Flex Consumption Plan)
resource "azurerm_service_plan" "plan" {
  name                = "plan-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "FC1" # Flex Consumption
  tags                = var.tags
}

# Static Web App Placeholder
resource "azurerm_static_web_app" "portal" {
  name                = "stapp-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = var.tags
}

# Identity and RBAC
resource "azurerm_user_assigned_identity" "solution_identity" {
  name                = "id-${var.prefix}-${random_string.unique.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  tags                = var.tags
}

# Least-privilege RBAC for the solution identity
resource "azurerm_role_assignment" "storage_blob_contributor" {
  scope                = azurerm_storage_account.st.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.solution_identity.principal_id
}

resource "azurerm_role_assignment" "storage_table_contributor" {
  scope                = azurerm_storage_account.st.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azurerm_user_assigned_identity.solution_identity.principal_id
}
