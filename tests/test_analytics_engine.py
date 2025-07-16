"""
Tests for Analytics Engine

This module tests the core analytics engine functionality including real-time KPI calculations,
event-driven data collection, and session-based storage.
"""

import unittest
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from core.analytics.analytics_engine import AnalyticsEngine, MetricData, KPICalculation, MetricType


class TestAnalyticsEngine(unittest.TestCase):
    """Test cases for AnalyticsEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.config_data = {
            "rolling_window_seconds": 60,  # 1 minute for testing
            "update_frequency_seconds": 0.1,
            "max_metrics_per_category": 100,
            "kpi_calculation_timeout_ms": 50,
            "enable_performance_monitoring": True,
            "enable_debug_mode": True,
            "categories": {
                "order_processing": {
                    "enabled": True,
                    "metrics": ["orders_per_hour", "avg_order_time", "completion_rate"]
                },
                "robot_performance": {
                    "enabled": True,
                    "metrics": ["utilization", "efficiency", "idle_time"]
                }
            }
        }
        
        # Create temporary config file
        self.config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.config_data, self.config_file)
        self.config_file.close()
        
        # Create analytics engine
        self.analytics = AnalyticsEngine(self.config_file.name)
        
        # Mock event system
        self.mock_event_system = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary config file
        os.unlink(self.config_file.name)
        
        # Shutdown analytics engine
        self.analytics.shutdown()
    
    def test_initialization(self):
        """Test analytics engine initialization."""
        self.assertIsNotNone(self.analytics)
        self.assertEqual(self.analytics.rolling_window_seconds, 60)
        self.assertEqual(self.analytics.update_frequency_seconds, 0.1)
        self.assertIsNotNone(self.analytics.metrics)
        self.assertIsNotNone(self.analytics.kpi_cache)
    
    def test_configuration_loading(self):
        """Test configuration loading from file."""
        config = self.analytics.config
        self.assertEqual(config["rolling_window_seconds"], 60)
        self.assertEqual(config["enable_debug_mode"], True)
        self.assertIn("order_processing", config["categories"])
        self.assertIn("robot_performance", config["categories"])
    
    def test_default_configuration(self):
        """Test default configuration when file not found."""
        # Create analytics with non-existent config file
        analytics = AnalyticsEngine("nonexistent.json")
        
        self.assertIsNotNone(analytics.config)
        self.assertEqual(analytics.rolling_window_seconds, 300)  # Default value
        self.assertEqual(analytics.update_frequency_seconds, 1.0)  # Default value
        
        analytics.shutdown()
    
    def test_record_metric(self):
        """Test metric recording functionality."""
        # Record a test metric
        success = self.analytics.record_metric("test_metric", 42.0, "test_category")
        
        self.assertTrue(success)
        
        # Check that metric was stored
        metric_key = "test_category.test_metric"
        self.assertIn(metric_key, self.analytics.metrics)
        self.assertEqual(len(self.analytics.metrics[metric_key]), 1)
        
        # Check metric data
        metric_data = self.analytics.metrics[metric_key][0]
        self.assertEqual(metric_data.name, "test_metric")
        self.assertEqual(metric_data.value, 42.0)
        self.assertEqual(metric_data.metadata, {})
    
    def test_record_metric_with_metadata(self):
        """Test metric recording with metadata."""
        metadata = {"source": "test", "priority": "high"}
        success = self.analytics.record_metric("test_metric", 42.0, "test_category", metadata)
        
        self.assertTrue(success)
        
        metric_key = "test_category.test_metric"
        metric_data = self.analytics.metrics[metric_key][0]
        self.assertEqual(metric_data.metadata, metadata)
    
    def test_record_metric_error_handling(self):
        """Test metric recording error handling."""
        # Test with invalid parameters
        success = self.analytics.record_metric("", -1.0, "")
        
        # Should still succeed due to error handling
        self.assertTrue(success)
    
    def test_get_recent_metrics(self):
        """Test getting recent metrics within time window."""
        # Record metrics at different times
        self.analytics.record_metric("test_metric", 10.0, "test_category")
        time.sleep(0.1)
        self.analytics.record_metric("test_metric", 20.0, "test_category")
        time.sleep(0.1)
        self.analytics.record_metric("test_metric", 30.0, "test_category")
        
        metric_key = "test_category.test_metric"
        recent_metrics = self.analytics._get_recent_metrics(metric_key, window_seconds=0.05)
        
        # Should only get the most recent metric due to time window
        self.assertEqual(len(recent_metrics), 1)
        self.assertEqual(recent_metrics[0].value, 30.0)
    
    def test_kpi_cache_update(self):
        """Test KPI cache update functionality."""
        # Record multiple metrics
        for i in range(5):
            self.analytics.record_metric("test_metric", float(i), "test_category")
        
        metric_key = "test_category.test_metric"
        
        # Check that KPI was calculated
        kpi = self.analytics.get_kpi(metric_key)
        self.assertIsNotNone(kpi)
        self.assertEqual(kpi.name, metric_key)
        self.assertEqual(kpi.value, 2.0)  # Average of 0,1,2,3,4
        self.assertEqual(kpi.unit, "units")
    
    def test_get_kpi(self):
        """Test getting specific KPI."""
        self.analytics.record_metric("test_metric", 42.0, "test_category")
        
        kpi = self.analytics.get_kpi("test_category.test_metric")
        self.assertIsNotNone(kpi)
        self.assertEqual(kpi.value, 42.0)
    
    def test_get_all_kpis(self):
        """Test getting all KPIs."""
        self.analytics.record_metric("metric1", 10.0, "category1")
        self.analytics.record_metric("metric2", 20.0, "category2")
        
        all_kpis = self.analytics.get_all_kpis()
        self.assertEqual(len(all_kpis), 2)
        self.assertIn("category1.metric1", all_kpis)
        self.assertIn("category2.metric2", all_kpis)
    
    def test_get_kpis_by_category(self):
        """Test getting KPIs by category."""
        self.analytics.record_metric("metric1", 10.0, "category1")
        self.analytics.record_metric("metric2", 20.0, "category1")
        self.analytics.record_metric("metric3", 30.0, "category2")
        
        category_kpis = self.analytics.get_kpis_by_category("category1")
        self.assertEqual(len(category_kpis), 2)
        self.assertIn("category1.metric1", category_kpis)
        self.assertIn("category1.metric2", category_kpis)
        self.assertNotIn("category2.metric3", category_kpis)
    
    def test_calculate_orders_per_hour(self):
        """Test orders per hour calculation."""
        # Simulate order completions
        for i in range(10):
            self.analytics.record_metric("order_completed", 1.0, "order_processing")
        
        orders_per_hour = self.analytics.calculate_orders_per_hour()
        
        # Should be approximately 10 orders per hour (10 orders in 1 minute window)
        self.assertGreater(orders_per_hour, 0)
        self.assertLess(orders_per_hour, 1000)  # Reasonable range
    
    def test_calculate_robot_utilization(self):
        """Test robot utilization calculation."""
        # Simulate robot activity
        for i in range(5):
            self.analytics.record_metric("active_time", 10.0, "robot_performance")
            self.analytics.record_metric("total_time", 20.0, "robot_performance")
        
        utilization = self.analytics.calculate_robot_utilization()
        
        # Should be 50% utilization (10/20 * 100)
        self.assertAlmostEqual(utilization, 50.0, delta=1.0)
    
    def test_performance_stats(self):
        """Test performance statistics."""
        import time
        
        # Add a small delay to ensure session duration > 0
        time.sleep(0.01)
        
        # Record some metrics to generate performance data
        for i in range(5):
            self.analytics.record_metric("test_metric", float(i), "test_category")

        stats = self.analytics.get_performance_stats()

        self.assertIn("avg_calculation_time_ms", stats)
        self.assertIn("total_metrics", stats)
        self.assertIn("kpi_count", stats)
        self.assertIn("session_duration_seconds", stats)

        self.assertGreaterEqual(stats["total_metrics"], 5)
        self.assertGreaterEqual(stats["kpi_count"], 1)
        self.assertGreater(stats["session_duration_seconds"], 0)
    
    def test_clear_session_data(self):
        """Test clearing session data."""
        # Record some metrics
        self.analytics.record_metric("test_metric", 42.0, "test_category")
        
        # Verify data exists
        self.assertGreater(len(self.analytics.metrics), 0)
        self.assertGreater(len(self.analytics.kpi_cache), 0)
        
        # Clear session data
        self.analytics.clear_session_data()
        
        # Verify data is cleared
        self.assertEqual(len(self.analytics.metrics), 0)
        self.assertEqual(len(self.analytics.kpi_cache), 0)
    
    def test_export_analytics_data(self):
        """Test analytics data export."""
        # Record some metrics
        self.analytics.record_metric("test_metric", 42.0, "test_category")
        
        # Export data
        export_data = self.analytics.export_analytics_data()
        
        self.assertIn("session_info", export_data)
        self.assertIn("kpis", export_data)
        self.assertIn("performance_stats", export_data)
        
        # Check session info
        session_info = export_data["session_info"]
        self.assertIn("start_time", session_info)
        self.assertIn("duration_seconds", session_info)
        self.assertIn("config", session_info)
        
        # Check KPIs
        kpis = export_data["kpis"]
        self.assertGreater(len(kpis), 0)
    
    def test_set_event_system(self):
        """Test event system integration."""
        success = self.analytics.set_event_system(self.mock_event_system)
        
        self.assertTrue(success)
        self.assertEqual(self.analytics.event_system, self.mock_event_system)
    
    def test_event_handlers(self):
        """Test event handler registration."""
        self.analytics.set_event_system(self.mock_event_system)
        
        # Verify event handlers were registered
        self.mock_event_system.register_handler.assert_called()
        
        # Check that all expected handlers were registered
        expected_events = [
            "order_created", "order_assigned", "order_completed", "order_cancelled",
            "robot_movement", "robot_state_change", "robot_path_update",
            "inventory_update", "item_collected", "performance_metric"
        ]
        
        # Extract event names from the call arguments (first element of each tuple)
        registered_events = [call[0][0] for call in self.mock_event_system.register_handler.call_args_list]
        for event in expected_events:
            self.assertIn(event, registered_events)
    
    def test_order_event_handlers(self):
        """Test order event handlers."""
        # Test order created handler
        event_data = {"order_id": "ORDER_001", "items": ["ITEM_A1", "ITEM_B2"]}
        self.analytics._handle_order_created(event_data)
        
        # Check that metric was recorded
        metric_key = "order_processing.order_created"
        self.assertIn(metric_key, self.analytics.metrics)
        self.assertEqual(len(self.analytics.metrics[metric_key]), 1)
        
        # Test order completed handler with completion time
        event_data = {"order_id": "ORDER_001", "completion_time": 30.5}
        self.analytics._handle_order_completed(event_data)
        
        # Check that completion time metric was recorded
        completion_time_key = "order_processing.order_completion_time"
        self.assertIn(completion_time_key, self.analytics.metrics)
        self.assertEqual(self.analytics.metrics[completion_time_key][0].value, 30.5)
    
    def test_robot_event_handlers(self):
        """Test robot event handlers."""
        # Test robot movement handler
        event_data = {"robot_id": "ROBOT_001", "distance": 15.5}
        self.analytics._handle_robot_movement(event_data)
        
        # Check that movement metric was recorded
        movement_key = "robot_performance.robot_movement"
        self.assertIn(movement_key, self.analytics.metrics)
        
        # Check that distance metric was recorded
        distance_key = "robot_performance.movement_distance"
        self.assertIn(distance_key, self.analytics.metrics)
        self.assertEqual(self.analytics.metrics[distance_key][0].value, 15.5)
        
        # Test robot state change handler
        event_data = {"robot_id": "ROBOT_001", "new_state": "IDLE"}
        self.analytics._handle_robot_state_change(event_data)
        
        # Check that state change metric was recorded
        state_key = "robot_performance.robot_state_change"
        self.assertIn(state_key, self.analytics.metrics)
    
    def test_inventory_event_handlers(self):
        """Test inventory event handlers."""
        # Test inventory update handler
        event_data = {"item_id": "ITEM_A1", "quantity": 95.0}
        self.analytics._handle_inventory_update(event_data)
        
        # Check that inventory update metric was recorded
        update_key = "inventory_management.inventory_update"
        self.assertIn(update_key, self.analytics.metrics)
        
        # Check that stock level metric was recorded
        stock_key = "inventory_management.stock_level"
        self.assertIn(stock_key, self.analytics.metrics)
        self.assertEqual(self.analytics.metrics[stock_key][0].value, 95.0)
    
    def test_performance_metric_handler(self):
        """Test performance metric handler."""
        event_data = {"metric_name": "response_time", "value": 25.5}
        self.analytics._handle_performance_metric(event_data)
        
        # Check that performance metric was recorded
        perf_key = "system_performance.response_time"
        self.assertIn(perf_key, self.analytics.metrics)
        self.assertEqual(self.analytics.metrics[perf_key][0].value, 25.5)
    
    def test_metric_units_and_descriptions(self):
        """Test metric unit and description mapping."""
        # Test order processing metrics
        self.analytics.record_metric("orders_per_hour", 10.0, "order_processing")
        kpi = self.analytics.get_kpi("order_processing.orders_per_hour")
        self.assertEqual(kpi.unit, "orders/hour")
        self.assertIn("Orders completed per hour", kpi.description)
        
        # Test robot performance metrics
        self.analytics.record_metric("utilization", 75.0, "robot_performance")
        kpi = self.analytics.get_kpi("robot_performance.utilization")
        self.assertEqual(kpi.unit, "percentage")
        self.assertIn("Percentage of time robots are active", kpi.description)
        
        # Test system performance metrics
        self.analytics.record_metric("response_time", 50.0, "system_performance")
        kpi = self.analytics.get_kpi("system_performance.response_time")
        self.assertEqual(kpi.unit, "milliseconds")
        self.assertIn("System operation response times", kpi.description)
    
    def test_memory_management(self):
        """Test memory management with large number of metrics."""
        # Record many metrics to test memory management
        for i in range(200):
            self.analytics.record_metric(f"metric_{i}", float(i), "test_category")
        
        # Check that metrics are limited by maxlen
        for metric_key in self.analytics.metrics:
            self.assertLessEqual(len(self.analytics.metrics[metric_key]), 1000)
    
    def test_thread_safety(self):
        """Test thread safety of analytics engine."""
        import threading
        
        def record_metrics():
            for i in range(10):
                self.analytics.record_metric(f"thread_metric_{i}", float(i), "thread_test")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=record_metrics)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all metrics were recorded safely
        total_metrics = sum(len(metrics) for metrics in self.analytics.metrics.values())
        self.assertEqual(total_metrics, 50)  # 5 threads * 10 metrics each


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 