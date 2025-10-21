"""
Data ingestion module for the pipeline
Handles data collection from various sources
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from google.cloud import pubsub_v1, storage
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    pubsub_v1 = None
    storage = None


logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles data ingestion from various sources"""
    
    def __init__(self, project_id: str, bucket_name: str):
        """
        Initialize data ingestion
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name for raw data
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        
        if GCP_AVAILABLE:
            self.storage_client = storage.Client(project=project_id)
        else:
            self.storage_client = None
            logger.warning("Google Cloud Storage not available. Install google-cloud-storage to use GCS features.")
        
    def ingest_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Ingest data from a local file
        
        Args:
            file_path: Path to the data file
            
        Returns:
            List of data records
        """
        logger.info(f"Ingesting data from file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]
                elif file_path.endswith('.jsonl'):
                    return [json.loads(line) for line in f]
                else:
                    # Assume text file with one record per line
                    return [{'content': line.strip()} for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error ingesting from file: {e}")
            raise
    
    def ingest_from_gcs(self, blob_name: str) -> List[Dict[str, Any]]:
        """
        Ingest data from Google Cloud Storage
        
        Args:
            blob_name: Name of the blob in GCS
            
        Returns:
            List of data records
        """
        if not GCP_AVAILABLE or self.storage_client is None:
            raise RuntimeError("Google Cloud Storage not available. Install google-cloud-storage.")
        
        logger.info(f"Ingesting data from GCS: gs://{self.bucket_name}/{blob_name}")
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            content = blob.download_as_text()
            
            if blob_name.endswith('.json'):
                data = json.loads(content)
                return data if isinstance(data, list) else [data]
            elif blob_name.endswith('.jsonl'):
                return [json.loads(line) for line in content.split('\n') if line.strip()]
            else:
                return [{'content': line.strip()} for line in content.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Error ingesting from GCS: {e}")
            raise
    
    def upload_to_gcs(self, data: List[Dict[str, Any]], destination_blob_name: str) -> str:
        """
        Upload data to Google Cloud Storage
        
        Args:
            data: List of data records
            destination_blob_name: Destination blob name
            
        Returns:
            GCS URI of uploaded data
        """
        if not GCP_AVAILABLE or self.storage_client is None:
            raise RuntimeError("Google Cloud Storage not available. Install google-cloud-storage.")
        
        logger.info(f"Uploading data to GCS: gs://{self.bucket_name}/{destination_blob_name}")
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Convert data to JSONL format
            content = '\n'.join([json.dumps(record) for record in data])
            blob.upload_from_string(content, content_type='application/json')
            
            return f"gs://{self.bucket_name}/{destination_blob_name}"
        except Exception as e:
            logger.error(f"Error uploading to GCS: {e}")
            raise


class PubSubPublisher:
    """Publishes messages to Google Cloud Pub/Sub"""
    
    def __init__(self, project_id: str, topic_id: str):
        """
        Initialize Pub/Sub publisher
        
        Args:
            project_id: GCP project ID
            topic_id: Pub/Sub topic ID
        """
        if not GCP_AVAILABLE:
            raise RuntimeError("Google Cloud Pub/Sub not available. Install google-cloud-pubsub.")
        
        self.project_id = project_id
        self.topic_id = topic_id
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)
        
    def publish_message(self, data: Dict[str, Any]) -> str:
        """
        Publish a single message to Pub/Sub
        
        Args:
            data: Data to publish
            
        Returns:
            Message ID
        """
        try:
            message_json = json.dumps(data)
            message_bytes = message_json.encode('utf-8')
            
            # Add timestamp attribute
            future = self.publisher.publish(
                self.topic_path,
                message_bytes,
                timestamp=datetime.utcnow().isoformat()
            )
            
            message_id = future.result()
            logger.info(f"Published message {message_id} to {self.topic_path}")
            return message_id
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            raise
    
    def publish_batch(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """
        Publish multiple messages to Pub/Sub
        
        Args:
            data_list: List of data records to publish
            
        Returns:
            List of message IDs
        """
        message_ids = []
        
        for data in data_list:
            try:
                message_id = self.publish_message(data)
                message_ids.append(message_id)
            except Exception as e:
                logger.error(f"Error in batch publish: {e}")
                continue
        
        logger.info(f"Published {len(message_ids)} messages to {self.topic_path}")
        return message_ids
