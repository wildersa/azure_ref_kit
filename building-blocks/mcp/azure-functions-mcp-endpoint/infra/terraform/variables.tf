variable "prefix" {
  description = "A prefix for all resources created by this module."
  type        = string
  default     = "mcp-af"
}

variable "location" {
  description = "The Azure region where resources will be deployed."
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Optional name of an existing resource group. If not provided, a new one will be created."
  type        = string
  default     = ""
}
