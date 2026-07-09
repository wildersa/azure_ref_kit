variable "location" {
  type        = string
  description = "The Azure region where resources will be created."
  default     = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "The name of the resource group."
}

variable "target_storage_container_id" {
  type        = string
  description = "The ID of the specific storage container for RBAC assignment."
}

variable "storage_account_name" {
  type        = string
  description = "The name of the storage account for identity-based connection."
}

variable "key_vault_id" {
  type        = string
  description = "The ID of the Key Vault for RBAC assignment."
}
