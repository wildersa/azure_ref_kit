output "identity_principal_id" {
  value       = azurerm_user_assigned_identity.example.principal_id
  description = "The Principal ID of the created User Assigned Identity."
}

output "identity_client_id" {
  value       = azurerm_user_assigned_identity.example.client_id
  description = "The Client ID of the created User Assigned Identity."
}
