"""
Tests for the monitoring module
"""
import unittest
from src.pipeline.monitoring import PipelineMetrics, setup_logging


class TestPipelineMetrics(unittest.TestCase):
    """Test cases for PipelineMetrics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.metrics = PipelineMetrics()
    
    def test_initial_state(self):
        """Test initial metrics state"""
        self.assertIsNone(self.metrics.metrics['start_time'])
        self.assertIsNone(self.metrics.metrics['end_time'])
        self.assertEqual(self.metrics.metrics['records_processed'], 0)
        self.assertEqual(self.metrics.metrics['errors'], 0)
        self.assertEqual(self.metrics.metrics['status'], 'not_started')
    
    def test_start_metrics(self):
        """Test starting metrics tracking"""
        self.metrics.start()
        
        self.assertIsNotNone(self.metrics.metrics['start_time'])
        self.assertEqual(self.metrics.metrics['status'], 'running')
    
    def test_end_metrics(self):
        """Test ending metrics tracking"""
        self.metrics.start()
        self.metrics.end(success=True)
        
        self.assertIsNotNone(self.metrics.metrics['end_time'])
        self.assertIsNotNone(self.metrics.metrics['duration_seconds'])
        self.assertEqual(self.metrics.metrics['status'], 'success')
    
    def test_increment_records(self):
        """Test incrementing record count"""
        self.metrics.increment_records(10)
        self.assertEqual(self.metrics.metrics['records_processed'], 10)
        
        self.metrics.increment_records(5)
        self.assertEqual(self.metrics.metrics['records_processed'], 15)
    
    def test_increment_errors(self):
        """Test incrementing error count"""
        self.metrics.increment_errors(1)
        self.assertEqual(self.metrics.metrics['errors'], 1)
        
        self.metrics.increment_errors(3)
        self.assertEqual(self.metrics.metrics['errors'], 4)
    
    def test_get_metrics(self):
        """Test getting metrics dictionary"""
        self.metrics.increment_records(5)
        self.metrics.increment_errors(1)
        
        metrics = self.metrics.get_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['records_processed'], 5)
        self.assertEqual(metrics['errors'], 1)


class TestLogging(unittest.TestCase):
    """Test cases for logging setup"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging(level='INFO')
        
        self.assertIsNotNone(logger)


if __name__ == '__main__':
    unittest.main()
