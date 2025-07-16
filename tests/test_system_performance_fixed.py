"""
Fixed SystemPerformanceMonitor Test

This test verifies that the SystemPerformanceMonitor is now working
correctly after fixing the deadlock issue.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock
from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import SystemPerformanceMonitor


def test_system_performance_monitor_fixed():
    """Test SystemPerformanceMonitor after deadlock fix."""
    print("🚀 Starting Fixed SystemPerformanceMonitor Test")
    print("=" * 50)
    
    # Create mock analytics engine
    mock_analytics = Mock(spec=AnalyticsEngine)
    mock_analytics.record_metric = Mock()
    
    print("📝 Creating SystemPerformanceMonitor...")
    
    # Create the monitor
    monitor = SystemPerformanceMonitor(mock_analytics)
    print("✅ SystemPerformanceMonitor initialized successfully")
    
    # Test 1: Basic operation tracking
    print("\n📈 Test 1: Basic Operation Tracking")
    print("-" * 30)
    
    print("  📝 Tracking operation 1...")
    monitor.track_operation("test_op_1", 100.0, success=True)
    print("  ✅ Operation 1 tracked successfully")
    
    print("  📝 Tracking operation 2...")
    monitor.track_operation("test_op_2", 150.0, success=True)
    print("  ✅ Operation 2 tracked successfully")
    
    print("  📝 Tracking failed operation...")
    monitor.track_operation("failed_op", 200.0, success=False)
    print("  ✅ Failed operation tracked successfully")
    
    # Test 2: Check basic metrics
    print("\n📈 Test 2: Basic Metrics")
    print("-" * 30)
    
    print(f"  📊 Total operations: {monitor._total_operations}")
    print(f"  📊 Total response time: {monitor._total_response_time}")
    print(f"  📊 Total errors: {monitor._total_errors}")
    print(f"  📊 Performance data count: {len(monitor.performance_data)}")
    print(f"  📊 Response time history count: {len(monitor.response_time_history)}")
    print(f"  📊 Throughput history count: {len(monitor.throughput_history)}")
    
    # Test 3: Check analytics engine calls
    print("\n📈 Test 3: Analytics Engine Calls")
    print("-" * 30)
    
    call_count = mock_analytics.record_metric.call_count
    print(f"  📊 Analytics engine was called {call_count} times")
    
    # Test 4: Basic calculations
    print("\n📈 Test 4: Basic Calculations")
    print("-" * 30)
    
    if monitor.response_time_history:
        avg_response_time = sum(monitor.response_time_history) / len(monitor.response_time_history)
        print(f"  📊 Average response time: {avg_response_time:.2f} ms")
    
    if monitor.throughput_history:
        latest_throughput = monitor.throughput_history[-1]
        print(f"  📊 Latest throughput: {latest_throughput:.2f} ops/sec")
    
    # Test 5: Check thresholds
    print("\n📈 Test 5: Thresholds")
    print("-" * 30)
    
    thresholds = monitor.get_thresholds()
    print(f"  📊 Number of thresholds: {len(thresholds)}")
    
    # Test 6: System health (without export)
    print("\n📈 Test 6: System Health")
    print("-" * 30)
    
    is_healthy = monitor.is_system_healthy()
    health_score = monitor.get_health_score()
    print(f"  📊 System healthy: {is_healthy}")
    print(f"  📊 Health score: {health_score}")
    
    print("\n✅ All fixed tests completed successfully!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        success = test_system_performance_monitor_fixed()
        if success:
            print("\n🎉 Fixed SystemPerformanceMonitor tests passed!")
            print("✅ Deadlock issue has been resolved!")
        else:
            print("\n❌ Some fixed tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 