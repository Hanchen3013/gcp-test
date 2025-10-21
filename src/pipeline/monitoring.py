"""
Monitoring and logging utilities for the pipeline
"""
import logging
import sys
from typing import Optional
from datetime import datetime


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_string: Optional custom format string
        
    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


class PipelineMetrics:
    """Tracks pipeline execution metrics"""
    
    def __init__(self):
        """Initialize metrics tracker"""
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': None,
            'records_processed': 0,
            'errors': 0,
            'status': 'not_started'
        }
    
    def start(self) -> None:
        """Mark pipeline start"""
        self.metrics['start_time'] = datetime.utcnow()
        self.metrics['status'] = 'running'
    
    def end(self, success: bool = True) -> None:
        """
        Mark pipeline end
        
        Args:
            success: Whether pipeline completed successfully
        """
        self.metrics['end_time'] = datetime.utcnow()
        self.metrics['duration_seconds'] = (
            self.metrics['end_time'] - self.metrics['start_time']
        ).total_seconds()
        self.metrics['status'] = 'success' if success else 'failed'
    
    def increment_records(self, count: int = 1) -> None:
        """
        Increment processed records count
        
        Args:
            count: Number of records to add
        """
        self.metrics['records_processed'] += count
    
    def increment_errors(self, count: int = 1) -> None:
        """
        Increment error count
        
        Args:
            count: Number of errors to add
        """
        self.metrics['errors'] += count
    
    def get_metrics(self) -> dict:
        """
        Get current metrics
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()
    
    def print_summary(self) -> None:
        """Print metrics summary"""
        print("\n" + "="*50)
        print("Pipeline Execution Summary")
        print("="*50)
        
        for key, value in self.metrics.items():
            if key in ['start_time', 'end_time'] and value:
                print(f"{key}: {value.isoformat()}")
            else:
                print(f"{key}: {value}")
        
        print("="*50 + "\n")
