output "function_app_name" {
  value       = azurerm_linux_function_app.func.name
  description = "The name of the deployed Function App."
}

output "function_app_default_hostname" {
  value       = azurerm_linux_function_app.func.default_hostname
  description = "The default hostname of the deployed Function App."
}

output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group."
}
