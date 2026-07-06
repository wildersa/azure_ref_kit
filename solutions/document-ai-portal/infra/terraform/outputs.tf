output "resource_group_name" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "The name of the storage account."
  value       = azurerm_storage_account.st.name
}

output "storage_account_id" {
  description = "The ID of the storage account."
  value       = azurerm_storage_account.st.id
}

output "application_insights_connection_string" {
  description = "The connection string for Application Insights."
  value       = azurerm_application_insights.ai.connection_string
  sensitive   = true
}

output "service_plan_id" {
  description = "The ID of the Service Plan (Flex Consumption)."
  value       = azurerm_service_plan.plan.id
}

output "static_web_app_name" {
  description = "The name of the Static Web App."
  value       = azurerm_static_web_app.portal.name
}

output "static_web_app_default_host_name" {
  description = "The default host name of the Static Web App."
  value       = azurerm_static_web_app.portal.default_host_name
}

output "solution_identity_principal_id" {
  description = "The principal ID of the user-assigned identity."
  value       = azurerm_user_assigned_identity.solution_identity.principal_id
}

output "solution_identity_client_id" {
  description = "The client ID of the user-assigned identity."
  value       = azurerm_user_assigned_identity.solution_identity.client_id
}
