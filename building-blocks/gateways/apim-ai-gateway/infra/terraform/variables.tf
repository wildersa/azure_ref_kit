variable "resource_group_name" {
  description = "The name of the existing resource group."
  type        = string
}

variable "location" {
  description = "Azure region for the deployment."
  type        = string
}

variable "apim_name" {
  description = "The name of the API Management instance."
  type        = string
}

variable "apim_sku" {
  description = "APIM SKU (Standard v2 recommended for GenAI capabilities)."
  type        = string
  default     = "StandardV2_1"
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

variable "token_limit_per_minute" {
  description = "The TPM limit to enforce at the gateway."
  type        = number
  default     = 5000
}

variable "max_request_size_bytes" {
  description = "The maximum allowed request body size in bytes."
  type        = number
  default     = 102400 # 100KB default
}

variable "model_resource_id" {
  description = "The fully qualified Azure Resource ID of the model (OpenAI/Foundry) for RBAC assignment."
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

variable "app_insights_instrumentation_key" {
  description = "Application Insights instrumentation key for metrics (optional)."
  type        = string
  default     = ""
}

variable "app_insights_resource_id" {
  description = "Application Insights resource ID for logging (optional)."
  type        = string
  default     = ""
}
