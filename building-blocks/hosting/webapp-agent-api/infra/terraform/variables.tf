variable "prefix" {
  type        = string
  description = "Prefix for all resources."
  default     = "webappapi"
}

variable "location" {
  type        = string
  description = "Azure region for deployment."
  default     = "eastus"
}

variable "python_version" {
  type        = string
  description = "The Python version to use (e.g., 3.12, 3.14)."
  default     = "3.12"
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the App Service Plan (e.g., B1, S1, P1v3)."
  default     = "B1"
}

variable "startup_command" {
  type        = string
  description = "Custom startup command for the web app (e.g., gunicorn command)."
  default     = null
}

variable "tags" {
  type        = map(string)
  description = "Tags for all resources."
  default = {
    module = "webapp-agent-api"
  }
}
