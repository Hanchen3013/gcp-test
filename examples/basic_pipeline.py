"""
Example: Basic pipeline execution
"""
from src.pipeline.pipeline import create_pipeline
from src.pipeline.monitoring import setup_logging

def main():
    # Setup logging
    logger = setup_logging(level='INFO')
    logger.info("Starting basic pipeline example")
    
    # Create pipeline
    pipeline = create_pipeline()
    
    # Add transformation to add metadata
    def add_metadata(data):
        for record in data:
            record['pipeline_version'] = '0.1.0'
            record['example'] = 'basic'
        return data
    
    pipeline.add_transformation(add_metadata)
    
    # Note: This is a dry-run example. Uncomment to run with actual GCP resources
    print("Pipeline created successfully!")
    print("To run the pipeline with your data:")
    print("1. Set up your GCP credentials")
    print("2. Configure environment variables in .env")
    print("3. Deploy infrastructure with: ./deploy.sh")
    print("4. Uncomment the pipeline.run() call below")
    print()
    
    # Uncomment to run:
    # result = pipeline.run(
    #     source='examples/sample_data.json',
    #     source_type='file',
    #     destination='bigquery',
    #     table_id='processed_data'
    # )
    # print(f"Pipeline result: {result}")

if __name__ == '__main__':
    main()
