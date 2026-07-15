# Local composition of the Foundry Agent with Queue Tool infrastructure.
# Reuses the agent-tool-queue-function building block.

module "queue_function" {
  source = "../../../building-blocks/functions/agent-tool-queue-function/infra/terraform"

  location    = var.location
  name_prefix = var.name_prefix
}

# Reference to existing AI Foundry Project
data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}
