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
    condition     = !contains(["Owner", "Contributor", "User Access Administrator"], var.role_definition_name) && !strcontains(var.role_definition_name, "*")
    error_message = "Broad or wildcard roles (Owner, Contributor, User Access Administrator, *) are strictly forbidden for least-privilege service access."
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
  default     = {}
}
