variable "name_prefix" {
  type        = string
  description = "Prefix for all resources created by this module."
  default     = "atool"
}

variable "location" {
  type        = string
  description = "Azure region for the resources."
  default     = "eastus"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, prod)."
  default     = "dev"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to all resources."
  default = {
    module = "agent-tool-http-function"
  }
}
