output "AZURE_AI_PROJECT_ENDPOINT" {
  description = "The Foundry project discovery URL for use in the solution."
  value       = "https://${azurerm_ai_hub.hub.location}.api.azureml.ms/discovery/subscriptions/${data.azurerm_subscription.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.MachineLearningServices/workspaces/${azurerm_ai_project.project.name}"
}

output "RESOURCE_GROUP_NAME" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}

data "azurerm_subscription" "current" {}
