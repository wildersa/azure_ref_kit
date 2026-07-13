output "identity_principal_id" {
  value       = azurerm_user_assigned_identity.workload.principal_id
  description = "The Principal ID of the created Managed Identity."
}

output "identity_client_id" {
  value       = azurerm_user_assigned_identity.workload.client_id
  description = "The Client ID of the created User-Assigned Managed Identity."
}

output "role_assignment_id" {
  value       = azurerm_role_assignment.least_privilege.id
  description = "The ID of the created Role Assignment."
}
