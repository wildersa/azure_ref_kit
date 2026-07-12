variable "name_prefix" {
  description = "Prefix for resource naming."
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9]{3,12}$", var.name_prefix))
    error_message = "Prefix must be 3-12 lowercase alphanumeric characters."
  }
}

variable "location" {
  description = "Azure region for resources."
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}
