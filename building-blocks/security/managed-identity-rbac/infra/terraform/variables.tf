variable "workload_name" {
  type        = string
  description = "Name of the workload for identity naming."
}

variable "location" {
  type        = string
  description = "Azure region for the identity."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group where the identity will be created."
}

variable "target_resource_id" {
  type        = string
  description = "The fully qualified Azure Resource ID of the target resource for RBAC assignment."
}

variable "role_definition_name" {
  type        = string
  description = "The name of the built-in Azure RBAC role to assign (e.g., 'Storage Blob Data Reader')."
  default     = "Storage Blob Data Reader"

  validation {
    condition = contains([
      "Storage Blob Data Reader",
      "Storage Blob Data Contributor",
      "Storage Queue Data Message Processor",
      "Storage Queue Data Contributor",
      "Storage Table Data Contributor",
      "Key Vault Secrets User",
      "Cognitive Services User",
      "Foundry User",
      "Search Index Data Reader"
    ], var.role_definition_name)
    error_message = "Only specific narrow Data Plane roles are permitted for this reference implementation. See module.yaml for the recommended allowlist."
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
  default     = {}
}
