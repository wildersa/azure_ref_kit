output "webapp_name" {
  value       = azurerm_linux_web_app.agent_api.name
  description = "The name of the deployed web app"
}

output "api_endpoint" {
  value       = azurerm_linux_web_app.agent_api.default_hostname
  description = "The default hostname of the deployed web app"
}

output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group"
}
