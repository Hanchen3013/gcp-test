"""
Data loading module for the pipeline
Handles loading data into BigQuery and other destinations
"""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    bigquery = None
    NotFound = Exception


logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Loads data into Google BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Initialize BigQuery loader
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        if not GCP_AVAILABLE:
            raise RuntimeError("Google Cloud BigQuery not available. Install google-cloud-bigquery.")
        
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_ref = self.client.dataset(dataset_id)
        
    def create_dataset_if_not_exists(self, location: str = 'US') -> None:
        """
        Create BigQuery dataset if it doesn't exist
        
        Args:
            location: Dataset location (e.g., 'US', 'EU')
        """
        try:
            self.client.get_dataset(self.dataset_ref)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = location
            dataset = self.client.create_dataset(dataset)
            logger.info(f"Created dataset {self.dataset_id}")
    
    def create_table_if_not_exists(
        self, 
        table_id: str, 
        schema: List
    ) -> None:
        """
        Create BigQuery table if it doesn't exist
        
        Args:
            table_id: Table ID
            schema: Table schema
        """
        table_ref = self.dataset_ref.table(table_id)
        
        try:
            self.client.get_table(table_ref)
            logger.info(f"Table {table_id} already exists")
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Created table {table_id}")
    
    def load_from_dataframe(
        self, 
        df: pd.DataFrame, 
        table_id: str,
        write_disposition: str = 'WRITE_APPEND'
    ):
        """
        Load data from pandas DataFrame into BigQuery
        
        Args:
            df: DataFrame to load
            table_id: Target table ID
            write_disposition: Write mode (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
            
        Returns:
            Load job
        """
        table_ref = self.dataset_ref.table(table_id)
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True,
        )
        
        logger.info(f"Loading {len(df)} rows into {table_id}")
        
        job = self.client.load_table_from_dataframe(
            df,
            table_ref,
            job_config=job_config
        )
        
        job.result()  # Wait for job to complete
        
        logger.info(f"Loaded {job.output_rows} rows into {table_id}")
        return job
    
    def load_from_records(
        self,
        records: List[Dict[str, Any]],
        table_id: str,
        write_disposition: str = 'WRITE_APPEND'
    ):
        """
        Load data from list of dictionaries into BigQuery
        
        Args:
            records: List of data records
            table_id: Target table ID
            write_disposition: Write mode
            
        Returns:
            Load job
        """
        df = pd.DataFrame(records)
        return self.load_from_dataframe(df, table_id, write_disposition)
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            sql: SQL query string
            
        Returns:
            Query results as DataFrame
        """
        logger.info(f"Executing query: {sql[:100]}...")
        
        query_job = self.client.query(sql)
        results = query_job.result()
        
        df = results.to_dataframe()
        logger.info(f"Query returned {len(df)} rows")
        
        return df
    
    def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """
        Get information about a table
        
        Args:
            table_id: Table ID
            
        Returns:
            Dictionary with table information
        """
        table_ref = self.dataset_ref.table(table_id)
        table = self.client.get_table(table_ref)
        
        return {
            'num_rows': table.num_rows,
            'num_bytes': table.num_bytes,
            'created': table.created,
            'modified': table.modified,
            'schema': [{'name': field.name, 'type': field.field_type} for field in table.schema]
        }


class DataLoader:
    """Main data loader orchestrating different loading strategies"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Initialize data loader
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        if GCP_AVAILABLE:
            self.bigquery_loader = BigQueryLoader(project_id, dataset_id)
        else:
            self.bigquery_loader = None
            logger.warning("BigQuery not available. Install google-cloud-bigquery to use BigQuery features.")
    
    def load(
        self,
        data: List[Dict[str, Any]],
        destination: str,
        table_id: str,
        **kwargs
    ) -> None:
        """
        Load data to specified destination
        
        Args:
            data: Data records to load
            destination: Destination type (currently supports 'bigquery')
            table_id: Target table ID
            **kwargs: Additional arguments for the loader
        """
        if destination.lower() == 'bigquery':
            if self.bigquery_loader is None:
                raise RuntimeError("BigQuery not available. Install google-cloud-bigquery.")
            self.bigquery_loader.load_from_records(data, table_id, **kwargs)
        else:
            raise ValueError(f"Unsupported destination: {destination}")
