variable "resource_group_name" {
  description = "Name of the existing resource group."
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

# APIM Gateway Inputs
variable "apim_name" {
  description = "Name of the APIM instance to create."
  type        = string
}

variable "publisher_email" {
  description = "Email address for APIM notifications."
  type        = string
}

variable "publisher_name" {
  description = "Organization name for APIM."
  type        = string
}

variable "model_endpoint" {
  description = "The target model endpoint URL (e.g., https://resourcename.openai.azure.com/)."
  type        = string
}

variable "model_id" {
  description = "Identifier for the model (e.g., 'gpt-4o') for metrics dimensions."
  type        = string
}

variable "model_resource_id" {
  description = "The fully qualified Azure Resource ID of the model (OpenAI/Foundry) for RBAC assignment."
  type        = string
}

variable "token_limit_per_minute" {
  description = "The TPM limit to enforce at the gateway."
  type        = number
  default     = 5000
}

# Foundry Project Inputs
variable "foundry_hub_id" {
  description = "The Resource ID of the existing Azure AI Foundry Hub (Cognitive Account)."
  type        = string
}

variable "foundry_project_id" {
  description = "The Resource ID of the existing Azure AI Foundry Project (Cognitive Account Project)."
  type        = string
}

variable "tenant_id" {
  description = "The Azure AD Tenant ID for JWT validation."
  type        = string
}

variable "audience" {
  description = "The expected audience for the Entra ID token."
  type        = string
  default     = "https://cognitiveservices.azure.com"
}
