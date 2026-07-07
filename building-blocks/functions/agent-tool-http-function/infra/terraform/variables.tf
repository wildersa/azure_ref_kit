variable "prefix" {
  type        = string
  description = "Prefix for all resources."
  default     = "agenttool"
}

variable "location" {
  type        = string
  description = "Azure region for deployment."
  default     = "eastus"
}

variable "tags" {
  type        = map(string)
  description = "Tags for all resources."
  default = {
    module = "agent-tool-http-function"
  }
}
