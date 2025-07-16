#!/usr/bin/env python3
"""
Standalone Performance Monitor & Data Export Test Script

This script demonstrates and tests the PerformanceMonitor and DataExport functionality
without requiring the full test suite. It provides comprehensive testing of performance
monitoring and data export features.
"""

import sys
import time
import tempfile
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.performance_monitor import PerformanceMonitor, PerformanceMetric
from core.analytics.data_export import DataExport


def create_test_config():
    """Create test configuration for analytics engine."""
    return {
        "rolling_window_seconds": 60,
        "max_metrics_per_category": 1000,
        "calculation_interval_seconds": 5,
        "memory_management": {
            "max_metrics_per_category": 1000,
            "cleanup_interval_seconds": 300
        }
    }


def test_performance_monitor_basic():
    """Test basic performance monitor functionality."""
    print("=== Testing Basic Performance Monitor ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create performance monitor
    performance_monitor = PerformanceMonitor(analytics_engine)
    
    # Test response time tracking
    print("1. Testing response time tracking...")
    performance_monitor.track_response_time("test_operation", 150.5, {"user_id": "test_user"})
    performance_monitor.track_response_time("slow_operation", 1200.0)  # Above threshold
    performance_monitor.track_response_time("fast_operation", 50.0)
    
    # Verify response time tracking
    assert len(performance_monitor.response_times) == 3
    assert performance_monitor._max_response_time == 1200.0
    assert performance_monitor._threshold_exceeded_count == 1
    print("   ✅ Response time tracking successful")
    
    # Test performance summary
    print("2. Testing performance summary...")
    summary = performance_monitor.get_system_performance_summary()
    
    response_stats = summary["response_time_stats"]
    assert response_stats["total_operations"] == 3
    assert response_stats["max_response_time"] == 1200.0
    assert response_stats["threshold_exceeded_count"] == 1
    print("   ✅ Performance summary generated")
    
    # Test performance history
    print("3. Testing performance history...")
    history = performance_monitor.get_performance_history()
    assert len(history) == 3
    
    response_history = performance_monitor.get_performance_history(PerformanceMetric.RESPONSE_TIME)
    assert len(response_history) == 3
    print("   ✅ Performance history retrieved")
    
    print("✅ All basic performance monitor tests passed!")
    return performance_monitor


def test_system_health_monitoring():
    """Test system health monitoring functionality."""
    print("\n=== Testing System Health Monitoring ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create performance monitor
    performance_monitor = PerformanceMonitor(analytics_engine)
    
    # Test healthy system
    print("1. Testing healthy system...")
    health_data = performance_monitor._generate_system_health_data(
        memory_percent=50.0,
        cpu_percent=60.0,
        disk_percent=70.0,
        network_bytes=1000000,
        thread_count=8,
        process_count=10,
        system_load=1.5
    )
    
    assert health_data.is_healthy == True
    assert health_data.health_score == 100.0
    assert len(health_data.alerts) == 0
    print("   ✅ Healthy system detection successful")
    
    # Test unhealthy system
    print("2. Testing unhealthy system...")
    health_data = performance_monitor._generate_system_health_data(
        memory_percent=85.0,  # Above threshold
        cpu_percent=95.0,     # Above threshold
        disk_percent=90.0,    # Above threshold
        network_bytes=1000000,
        thread_count=8,
        process_count=10,
        system_load=1.5
    )
    
    assert health_data.is_healthy == False
    assert health_data.health_score < 100.0
    assert len(health_data.alerts) > 0
    print("   ✅ Unhealthy system detection successful")
    
    # Test health status methods
    print("3. Testing health status methods...")
    performance_monitor.system_health_history.append(health_data)
    
    assert performance_monitor.is_system_healthy() == False
    assert performance_monitor.get_health_score() < 100.0
    assert len(performance_monitor.get_performance_alerts()) > 0
    print("   ✅ Health status methods working")
    
    print("✅ All system health monitoring tests passed!")
    return performance_monitor


def test_data_export_basic():
    """Test basic data export functionality."""
    print("\n=== Testing Basic Data Export ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create data export
    data_export = DataExport(analytics_engine)
    
    # Add test metrics
    analytics_engine.record_metric("test_metric", 100.0, "test_category")
    analytics_engine.record_metric("another_metric", 200.0, "test_category")
    analytics_engine.record_metric("performance_metric", 150.5, "performance", {"user_id": "test_user"})
    
    # Test JSON export
    print("1. Testing JSON export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "test_export")
        result = data_export.export_analytics_data(export_path, 'json')
        
        assert result["format"] == "json"
        assert result["status"] == "success"
        assert result["file_path"].endswith('.json')
        assert result["file_size"] > 0
        assert result["data_points"] > 0
        print("   ✅ JSON export successful")
    
    # Test CSV export
    print("2. Testing CSV export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "test_export")
        result = data_export.export_analytics_data(export_path, 'csv')
        
        assert result["format"] == "csv"
        assert result["status"] == "success"
        assert result["file_path"].endswith('.csv')
        assert result["file_size"] > 0
        assert result["data_points"] > 0
        print("   ✅ CSV export successful")
    
    # Test export formats
    print("3. Testing export formats...")
    formats = data_export.get_export_formats()
    assert "json" in formats
    assert "csv" in formats
    print("   ✅ Export formats retrieved")
    
    print("✅ All basic data export tests passed!")
    return data_export


def test_data_export_advanced():
    """Test advanced data export functionality."""
    print("\n=== Testing Advanced Data Export ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create data export
    data_export = DataExport(analytics_engine)
    
    # Test performance data export
    print("1. Testing performance data export...")
    performance_data = [
        {"timestamp": 1234567890, "metric": "response_time", "value": 150.0},
        {"timestamp": 1234567891, "metric": "memory_usage", "value": 65.5},
        {"timestamp": 1234567892, "metric": "cpu_usage", "value": 45.2}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "performance_export")
        result = data_export.export_performance_data(performance_data, export_path, 'json')
        
        assert result["format"] == "json"
        assert result["status"] == "success"
        print("   ✅ Performance data export successful")
    
    # Test robot analytics export
    print("2. Testing robot analytics export...")
    from unittest.mock import Mock
    
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
    mock_robot_analytics.robots = {"ROBOT_001": Mock()}
    mock_robot_analytics.get_robot_analytics.return_value = {
        "robot_id": "ROBOT_001",
        "total_distance_moved": 75.0
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "robot_export")
        result = data_export.export_robot_analytics(mock_robot_analytics, export_path, 'json')
        
        assert result["format"] == "json"
        assert result["status"] == "success"
        print("   ✅ Robot analytics export successful")
    
    # Test order analytics export
    print("3. Testing order analytics export...")
    mock_order_analytics = Mock()
    mock_order_analytics.get_order_summary.return_value = {
        "total_orders": 50,
        "completed_orders": 45,
        "completion_rate": 90.0
    }
    mock_order_analytics.get_order_history.return_value = [
        {"order_id": "ORDER_001", "status": "completed"}
    ]
    mock_order_analytics.get_queue_analytics.return_value = {
        "queue_length": 5,
        "average_wait_time": 30.5
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "order_export")
        result = data_export.export_order_analytics(mock_order_analytics, export_path, 'json')
        
        assert result["format"] == "json"
        assert result["status"] == "success"
        print("   ✅ Order analytics export successful")
    
    # Test system performance export
    print("4. Testing system performance export...")
    mock_performance_monitor = Mock()
    mock_performance_monitor.get_system_performance_summary.return_value = {
        "response_time_stats": {"average_response_time": 150.0},
        "system_health": {"health_score": 95.0}
    }
    mock_performance_monitor.get_system_health_history.return_value = [
        Mock(timestamp=1234567890, health_score=95.0, is_healthy=True)
    ]
    mock_performance_monitor.get_performance_alerts.return_value = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "system_export")
        result = data_export.export_system_performance(mock_performance_monitor, export_path, 'json')
        
        assert result["format"] == "json"
        assert result["status"] == "success"
        print("   ✅ System performance export successful")
    
    print("✅ All advanced data export tests passed!")
    return data_export


def test_integration():
    """Test integration between performance monitor and data export."""
    print("\n=== Testing Integration ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create performance monitor
    performance_monitor = PerformanceMonitor(analytics_engine)
    
    # Add performance data
    performance_monitor.track_response_time("operation_1", 100.0)
    performance_monitor.track_response_time("operation_2", 200.0)
    performance_monitor.track_response_time("operation_3", 150.0)
    
    # Create data export
    data_export = DataExport(analytics_engine)
    
    # Export all data
    print("1. Testing integrated data export...")
    with tempfile.TemporaryDirectory() as temp_dir:
        result = data_export.export_all_data(temp_dir)
        
        assert result["status"] == "success"
        assert result["total_files"] > 0
        assert len(result["files_exported"]) > 0
        print("   ✅ Integrated data export successful")
    
    # Test threshold updates
    print("2. Testing threshold updates...")
    performance_monitor.update_thresholds(
        memory_threshold=70.0,
        cpu_threshold=80.0,
        response_time_threshold=500.0
    )
    
    assert performance_monitor.memory_threshold == 70.0
    assert performance_monitor.cpu_threshold == 80.0
    assert performance_monitor.response_time_threshold == 500.0
    print("   ✅ Threshold updates successful")
    
    # Test monitoring interval update
    print("3. Testing monitoring interval update...")
    performance_monitor.update_monitoring_interval(10.0)
    assert performance_monitor.monitoring_interval == 10.0
    print("   ✅ Monitoring interval update successful")
    
    print("✅ All integration tests passed!")


def main():
    """Run all performance monitor and data export tests."""
    print("📊 Performance Monitor & Data Export Standalone Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_performance_monitor_basic()
        test_system_health_monitoring()
        test_data_export_basic()
        test_data_export_advanced()
        test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Performance Monitor & Data Export are working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 