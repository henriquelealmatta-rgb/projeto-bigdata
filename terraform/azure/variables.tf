variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "moviespipeline"
}

variable "enable_versioning" {
  description = "Enable blob versioning"
  type        = bool
  default     = true
}

variable "account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"
}

variable "lifecycle_delete_days" {
  description = "Days before deleting old data"
  type        = number
  default     = 365
}

