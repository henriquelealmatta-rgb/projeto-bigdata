# Enable required APIs
resource "google_project_service" "storage_api" {
  project = var.project_id
  service = "storage.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "logging_api" {
  project = var.project_id
  service = "logging.googleapis.com"

  disable_on_destroy = false
}

# GCS Bucket for Bronze Layer
resource "google_storage_bucket" "bronze" {
  name          = "${var.project_name}-${var.environment}-bronze"
  location      = var.bucket_location
  storage_class = var.storage_class
  project       = var.project_id

  uniform_bucket_level_access = true

  versioning {
    enabled = var.enable_versioning
  }

  lifecycle_rule {
    condition {
      age = var.lifecycle_age_bronze
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = var.lifecycle_age_bronze * 2
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = var.lifecycle_age_bronze * 4
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  labels = {
    project     = "movies-big-data-pipeline"
    environment = var.environment
    layer       = "bronze"
    managed-by  = "terraform"
  }

  depends_on = [google_project_service.storage_api]
}

# GCS Bucket for Silver Layer
resource "google_storage_bucket" "silver" {
  name          = "${var.project_name}-${var.environment}-silver"
  location      = var.bucket_location
  storage_class = var.storage_class
  project       = var.project_id

  uniform_bucket_level_access = true

  versioning {
    enabled = var.enable_versioning
  }

  lifecycle_rule {
    condition {
      age = var.lifecycle_age_silver
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = var.lifecycle_age_silver * 2
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  labels = {
    project     = "movies-big-data-pipeline"
    environment = var.environment
    layer       = "silver"
    managed-by  = "terraform"
  }

  depends_on = [google_project_service.storage_api]
}

# GCS Bucket for Gold Layer
resource "google_storage_bucket" "gold" {
  name          = "${var.project_name}-${var.environment}-gold"
  location      = var.bucket_location
  storage_class = var.storage_class
  project       = var.project_id

  uniform_bucket_level_access = true

  versioning {
    enabled = var.enable_versioning
  }

  # Gold layer stays in STANDARD storage
  # No lifecycle rules for frequent access

  labels = {
    project     = "movies-big-data-pipeline"
    environment = var.environment
    layer       = "gold"
    managed-by  = "terraform"
  }

  depends_on = [google_project_service.storage_api]
}

# Service Account for Pipeline
resource "google_service_account" "pipeline_sa" {
  account_id   = "${var.project_name}-${var.environment}-sa"
  display_name = "Movies Pipeline Service Account"
  project      = var.project_id
}

# IAM Binding - Storage Object Admin for Bronze
resource "google_storage_bucket_iam_member" "bronze_admin" {
  bucket = google_storage_bucket.bronze.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# IAM Binding - Storage Object Admin for Silver
resource "google_storage_bucket_iam_member" "silver_admin" {
  bucket = google_storage_bucket.silver.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# IAM Binding - Storage Object Admin for Gold
resource "google_storage_bucket_iam_member" "gold_admin" {
  bucket = google_storage_bucket.gold.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# Log Sink for GCS access logs
resource "google_logging_project_sink" "storage_sink" {
  name        = "${var.project_name}-${var.environment}-storage-logs"
  destination = "storage.googleapis.com/${google_storage_bucket.logs.name}"
  project     = var.project_id

  filter = "resource.type=\"gcs_bucket\" AND (protoPayload.methodName=\"storage.objects.get\" OR protoPayload.methodName=\"storage.objects.create\" OR protoPayload.methodName=\"storage.objects.delete\")"

  unique_writer_identity = true

  depends_on = [google_project_service.logging_api]
}

# GCS Bucket for Logs
resource "google_storage_bucket" "logs" {
  name          = "${var.project_name}-${var.environment}-logs"
  location      = var.bucket_location
  storage_class = "STANDARD"
  project       = var.project_id

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    project     = "movies-big-data-pipeline"
    environment = var.environment
    purpose     = "logs"
    managed-by  = "terraform"
  }

  depends_on = [google_project_service.storage_api]
}

# IAM Binding for Log Sink
resource "google_storage_bucket_iam_member" "log_writer" {
  bucket = google_storage_bucket.logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.storage_sink.writer_identity
}

