"""
Example: Advanced pipeline with custom transformations
"""
from src.pipeline.pipeline import create_pipeline
from src.pipeline.transformation import DataTransformer
from src.pipeline.monitoring import setup_logging, PipelineMetrics
import json

def main():
    # Setup logging
    logger = setup_logging(level='INFO')
    
    # Initialize metrics
    metrics = PipelineMetrics()
    metrics.start()
    
    logger.info("Starting advanced pipeline example")
    
    # Create pipeline
    pipeline = create_pipeline()
    
    # Add multiple transformations
    
    # 1. Validate required fields
    def validate_required_fields(data):
        required = ['id', 'name', 'value']
        return DataTransformer.validate_schema(data, required)
    
    # 2. Clean and enrich data
    def enrich_data(data):
        for record in data:
            # Add computed field
            record['value_category'] = 'high' if record.get('value', 0) > 200 else 'low'
            # Add metadata
            record['processed_by'] = 'advanced_pipeline'
        return data
    
    # 3. Filter records
    def filter_active_records(data):
        # Example: Only keep records with value > 100
        return DataTransformer.filter_records(
            data,
            condition=lambda r: r.get('value', 0) > 100
        )
    
    # Add transformations to pipeline
    pipeline.add_transformation(validate_required_fields)
    pipeline.add_transformation(enrich_data)
    pipeline.add_transformation(lambda d: DataTransformer.add_timestamp(d))
    pipeline.add_transformation(filter_active_records)
    
    print("Advanced pipeline configured with transformations:")
    print("1. Schema validation")
    print("2. Data enrichment")
    print("3. Timestamp addition")
    print("4. Record filtering")
    print()
    print("To run: Configure GCP credentials and uncomment pipeline.run()")
    
    # Uncomment to run:
    # result = pipeline.run(
    #     source='examples/sample_data.json',
    #     source_type='file',
    #     publish_to_pubsub=True
    # )
    # 
    # metrics.increment_records(result.get('records_loaded', 0))
    # metrics.end(success=result['status'] == 'success')
    # metrics.print_summary()

if __name__ == '__main__':
    main()
