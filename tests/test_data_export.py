"""
Unit tests for DataExport module.

Tests data export functionality including JSON, CSV export,
and various analytics data export capabilities.
"""

import unittest
import json
import csv
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.data_export import DataExport


class TestDataExport(unittest.TestCase):
    """Test cases for DataExport class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary analytics config
        self.config_data = {
            "rolling_window_seconds": 60,
            "max_metrics_per_category": 1000,
            "calculation_interval_seconds": 5,
            "memory_management": {
                "max_metrics_per_category": 1000,
                "cleanup_interval_seconds": 300
            }
        }
        
        # Create analytics engine with custom config
        self.analytics_engine = AnalyticsEngine()
        # Override config with test data
        self.analytics_engine.config = self.config_data
        self.analytics_engine.rolling_window_seconds = self.config_data.get("rolling_window_seconds", 60)
        
        # Create data export
        self.data_export = DataExport(self.analytics_engine)
        
        # Clear any existing metrics to start fresh
        self.analytics_engine.clear_session_data()
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        self.analytics_engine.shutdown()
        
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test DataExport initialization."""
        self.assertIsNotNone(self.data_export.analytics)
        self.assertIsNotNone(self.data_export.export_timestamp)
        self.assertEqual(self.data_export.export_formats, ['json', 'csv'])
    
    def test_export_analytics_data_json(self):
        """Test analytics data export to JSON."""
        # Add some test metrics
        self.analytics_engine.record_metric("test_metric", 100.0, "test_category")
        self.analytics_engine.record_metric("another_metric", 200.0, "test_category")
        
        export_path = os.path.join(self.temp_dir, "test_export")
        result = self.data_export.export_analytics_data(export_path, 'json')
        
        # Check result
        self.assertEqual(result["format"], "json")
        self.assertTrue(result["file_path"].endswith('.json'))
        self.assertGreater(result["file_size"], 0)
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["data_points"], 0)
        
        # Check file was created
        json_file = Path(result["file_path"])
        self.assertTrue(json_file.exists())
        
        # Check JSON content
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("export_timestamp", data)
        self.assertIn("export_datetime", data)
        self.assertIn("analytics_version", data)
        self.assertIn("data_sources", data)
        self.assertIn("test_category", data["data_sources"])
    
    def test_export_analytics_data_csv(self):
        """Test analytics data export to CSV."""
        # Add some test metrics
        self.analytics_engine.record_metric("test_metric", 100.0, "test_category")
        self.analytics_engine.record_metric("another_metric", 200.0, "test_category")
        
        export_path = os.path.join(self.temp_dir, "test_export")
        result = self.data_export.export_analytics_data(export_path, 'csv')
        
        # Check result
        self.assertEqual(result["format"], "csv")
        self.assertTrue(result["file_path"].endswith('.csv'))
        self.assertGreater(result["file_size"], 0)
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["data_points"], 0)
        
        # Check file was created
        csv_file = Path(result["file_path"])
        self.assertTrue(csv_file.exists())
        
        # Check CSV content
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertGreater(len(rows), 0)
        self.assertIn("data_type", rows[0])
        self.assertIn("category", rows[0])
        self.assertIn("metric_name", rows[0])
        self.assertIn("value", rows[0])
    
    def test_export_analytics_data_with_metadata(self):
        """Test analytics data export with metadata."""
        # Add metrics with metadata
        self.analytics_engine.record_metric("test_metric", 100.0, "test_category", 
                                          {"user_id": "test_user", "session": "test_session"})
        
        export_path = os.path.join(self.temp_dir, "test_export")
        result = self.data_export.export_analytics_data(export_path, 'json', include_metadata=True)
        
        # Check JSON content includes metadata
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        test_category = data["data_sources"]["test_category"]
        test_metric = test_category["metrics"]["test_metric"]
        self.assertIn("metadata", test_metric)
        self.assertEqual(test_metric["metadata"]["user_id"], "test_user")
        self.assertEqual(test_metric["metadata"]["session"], "test_session")
    
    def test_export_analytics_data_without_metadata(self):
        """Test analytics data export without metadata."""
        # Add metrics with metadata
        self.analytics_engine.record_metric("test_metric", 100.0, "test_category", 
                                          {"user_id": "test_user"})
        
        export_path = os.path.join(self.temp_dir, "test_export")
        result = self.data_export.export_analytics_data(export_path, 'json', include_metadata=False)
        
        # Check JSON content excludes metadata
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        test_category = data["data_sources"]["test_category"]
        test_metric = test_category["metrics"]["test_metric"]
        self.assertNotIn("metadata", test_metric)
    
    def test_export_performance_data(self):
        """Test performance data export."""
        # Create mock performance data
        performance_data = [
            {"timestamp": 1234567890, "metric": "response_time", "value": 150.0},
            {"timestamp": 1234567891, "metric": "memory_usage", "value": 65.5}
        ]
        
        export_path = os.path.join(self.temp_dir, "performance_export")
        result = self.data_export.export_performance_data(performance_data, export_path, 'json')
        
        # Check result
        self.assertEqual(result["format"], "json")
        self.assertTrue(result["file_path"].endswith('.json'))
        self.assertEqual(result["status"], "success")
        
        # Check JSON content
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("export_timestamp", data)
        self.assertIn("data_type", data)
        self.assertEqual(data["data_type"], "performance_data")
        self.assertIn("performance_metrics", data)
        self.assertEqual(len(data["performance_metrics"]), 2)
    
    def test_export_robot_analytics(self):
        """Test robot analytics export."""
        # Create mock robot analytics object
        mock_robot_analytics = Mock()
        mock_robot_analytics.get_robot_performance_summary.return_value = {
            "total_robots": 3,
            "active_robots": 2,
            "total_distance_moved": 150.5
        }
        mock_robot_analytics.get_movement_analytics.return_value = {
            "total_distance": 150.5,
            "average_movement": 50.2
        }
        mock_robot_analytics.get_path_optimization_analytics.return_value = {
            "total_savings": 25.3,
            "average_savings": 8.4
        }
        mock_robot_analytics.robots = {
            "ROBOT_001": Mock(),
            "ROBOT_002": Mock()
        }
        mock_robot_analytics.get_robot_analytics.side_effect = lambda robot_id: {
            "robot_id": robot_id,
            "total_distance_moved": 75.0,
            "utilization_rate": 85.5
        }
        
        export_path = os.path.join(self.temp_dir, "robot_export")
        result = self.data_export.export_robot_analytics(mock_robot_analytics, export_path, 'json')
        
        # Check result
        self.assertEqual(result["format"], "json")
        self.assertEqual(result["status"], "success")
        
        # Check JSON content
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["data_type"], "robot_analytics")
        self.assertIn("robot_performance", data)
        self.assertIn("robot_summary", data)
        self.assertIn("movement_analytics", data)
        self.assertIn("path_optimization", data)
        self.assertEqual(data["robot_summary"]["total_robots"], 3)
    
    def test_export_order_analytics(self):
        """Test order analytics export."""
        # Create mock order analytics object
        mock_order_analytics = Mock()
        mock_order_analytics.get_order_summary.return_value = {
            "total_orders": 50,
            "completed_orders": 45,
            "completion_rate": 90.0
        }
        mock_order_analytics.get_order_history.return_value = [
            {"order_id": "ORDER_001", "status": "completed"},
            {"order_id": "ORDER_002", "status": "processing"}
        ]
        mock_order_analytics.get_queue_analytics.return_value = {
            "queue_length": 5,
            "average_wait_time": 30.5
        }
        
        export_path = os.path.join(self.temp_dir, "order_export")
        result = self.data_export.export_order_analytics(mock_order_analytics, export_path, 'json')
        
        # Check result
        self.assertEqual(result["format"], "json")
        self.assertEqual(result["status"], "success")
        
        # Check JSON content
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["data_type"], "order_analytics")
        self.assertIn("order_summary", data)
        self.assertIn("order_history", data)
        self.assertIn("queue_analytics", data)
        self.assertEqual(data["order_summary"]["total_orders"], 50)
    
    def test_export_system_performance(self):
        """Test system performance export."""
        # Create mock performance monitor object
        mock_performance_monitor = Mock()
        mock_performance_monitor.get_system_performance_summary.return_value = {
            "response_time_stats": {"average_response_time": 150.0},
            "memory_stats": {"current_usage": 65.5},
            "system_health": {"health_score": 95.0}
        }
        mock_performance_monitor.get_system_health_history.return_value = [
            Mock(timestamp=1234567890, health_score=95.0, is_healthy=True),
            Mock(timestamp=1234567891, health_score=90.0, is_healthy=True)
        ]
        mock_performance_monitor.get_performance_alerts.return_value = [
            "High memory usage detected"
        ]
        
        export_path = os.path.join(self.temp_dir, "system_export")
        result = self.data_export.export_system_performance(mock_performance_monitor, export_path, 'json')
        
        # Check result
        self.assertEqual(result["format"], "json")
        self.assertEqual(result["status"], "success")
        
        # Check JSON content
        json_file = Path(result["file_path"])
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["data_type"], "system_performance")
        self.assertIn("performance_summary", data)
        self.assertIn("health_history", data)
        self.assertIn("performance_alerts", data)
        self.assertEqual(data["performance_summary"]["system_health"]["health_score"], 95.0)
    
    def test_export_all_data(self):
        """Test export all data functionality."""
        # Add some test metrics
        self.analytics_engine.record_metric("test_metric", 100.0, "test_category")
        
        export_dir = os.path.join(self.temp_dir, "all_data")
        result = self.data_export.export_all_data(export_dir)
        
        # Check result
        self.assertIn("export_timestamp", result)
        self.assertIn("export_datetime", result)
        self.assertIn("export_directory", result)
        self.assertIn("files_exported", result)
        self.assertIn("total_files", result)
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["total_files"], 0)
        
        # Check files were created
        export_path = Path(export_dir)
        self.assertTrue(export_path.exists())
        
        # Check JSON and CSV files exist
        json_files = list(export_path.glob("*.json"))
        csv_files = list(export_path.glob("*.csv"))
        self.assertGreater(len(json_files), 0)
        self.assertGreater(len(csv_files), 0)
    
    def test_get_export_formats(self):
        """Test get export formats."""
        formats = self.data_export.get_export_formats()
        self.assertEqual(formats, ['json', 'csv'])
        # Check that returned list is a copy
        formats.append('xml')
        self.assertEqual(self.data_export.export_formats, ['json', 'csv'])
    
    def test_validate_export_path(self):
        """Test export path validation."""
        # Valid path
        valid_path = os.path.join(self.temp_dir, "test_export.json")
        self.assertTrue(self.data_export.validate_export_path(valid_path))
        
        # Invalid path (non-existent parent directory)
        invalid_path = "/non/existent/path/test.json"
        self.assertFalse(self.data_export.validate_export_path(invalid_path))
    
    def test_unsupported_export_format(self):
        """Test unsupported export format handling."""
        export_path = os.path.join(self.temp_dir, "test_export")
        
        with self.assertRaises(ValueError):
            self.data_export.export_analytics_data(export_path, 'xml')
    
    def test_json_serializer(self):
        """Test JSON serializer for non-serializable objects."""
        # Test with dataclass
        from dataclasses import dataclass
        
        @dataclass
        class TestData:
            value: int
            name: str
        
        test_obj = TestData(value=100, name="test")
        serialized = self.data_export._json_serializer(test_obj)
        
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized["value"], 100)
        self.assertEqual(serialized["name"], "test")
        
        # Test with string
        string_obj = "test_string"
        serialized = self.data_export._json_serializer(string_obj)
        self.assertEqual(serialized, "test_string")
    
    def test_count_data_points(self):
        """Test data point counting."""
        # Empty data
        empty_data = {"data_sources": {}}
        count = self.data_export._count_data_points(empty_data)
        self.assertEqual(count, 0)
        
        # Data with metrics and KPIs
        test_data = {
            "data_sources": {
                "category1": {
                    "metrics": {"metric1": {}, "metric2": {}},
                    "kpis": {"kpi1": {}}
                },
                "category2": {
                    "metrics": {"metric3": {}},
                    "kpis": {}
                }
            }
        }
        count = self.data_export._count_data_points(test_data)
        self.assertEqual(count, 4)  # 3 metrics + 1 KPI
    
    def test_flatten_data_for_csv(self):
        """Test data flattening for CSV export."""
        test_data = {
            "export_timestamp": 1234567890,
            "export_datetime": "2023-01-01T00:00:00",
            "analytics_version": "1.0",
            "data_sources": {
                "test_category": {
                    "metrics": {
                        "test_metric": {
                            "value": 100.0,
                            "unit": "ms",
                            "timestamp": 1234567890
                        }
                    },
                    "kpis": {
                        "test_kpi": {
                            "value": 95.0,
                            "calculation_type": "average",
                            "rolling_window": 60
                        }
                    }
                }
            }
        }
        
        flattened = self.data_export._flatten_data_for_csv(test_data)
        
        # Check structure
        self.assertGreater(len(flattened), 0)
        self.assertIn("data_type", flattened[0])
        self.assertIn("category", flattened[0])
        self.assertIn("metric_name", flattened[0])
        self.assertIn("value", flattened[0])
        
        # Check metadata row
        metadata_row = flattened[0]
        self.assertEqual(metadata_row["data_type"], "export_metadata")
        
        # Check metric row
        metric_rows = [row for row in flattened if row["data_type"] == "metric"]
        self.assertGreater(len(metric_rows), 0)
        
        # Check KPI row
        kpi_rows = [row for row in flattened if row["data_type"] == "kpi"]
        self.assertGreater(len(kpi_rows), 0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 