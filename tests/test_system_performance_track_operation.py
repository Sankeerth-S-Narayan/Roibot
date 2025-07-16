"""
Track Operation Isolation Test

This test specifically isolates the track_operation method to identify
exactly where the hanging occurs.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import SystemPerformanceMonitor


def test_track_operation_isolation():
    """Test track_operation method in isolation."""
    print("🚀 Starting Track Operation Isolation Test")
    print("=" * 50)
    
    # Create mock analytics engine
    mock_analytics = Mock(spec=AnalyticsEngine)
    mock_analytics.record_metric = Mock()
    
    print("📝 Creating SystemPerformanceMonitor...")
    
    # Create the monitor
    monitor = SystemPerformanceMonitor(mock_analytics)
    print("✅ SystemPerformanceMonitor initialized successfully")
    
    # Test 1: Track operation without any system metrics collection
    print("\n📈 Test 1: Track Operation (No System Metrics)")
    print("-" * 30)
    
    # Mock the _collect_system_performance_metrics method to do nothing
    original_collect_method = monitor._collect_system_performance_metrics
    
    def mock_collect_metrics():
        print("  🔧 Mocked system metrics collection (doing nothing)")
        return
    
    monitor._collect_system_performance_metrics = mock_collect_metrics
    
    print("  📝 About to call track_operation...")
    start_time = time.time()
    
    # Call track_operation
    monitor.track_operation("test_op_1", 100.0, success=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"  ✅ track_operation completed in {duration:.3f} seconds")
    print(f"  📊 Total operations: {monitor._total_operations}")
    print(f"  📊 Performance data count: {len(monitor.performance_data)}")
    
    # Test 2: Track multiple operations
    print("\n📈 Test 2: Multiple Operations")
    print("-" * 30)
    
    for i in range(3):
        print(f"  📝 Tracking operation {i+2}...")
        start_time = time.time()
        
        monitor.track_operation(f"test_op_{i+2}", 50.0 + i*10, success=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"  ✅ Operation {i+2} completed in {duration:.3f} seconds")
    
    print(f"  📊 Final total operations: {monitor._total_operations}")
    print(f"  📊 Final performance data count: {len(monitor.performance_data)}")
    
    # Test 3: Track failed operations
    print("\n📈 Test 3: Failed Operations")
    print("-" * 30)
    
    for i in range(2):
        print(f"  📝 Tracking failed operation {i+1}...")
        start_time = time.time()
        
        monitor.track_operation(f"failed_op_{i+1}", 200.0, success=False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"  ✅ Failed operation {i+1} completed in {duration:.3f} seconds")
    
    print(f"  📊 Total errors: {monitor._total_errors}")
    
    # Test 4: Check analytics engine calls
    print("\n📈 Test 4: Analytics Engine Calls")
    print("-" * 30)
    
    call_count = mock_analytics.record_metric.call_count
    print(f"  📊 Analytics engine was called {call_count} times")
    
    # Test 5: Check throughput calculation
    print("\n📈 Test 5: Throughput Calculation")
    print("-" * 30)
    
    if monitor.throughput_history:
        latest_throughput = monitor.throughput_history[-1]
        print(f"  📊 Latest throughput: {latest_throughput:.2f} ops/sec")
    
    # Test 6: Check response time calculation
    print("\n📈 Test 6: Response Time Calculation")
    print("-" * 30)
    
    if monitor.response_time_history:
        avg_response_time = sum(monitor.response_time_history) / len(monitor.response_time_history)
        print(f"  📊 Average response time: {avg_response_time:.2f} ms")
    
    # Restore original method
    monitor._collect_system_performance_metrics = original_collect_method
    
    print("\n✅ All track_operation isolation tests completed successfully!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        success = test_track_operation_isolation()
        if success:
            print("\n🎉 Track operation isolation tests passed!")
        else:
            print("\n❌ Some track operation isolation tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 