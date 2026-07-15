terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

# Azure Static Web App for the Customer Status Portal
# This resource hosts the React/TypeScript frontend.
resource "azurerm_static_web_app" "portal" {
  name                = "${var.name_prefix}-status-portal"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_tier            = var.sku_tier
  sku_size            = var.sku_size

  tags = var.tags
}
