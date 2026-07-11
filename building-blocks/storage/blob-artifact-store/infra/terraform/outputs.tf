output "artifact_store_blob_endpoint" {
  description = "The primary blob service endpoint"
  value       = azurerm_storage_account.artifact_store.primary_blob_endpoint
}

output "artifact_container_name" {
  description = "The name of the artifact container"
  value       = azurerm_storage_container.artifacts.name
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = azurerm_storage_account.artifact_store.name
}
