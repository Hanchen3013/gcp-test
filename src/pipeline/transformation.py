"""
Data transformation module for the pipeline
Handles data cleaning, validation, and transformation
"""
import logging
import pandas as pd
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class DataTransformer:
    """Handles data transformation operations"""
    
    def __init__(self):
        """Initialize data transformer"""
        self.transformations = []
    
    def add_transformation(self, func: Callable) -> 'DataTransformer':
        """
        Add a transformation function to the pipeline
        
        Args:
            func: Transformation function that takes data and returns transformed data
            
        Returns:
            Self for chaining
        """
        self.transformations.append(func)
        return self
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply all transformations to the data
        
        Args:
            data: Input data records
            
        Returns:
            Transformed data records
        """
        logger.info(f"Applying {len(self.transformations)} transformations to {len(data)} records")
        
        result = data
        for func in self.transformations:
            try:
                result = func(result)
            except Exception as e:
                logger.error(f"Error in transformation {func.__name__}: {e}")
                raise
        
        logger.info(f"Transformation complete. Output: {len(result)} records")
        return result
    
    @staticmethod
    def validate_schema(data: List[Dict[str, Any]], required_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Validate that records contain required fields
        
        Args:
            data: Input data records
            required_fields: List of required field names
            
        Returns:
            Validated data records (invalid records are filtered out)
        """
        valid_records = []
        
        for record in data:
            if all(field in record for field in required_fields):
                valid_records.append(record)
            else:
                logger.warning(f"Record missing required fields: {record}")
        
        logger.info(f"Validated {len(valid_records)}/{len(data)} records")
        return valid_records
    
    @staticmethod
    def clean_nulls(data: List[Dict[str, Any]], fill_value: Any = None) -> List[Dict[str, Any]]:
        """
        Clean null values in records
        
        Args:
            data: Input data records
            fill_value: Value to replace nulls with
            
        Returns:
            Cleaned data records
        """
        cleaned = []
        
        for record in data:
            cleaned_record = {}
            for key, value in record.items():
                if value is None:
                    cleaned_record[key] = fill_value
                else:
                    cleaned_record[key] = value
            cleaned.append(cleaned_record)
        
        return cleaned
    
    @staticmethod
    def add_timestamp(data: List[Dict[str, Any]], field_name: str = 'processed_at') -> List[Dict[str, Any]]:
        """
        Add processing timestamp to each record
        
        Args:
            data: Input data records
            field_name: Name of the timestamp field
            
        Returns:
            Data records with timestamp
        """
        timestamp = datetime.utcnow().isoformat()
        
        for record in data:
            record[field_name] = timestamp
        
        return data
    
    @staticmethod
    def filter_records(data: List[Dict[str, Any]], condition: Callable) -> List[Dict[str, Any]]:
        """
        Filter records based on a condition
        
        Args:
            data: Input data records
            condition: Function that returns True for records to keep
            
        Returns:
            Filtered data records
        """
        filtered = [record for record in data if condition(record)]
        logger.info(f"Filtered {len(filtered)}/{len(data)} records")
        return filtered
    
    @staticmethod
    def aggregate_data(data: List[Dict[str, Any]], group_by: str, agg_func: str = 'count') -> pd.DataFrame:
        """
        Aggregate data using pandas
        
        Args:
            data: Input data records
            group_by: Field to group by
            agg_func: Aggregation function (count, sum, mean, etc.)
            
        Returns:
            Aggregated data as DataFrame
        """
        df = pd.DataFrame(data)
        
        if agg_func == 'count':
            result = df.groupby(group_by).size().reset_index(name='count')
        else:
            result = df.groupby(group_by).agg(agg_func).reset_index()
        
        logger.info(f"Aggregated data by {group_by} using {agg_func}")
        return result
    
    @staticmethod
    def deduplicate(data: List[Dict[str, Any]], key_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Remove duplicate records based on key fields
        
        Args:
            data: Input data records
            key_fields: Fields to use for deduplication
            
        Returns:
            Deduplicated data records
        """
        seen = set()
        deduped = []
        
        for record in data:
            # Create a tuple of key field values
            key = tuple(record.get(field) for field in key_fields)
            
            if key not in seen:
                seen.add(key)
                deduped.append(record)
        
        logger.info(f"Deduplicated {len(data)} -> {len(deduped)} records")
        return deduped
