output "gateway_url" {
  description = "The URL of the AI Gateway."
  value       = module.ai_gateway.gateway_url
}

output "foundry_connection_id" {
  description = "The ID of the Foundry connection to the AI Gateway."
  value       = azapi_resource.foundry_apim_connection.id
}

output "apim_subscription_key" {
  description = "The subscription key for the Foundry Agent in APIM."
  value       = azurerm_api_management_subscription.foundry_sub.primary_key
  sensitive   = true
}
