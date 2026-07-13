variable "prefix" {
  type        = string
  description = "Prefix for resources"
  default     = "agent-api"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "East US"
}

variable "container_image" {
  type        = string
  description = "The container image to deploy (e.g., <registry>.azurecr.io/agent-api:v1)"
}

variable "container_registry_server" {
  type        = string
  description = "The FQDN of the container registry"
}

variable "container_registry_id" {
  type        = string
  description = "The ID of the Azure Container Registry to grant AcrPull permissions (optional if image is public)"
  default     = null
}

variable "tags" {
  type        = map(string)
  description = "Tags for resources"
  default = {
    environment = "reference"
    component   = "container-agent-api"
  }
}
