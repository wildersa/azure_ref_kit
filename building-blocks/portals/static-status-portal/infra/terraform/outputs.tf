output "static_web_app_id" {
  value       = azurerm_static_web_app.portal.id
  description = "The ID of the Static Web App."
}

output "static_web_app_name" {
  value       = azurerm_static_web_app.portal.name
  description = "The name of the Static Web App."
}

output "static_web_app_default_host_name" {
  value       = azurerm_static_web_app.portal.default_host_name
  description = "The default host name of the Static Web App."
}

output "resource_group_name" {
  value       = var.resource_group_name
  description = "The name of the resource group."
}
