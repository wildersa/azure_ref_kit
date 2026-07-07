output "function_app_name" {
  value = azurerm_function_app_flex_consumption.example.name
}

output "function_app_default_hostname" {
  value = azurerm_function_app_flex_consumption.example.default_hostname
}

output "mcp_endpoint_url" {
  value = "https://${azurerm_function_app_flex_consumption.example.default_hostname}/runtime/webhooks/mcp"
}
