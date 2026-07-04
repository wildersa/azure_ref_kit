output "function_app_name" {
  value = azurerm_linux_function_app.function.name
}

output "function_app_default_hostname" {
  value = azurerm_linux_function_app.function.default_hostname
}

output "input_queue_name" {
  value = azurerm_storage_queue.input_queue.name
}

output "output_queue_name" {
  value = azurerm_storage_queue.output_queue.name
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}
