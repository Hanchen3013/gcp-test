# Terraform configuration for GCP Data Pipeline

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "pipeline_data"
}

variable "bucket_name" {
  description = "GCS bucket name for data storage"
  type        = string
}

# Google Cloud Storage Bucket
resource "google_storage_bucket" "data_bucket" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "pipeline_dataset" {
  dataset_id  = var.dataset_id
  location    = "US"
  description = "Dataset for data pipeline processed data"
  
  default_table_expiration_ms = null
  
  labels = {
    environment = "production"
    managed_by  = "terraform"
  }
}

# BigQuery Table
resource "google_bigquery_table" "processed_data" {
  dataset_id = google_bigquery_dataset.pipeline_dataset.dataset_id
  table_id   = "processed_data"
  
  time_partitioning {
    type  = "DAY"
    field = "processed_at"
  }
  
  schema = jsonencode([
    {
      name        = "id"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Record ID"
    },
    {
      name        = "data"
      type        = "JSON"
      mode        = "NULLABLE"
      description = "Data payload"
    },
    {
      name        = "processed_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Processing timestamp"
    },
    {
      name        = "source"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Data source"
    }
  ])
  
  labels = {
    environment = "production"
  }
}

# Pub/Sub Topic
resource "google_pubsub_topic" "data_ingestion" {
  name = "data-ingestion-topic"
  
  labels = {
    environment = "production"
  }
  
  message_retention_duration = "86400s"  # 1 day
}

# Pub/Sub Subscription
resource "google_pubsub_subscription" "data_ingestion_sub" {
  name  = "data-ingestion-sub"
  topic = google_pubsub_topic.data_ingestion.name
  
  ack_deadline_seconds = 20
  
  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  expiration_policy {
    ttl = ""  # Never expire
  }
}

# Service Account for Cloud Functions
resource "google_service_account" "pipeline_function_sa" {
  account_id   = "pipeline-function-sa"
  display_name = "Service Account for Pipeline Cloud Functions"
}

# IAM permissions for Service Account
resource "google_project_iam_member" "function_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_function_sa.email}"
}

resource "google_project_iam_member" "function_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pipeline_function_sa.email}"
}

resource "google_project_iam_member" "function_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_function_sa.email}"
}

# Outputs
output "bucket_name" {
  value       = google_storage_bucket.data_bucket.name
  description = "GCS bucket name"
}

output "dataset_id" {
  value       = google_bigquery_dataset.pipeline_dataset.dataset_id
  description = "BigQuery dataset ID"
}

output "pubsub_topic" {
  value       = google_pubsub_topic.data_ingestion.name
  description = "Pub/Sub topic name"
}

output "pubsub_subscription" {
  value       = google_pubsub_subscription.data_ingestion_sub.name
  description = "Pub/Sub subscription name"
}

output "service_account_email" {
  value       = google_service_account.pipeline_function_sa.email
  description = "Service account email for Cloud Functions"
}
