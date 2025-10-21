"""
Tests for the configuration module
"""
import unittest
import os
import tempfile
from pathlib import Path
from src.pipeline.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_content = """
gcp:
  project_id: test-project
  region: us-central1
  bucket: test-bucket

pubsub:
  topic: test-topic
  subscription: test-sub

bigquery:
  dataset: test_dataset
  table: test_table

pipeline:
  batch_size: 50
  max_workers: 2
"""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
        with open(self.config_file, 'w') as f:
            f.write(self.test_config_content)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.config_file.exists():
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        config = Config(str(self.config_file))
        
        self.assertEqual(config.get('gcp.project_id'), 'test-project')
        self.assertEqual(config.get('gcp.region'), 'us-central1')
        self.assertEqual(config.get('pubsub.topic'), 'test-topic')
        self.assertEqual(config.get('bigquery.dataset'), 'test_dataset')
        self.assertEqual(config.get('pipeline.batch_size'), 50)
    
    def test_get_nested_config(self):
        """Test getting nested configuration values"""
        config = Config(str(self.config_file))
        
        # Test nested access
        self.assertEqual(config.get('gcp.project_id'), 'test-project')
        
        # Test with default value
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
    
    def test_default_config(self):
        """Test default configuration when file doesn't exist"""
        config = Config('/nonexistent/path/config.yaml')
        
        # Should return default values
        self.assertIsNotNone(config.get('gcp.project_id'))
        self.assertIsNotNone(config.get('pubsub.topic'))
    
    def test_config_property(self):
        """Test config property returns full dictionary"""
        config = Config(str(self.config_file))
        
        full_config = config.config
        self.assertIsInstance(full_config, dict)
        self.assertIn('gcp', full_config)
        self.assertIn('pubsub', full_config)


if __name__ == '__main__':
    unittest.main()
