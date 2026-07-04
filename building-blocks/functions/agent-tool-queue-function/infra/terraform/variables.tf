variable "location" {
  description = "The Azure region where resources will be deployed."
  type        = string
  default     = "eastus2"
}

variable "prefix" {
  description = "A prefix to use for naming resources."
  type        = string
  default     = "queue-tool"
}

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default = {
    module = "agent-tool-queue-function"
  }
}
