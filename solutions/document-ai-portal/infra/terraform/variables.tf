variable "prefix" {
  description = "A prefix for all resources in this deployment."
  type        = string
  default     = "docai"
}

variable "location" {
  description = "The Azure region where all resources will be deployed."
  type        = string
  default     = "eastus2"
}

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default = {
    solution = "document-ai-portal"
    env      = "dev"
  }
}

variable "document_intelligence_endpoint" {
  description = "The endpoint for the Azure AI Document Intelligence resource."
  type        = string
  default     = ""
}
