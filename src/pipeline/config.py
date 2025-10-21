"""
Configuration management for the data pipeline
"""
import os
import yaml
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for the data pipeline"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config_path = config_path or os.getenv(
            'PIPELINE_CONFIG', 
            'config/pipeline_config.yaml'
        )
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'gcp': {
                'project_id': os.getenv('GCP_PROJECT_ID', 'your-project-id'),
                'region': os.getenv('GCP_REGION', 'us-central1'),
                'bucket': os.getenv('GCS_BUCKET', 'your-data-bucket'),
            },
            'pubsub': {
                'topic': os.getenv('PUBSUB_TOPIC', 'data-ingestion-topic'),
                'subscription': os.getenv('PUBSUB_SUBSCRIPTION', 'data-ingestion-sub'),
            },
            'bigquery': {
                'dataset': os.getenv('BQ_DATASET', 'pipeline_data'),
                'table': os.getenv('BQ_TABLE', 'processed_data'),
            },
            'pipeline': {
                'batch_size': int(os.getenv('BATCH_SIZE', '100')),
                'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., 'gcp.project_id')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary"""
        return self._config
