variable "location" {
  description = "The Azure region where resources will be deployed."
  type        = string
  default     = "eastus2"
}

variable "name_prefix" {
  description = "A prefix for resource names to ensure uniqueness."
  type        = string
  default     = "foundryasync" # Aligned with bb validation regex
}

variable "ai_foundry_hub_name" {
  description = "Name of the existing Azure AI Foundry Hub."
  type        = string
}

variable "ai_foundry_project_name" {
  description = "Name of the existing Azure AI Foundry Project."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the existing resource group."
  type        = string
}
