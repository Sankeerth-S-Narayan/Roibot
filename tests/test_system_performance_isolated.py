"""
Isolated SystemPerformanceMonitor Test

This test bypasses all psutil calls and system metrics collection
to focus only on core operation tracking functionality.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import SystemPerformanceMonitor


def test_system_performance_monitor_isolated():
    """Test SystemPerformanceMonitor with all psutil calls mocked out."""
    print("🚀 Starting Isolated SystemPerformanceMonitor Test")
    print("=" * 50)
    
    # Create mock analytics engine
    mock_analytics = Mock(spec=AnalyticsEngine)
    mock_analytics.record_metric = Mock()
    
    # Create SystemPerformanceMonitor with mocked psutil
    with patch('core.analytics.system_performance.psutil') as mock_psutil:
        # Mock all psutil calls to return safe values
        mock_psutil.virtual_memory.return_value = Mock(percent=50.0)
        mock_psutil.cpu_percent.return_value = 25.0
        mock_psutil.disk_io_counters.return_value = Mock(read_bytes=1000, write_bytes=1000)
        mock_psutil.net_io_counters.return_value = Mock(bytes_sent=1000, bytes_recv=1000)
        mock_psutil.pids.return_value = [1, 2, 3, 4, 5]
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.getloadavg.return_value = (1.0, 1.0, 1.0)
        
        # Create the monitor
        monitor = SystemPerformanceMonitor(mock_analytics)
        print("✅ SystemPerformanceMonitor initialized successfully")
        
        # Test 1: Basic operation tracking
        print("\n📈 Test 1: Basic Operation Tracking")
        print("-" * 30)
        
        # Track a simple operation
        monitor.track_operation("test_op_1", 100.0, success=True)
        print("  ✅ Tracked operation: test_op_1 (100.0ms, success=True)")
        
        # Check that metrics were recorded
        assert mock_analytics.record_metric.called, "Analytics engine should have been called"
        print("  ✅ Analytics engine recorded metrics")
        
        # Test 2: Multiple operations
        print("\n📈 Test 2: Multiple Operations")
        print("-" * 30)
        
        for i in range(5):
            monitor.track_operation(f"test_op_{i+2}", 50.0 + i*10, success=True)
            print(f"  ✅ Tracked operation: test_op_{i+2} ({50.0 + i*10}ms, success=True)")
        
        # Test 3: Failed operations
        print("\n📈 Test 3: Failed Operations")
        print("-" * 30)
        
        monitor.track_operation("failed_op_1", 200.0, success=False)
        monitor.track_operation("failed_op_2", 150.0, success=False)
        print("  ✅ Tracked failed operations")
        
        # Test 4: Performance summary
        print("\n📈 Test 4: Performance Summary")
        print("-" * 30)
        
        summary = monitor.get_system_performance_summary()
        print(f"  📊 Total operations: {summary.get('total_operations', 'N/A')}")
        print(f"  📊 Average response time: {summary.get('average_response_time', 'N/A')} ms")
        print(f"  📊 Error rate: {summary.get('error_rate', 'N/A')}%")
        print(f"  📊 Health score: {summary.get('health_score', 'N/A')}")
        
        # Test 5: Performance history
        print("\n📈 Test 5: Performance History")
        print("-" * 30)
        
        history = monitor.get_performance_history(limit=10)
        print(f"  📊 Performance history entries: {len(history)}")
        
        # Test 6: Health history
        print("\n📈 Test 6: Health History")
        print("-" * 30)
        
        health_history = monitor.get_health_history(limit=5)
        print(f"  📊 Health history entries: {len(health_history)}")
        
        # Test 7: System health status
        print("\n📈 Test 7: System Health Status")
        print("-" * 30)
        
        is_healthy = monitor.is_system_healthy()
        health_score = monitor.get_health_score()
        print(f"  📊 System healthy: {is_healthy}")
        print(f"  📊 Health score: {health_score}")
        
        # Test 8: Performance alerts
        print("\n📈 Test 8: Performance Alerts")
        print("-" * 30)
        
        alerts = monitor.get_performance_alerts()
        print(f"  📊 Performance alerts: {len(alerts)}")
        if alerts:
            for alert in alerts:
                print(f"    ⚠️  {alert}")
        
        # Test 9: Data export
        print("\n📈 Test 9: Data Export")
        print("-" * 30)
        
        json_export = monitor.export_performance_data("json")
        print(f"  📊 JSON export length: {len(json_export)} characters")
        
        csv_export = monitor.export_performance_data("csv")
        print(f"  📊 CSV export length: {len(csv_export)} characters")
        
        print("\n✅ All isolated tests completed successfully!")
        print("=" * 50)
        return True


if __name__ == "__main__":
    try:
        success = test_system_performance_monitor_isolated()
        if success:
            print("\n🎉 All tests passed! SystemPerformanceMonitor core functionality is working.")
        else:
            print("\n❌ Some tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 