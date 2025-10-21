"""
Main pipeline orchestrator
Coordinates ingestion, transformation, and loading
"""
import logging
from typing import List, Dict, Any, Optional
from .config import Config
from .ingestion import DataIngestion, PubSubPublisher
from .transformation import DataTransformer
from .loader import DataLoader


logger = logging.getLogger(__name__)


class Pipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize pipeline
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        
        # Initialize components
        self.ingestion = DataIngestion(
            project_id=self.config.get('gcp.project_id'),
            bucket_name=self.config.get('gcp.bucket')
        )
        
        self.transformer = DataTransformer()
        
        self.loader = DataLoader(
            project_id=self.config.get('gcp.project_id'),
            dataset_id=self.config.get('bigquery.dataset')
        )
        
        # PubSub publisher is optional
        try:
            self.publisher = PubSubPublisher(
                project_id=self.config.get('gcp.project_id'),
                topic_id=self.config.get('pubsub.topic')
            )
        except RuntimeError:
            self.publisher = None
            logger.warning("Pub/Sub publisher not available. Install google-cloud-pubsub to use Pub/Sub features.")
        
        logger.info("Pipeline initialized")
    
    def run(
        self,
        source: str,
        source_type: str = 'file',
        destination: str = 'bigquery',
        table_id: Optional[str] = None,
        publish_to_pubsub: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline
        
        Args:
            source: Data source (file path or GCS blob name)
            source_type: Type of source ('file' or 'gcs')
            destination: Destination type (default: 'bigquery')
            table_id: Target table ID (default from config)
            publish_to_pubsub: Whether to publish to Pub/Sub
            
        Returns:
            Pipeline execution summary
        """
        logger.info(f"Starting pipeline: {source_type}:{source} -> {destination}")
        
        try:
            # Step 1: Ingest data
            if source_type == 'file':
                data = self.ingestion.ingest_from_file(source)
            elif source_type == 'gcs':
                data = self.ingestion.ingest_from_gcs(source)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            logger.info(f"Ingested {len(data)} records")
            
            # Step 2: Transform data
            transformed_data = self.transformer.transform(data)
            logger.info(f"Transformed {len(transformed_data)} records")
            
            # Step 3: Load data
            table_id = table_id or self.config.get('bigquery.table')
            self.loader.load(transformed_data, destination, table_id)
            logger.info(f"Loaded {len(transformed_data)} records to {destination}:{table_id}")
            
            # Optional: Publish to Pub/Sub
            if publish_to_pubsub:
                if self.publisher is None:
                    logger.warning("Pub/Sub publisher not available. Skipping Pub/Sub publish.")
                else:
                    message_ids = self.publisher.publish_batch(transformed_data)
                    logger.info(f"Published {len(message_ids)} messages to Pub/Sub")
            
            return {
                'status': 'success',
                'records_ingested': len(data),
                'records_transformed': len(transformed_data),
                'records_loaded': len(transformed_data),
                'destination': f"{destination}:{table_id}"
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def add_transformation(self, transformation_func) -> 'Pipeline':
        """
        Add a transformation to the pipeline
        
        Args:
            transformation_func: Transformation function
            
        Returns:
            Self for chaining
        """
        self.transformer.add_transformation(transformation_func)
        return self


def create_pipeline(config_path: Optional[str] = None) -> Pipeline:
    """
    Factory function to create a pipeline instance
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Pipeline instance
    """
    config = Config(config_path) if config_path else Config()
    return Pipeline(config)
