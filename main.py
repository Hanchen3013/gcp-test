"""
Main entry point for the GCP Data Pipeline
"""
import argparse
import sys
from src.pipeline.pipeline import create_pipeline
from src.pipeline.transformation import DataTransformer
from src.pipeline.monitoring import setup_logging, PipelineMetrics


def main():
    """Main function to run the pipeline from command line"""
    parser = argparse.ArgumentParser(description='GCP Data Pipeline')
    
    parser.add_argument(
        '--source',
        required=True,
        help='Data source (file path or GCS blob name)'
    )
    
    parser.add_argument(
        '--source-type',
        choices=['file', 'gcs'],
        default='file',
        help='Type of data source'
    )
    
    parser.add_argument(
        '--destination',
        default='bigquery',
        help='Destination type (default: bigquery)'
    )
    
    parser.add_argument(
        '--table-id',
        help='Target table ID (default from config)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--publish-pubsub',
        action='store_true',
        help='Publish to Pub/Sub in addition to loading'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--add-timestamp',
        action='store_true',
        help='Add processing timestamp to records'
    )
    
    parser.add_argument(
        '--validate-schema',
        nargs='+',
        help='Required fields for schema validation'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level)
    logger.info("Starting GCP Data Pipeline")
    
    # Initialize metrics
    metrics = PipelineMetrics()
    metrics.start()
    
    try:
        # Create pipeline
        pipeline = create_pipeline(args.config)
        
        # Add transformations based on arguments
        if args.validate_schema:
            def validate(data):
                return DataTransformer.validate_schema(data, args.validate_schema)
            pipeline.add_transformation(validate)
            logger.info(f"Added schema validation for fields: {args.validate_schema}")
        
        if args.add_timestamp:
            pipeline.add_transformation(lambda d: DataTransformer.add_timestamp(d))
            logger.info("Added timestamp transformation")
        
        # Run pipeline
        result = pipeline.run(
            source=args.source,
            source_type=args.source_type,
            destination=args.destination,
            table_id=args.table_id,
            publish_to_pubsub=args.publish_pubsub
        )
        
        # Update metrics
        if result['status'] == 'success':
            metrics.increment_records(result.get('records_loaded', 0))
            metrics.end(success=True)
            logger.info(f"Pipeline completed successfully: {result}")
        else:
            metrics.end(success=False)
            logger.error(f"Pipeline failed: {result}")
            sys.exit(1)
        
        # Print summary
        metrics.print_summary()
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        metrics.increment_errors()
        metrics.end(success=False)
        metrics.print_summary()
        sys.exit(1)


if __name__ == '__main__':
    main()
