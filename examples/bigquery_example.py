"""
Example: Working with BigQuery directly
"""
from src.pipeline.loader import BigQueryLoader
from src.pipeline.config import Config
from src.pipeline.monitoring import setup_logging

def main():
    # Setup logging
    logger = setup_logging(level='INFO')
    logger.info("BigQuery example")
    
    # Load configuration
    config = Config()
    
    # Create BigQuery loader
    loader = BigQueryLoader(
        project_id=config.get('gcp.project_id'),
        dataset_id=config.get('bigquery.dataset')
    )
    
    print("BigQuery Loader initialized")
    print(f"Project: {config.get('gcp.project_id')}")
    print(f"Dataset: {config.get('bigquery.dataset')}")
    print()
    
    # Example operations (uncomment to run with actual GCP credentials)
    
    # 1. Create dataset
    # loader.create_dataset_if_not_exists()
    
    # 2. Load data
    # sample_data = [
    #     {'id': '1', 'name': 'Test 1', 'value': 100},
    #     {'id': '2', 'name': 'Test 2', 'value': 200}
    # ]
    # loader.load_from_records(sample_data, 'processed_data')
    
    # 3. Query data
    # df = loader.query('SELECT * FROM pipeline_data.processed_data LIMIT 10')
    # print(df)
    
    # 4. Get table info
    # info = loader.get_table_info('processed_data')
    # print(f"Table info: {info}")
    
    print("To run this example:")
    print("1. Set GCP_PROJECT_ID in your environment")
    print("2. Authenticate with: gcloud auth application-default login")
    print("3. Uncomment the operations above")

if __name__ == '__main__':
    main()
