variable "prefix" {
  type        = string
  description = "Prefix for all resources."
  default     = "webappapi"
}

variable "location" {
  type        = string
  description = "Azure region for deployment."
  default     = "eastus"
}

variable "container_image" {
  type        = string
  description = "The container image to deploy (e.g., mcr.microsoft.com/azuredocs/containerapps-helloworld:latest or <registry>.azurecr.io/agent-api:v1)"
}

variable "use_managed_identity_for_registry" {
  type        = bool
  description = "Whether to use the system-assigned managed identity to pull the container image from the registry."
  default     = false
}

variable "listen_port" {
  type        = number
  description = "The port the container listens on."
  default     = 8080
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the App Service Plan (e.g., B1, S1, P1v3)."
  default     = "B1"
}

variable "tags" {
  type        = map(string)
  description = "Tags for all resources."
  default = {
    module = "webapp-agent-api"
  }
}
