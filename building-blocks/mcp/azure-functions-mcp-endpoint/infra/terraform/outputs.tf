output "function_app_name" {
  description = "The name of the Azure Function App."
  value       = azurerm_function_app_flex_consumption.example.name
}

output "function_app_default_hostname" {
  description = "The default hostname of the Azure Function App."
  value       = azurerm_function_app_flex_consumption.example.default_hostname
}

output "mcp_endpoint_url" {
  description = "The full URL for the MCP Streamable HTTP endpoint."
  value       = "https://${azurerm_function_app_flex_consumption.example.default_hostname}/runtime/webhooks/mcp"
}

output "resource_group_name" {
  description = "The name of the resource group."
  value       = local.resource_group_name
}
