output "function_app_name" {
  value = azurerm_linux_function_app.main.name
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "input_queue_name" {
  value = azurerm_storage_queue.input.name
}

output "output_queue_name" {
  value = azurerm_storage_queue.output.name
}
