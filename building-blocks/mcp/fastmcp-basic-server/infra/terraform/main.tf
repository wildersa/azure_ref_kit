# This module is currently local-only and does not provision any Azure resources.
# Azure hosting for FastMCP is deferred to building-blocks/mcp/azure-functions-mcp-endpoint/.

provider "azurerm" {
  features {}
}
