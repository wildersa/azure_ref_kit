output "api_endpoint" {
  value       = azurerm_container_app.agent_api.latest_revision_fqdn
  description = "The FQDN of the deployed container app"
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}
