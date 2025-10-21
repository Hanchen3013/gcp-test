# GCP Data Pipeline

A comprehensive data pipeline application designed for deployment on Google Cloud Platform (GCP). This pipeline provides a robust framework for ingesting, transforming, and loading data using GCP services including Cloud Storage, Pub/Sub, and BigQuery.

## Features

- **Data Ingestion**: Supports multiple data sources including local files, Google Cloud Storage, and Pub/Sub streams
- **Data Transformation**: Flexible transformation framework with built-in data validation, cleaning, and enrichment
- **Data Loading**: Automated loading to BigQuery with schema management
- **Serverless Processing**: Cloud Functions for event-driven data processing
- **Infrastructure as Code**: Terraform configurations for automated GCP resource provisioning
- **Monitoring**: Built-in metrics tracking and logging
- **Scalable**: Designed for horizontal scaling on GCP

## Architecture

```
Data Sources → Ingestion → Transformation → Loading → BigQuery
                    ↓
                Pub/Sub → Cloud Function → BigQuery
```

### Components

1. **Ingestion Module** (`src/pipeline/ingestion.py`)
   - File ingestion (JSON, JSONL, text)
   - Google Cloud Storage integration
   - Pub/Sub message publishing

2. **Transformation Module** (`src/pipeline/transformation.py`)
   - Schema validation
   - Data cleaning and enrichment
   - Filtering and deduplication
   - Custom transformation support

3. **Loader Module** (`src/pipeline/loader.py`)
   - BigQuery integration
   - Automated schema management
   - Batch and streaming loading

4. **Cloud Functions** (`cloud_functions/`)
   - Event-driven processing
   - Pub/Sub message handling
   - Serverless data transformation

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- GCP Project with billing enabled
- gcloud CLI installed and configured
- Terraform >= 1.0 (for infrastructure deployment)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Hanchen3013/gcp-test.git
cd gcp-test
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package with dependencies
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### 3. Configure GCP Credentials

```bash
# Authenticate with GCP
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Set Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCS_BUCKET`: Google Cloud Storage bucket name
- `GCP_REGION`: GCP region (default: us-central1)
- `PUBSUB_TOPIC`: Pub/Sub topic name
- `BQ_DATASET`: BigQuery dataset name

### 5. Deploy Infrastructure

```bash
# Using Terraform
cd terraform
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID" -var="bucket_name=YOUR_BUCKET"
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="bucket_name=YOUR_BUCKET"

# Or use the deployment script
./deploy.sh
```

## Usage

### Running the Pipeline

#### Basic Usage

```python
from src.pipeline.pipeline import create_pipeline
from src.pipeline.monitoring import setup_logging

# Setup logging
setup_logging(level='INFO')

# Create pipeline
pipeline = create_pipeline()

# Run pipeline
result = pipeline.run(
    source='data/input.json',
    source_type='file',
    destination='bigquery',
    table_id='processed_data'
)

print(f"Pipeline result: {result}")
```

#### With Custom Transformations

```python
from src.pipeline.pipeline import create_pipeline
from src.pipeline.transformation import DataTransformer

# Create pipeline
pipeline = create_pipeline()

# Add custom transformation
def enrich_data(data):
    for record in data:
        record['enriched'] = True
        record['source'] = 'custom_source'
    return data

pipeline.add_transformation(enrich_data)
pipeline.add_transformation(lambda d: DataTransformer.add_timestamp(d))

# Run pipeline
result = pipeline.run(
    source='gs://your-bucket/data.json',
    source_type='gcs',
    publish_to_pubsub=True
)
```

#### Using the Shell Script

```bash
# Run the pipeline with the provided script
./run_pipeline.sh
```

### Data Ingestion

#### From Local File

```python
from src.pipeline.ingestion import DataIngestion

ingestion = DataIngestion(
    project_id='your-project-id',
    bucket_name='your-bucket'
)

# Ingest from local file
data = ingestion.ingest_from_file('data/sample.json')
```

#### From Google Cloud Storage

```python
# Ingest from GCS
data = ingestion.ingest_from_gcs('path/to/blob.json')
```

#### Publishing to Pub/Sub

```python
from src.pipeline.ingestion import PubSubPublisher

publisher = PubSubPublisher(
    project_id='your-project-id',
    topic_id='data-ingestion-topic'
)

# Publish single message
message_id = publisher.publish_message({'key': 'value'})

# Publish batch
message_ids = publisher.publish_batch([
    {'key': 'value1'},
    {'key': 'value2'}
])
```

