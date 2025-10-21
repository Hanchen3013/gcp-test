"""
Google Cloud Function for processing Pub/Sub messages
This function is triggered by Pub/Sub messages and processes incoming data
"""
import json
import logging
import base64
from google.cloud import bigquery
from datetime import datetime


# Initialize BigQuery client
client = bigquery.Client()

# Configuration
PROJECT_ID = 'your-project-id'  # Replace with your project ID
DATASET_ID = 'pipeline_data'
TABLE_ID = 'processed_data'

logger = logging.getLogger(__name__)


def process_pubsub_message(event, context):
    """
    Background Cloud Function to be triggered by Pub/Sub.
    
    Args:
        event (dict): Event payload containing Pub/Sub message
        context (google.cloud.functions.Context): Metadata for the event
    """
    try:
        # Decode the Pub/Sub message
        if 'data' in event:
            message_data = base64.b64decode(event['data']).decode('utf-8')
            data = json.loads(message_data)
            
            logger.info(f"Processing message: {context.event_id}")
            
            # Add processing metadata
            data['processed_at'] = datetime.utcnow().isoformat()
            data['message_id'] = context.event_id
            data['timestamp'] = event.get('attributes', {}).get('timestamp', 
                                                                 datetime.utcnow().isoformat())
            
            # Transform data (add your custom logic here)
            transformed_data = transform_data(data)
            
            # Load to BigQuery
            load_to_bigquery(transformed_data)
            
            logger.info(f"Successfully processed message {context.event_id}")
            
        else:
            logger.warning("No data in Pub/Sub message")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise


def transform_data(data):
    """
    Transform the data (customize based on your needs)
    
    Args:
        data: Input data dictionary
        
    Returns:
        Transformed data dictionary
    """
    # Example transformations
    if 'timestamp' not in data:
        data['timestamp'] = datetime.utcnow().isoformat()
    
    # Add any custom transformation logic here
    
    return data


def load_to_bigquery(data):
    """
    Load data to BigQuery
    
    Args:
        data: Data dictionary to load
    """
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    
    # Insert single row
    errors = client.insert_rows_json(table_ref, [data])
    
    if errors:
        logger.error(f"Errors inserting rows: {errors}")
        raise Exception(f"Failed to insert data: {errors}")
    
    logger.info("Data loaded to BigQuery successfully")
