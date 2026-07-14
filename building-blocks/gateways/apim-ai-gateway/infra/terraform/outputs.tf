output "gateway_url" {
  description = "The base URL of the AI Gateway."
  value       = azurerm_api_management.apim.gateway_url
}

output "api_path" {
  description = "The path for the model API."
  value       = azurerm_api_management_api.model_api.path
}

output "identity_principal_id" {
  description = "The Principal ID of the APIM identity."
  value       = azurerm_user_assigned_identity.apim_identity.principal_id
}

output "identity_client_id" {
  description = "The Client ID of the APIM identity."
  value       = azurerm_user_assigned_identity.apim_identity.client_id
}
