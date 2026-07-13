output "static_web_app_id" {
  value       = azurerm_static_web_app.portal.id
  description = "The ID of the Static Web App."
}

output "static_web_app_default_host_name" {
  value       = azurerm_static_web_app.portal.default_host_name
  description = "The default host name of the Static Web App."
}

output "static_web_app_api_key" {
  value       = azurerm_static_web_app.portal.api_key
  sensitive   = true
  description = "The API key for the Static Web App, used for deployment."
}
