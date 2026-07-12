variable "name_prefix" {
  type        = string
  description = "Prefix for all resources created by this module."
  default     = "atool"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,12}$", var.name_prefix))
    error_message = "name_prefix must be 3-12 characters, lowercase alphanumeric and hyphens."
  }
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

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, prod."
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to all resources."
  default = {
    module = "agent-tool-http-function"
  }
}
