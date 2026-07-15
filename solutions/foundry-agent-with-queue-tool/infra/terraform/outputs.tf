output "foundry_agent_config" {
  description = "Configuration for the Foundry Agent to connect to the async tool."
  value = {
    submit_url          = "https://${module.queue_function.function_app_name}.azurewebsites.net/api/submit"
    status_url_template = "https://${module.queue_function.function_app_name}.azurewebsites.net/api/status/{correlation_id}"
  }
}

output "storage_account_name" {
  value = module.queue_function.storage_account_name
}
