variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "movies-pipeline"
}

variable "bucket_location" {
  description = "Bucket location"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Default storage class"
  type        = string
  default     = "STANDARD"
}

variable "enable_versioning" {
  description = "Enable object versioning"
  type        = bool
  default     = true
}

variable "lifecycle_age_bronze" {
  description = "Days before transitioning bronze data to Nearline"
  type        = number
  default     = 90
}

variable "lifecycle_age_silver" {
  description = "Days before transitioning silver data to Nearline"
  type        = number
  default     = 180
}

