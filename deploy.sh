#!/bin/bash
# Deployment script for GCP Data Pipeline

set -e

echo "========================================="
echo "GCP Data Pipeline Deployment Script"
echo "========================================="

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

if [ -z "$GCS_BUCKET" ]; then
    echo "Error: GCS_BUCKET environment variable is not set"
    exit 1
fi

# Set default region if not specified
REGION=${GCP_REGION:-us-central1}

echo "Project ID: $GCP_PROJECT_ID"
echo "Region: $REGION"
echo "Bucket: $GCS_BUCKET"
echo ""

# Step 1: Deploy infrastructure with Terraform
echo "Step 1: Deploying infrastructure with Terraform..."
cd terraform
terraform init
terraform plan -var="project_id=$GCP_PROJECT_ID" -var="bucket_name=$GCS_BUCKET" -var="region=$REGION"
terraform apply -auto-approve -var="project_id=$GCP_PROJECT_ID" -var="bucket_name=$GCS_BUCKET" -var="region=$REGION"
cd ..

echo "Infrastructure deployed successfully!"
echo ""

# Step 2: Deploy Cloud Function
echo "Step 2: Deploying Cloud Function..."
gcloud functions deploy pubsub-processor \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=./cloud_functions/pubsub_processor \
    --entry-point=process_pubsub_message \
    --trigger-topic=data-ingestion-topic \
    --set-env-vars=GCP_PROJECT_ID=$GCP_PROJECT_ID

echo "Cloud Function deployed successfully!"
echo ""

# Step 3: Create BigQuery dataset and table (if not exists via Terraform)
echo "Step 3: Verifying BigQuery setup..."
bq --project_id=$GCP_PROJECT_ID show --dataset pipeline_data || \
    bq --project_id=$GCP_PROJECT_ID mk --dataset --location=US pipeline_data

echo "BigQuery dataset verified!"
echo ""

echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Update config/pipeline_config.yaml with your project settings"
echo "2. Run the pipeline: python -m src.pipeline.pipeline"
echo "3. Monitor logs in Cloud Logging"
