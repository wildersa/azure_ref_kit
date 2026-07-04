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

# Azure AI Foundry Hub (Modern AzureRM pattern using Cognitive Account)
resource "azurerm_cognitive_account" "hub" {
  name                = "hub-${var.prefix}-${random_string.unique.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "AIServices"
  sku_name            = "S0"

  # Required for stateful development in Foundry including agent service
  custom_subdomain_name      = "hub-${var.prefix}-${random_string.unique.result}"
  project_management_enabled = true

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Azure AI Foundry Project
resource "azurerm_cognitive_account_project" "project" {
  name                 = "proj-${var.prefix}-${random_string.unique.result}"
  cognitive_account_id = azurerm_cognitive_account.hub.id
  location             = azurerm_resource_group.rg.location

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Model Deployment for the Agent
resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.hub.id

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
