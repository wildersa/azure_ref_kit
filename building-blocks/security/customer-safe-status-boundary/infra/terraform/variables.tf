variable "prefix" {
  description = "A prefix for resources, used for future-proofing even if no resources are declared here."
  type        = string
  default     = "safe-boundary"
}

variable "location" {
  description = "The Azure region where related resources should be deployed."
  type        = string
  default     = "East US"
}
