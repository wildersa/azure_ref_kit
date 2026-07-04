output "AZURE_AI_PROJECT_ENDPOINT" {
  description = "The Foundry project endpoint for SDK invocation."
  value       = "https://${azurerm_cognitive_account.hub.name}.ai.azure.com/api/projects/${azurerm_cognitive_account_project.project.name}"
}

output "RESOURCE_GROUP_NAME" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}
