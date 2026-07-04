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
  name                     = "st${var.prefix}${random_string.unique.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}

resource "azurerm_key_vault" "kv" {
  name                = "kv-${var.prefix}-${random_string.unique.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  tags                = var.tags
}

resource "azurerm_ai_services" "ai_services" {
  name                = "ais-${var.prefix}-${random_string.unique.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku_name            = "S0"
  tags                = var.tags
}

# Azure AI Foundry Hub
resource "azurerm_ai_hub" "hub" {
  name                = "hub-${var.prefix}-${random_string.unique.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  storage_account_id  = azurerm_storage_account.storage.id
  key_vault_id        = azurerm_key_vault.kv.id

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Azure AI Foundry Project
resource "azurerm_ai_project" "project" {
  name           = "proj-${var.prefix}-${random_string.unique.result}"
  location       = azurerm_resource_group.rg.location
  ai_hub_id      = azurerm_ai_hub.hub.id

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Model Deployment for the Agent
resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_ai_services.ai_services.id

  sku {
    name     = "GlobalStandard"
    capacity = 10 # 10k TPM
  }

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }
}

data "azurerm_client_config" "current" {}
