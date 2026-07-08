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

variable "docker_registry_url" {
  type        = string
  description = "The URL of the Docker registry."
  default     = "https://mcr.microsoft.com"
}

variable "docker_registry_username" {
  type        = string
  description = "The username for the Docker registry (if not using Managed Identity)."
  default     = null
}

variable "docker_registry_password" {
  type        = string
  description = "The password for the Docker registry (if not using Managed Identity)."
  default     = null
  sensitive   = true
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the App Service Plan (e.g., B1, S1, P1v3)."
  default     = "B1"
}

variable "startup_command" {
  type        = string
  description = "Custom startup command for the web app (e.g., gunicorn command)."
  default     = null
}

variable "tags" {
  type        = map(string)
  description = "Tags for all resources."
  default = {
    module = "webapp-agent-api"
  }
}
