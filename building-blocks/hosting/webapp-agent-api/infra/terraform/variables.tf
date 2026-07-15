variable "prefix" {
  type        = string
  description = "Prefix for resources"
  default     = "webapp-agent"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "East US"
}

variable "container_image" {
  type        = string
  description = "The container image to deploy (e.g., repo/image:tag)"
}

variable "container_registry_server" {
  type        = string
  description = "The FQDN of the container registry"
}

variable "container_registry_id" {
  type        = string
  description = "The ID of the Azure Container Registry to grant AcrPull permissions"
  default     = null
}

variable "client_id" {
  type        = string
  description = "The Client ID for Microsoft Entra ID authentication (EasyAuth)"
}

variable "tenant_id" {
  type        = string
  description = "The Tenant ID for Microsoft Entra ID authentication (EasyAuth)"
}

variable "tags" {
  type        = map(string)
  description = "Tags for resources"
  default = {
    environment = "reference"
    component   = "webapp-agent-api"
  }
}
