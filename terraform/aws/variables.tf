variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "movies-pipeline"
}

variable "enable_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable S3 bucket encryption"
  type        = bool
  default     = true
}

variable "lifecycle_days_bronze" {
  description = "Days to transition bronze data to Glacier"
  type        = number
  default     = 90
}

variable "lifecycle_days_silver" {
  description = "Days to transition silver data to Glacier"
  type        = number
  default     = 180
}

