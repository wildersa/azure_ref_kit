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
  description = "The container image to deploy"
  default     = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
}

variable "tags" {
  type        = map(string)
  description = "Tags for resources"
  default     = {
    environment = "reference"
    component   = "container-agent-api"
  }
}
