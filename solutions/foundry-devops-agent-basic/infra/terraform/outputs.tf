output "project_endpoint" {
  value       = azurerm_cognitive_account_project.project.endpoint
  description = "The endpoint for the Azure AI Project."
}

output "hub_name" {
  value       = azurerm_cognitive_account.hub.name
  description = "The name of the Azure AI Foundry Hub."
}

output "project_name" {
  value       = azurerm_cognitive_account_project.project.name
  description = "The name of the Azure AI Foundry Project."
}

output "model_deployment_name" {
  value       = azurerm_cognitive_deployment.gpt.name
  description = "The name of the model deployment."
}
