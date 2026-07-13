variable "resource_group_name" {
  type        = string
  description = "The name of the resource group in which to create the Static Web App."
}

variable "location" {
  type        = string
  description = "The Azure region where the Static Web App should be created."
  default     = "West US 2"
}

variable "name_prefix" {
  type        = string
  description = "A prefix for the name of the Static Web App."

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.name_prefix))
    error_message = "The name_prefix must only contain lowercase alphanumeric characters and hyphens."
  }
}

variable "sku_tier" {
  type        = string
  description = "The SKU tier of the Static Web App. Possible values are 'Free' or 'Standard'."
  default     = "Standard"

  validation {
    condition     = contains(["Free", "Standard"], var.sku_tier)
    error_message = "The sku_tier must be either 'Free' or 'Standard'."
  }
}

variable "sku_size" {
  type        = string
  description = "The SKU size of the Static Web App. Possible values are 'Free' or 'Standard'."
  default     = "Standard"

  validation {
    condition     = contains(["Free", "Standard"], var.sku_size)
    error_message = "The sku_size must be either 'Free' or 'Standard'."
  }
}

variable "tags" {
  type        = map(string)
  description = "A mapping of tags to assign to the resource."
  default     = {}
}