### Data Transformation

```python
from src.pipeline.transformation import DataTransformer

transformer = DataTransformer()

# Validate schema
data = transformer.validate_schema(data, required_fields=['id', 'name'])

# Clean null values
data = transformer.clean_nulls(data, fill_value='N/A')

# Add timestamp
data = transformer.add_timestamp(data)

# Filter records
data = transformer.filter_records(data, condition=lambda r: r.get('active', False))

# Deduplicate
data = transformer.deduplicate(data, key_fields=['id'])
```

### Loading to BigQuery

```python
from src.pipeline.loader import BigQueryLoader

loader = BigQueryLoader(
    project_id='your-project-id',
    dataset_id='pipeline_data'
)

# Create dataset if not exists
loader.create_dataset_if_not_exists()

# Load data
loader.load_from_records(
    records=data,
    table_id='processed_data',
    write_disposition='WRITE_APPEND'
)

# Query data
df = loader.query('SELECT * FROM pipeline_data.processed_data LIMIT 10')
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_transformation.py

# Run with verbose output
pytest -v
```

## Configuration

### Pipeline Configuration File

Edit `config/pipeline_config.yaml`:

```yaml
gcp:
  project_id: ${GCP_PROJECT_ID}
  region: us-central1
  bucket: ${GCS_BUCKET}

pubsub:
  topic: data-ingestion-topic
  subscription: data-ingestion-sub

bigquery:
  dataset: pipeline_data
  table: processed_data

pipeline:
  batch_size: 100
  max_workers: 4
```

## Cloud Functions

Deploy the Pub/Sub processing function:

```bash
cd cloud_functions/pubsub_processor

gcloud functions deploy pubsub-processor \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=process_pubsub_message \
    --trigger-topic=data-ingestion-topic \
    --set-env-vars=GCP_PROJECT_ID=your-project-id
```

## Monitoring

### View Logs

```bash
# View Cloud Function logs
gcloud functions logs read pubsub-processor --region=us-central1

# View all logs for the project
gcloud logging read "resource.type=cloud_function" --limit 50
```

### Metrics

The pipeline includes built-in metrics tracking:

```python
from src.pipeline.monitoring import PipelineMetrics

metrics = PipelineMetrics()
metrics.start()

# ... run pipeline ...

metrics.increment_records(100)
metrics.end(success=True)

# Print summary
metrics.print_summary()
```

## Project Structure

```
gcp-test/
├── src/
│   └── pipeline/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── ingestion.py       # Data ingestion
│       ├── transformation.py  # Data transformation
│       ├── loader.py          # Data loading
│       ├── pipeline.py        # Pipeline orchestrator
│       └── monitoring.py      # Monitoring and logging
├── tests/
│   ├── test_config.py
│   ├── test_transformation.py
│   ├── test_pipeline.py
│   └── test_monitoring.py
├── cloud_functions/
│   └── pubsub_processor/
│       ├── main.py
│       └── requirements.txt
├── terraform/
│   ├── main.tf
│   └── terraform.tfvars.example
├── config/
│   └── pipeline_config.yaml
├── setup.py
├── requirements.txt
├── pyproject.toml
├── deploy.sh              # Deployment script
├── run_pipeline.sh        # Pipeline execution script
├── .env.example
└── README.md
```

## Best Practices

1. **Security**
   - Never commit credentials or API keys
   - Use service accounts with minimal required permissions
   - Enable audit logging

2. **Data Validation**
   - Always validate data schema before processing
   - Handle missing or null values appropriately
   - Log validation failures

3. **Error Handling**
   - Implement retry logic for transient failures
   - Use dead letter queues for failed messages
   - Monitor error rates

4. **Performance**
   - Use batching for large datasets
   - Partition BigQuery tables by date
   - Optimize transformation logic

5. **Cost Optimization**
   - Set lifecycle policies on Cloud Storage
   - Use BigQuery partitioning and clustering
   - Monitor and optimize Cloud Function execution

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Reset authentication
   gcloud auth application-default login
   ```

2. **Permission Errors**
   ```bash
   # Grant necessary IAM roles
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member=serviceAccount:SERVICE_ACCOUNT \
       --role=roles/bigquery.dataEditor
   ```

3. **Import Errors**
   ```bash
   # Reinstall package in development mode
   pip install -e .
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the development team

## Acknowledgments

- Built for Google Cloud Platform
- Uses Apache Beam for data processing
- Leverages Terraform for infrastructure management