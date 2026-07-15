output "function_app_name" {
  value = azurerm_function_app_flex_consumption.function.name
}

output "function_app_default_hostname" {
  value = azurerm_function_app_flex_consumption.function.default_hostname
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "api_endpoint" {
  value = "https://${azurerm_function_app_flex_consumption.function.default_hostname}"
}
# Force inclusion in PR
