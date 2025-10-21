"""
Tests for the transformation module
"""
import unittest
from src.pipeline.transformation import DataTransformer


class TestDataTransformer(unittest.TestCase):
    """Test cases for DataTransformer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.transformer = DataTransformer()
        self.sample_data = [
            {'id': 1, 'name': 'Alice', 'age': 30},
            {'id': 2, 'name': 'Bob', 'age': 25},
            {'id': 3, 'name': 'Charlie', 'age': 35}
        ]
    
    def test_validate_schema(self):
        """Test schema validation"""
        valid_data = DataTransformer.validate_schema(
            self.sample_data,
            required_fields=['id', 'name']
        )
        
        self.assertEqual(len(valid_data), 3)
        
        # Test with missing fields
        invalid_data = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2},  # Missing 'name'
            {'name': 'Charlie'}  # Missing 'id'
        ]
        
        valid_data = DataTransformer.validate_schema(
            invalid_data,
            required_fields=['id', 'name']
        )
        
        self.assertEqual(len(valid_data), 1)
    
    def test_clean_nulls(self):
        """Test null value cleaning"""
        data_with_nulls = [
            {'id': 1, 'name': 'Alice', 'age': None},
            {'id': 2, 'name': None, 'age': 25}
        ]
        
        cleaned = DataTransformer.clean_nulls(data_with_nulls, fill_value='N/A')
        
        self.assertEqual(cleaned[0]['age'], 'N/A')
        self.assertEqual(cleaned[1]['name'], 'N/A')
    
    def test_add_timestamp(self):
        """Test adding timestamp to records"""
        result = DataTransformer.add_timestamp(
            self.sample_data.copy(),
            field_name='processed_at'
        )
        
        self.assertTrue(all('processed_at' in record for record in result))
    
    def test_filter_records(self):
        """Test filtering records"""
        # Filter records where age > 28
        filtered = DataTransformer.filter_records(
            self.sample_data,
            condition=lambda r: r.get('age', 0) > 28
        )
        
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r['age'] > 28 for r in filtered))
    
    def test_deduplicate(self):
        """Test deduplication"""
        data_with_dupes = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
            {'id': 1, 'name': 'Alice'},  # Duplicate
            {'id': 3, 'name': 'Charlie'}
        ]
        
        deduped = DataTransformer.deduplicate(data_with_dupes, key_fields=['id'])
        
        self.assertEqual(len(deduped), 3)
    
    def test_transformation_chaining(self):
        """Test chaining multiple transformations"""
        def add_prefix(data):
            for record in data:
                record['name'] = f"Mr./Ms. {record['name']}"
            return data
        
        def uppercase_names(data):
            for record in data:
                record['name'] = record['name'].upper()
            return data
        
        self.transformer.add_transformation(add_prefix)
        self.transformer.add_transformation(uppercase_names)
        
        result = self.transformer.transform(self.sample_data.copy())
        
        self.assertTrue(all(record['name'].startswith('MR./MS.') for record in result))


if __name__ == '__main__':
    unittest.main()
