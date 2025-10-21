#!/bin/bash
# Script to run the data pipeline locally

set -e

echo "========================================="
echo "Running GCP Data Pipeline"
echo "========================================="

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Run pipeline
echo "Starting pipeline..."
python3 -c "
from src.pipeline.pipeline import create_pipeline
from src.pipeline.monitoring import setup_logging

# Setup logging
setup_logging(level='INFO')

# Create and configure pipeline
pipeline = create_pipeline()

# Add transformations (example)
from src.pipeline.transformation import DataTransformer

def add_metadata(data):
    for record in data:
        record['pipeline_version'] = '0.1.0'
    return data

pipeline.add_transformation(add_metadata)
pipeline.add_transformation(lambda d: DataTransformer.add_timestamp(d))

# Run pipeline (modify source as needed)
# result = pipeline.run(
#     source='data/sample_data.json',
#     source_type='file',
#     publish_to_pubsub=False
# )
# 
# print(result)
print('Pipeline setup complete. Modify run_pipeline.sh to execute with your data.')
"

echo ""
echo "========================================="
echo "Pipeline execution completed"
echo "========================================="
