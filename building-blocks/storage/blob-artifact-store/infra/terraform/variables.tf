variable "prefix" {
  description = "Prefix for all resources"
  type        = string
  default     = "refkit"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "container_name" {
  description = "Name of the blob container for artifacts"
  type        = string
  default     = "artifacts"
}
