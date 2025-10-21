"""
Tests for the pipeline orchestrator
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock google cloud modules before importing pipeline
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.pubsub_v1'] = MagicMock()
sys.modules['google.cloud.storage'] = MagicMock()
sys.modules['google.cloud.bigquery'] = MagicMock()
sys.modules['google.cloud.exceptions'] = MagicMock()

from src.pipeline.pipeline import Pipeline, create_pipeline
from src.pipeline.config import Config


class TestPipeline(unittest.TestCase):
    """Test cases for Pipeline class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create pipeline
        self.pipeline = Pipeline()
    
    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly"""
        self.assertIsNotNone(self.pipeline.config)
        self.assertIsNotNone(self.pipeline.transformer)
    
    def test_add_transformation(self):
        """Test adding transformations to pipeline"""
        def dummy_transform(data):
            return data
        
        result = self.pipeline.add_transformation(dummy_transform)
        
        # Should return self for chaining
        self.assertEqual(result, self.pipeline)
    
    def test_create_pipeline_factory(self):
        """Test pipeline factory function"""
        pipeline = create_pipeline()
        
        self.assertIsInstance(pipeline, Pipeline)
        self.assertIsInstance(pipeline.config, Config)


if __name__ == '__main__':
    unittest.main()
