variable "resource_group_name" {
  description = "Name of the resource group where the solution-local resources (Foundry Connection) will be deployed."
  type        = string
}

variable "location" {
  description = "Azure region for deployment."
  type        = string
}

variable "prefix" {
  description = "Prefix for resource names."
  type        = string
  default     = "foundry-gw"
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}

# Existing AI Gateway Inputs
variable "apim_name" {
  description = "Name of the existing APIM instance."
  type        = string
}

variable "apim_resource_group_name" {
  description = "The resource group of the existing APIM instance."
  type        = string
}

variable "gateway_url" {
  description = "The base URL of the existing AI Gateway."
  type        = string
}

variable "gateway_api_id" {
  description = "The resource ID of the existing APIM API for the model gateway."
  type        = string
}

variable "model_id" {
  description = "Identifier for the model (e.g., 'gpt-4o') configured in the gateway."
  type        = string
}

# Foundry Project Inputs
variable "foundry_hub_id" {
  description = "The Resource ID of the existing Azure AI Foundry Hub (Cognitive Account)."
  type        = string
}

variable "foundry_project_id" {
  description = "The Resource ID of the existing Azure AI Foundry Project (Cognitive Account Project) where the connection will be scoped."
  type        = string
}
