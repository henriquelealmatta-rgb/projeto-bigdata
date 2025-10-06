output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bronze_bucket_name" {
  description = "Name of the bronze bucket"
  value       = google_storage_bucket.bronze.name
}

output "bronze_bucket_url" {
  description = "URL of the bronze bucket"
  value       = google_storage_bucket.bronze.url
}

output "silver_bucket_name" {
  description = "Name of the silver bucket"
  value       = google_storage_bucket.silver.name
}

output "silver_bucket_url" {
  description = "URL of the silver bucket"
  value       = google_storage_bucket.silver.url
}

output "gold_bucket_name" {
  description = "Name of the gold bucket"
  value       = google_storage_bucket.gold.name
}

output "gold_bucket_url" {
  description = "URL of the gold bucket"
  value       = google_storage_bucket.gold.url
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = google_storage_bucket.logs.name
}

output "service_account_email" {
  description = "Email of the pipeline service account"
  value       = google_service_account.pipeline_sa.email
}

output "service_account_name" {
  description = "Name of the pipeline service account"
  value       = google_service_account.pipeline_sa.name
}

