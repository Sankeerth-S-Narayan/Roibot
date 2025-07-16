"""
Unit tests for PerformanceMonitor module.

Tests performance monitoring functionality including response time tracking,
system metrics collection, health scoring, and alerting capabilities.
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.performance_monitor import PerformanceMonitor, PerformanceMetric, PerformanceData, SystemHealthData


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor class."""
    
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
        
        # Create performance monitor
        self.performance_monitor = PerformanceMonitor(self.analytics_engine)
        
        # Clear any existing metrics to start fresh
        self.analytics_engine.clear_session_data()
    
    def tearDown(self):
        """Clean up after tests."""
        self.performance_monitor.clear_performance_data()
        self.analytics_engine.shutdown()
    
    def test_initialization(self):
        """Test PerformanceMonitor initialization."""
        self.assertIsNotNone(self.performance_monitor.analytics)
        self.assertEqual(len(self.performance_monitor.performance_data), 0)
        self.assertEqual(len(self.performance_monitor.system_health_history), 0)
        self.assertEqual(len(self.performance_monitor.response_times), 0)
        self.assertEqual(len(self.performance_monitor.memory_usage_history), 0)
        self.assertEqual(len(self.performance_monitor.cpu_usage_history), 0)
        
        # Check thresholds
        self.assertEqual(self.performance_monitor.memory_threshold, 80.0)
        self.assertEqual(self.performance_monitor.cpu_threshold, 90.0)
        self.assertEqual(self.performance_monitor.disk_threshold, 85.0)
        self.assertEqual(self.performance_monitor.response_time_threshold, 1000.0)
        
        # Check internal counters
        self.assertEqual(self.performance_monitor._total_response_time, 0.0)
        self.assertEqual(self.performance_monitor._max_response_time, 0.0)
        self.assertEqual(self.performance_monitor._threshold_exceeded_count, 0)
        self.assertEqual(self.performance_monitor._total_alerts, 0)
    
    def test_track_response_time(self):
        """Test response time tracking."""
        operation_name = "test_operation"
        response_time_ms = 150.5
        metadata = {"user_id": "test_user", "session_id": "test_session"}
        
        self.performance_monitor.track_response_time(operation_name, response_time_ms, metadata)
        
        # Check performance data was recorded
        self.assertEqual(len(self.performance_monitor.performance_data), 1)
        performance_data = self.performance_monitor.performance_data[0]
        self.assertEqual(performance_data.metric_type, PerformanceMetric.RESPONSE_TIME)
        self.assertEqual(performance_data.value, response_time_ms)
        self.assertEqual(performance_data.unit, "ms")
        self.assertEqual(performance_data.metadata["operation"], operation_name)
        self.assertEqual(performance_data.metadata["user_id"], "test_user")
        
        # Check response times list
        self.assertEqual(len(self.performance_monitor.response_times), 1)
        self.assertEqual(self.performance_monitor.response_times[0], response_time_ms)
        
        # Check internal counters
        self.assertEqual(self.performance_monitor._total_response_time, response_time_ms)
        self.assertEqual(self.performance_monitor._max_response_time, response_time_ms)
        self.assertEqual(self.performance_monitor._threshold_exceeded_count, 0)
    
    def test_track_response_time_threshold_exceeded(self):
        """Test response time tracking when threshold is exceeded."""
        operation_name = "slow_operation"
        response_time_ms = 1500.0  # Above 1000ms threshold
        
        self.performance_monitor.track_response_time(operation_name, response_time_ms)
        
        # Check threshold exceeded count
        self.assertEqual(self.performance_monitor._threshold_exceeded_count, 1)
        self.assertEqual(self.performance_monitor._max_response_time, response_time_ms)
    
    def test_multiple_response_times(self):
        """Test tracking multiple response times."""
        response_times = [100.0, 200.0, 150.0, 300.0, 250.0]
        
        for i, response_time in enumerate(response_times):
            self.performance_monitor.track_response_time(f"operation_{i}", response_time)
        
        # Check all response times were recorded
        self.assertEqual(len(self.performance_monitor.response_times), 5)
        self.assertEqual(self.performance_monitor.response_times, response_times)
        
        # Check max response time
        self.assertEqual(self.performance_monitor._max_response_time, 300.0)
        
        # Check total response time
        expected_total = sum(response_times)
        self.assertEqual(self.performance_monitor._total_response_time, expected_total)
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    @patch('psutil.pids')
    @patch('psutil.cpu_count')
    def test_collect_system_metrics(self, mock_cpu_count, mock_pids, mock_net_io, 
                                  mock_disk_usage, mock_cpu_percent, mock_virtual_memory):
        """Test system metrics collection."""
        # Mock system metrics
        mock_virtual_memory.return_value.percent = 65.5
        mock_cpu_percent.return_value = 45.2
        mock_disk_usage.return_value.percent = 72.8
        mock_net_io.return_value.bytes_sent = 1000000
        mock_net_io.return_value.bytes_recv = 2000000
        mock_pids.return_value = [1, 2, 3, 4, 5]  # 5 processes
        mock_cpu_count.return_value = 8  # 8 threads
        
        self.performance_monitor._collect_system_metrics()
        
        # Check that metrics were recorded
        memory_kpi = self.analytics_engine.get_kpi("system_performance.system_memory_usage")
        cpu_kpi = self.analytics_engine.get_kpi("system_performance.system_cpu_utilization")
        disk_kpi = self.analytics_engine.get_kpi("system_performance.system_disk_usage")
        network_kpi = self.analytics_engine.get_kpi("system_performance.system_network_io")
        thread_kpi = self.analytics_engine.get_kpi("system_performance.system_thread_count")
        process_kpi = self.analytics_engine.get_kpi("system_performance.system_process_count")
        
        # Verify metrics were recorded (values will be from mocks)
        self.assertIsNotNone(memory_kpi)
        self.assertIsNotNone(cpu_kpi)
        self.assertIsNotNone(disk_kpi)
        self.assertIsNotNone(network_kpi)
        self.assertIsNotNone(thread_kpi)
        self.assertIsNotNone(process_kpi)
        
        # Check history was updated
        self.assertEqual(len(self.performance_monitor.memory_usage_history), 1)
        self.assertEqual(len(self.performance_monitor.cpu_usage_history), 1)
        self.assertEqual(len(self.performance_monitor.system_health_history), 1)
    
    def test_generate_system_health_data_healthy(self):
        """Test system health data generation for healthy system."""
        health_data = self.performance_monitor._generate_system_health_data(
            memory_percent=50.0,
            cpu_percent=60.0,
            disk_percent=70.0,
            network_bytes=1000000,
            thread_count=8,
            process_count=10,
            system_load=1.5
        )
        
        # Check health data
        self.assertEqual(health_data.memory_percent, 50.0)
        self.assertEqual(health_data.cpu_percent, 60.0)
        self.assertEqual(health_data.disk_usage_percent, 70.0)
        self.assertEqual(health_data.network_io_bytes, 1000000)
        self.assertEqual(health_data.thread_count, 8)
        self.assertEqual(health_data.process_count, 10)
        self.assertEqual(health_data.system_load, 1.5)
        self.assertTrue(health_data.is_healthy)
        self.assertEqual(health_data.health_score, 100.0)
        self.assertEqual(len(health_data.alerts), 0)
    
    def test_generate_system_health_data_unhealthy(self):
        """Test system health data generation for unhealthy system."""
        health_data = self.performance_monitor._generate_system_health_data(
            memory_percent=85.0,  # Above 80% threshold
            cpu_percent=95.0,     # Above 90% threshold
            disk_percent=90.0,    # Above 85% threshold
            network_bytes=1000000,
            thread_count=8,
            process_count=10,
            system_load=1.5
        )
        
        # Check health data
        self.assertFalse(health_data.is_healthy)
        self.assertLess(health_data.health_score, 100.0)
        self.assertGreater(len(health_data.alerts), 0)
        
        # Check alerts
        alert_texts = [alert.lower() for alert in health_data.alerts]
        self.assertTrue(any("memory" in alert for alert in alert_texts))
        self.assertTrue(any("cpu" in alert for alert in alert_texts))
        self.assertTrue(any("disk" in alert for alert in alert_texts))
    
    def test_get_system_performance_summary(self):
        """Test system performance summary generation."""
        # Add some performance data
        self.performance_monitor.track_response_time("test_op_1", 100.0)
        self.performance_monitor.track_response_time("test_op_2", 200.0)
        self.performance_monitor.track_response_time("test_op_3", 150.0)
        
        # Mock system metrics collection
        with patch.object(self.performance_monitor, '_collect_system_metrics'):
            self.performance_monitor._collect_system_metrics()
        
        summary = self.performance_monitor.get_system_performance_summary()
        
        # Check response time stats
        response_stats = summary["response_time_stats"]
        self.assertEqual(response_stats["average_response_time"], 150.0)
        self.assertEqual(response_stats["max_response_time"], 200.0)
        self.assertEqual(response_stats["min_response_time"], 100.0)
        self.assertEqual(response_stats["total_operations"], 3)
        self.assertEqual(response_stats["threshold_exceeded_count"], 0)
        
        # Check system resources exist
        self.assertIn("system_resources", summary)
        self.assertIn("system_health", summary)
    
    def test_get_performance_history(self):
        """Test performance history retrieval."""
        # Add some performance data
        self.performance_monitor.track_response_time("test_op_1", 100.0)
        self.performance_monitor.track_response_time("test_op_2", 200.0)
        
        # Get all performance history
        history = self.performance_monitor.get_performance_history()
        self.assertEqual(len(history), 2)
        
        # Get response time history only
        response_history = self.performance_monitor.get_performance_history(
            PerformanceMetric.RESPONSE_TIME
        )
        self.assertEqual(len(response_history), 2)
        
        # Get limited history
        limited_history = self.performance_monitor.get_performance_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_get_system_health_history(self):
        """Test system health history retrieval."""
        print(f"DEBUG: Initial health history length: {len(self.performance_monitor.system_health_history)}")
        
        # Mock the actual system metrics collection
        with patch('psutil.virtual_memory') as mock_memory:
            with patch('psutil.cpu_percent') as mock_cpu:
                with patch('psutil.disk_usage') as mock_disk:
                    with patch('psutil.net_io_counters') as mock_net:
                        with patch('psutil.pids') as mock_pids:
                            with patch('psutil.cpu_count') as mock_cpu_count:
                                # Set up mock values
                                mock_memory.return_value.percent = 50.0
                                mock_cpu.return_value = 30.0
                                mock_disk.return_value.percent = 60.0
                                mock_net.return_value.bytes_sent = 1000
                                mock_net.return_value.bytes_recv = 2000
                                mock_pids.return_value = [1, 2, 3, 4, 5]
                                mock_cpu_count.return_value = 8
                                
                                print("DEBUG: About to call _collect_system_metrics")
                                # Call the actual method
                                self.performance_monitor._collect_system_metrics()
                                print(f"DEBUG: After first call, health history length: {len(self.performance_monitor.system_health_history)}")
                                self.performance_monitor._collect_system_metrics()
                                print(f"DEBUG: After second call, health history length: {len(self.performance_monitor.system_health_history)}")
        
        # Get health history
        health_history = self.performance_monitor.get_system_health_history()
        print(f"DEBUG: Final health history length: {len(health_history)}")
        self.assertGreater(len(health_history), 0)
        
        # Get limited history
        limited_history = self.performance_monitor.get_system_health_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_get_performance_alerts(self):
        """Test performance alerts retrieval."""
        print(f"DEBUG: Initial alerts count: {len(self.performance_monitor.get_performance_alerts())}")
        print(f"DEBUG: Initial health history length: {len(self.performance_monitor.system_health_history)}")
        
        # Initially no alerts
        alerts = self.performance_monitor.get_performance_alerts()
        self.assertEqual(len(alerts), 0)
        
        # Mock unhealthy system
        with patch('psutil.virtual_memory') as mock_memory:
            with patch('psutil.cpu_percent') as mock_cpu:
                with patch('psutil.disk_usage') as mock_disk:
                    with patch('psutil.net_io_counters') as mock_net:
                        with patch('psutil.pids') as mock_pids:
                            with patch('psutil.cpu_count') as mock_cpu_count:
                                # Set up mock values for unhealthy system
                                mock_memory.return_value.percent = 85.0
                                mock_cpu.return_value = 95.0
                                mock_disk.return_value.percent = 90.0
                                mock_net.return_value.bytes_sent = 1000
                                mock_net.return_value.bytes_recv = 2000
                                mock_pids.return_value = [1, 2, 3, 4, 5]
                                mock_cpu_count.return_value = 8
                                
                                print("DEBUG: About to call _collect_system_metrics for alerts test")
                                # Call the actual method
                                self.performance_monitor._collect_system_metrics()
                                print(f"DEBUG: After call, health history length: {len(self.performance_monitor.system_health_history)}")
                                if self.performance_monitor.system_health_history:
                                    print(f"DEBUG: Latest health data alerts: {self.performance_monitor.system_health_history[-1].alerts}")
        
        # Should have alerts now
        alerts = self.performance_monitor.get_performance_alerts()
        print(f"DEBUG: Final alerts count: {len(alerts)}")
        print(f"DEBUG: Final alerts: {alerts}")
        self.assertGreater(len(alerts), 0)
    
    def test_is_system_healthy(self):
        """Test system health status checking."""
        print(f"DEBUG: Initial system healthy: {self.performance_monitor.is_system_healthy()}")
        print(f"DEBUG: Initial health history length: {len(self.performance_monitor.system_health_history)}")
        
        # Initially healthy
        self.assertTrue(self.performance_monitor.is_system_healthy())
        
        # Mock unhealthy system
        with patch('psutil.virtual_memory') as mock_memory:
            with patch('psutil.cpu_percent') as mock_cpu:
                with patch('psutil.disk_usage') as mock_disk:
                    with patch('psutil.net_io_counters') as mock_net:
                        with patch('psutil.pids') as mock_pids:
                            with patch('psutil.cpu_count') as mock_cpu_count:
                                # Set up mock values for unhealthy system
                                mock_memory.return_value.percent = 85.0
                                mock_cpu.return_value = 95.0
                                mock_disk.return_value.percent = 90.0
                                mock_net.return_value.bytes_sent = 1000
                                mock_net.return_value.bytes_recv = 2000
                                mock_pids.return_value = [1, 2, 3, 4, 5]
                                mock_cpu_count.return_value = 8
                                
                                print("DEBUG: About to call _collect_system_metrics for health test")
                                # Call the actual method
                                self.performance_monitor._collect_system_metrics()
                                print(f"DEBUG: After call, health history length: {len(self.performance_monitor.system_health_history)}")
                                if self.performance_monitor.system_health_history:
                                    latest_health = self.performance_monitor.system_health_history[-1]
                                    print(f"DEBUG: Latest health data - is_healthy: {latest_health.is_healthy}, score: {latest_health.health_score}, alerts: {latest_health.alerts}")
        
        # Should be unhealthy now
        final_health = self.performance_monitor.is_system_healthy()
        print(f"DEBUG: Final system healthy: {final_health}")
        self.assertFalse(final_health)
    
    def test_get_health_score(self):
        """Test health score retrieval."""
        print(f"DEBUG: Initial health score: {self.performance_monitor.get_health_score()}")
        print(f"DEBUG: Initial health history length: {len(self.performance_monitor.system_health_history)}")
        
        # Initially 100
        self.assertEqual(self.performance_monitor.get_health_score(), 100.0)
        
        # Mock unhealthy system
        with patch('psutil.virtual_memory') as mock_memory:
            with patch('psutil.cpu_percent') as mock_cpu:
                with patch('psutil.disk_usage') as mock_disk:
                    with patch('psutil.net_io_counters') as mock_net:
                        with patch('psutil.pids') as mock_pids:
                            with patch('psutil.cpu_count') as mock_cpu_count:
                                # Set up mock values for unhealthy system
                                mock_memory.return_value.percent = 85.0
                                mock_cpu.return_value = 95.0
                                mock_disk.return_value.percent = 90.0
                                mock_net.return_value.bytes_sent = 1000
                                mock_net.return_value.bytes_recv = 2000
                                mock_pids.return_value = [1, 2, 3, 4, 5]
                                mock_cpu_count.return_value = 8
                                
                                print("DEBUG: About to call _collect_system_metrics for score test")
                                # Call the actual method
                                self.performance_monitor._collect_system_metrics()
                                print(f"DEBUG: After call, health history length: {len(self.performance_monitor.system_health_history)}")
                                if self.performance_monitor.system_health_history:
                                    latest_health = self.performance_monitor.system_health_history[-1]
                                    print(f"DEBUG: Latest health data - score: {latest_health.health_score}, alerts: {latest_health.alerts}")
        
        # Should be less than 100
        final_score = self.performance_monitor.get_health_score()
        print(f"DEBUG: Final health score: {final_score}")
        self.assertLess(final_score, 100.0)
    
    def test_update_monitoring_interval(self):
        """Test monitoring interval update."""
        original_interval = self.performance_monitor.monitoring_interval
        new_interval = 10.0
        
        self.performance_monitor.update_monitoring_interval(new_interval)
        self.assertEqual(self.performance_monitor.monitoring_interval, new_interval)
    
    def test_update_thresholds(self):
        """Test threshold updates."""
        # Update all thresholds
        self.performance_monitor.update_thresholds(
            memory_threshold=70.0,
            cpu_threshold=80.0,
            disk_threshold=75.0,
            response_time_threshold=500.0
        )
        
        self.assertEqual(self.performance_monitor.memory_threshold, 70.0)
        self.assertEqual(self.performance_monitor.cpu_threshold, 80.0)
        self.assertEqual(self.performance_monitor.disk_threshold, 75.0)
        self.assertEqual(self.performance_monitor.response_time_threshold, 500.0)
        
        # Update only some thresholds
        self.performance_monitor.update_thresholds(memory_threshold=60.0)
        self.assertEqual(self.performance_monitor.memory_threshold, 60.0)
        self.assertEqual(self.performance_monitor.cpu_threshold, 80.0)  # Unchanged
    
    def test_cleanup_old_data(self):
        """Test old data cleanup functionality."""
        # Add data beyond max history size
        max_size = self.performance_monitor.max_history_size
        for i in range(max_size + 10):
            self.performance_monitor.track_response_time(f"op_{i}", 100.0)
        
        # Check that data was cleaned up
        self.assertLessEqual(len(self.performance_monitor.performance_data), max_size)
        self.assertLessEqual(len(self.performance_monitor.response_times), max_size)
    
    def test_clear_performance_data(self):
        """Test performance data clearing."""
        # Add some data
        self.performance_monitor.track_response_time("test_op", 100.0)
        
        # Verify data exists
        self.assertEqual(len(self.performance_monitor.performance_data), 1)
        self.assertEqual(len(self.performance_monitor.response_times), 1)
        
        # Clear data
        self.performance_monitor.clear_performance_data()
        
        # Verify data is cleared
        self.assertEqual(len(self.performance_monitor.performance_data), 0)
        self.assertEqual(len(self.performance_monitor.response_times), 0)
        self.assertEqual(len(self.performance_monitor.system_health_history), 0)
        self.assertEqual(len(self.performance_monitor.memory_usage_history), 0)
        self.assertEqual(len(self.performance_monitor.cpu_usage_history), 0)
        
        # Check internal counters are reset
        self.assertEqual(self.performance_monitor._total_response_time, 0.0)
        self.assertEqual(self.performance_monitor._max_response_time, 0.0)
        self.assertEqual(self.performance_monitor._threshold_exceeded_count, 0)
        self.assertEqual(self.performance_monitor._total_alerts, 0)
    
    def test_start_performance_tracking(self):
        """Test performance tracking start."""
        original_time = self.performance_monitor.last_monitoring_time
        
        # Add a small delay to ensure time difference
        import time
        time.sleep(0.001)
        
        # Start tracking
        self.performance_monitor.start_performance_tracking()
        
        # Check that monitoring time was updated
        self.assertGreater(self.performance_monitor.last_monitoring_time, original_time)
    
    def test_error_handling_in_metrics_collection(self):
        """Test error handling in system metrics collection."""
        # Mock psutil to raise an exception
        with patch('psutil.virtual_memory', side_effect=Exception("Test error")):
            # Should not raise exception
            self.performance_monitor._collect_system_metrics()
            
            # Should continue to work
            self.performance_monitor.track_response_time("test_op", 100.0)
            self.assertEqual(len(self.performance_monitor.response_times), 1)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 