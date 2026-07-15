variable "location" {
  type        = string
  description = "The Azure region where resources will be created."
  default     = "eastus2"
}

variable "prefix" {
  type        = string
  description = "A prefix for naming resources."
  default     = "devops-agent"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
  default = {
    solution = "foundry-devops-agent-basic"
    track    = "AGENT-004"
  }
}

variable "gpt_model_name" {
  type        = string
  description = "The name of the GPT model to deploy."
  default     = "gpt-4o-mini"
}

variable "gpt_model_version" {
  type        = string
  description = "The version of the GPT model."
  default     = "2024-07-18"
}
