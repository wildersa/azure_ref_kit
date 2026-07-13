output "webapp_name" {
  value       = azurerm_linux_web_app.webapp.name
  description = "The name of the deployed web app."
}

output "api_endpoint" {
  value       = "https://${azurerm_linux_web_app.webapp.default_hostname}"
  description = "The public URL of the hosted API."
}

output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group."
}

output "principal_id" {
  value       = azurerm_linux_web_app.webapp.identity[0].principal_id
  description = "The principal ID of the system-assigned managed identity."
}
