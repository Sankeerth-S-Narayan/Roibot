"""
Unit tests for SystemPerformanceMonitor class.

Tests comprehensive system performance monitoring functionality including
performance tracking, health monitoring, threshold management, and data export.
"""

import unittest
import time
import json
from unittest.mock import patch, MagicMock
from dataclasses import asdict

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import (
    SystemPerformanceMonitor, SystemMetric, SystemPerformanceData,
    SystemHealthSnapshot, PerformanceThreshold
)


class TestSystemPerformanceMonitor(unittest.TestCase):
    """Test cases for SystemPerformanceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create analytics engine
        self.analytics_engine = AnalyticsEngine()
        
        # Create system performance monitor
        self.system_monitor = SystemPerformanceMonitor(self.analytics_engine)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.analytics_engine.shutdown()
    
    def test_initialization(self):
        """Test SystemPerformanceMonitor initialization."""
        # Check basic attributes
        self.assertIsNotNone(self.system_monitor.analytics)
        self.assertEqual(len(self.system_monitor.performance_data), 0)
        self.assertEqual(len(self.system_monitor.health_snapshots), 0)
        self.assertEqual(len(self.system_monitor.throughput_history), 0)
        self.assertEqual(len(self.system_monitor.response_time_history), 0)
        self.assertEqual(len(self.system_monitor.error_count_history), 0)
        
        # Check thresholds
        self.assertIn("throughput", self.system_monitor.thresholds)
        self.assertIn("response_time", self.system_monitor.thresholds)
        self.assertIn("memory_usage", self.system_monitor.thresholds)
        self.assertIn("cpu_utilization", self.system_monitor.thresholds)
        self.assertIn("error_rate", self.system_monitor.thresholds)
        self.assertIn("system_load", self.system_monitor.thresholds)
        
        # Check counters
        self.assertEqual(self.system_monitor._total_operations, 0)
        self.assertEqual(self.system_monitor._total_response_time, 0.0)
        self.assertEqual(self.system_monitor._total_errors, 0)
    
    def test_track_operation_success(self):
        """Test tracking successful operations."""
        # Track successful operation
        self.system_monitor.track_operation("test_op", 100.0, success=True)
        
        # Check performance data
        self.assertEqual(len(self.system_monitor.performance_data), 1)
        self.assertEqual(self.system_monitor.performance_data[0].metric_type, SystemMetric.RESPONSE_TIME)
        self.assertEqual(self.system_monitor.performance_data[0].value, 100.0)
        self.assertEqual(self.system_monitor.performance_data[0].unit, "ms")
        self.assertEqual(self.system_monitor.performance_data[0].metadata["operation"], "test_op")
        self.assertEqual(self.system_monitor.performance_data[0].metadata["success"], True)
        
        # Check counters
        self.assertEqual(self.system_monitor._total_operations, 1)
        self.assertEqual(self.system_monitor._total_response_time, 100.0)
        self.assertEqual(self.system_monitor._total_errors, 0)
        
        # Check response time history
        self.assertEqual(len(self.system_monitor.response_time_history), 1)
        self.assertEqual(self.system_monitor.response_time_history[0], 100.0)
        
        # Check error count history
        self.assertEqual(len(self.system_monitor.error_count_history), 1)
        self.assertEqual(self.system_monitor.error_count_history[0], 0)
    
    def test_track_operation_failure(self):
        """Test tracking failed operations."""
        # Track failed operation
        self.system_monitor.track_operation("test_op", 200.0, success=False)
        
        # Check performance data
        self.assertEqual(len(self.system_monitor.performance_data), 1)
        self.assertEqual(self.system_monitor.performance_data[0].metadata["success"], False)
        
        # Check counters
        self.assertEqual(self.system_monitor._total_operations, 1)
        self.assertEqual(self.system_monitor._total_response_time, 200.0)
        self.assertEqual(self.system_monitor._total_errors, 1)
        
        # Check error count history
        self.assertEqual(len(self.system_monitor.error_count_history), 1)
        self.assertEqual(self.system_monitor.error_count_history[0], 1)
    
    def test_multiple_operations(self):
        """Test tracking multiple operations."""
        # Track multiple operations
        operations = [
            ("op1", 100.0, True),
            ("op2", 150.0, True),
            ("op3", 200.0, False),
            ("op4", 120.0, True)
        ]
        
        for op_name, response_time, success in operations:
            self.system_monitor.track_operation(op_name, response_time, success)
        
        # Check performance data
        self.assertEqual(len(self.system_monitor.performance_data), 4)
        
        # Check counters
        self.assertEqual(self.system_monitor._total_operations, 4)
        self.assertEqual(self.system_monitor._total_response_time, 570.0)
        self.assertEqual(self.system_monitor._total_errors, 1)
        
        # Check response time history
        self.assertEqual(len(self.system_monitor.response_time_history), 4)
        self.assertEqual(self.system_monitor.response_time_history, [100.0, 150.0, 200.0, 120.0])
        
        # Check error count history
        self.assertEqual(len(self.system_monitor.error_count_history), 4)
        self.assertEqual(self.system_monitor.error_count_history, [0, 0, 1, 0])
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    @patch('psutil.pids')
    @patch('psutil.cpu_count')
    def test_collect_system_performance_metrics(self, mock_cpu_count, mock_pids, 
                                              mock_net_io, mock_disk_io, 
                                              mock_cpu_percent, mock_virtual_memory):
        """Test system performance metrics collection."""
        # Set up mock values
        mock_virtual_memory.return_value.percent = 50.0
        mock_cpu_percent.return_value = 30.0
        mock_disk_io.return_value.read_bytes = 1024 * 1024  # 1MB
        mock_disk_io.return_value.write_bytes = 2048 * 1024  # 2MB
        mock_net_io.return_value.bytes_sent = 512 * 1024  # 512KB
        mock_net_io.return_value.bytes_recv = 1024 * 1024  # 1MB
        mock_pids.return_value = [1, 2, 3, 4, 5]
        mock_cpu_count.return_value = 8
        
        # Add some performance data first
        self.system_monitor.track_operation("test_op", 100.0, success=True)
        
        # Collect metrics
        self.system_monitor._collect_system_performance_metrics()
        
        # Check that health snapshot was created
        self.assertEqual(len(self.system_monitor.health_snapshots), 1)
        
        # Check health snapshot data
        snapshot = self.system_monitor.health_snapshots[0]
        self.assertEqual(snapshot.memory_usage_percent, 50.0)
        self.assertEqual(snapshot.cpu_utilization_percent, 30.0)
        self.assertEqual(snapshot.process_count, 5)
        self.assertEqual(snapshot.thread_count, 8)
        self.assertIsInstance(snapshot.health_score, float)
        self.assertIsInstance(snapshot.is_healthy, bool)
        self.assertIsInstance(snapshot.alerts, list)
    
    def test_generate_health_snapshot_healthy(self):
        """Test health snapshot generation for healthy system."""
        # Generate health snapshot with healthy metrics
        snapshot = self.system_monitor._generate_health_snapshot(
            timestamp=time.time(),
            throughput=150.0,  # Good throughput
            response_time=500.0,  # Good response time
            memory_percent=50.0,  # Good memory usage
            cpu_percent=30.0,  # Good CPU usage
            disk_io=10.0,  # Normal disk I/O
            network_io=5.0,  # Normal network I/O
            error_rate=1.0,  # Low error rate
            system_load=1.0,  # Normal system load
            process_count=10,
            thread_count=16
        )
        
        # Check snapshot data
        self.assertEqual(snapshot.throughput_ops_per_sec, 150.0)
        self.assertEqual(snapshot.average_response_time, 500.0)
        self.assertEqual(snapshot.memory_usage_percent, 50.0)
        self.assertEqual(snapshot.cpu_utilization_percent, 30.0)
        self.assertEqual(snapshot.error_rate_percent, 1.0)
        self.assertEqual(snapshot.process_count, 10)
        self.assertEqual(snapshot.thread_count, 16)
        
        # Should be healthy
        self.assertTrue(snapshot.is_healthy)
        self.assertEqual(len(snapshot.alerts), 0)
        self.assertEqual(snapshot.health_score, 100.0)
    
    def test_generate_health_snapshot_unhealthy(self):
        """Test health snapshot generation for unhealthy system."""
        # Generate health snapshot with unhealthy metrics
        snapshot = self.system_monitor._generate_health_snapshot(
            timestamp=time.time(),
            throughput=30.0,  # Low throughput
            response_time=2500.0,  # High response time
            memory_percent=95.0,  # High memory usage
            cpu_percent=98.0,  # High CPU usage
            disk_io=10.0,  # Normal disk I/O
            network_io=5.0,  # Normal network I/O
            error_rate=15.0,  # High error rate
            system_load=6.0,  # High system load
            process_count=10,
            thread_count=16
        )
        
        # Check snapshot data
        self.assertEqual(snapshot.throughput_ops_per_sec, 30.0)
        self.assertEqual(snapshot.average_response_time, 2500.0)
        self.assertEqual(snapshot.memory_usage_percent, 95.0)
        self.assertEqual(snapshot.cpu_utilization_percent, 98.0)
        self.assertEqual(snapshot.error_rate_percent, 15.0)
        self.assertEqual(snapshot.system_load, 6.0)
        
        # Should be unhealthy
        self.assertFalse(snapshot.is_healthy)
        self.assertGreater(len(snapshot.alerts), 0)
        self.assertLess(snapshot.health_score, 100.0)
    
    def test_get_system_performance_summary(self):
        """Test system performance summary generation."""
        # Add some performance data
        self.system_monitor.track_operation("test_op_1", 100.0, success=True)
        self.system_monitor.track_operation("test_op_2", 200.0, success=True)
        self.system_monitor.track_operation("test_op_3", 150.0, success=False)
        
        # Mock system metrics collection
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            self.system_monitor._collect_system_performance_metrics()
        
        summary = self.system_monitor.get_system_performance_summary()
        
        # Check throughput stats
        throughput_stats = summary["throughput_stats"]
        self.assertIn("current_throughput", throughput_stats)
        self.assertIn("average_throughput", throughput_stats)
        self.assertIn("max_throughput", throughput_stats)
        self.assertIn("min_throughput", throughput_stats)
        
        # Check response time stats
        response_time_stats = summary["response_time_stats"]
        self.assertIn("current_response_time", response_time_stats)
        self.assertIn("average_response_time", response_time_stats)
        self.assertIn("max_response_time", response_time_stats)
        self.assertIn("min_response_time", response_time_stats)
        
        # Check system health
        system_health = summary["system_health"]
        self.assertIn("current_score", system_health)
        self.assertIn("is_healthy", system_health)
        self.assertIn("alerts", system_health)
        self.assertIn("alert_count", system_health)
        
        # Check system resources
        system_resources = summary["system_resources"]
        self.assertIn("memory_usage", system_resources)
        self.assertIn("cpu_utilization", system_resources)
        self.assertIn("disk_io", system_resources)
        self.assertIn("network_io", system_resources)
        self.assertIn("system_load", system_resources)
        self.assertIn("process_count", system_resources)
        self.assertIn("thread_count", system_resources)
        
        # Check performance metrics
        performance_metrics = summary["performance_metrics"]
        self.assertEqual(performance_metrics["total_operations"], 3)
        self.assertEqual(performance_metrics["total_errors"], 1)
        self.assertIn("error_rate", performance_metrics)
        self.assertIn("throughput", performance_metrics)
        self.assertIn("response_time", performance_metrics)
    
    def test_get_performance_history(self):
        """Test performance history retrieval."""
        # Add some performance data
        self.system_monitor.track_operation("test_op_1", 100.0, success=True)
        self.system_monitor.track_operation("test_op_2", 200.0, success=True)
        
        # Get all performance history
        history = self.system_monitor.get_performance_history()
        self.assertEqual(len(history), 2)
        
        # Get response time history only
        response_history = self.system_monitor.get_performance_history(
            SystemMetric.RESPONSE_TIME
        )
        self.assertEqual(len(response_history), 2)
        
        # Get limited history
        limited_history = self.system_monitor.get_performance_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_get_health_history(self):
        """Test health history retrieval."""
        # Mock system metrics collection to generate health data
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            # Mock the actual system metrics collection
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.cpu_percent') as mock_cpu:
                    with patch('psutil.disk_io_counters') as mock_disk:
                        with patch('psutil.net_io_counters') as mock_net:
                            with patch('psutil.pids') as mock_pids:
                                with patch('psutil.cpu_count') as mock_cpu_count:
                                    # Set up mock values
                                    mock_memory.return_value.percent = 50.0
                                    mock_cpu.return_value = 30.0
                                    mock_disk.return_value.read_bytes = 1024 * 1024
                                    mock_disk.return_value.write_bytes = 2048 * 1024
                                    mock_net.return_value.bytes_sent = 512 * 1024
                                    mock_net.return_value.bytes_recv = 1024 * 1024
                                    mock_pids.return_value = [1, 2, 3, 4, 5]
                                    mock_cpu_count.return_value = 8
                                    
                                    # Call the actual method
                                    self.system_monitor._collect_system_performance_metrics()
                                    self.system_monitor._collect_system_performance_metrics()
        
        # Get health history
        health_history = self.system_monitor.get_health_history()
        self.assertGreater(len(health_history), 0)
        
        # Get limited history
        limited_history = self.system_monitor.get_health_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_get_performance_alerts(self):
        """Test performance alerts retrieval."""
        # Initially no alerts
        alerts = self.system_monitor.get_performance_alerts()
        self.assertEqual(len(alerts), 0)
        
        # Mock unhealthy system
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.cpu_percent') as mock_cpu:
                    with patch('psutil.disk_io_counters') as mock_disk:
                        with patch('psutil.net_io_counters') as mock_net:
                            with patch('psutil.pids') as mock_pids:
                                with patch('psutil.cpu_count') as mock_cpu_count:
                                    # Set up mock values for unhealthy system
                                    mock_memory.return_value.percent = 95.0
                                    mock_cpu.return_value = 98.0
                                    mock_disk.return_value.read_bytes = 1024 * 1024
                                    mock_disk.return_value.write_bytes = 2048 * 1024
                                    mock_net.return_value.bytes_sent = 512 * 1024
                                    mock_net.return_value.bytes_recv = 1024 * 1024
                                    mock_pids.return_value = [1, 2, 3, 4, 5]
                                    mock_cpu_count.return_value = 8
                                    
                                    # Call the actual method
                                    self.system_monitor._collect_system_performance_metrics()
        
        # Should have alerts now
        alerts = self.system_monitor.get_performance_alerts()
        self.assertGreater(len(alerts), 0)
    
    def test_is_system_healthy(self):
        """Test system health status checking."""
        # Initially healthy
        self.assertTrue(self.system_monitor.is_system_healthy())
        
        # Mock unhealthy system
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.cpu_percent') as mock_cpu:
                    with patch('psutil.disk_io_counters') as mock_disk:
                        with patch('psutil.net_io_counters') as mock_net:
                            with patch('psutil.pids') as mock_pids:
                                with patch('psutil.cpu_count') as mock_cpu_count:
                                    # Set up mock values for unhealthy system
                                    mock_memory.return_value.percent = 95.0
                                    mock_cpu.return_value = 98.0
                                    mock_disk.return_value.read_bytes = 1024 * 1024
                                    mock_disk.return_value.write_bytes = 2048 * 1024
                                    mock_net.return_value.bytes_sent = 512 * 1024
                                    mock_net.return_value.bytes_recv = 1024 * 1024
                                    mock_pids.return_value = [1, 2, 3, 4, 5]
                                    mock_cpu_count.return_value = 8
                                    
                                    # Call the actual method
                                    self.system_monitor._collect_system_performance_metrics()
        
        # Should be unhealthy now
        self.assertFalse(self.system_monitor.is_system_healthy())
    
    def test_get_health_score(self):
        """Test health score retrieval."""
        # Initially 100
        self.assertEqual(self.system_monitor.get_health_score(), 100.0)
        
        # Mock unhealthy system
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.cpu_percent') as mock_cpu:
                    with patch('psutil.disk_io_counters') as mock_disk:
                        with patch('psutil.net_io_counters') as mock_net:
                            with patch('psutil.pids') as mock_pids:
                                with patch('psutil.cpu_count') as mock_cpu_count:
                                    # Set up mock values for unhealthy system
                                    mock_memory.return_value.percent = 95.0
                                    mock_cpu.return_value = 98.0
                                    mock_disk.return_value.read_bytes = 1024 * 1024
                                    mock_disk.return_value.write_bytes = 2048 * 1024
                                    mock_net.return_value.bytes_sent = 512 * 1024
                                    mock_net.return_value.bytes_recv = 1024 * 1024
                                    mock_pids.return_value = [1, 2, 3, 4, 5]
                                    mock_cpu_count.return_value = 8
                                    
                                    # Call the actual method
                                    self.system_monitor._collect_system_performance_metrics()
        
        # Should be less than 100
        self.assertLess(self.system_monitor.get_health_score(), 100.0)
    
    def test_update_thresholds(self):
        """Test threshold updates."""
        # Update thresholds
        self.system_monitor.update_thresholds(
            throughput=(80.0, 40.0),  # warning, critical
            response_time=(800.0, 1500.0),  # warning, critical
            memory_usage=70.0,  # critical only
            cpu_utilization=75.0  # critical only
        )
        
        # Check updated thresholds
        self.assertEqual(self.system_monitor.thresholds["throughput"].warning_threshold, 80.0)
        self.assertEqual(self.system_monitor.thresholds["throughput"].critical_threshold, 40.0)
        self.assertEqual(self.system_monitor.thresholds["response_time"].warning_threshold, 800.0)
        self.assertEqual(self.system_monitor.thresholds["response_time"].critical_threshold, 1500.0)
        self.assertEqual(self.system_monitor.thresholds["memory_usage"].critical_threshold, 70.0)
        self.assertEqual(self.system_monitor.thresholds["cpu_utilization"].critical_threshold, 75.0)
    
    def test_get_thresholds(self):
        """Test threshold retrieval."""
        thresholds = self.system_monitor.get_thresholds()
        
        # Check that all expected thresholds are present
        self.assertIn("throughput", thresholds)
        self.assertIn("response_time", thresholds)
        self.assertIn("memory_usage", thresholds)
        self.assertIn("cpu_utilization", thresholds)
        self.assertIn("error_rate", thresholds)
        self.assertIn("system_load", thresholds)
        
        # Check that thresholds are PerformanceThreshold objects
        for threshold in thresholds.values():
            self.assertIsInstance(threshold, PerformanceThreshold)
    
    def test_cleanup_old_data(self):
        """Test old data cleanup functionality."""
        # Add data beyond max history size
        max_size = self.system_monitor.max_history_size
        for i in range(max_size + 10):
            self.system_monitor.track_operation(f"op_{i}", 100.0, success=True)
        
        # Check that data was cleaned up
        self.assertLessEqual(len(self.system_monitor.performance_data), max_size)
        self.assertLessEqual(len(self.system_monitor.response_time_history), max_size)
        self.assertLessEqual(len(self.system_monitor.error_count_history), max_size)
    
    def test_clear_performance_data(self):
        """Test performance data clearing."""
        # Add some data
        self.system_monitor.track_operation("test_op", 100.0, success=True)
        
        # Verify data exists
        self.assertEqual(len(self.system_monitor.performance_data), 1)
        self.assertEqual(len(self.system_monitor.response_time_history), 1)
        self.assertEqual(len(self.system_monitor.error_count_history), 1)
        
        # Clear data
        self.system_monitor.clear_performance_data()
        
        # Verify data is cleared
        self.assertEqual(len(self.system_monitor.performance_data), 0)
        self.assertEqual(len(self.system_monitor.response_time_history), 0)
        self.assertEqual(len(self.system_monitor.error_count_history), 0)
        self.assertEqual(len(self.system_monitor.health_snapshots), 0)
        self.assertEqual(len(self.system_monitor.throughput_history), 0)
        
        # Check internal counters are reset
        self.assertEqual(self.system_monitor._total_operations, 0)
        self.assertEqual(self.system_monitor._total_response_time, 0.0)
        self.assertEqual(self.system_monitor._total_errors, 0)
    
    def test_export_performance_data_json(self):
        """Test JSON export functionality."""
        # Add some performance data
        self.system_monitor.track_operation("test_op_1", 100.0, success=True)
        self.system_monitor.track_operation("test_op_2", 200.0, success=False)
        
        # Mock system metrics collection
        with patch.object(self.system_monitor, '_collect_system_performance_metrics'):
            with patch('psutil.virtual_memory') as mock_memory:
                with patch('psutil.cpu_percent') as mock_cpu:
                    with patch('psutil.disk_io_counters') as mock_disk:
                        with patch('psutil.net_io_counters') as mock_net:
                            with patch('psutil.pids') as mock_pids:
                                with patch('psutil.cpu_count') as mock_cpu_count:
                                    # Set up mock values
                                    mock_memory.return_value.percent = 50.0
                                    mock_cpu.return_value = 30.0
                                    mock_disk.return_value.read_bytes = 1024 * 1024
                                    mock_disk.return_value.write_bytes = 2048 * 1024
                                    mock_net.return_value.bytes_sent = 512 * 1024
                                    mock_net.return_value.bytes_recv = 1024 * 1024
                                    mock_pids.return_value = [1, 2, 3, 4, 5]
                                    mock_cpu_count.return_value = 8
                                    
                                    self.system_monitor._collect_system_performance_metrics()
        
        # Export to JSON
        json_data = self.system_monitor.export_performance_data("json")
        
        # Parse JSON and verify structure
        data = json.loads(json_data)
        self.assertIn("export_timestamp", data)
        self.assertIn("performance_data", data)
        self.assertIn("health_snapshots", data)
        self.assertIn("summary", data)
        
        # Check performance data
        self.assertEqual(len(data["performance_data"]), 2)
        self.assertEqual(data["performance_data"][0]["metric_type"], "response_time")
        self.assertEqual(data["performance_data"][0]["value"], 100.0)
        self.assertEqual(data["performance_data"][0]["unit"], "ms")
        
        # Check health snapshots
        self.assertEqual(len(data["health_snapshots"]), 1)
        self.assertIn("health_score", data["health_snapshots"][0])
        self.assertIn("is_healthy", data["health_snapshots"][0])
        self.assertIn("alerts", data["health_snapshots"][0])
    
    def test_export_performance_data_csv(self):
        """Test CSV export functionality."""
        # Add some performance data
        self.system_monitor.track_operation("test_op_1", 100.0, success=True)
        self.system_monitor.track_operation("test_op_2", 200.0, success=False)
        
        # Export to CSV
        csv_data = self.system_monitor.export_performance_data("csv")
        
        # Verify CSV structure
        lines = csv_data.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Header + data
        
        # Check header
        header = lines[0]
        self.assertIn("timestamp", header)
        self.assertIn("metric_type", header)
        self.assertIn("value", header)
        self.assertIn("unit", header)
        self.assertIn("metadata", header)
        
        # Check data rows
        self.assertEqual(len(lines), 3)  # Header + 2 data rows
    
    def test_export_performance_data_invalid_format(self):
        """Test export with invalid format."""
        with self.assertRaises(ValueError):
            self.system_monitor.export_performance_data("invalid_format")
    
    def test_thread_safety(self):
        """Test thread safety of performance monitoring."""
        import threading
        import time
        
        # Create multiple threads that track operations
        def track_operations(thread_id):
            for i in range(10):
                self.system_monitor.track_operation(f"thread_{thread_id}_op_{i}", 100.0 + i, success=True)
                time.sleep(0.001)  # Small delay
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=track_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify data integrity
        self.assertEqual(self.system_monitor._total_operations, 50)  # 5 threads * 10 operations
        self.assertEqual(len(self.system_monitor.performance_data), 50)
        self.assertEqual(len(self.system_monitor.response_time_history), 50)
        self.assertEqual(len(self.system_monitor.error_count_history), 50)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 