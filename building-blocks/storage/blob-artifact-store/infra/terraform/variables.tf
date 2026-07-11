variable "prefix" {
  description = "Prefix for all resources. Must be 1-10 alphanumeric characters."
  type        = string
  default     = "refkit"

  validation {
    condition     = can(regex("^[a-z0-9]{1,10}$", var.prefix))
    error_message = "Prefix must be 1-10 lowercase alphanumeric characters."
  }
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
  description = "Name of the blob container for artifacts. Must follow Azure naming rules."
  type        = string
  default     = "artifacts"

  validation {
    # RE2 does not support lookahead. Use simpler regex + strcontains.
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", var.container_name)) && !strcontains(var.container_name, "--")
    error_message = "Invalid container name. Must follow Azure naming rules: 3-63 characters, lowercase, numbers, and hyphens. No consecutive hyphens allowed."
  }
}

variable "runtime_principal_id" {
  description = "The principal ID of the runtime managed identity (e.g. Function App) to grant 'Storage Blob Data Owner' access."
  type        = string
}

variable "allowed_ips" {
  description = "List of public IP addresses or CIDR blocks allowed to access the storage account. This is required to ensure at least one usable network path (public allowlist) when default_action is 'Deny'. Private endpoints are not supported by this module."
  type        = list(string)

  validation {
    condition     = length(var.allowed_ips) > 0
    error_message = "At least one IP address or CIDR block must be provided in allowed_ips to ensure connectivity. This module does not support private endpoints."
  }

  validation {
    condition     = alltrue([for ip in var.allowed_ips : can(regex("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}(?:/[0-9]{1,2})?$", ip))])
    error_message = "All allowed_ips must be valid IPv4 addresses or CIDR blocks."
  }
}
