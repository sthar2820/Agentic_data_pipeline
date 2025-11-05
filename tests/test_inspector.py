import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.inspector.inspector_agent import InspectorAgent
from orchestrator.types import DataQuality


class TestInspectorAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'max_rows_sample': 1000,
            'quality_checks': [
                'missing_values',
                'data_types',
                'duplicates',
                'outliers',
                'column_statistics'
            ]
        }
        self.inspector = InspectorAgent(self.config)
    
    def test_init(self):
        """Test InspectorAgent initialization"""
        self.assertEqual(self.inspector.config, self.config)
        self.assertIsNotNone(self.inspector.logger)
    
    def test_analyze_missing_values(self):
        """Test missing values analysis"""
        # Create test data with missing values
        data = pd.DataFrame({
            'col1': [1, 2, None, 4, 5],
            'col2': [1, None, None, 4, 5],
            'col3': [1, 2, 3, 4, 5]
        })
        
        missing_values = self.inspector._analyze_missing_values(data)
        
        self.assertEqual(missing_values['col1'], 20.0)  # 1/5 = 20%
        self.assertEqual(missing_values['col2'], 40.0)  # 2/5 = 40%
        self.assertEqual(missing_values['col3'], 0.0)   # 0/5 = 0%
    
    def test_analyze_data_types(self):
        """Test data types analysis"""
        data = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'str_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        data_types = self.inspector._analyze_data_types(data)
        
        self.assertEqual(data_types['int_col'], 'int64')
        self.assertEqual(data_types['float_col'], 'float64')
        self.assertEqual(data_types['str_col'], 'object')
    
    def test_count_duplicates(self):
        """Test duplicate counting"""
        data = pd.DataFrame({
            'col1': [1, 2, 3, 2, 1],
            'col2': ['a', 'b', 'c', 'b', 'a']
        })
        
        duplicate_count = self.inspector._count_duplicates(data)
        self.assertEqual(duplicate_count, 2)  # Two duplicate rows
    
    def test_detect_outliers(self):
        """Test outlier detection"""
        # Create data with obvious outliers
        normal_data = np.random.normal(0, 1, 100)
        outliers = [10, -10]  # Clear outliers
        data = pd.DataFrame({
            'normal_col': np.concatenate([normal_data, outliers])
        })
        
        outlier_count = self.inspector._detect_outliers(data)
        self.assertGreater(outlier_count, 0)
    
    def test_calculate_column_statistics(self):
        """Test column statistics calculation"""
        data = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'string_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        stats = self.inspector._calculate_column_statistics(data)
        
        # Check numeric column stats
        self.assertEqual(stats['numeric_col']['count'], 5)
        self.assertEqual(stats['numeric_col']['unique_count'], 5)
        self.assertEqual(stats['numeric_col']['mean'], 3.0)
        self.assertEqual(stats['numeric_col']['min'], 1.0)
        self.assertEqual(stats['numeric_col']['max'], 5.0)
        
        # Check string column stats
        self.assertEqual(stats['string_col']['count'], 5)
        self.assertEqual(stats['string_col']['unique_count'], 5)
        self.assertNotIn('mean', stats['string_col'])
    
    def test_assess_overall_quality_excellent(self):
        """Test excellent quality assessment"""
        missing_values = {'col1': 0.0, 'col2': 0.0}
        duplicate_count = 0
        outlier_count = 0
        
        quality = self.inspector._assess_overall_quality(
            missing_values, duplicate_count, outlier_count
        )
        
        self.assertEqual(quality, DataQuality.EXCELLENT)
    
    def test_assess_overall_quality_poor(self):
        """Test poor quality assessment"""
        missing_values = {'col1': 50.0, 'col2': 60.0}  # High missing values
        duplicate_count = 100
        outlier_count = 200
        
        quality = self.inspector._assess_overall_quality(
            missing_values, duplicate_count, outlier_count
        )
        
        self.assertEqual(quality, DataQuality.POOR)
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        missing_values = {'col1': 60.0, 'col2': 5.0}  # High and low missing
        duplicate_count = 10
        outlier_count = 25
        data_types = {'col1': 'object', 'col2': 'int64'}
        
        recommendations = self.inspector._generate_recommendations(
            missing_values, duplicate_count, outlier_count, data_types
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check for specific recommendations
        rec_text = ' '.join(recommendations)
        self.assertIn('col1', rec_text)  # Should mention high missing column
        self.assertIn('duplicate', rec_text.lower())
        self.assertIn('outlier', rec_text.lower())
    
    @patch('agents.inspector.inspector_agent.logging')
    def test_analyze_data_complete(self, mock_logging):
        """Test complete data analysis workflow"""
        # Create comprehensive test data
        data = pd.DataFrame({
            'id': range(100),
            'value': np.random.normal(0, 1, 100),
            'category': np.random.choice(['A', 'B', 'C'], 100),
            'missing_col': [1 if i % 5 == 0 else None for i in range(100)]
        })
        
        # Add some duplicates
        data = pd.concat([data, data.head(5)], ignore_index=True)
        
        report = self.inspector.analyze_data(data)
        
        # Verify report structure
        self.assertIsNotNone(report.overall_quality)
        self.assertIsInstance(report.missing_values, dict)
        self.assertIsInstance(report.data_types, dict)
        self.assertIsInstance(report.duplicate_count, int)
        self.assertIsInstance(report.outlier_count, int)
        self.assertIsInstance(report.column_stats, dict)
        self.assertIsInstance(report.recommendations, list)
        self.assertIsNotNone(report.timestamp)
        
        # Verify specific values
        self.assertEqual(report.duplicate_count, 5)
        self.assertEqual(len(report.data_types), 4)
        self.assertGreater(report.missing_values['missing_col'], 0)


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInspectorAgent)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(not result.wasSuccessful())
