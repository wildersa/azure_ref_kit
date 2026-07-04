output "AZURE_AI_PROJECT_DISCOVERY_ENDPOINT" {
  description = "The Foundry project discovery URL (Azure ML format)."
  value       = "https://${azurerm_ai_hub.hub.location}.api.azureml.ms/discovery/subscriptions/${data.azurerm_subscription.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.MachineLearningServices/workspaces/${azurerm_ai_project.project.name}"
}

output "AZURE_AI_PROJECT_ENDPOINT" {
  description = "The Foundry project endpoint for SDK invocation (Foundry format)."
  value       = "https://${azurerm_ai_hub.hub.name}.ai.azure.com/api/projects/${azurerm_ai_project.project.name}"
}

output "RESOURCE_GROUP_NAME" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}

data "azurerm_subscription" "current" {}
