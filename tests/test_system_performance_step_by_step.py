"""
Step-by-Step Track Operation Test

This test breaks down the track_operation method step by step
to identify exactly where the hanging occurs.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock
from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import SystemPerformanceMonitor, SystemPerformanceData, SystemMetric


def test_track_operation_step_by_step():
    """Test track_operation method step by step."""
    print("🚀 Starting Step-by-Step Track Operation Test")
    print("=" * 50)
    
    # Create mock analytics engine
    mock_analytics = Mock(spec=AnalyticsEngine)
    mock_analytics.record_metric = Mock()
    
    print("📝 Creating SystemPerformanceMonitor...")
    
    # Create the monitor
    monitor = SystemPerformanceMonitor(mock_analytics)
    print("✅ SystemPerformanceMonitor initialized successfully")
    
    # Test 1: Manual step-by-step execution
    print("\n📈 Test 1: Manual Step-by-Step Execution")
    print("-" * 30)
    
    operation_name = "test_op_1"
    response_time_ms = 100.0
    success = True
    metadata = None
    
    print("  📝 Step 1: Acquiring lock...")
    start_time = time.time()
    
    with monitor._lock:
        print(f"  ✅ Lock acquired in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 2: Getting current time...")
        start_time = time.time()
        current_time = time.time()
        print(f"  ✅ Current time: {current_time:.3f} seconds")
        
        print("  📝 Step 3: Creating SystemPerformanceData...")
        start_time = time.time()
        
        performance_data = SystemPerformanceData(
            timestamp=current_time,
            metric_type=SystemMetric.RESPONSE_TIME,
            value=response_time_ms,
            unit="ms",
            metadata={
                "operation": operation_name,
                "success": success,
                **(metadata or {})
            }
        )
        print(f"  ✅ SystemPerformanceData created in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 4: Appending to performance_data...")
        start_time = time.time()
        monitor.performance_data.append(performance_data)
        print(f"  ✅ Appended to performance_data in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 5: Appending to response_time_history...")
        start_time = time.time()
        monitor.response_time_history.append(response_time_ms)
        print(f"  ✅ Appended to response_time_history in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 6: Updating counters...")
        start_time = time.time()
        monitor._total_operations += 1
        monitor._total_response_time += response_time_ms
        print(f"  ✅ Counters updated in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 7: Handling success/failure...")
        start_time = time.time()
        if not success:
            monitor._total_errors += 1
            monitor.error_count_history.append(1)
        else:
            monitor.error_count_history.append(0)
        print(f"  ✅ Success/failure handled in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 8: Calculating average response time...")
        start_time = time.time()
        if monitor.response_time_history:
            # Use manual calculation instead of statistics.mean()
            avg_response_time = sum(monitor.response_time_history) / len(monitor.response_time_history)
            print(f"  ✅ Average response time calculated: {avg_response_time:.2f} ms")
        else:
            avg_response_time = 0.0
            print("  ✅ No response time history, using 0.0")
        print(f"  ✅ Average calculation completed in {time.time() - start_time:.3f} seconds")
        
        print("  📝 Step 9: Calling analytics.record_metric...")
        start_time = time.time()
        try:
            monitor.analytics.record_metric("system_response_time", avg_response_time, "system_performance")
            print(f"  ✅ Analytics call completed in {time.time() - start_time:.3f} seconds")
        except Exception as e:
            print(f"  ❌ Analytics call failed: {e}")
        
        print("  📝 Step 10: Calling _update_throughput_metrics_simple...")
        start_time = time.time()
        try:
            monitor._update_throughput_metrics_simple()
            print(f"  ✅ Throughput update completed in {time.time() - start_time:.3f} seconds")
        except Exception as e:
            print(f"  ❌ Throughput update failed: {e}")
        
        print("  📝 Step 11: Calling _cleanup_old_data...")
        start_time = time.time()
        try:
            monitor._cleanup_old_data()
            print(f"  ✅ Cleanup completed in {time.time() - start_time:.3f} seconds")
        except Exception as e:
            print(f"  ❌ Cleanup failed: {e}")
    
    print("  ✅ All steps completed successfully!")
    
    # Test 2: Check results
    print("\n📈 Test 2: Check Results")
    print("-" * 30)
    
    print(f"  📊 Total operations: {monitor._total_operations}")
    print(f"  📊 Total response time: {monitor._total_response_time}")
    print(f"  📊 Performance data count: {len(monitor.performance_data)}")
    print(f"  📊 Response time history count: {len(monitor.response_time_history)}")
    print(f"  📊 Throughput history count: {len(monitor.throughput_history)}")
    print(f"  📊 Analytics engine calls: {mock_analytics.record_metric.call_count}")
    
    print("\n✅ All step-by-step tests completed successfully!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        success = test_track_operation_step_by_step()
        if success:
            print("\n🎉 Step-by-step tests passed!")
        else:
            print("\n❌ Some step-by-step tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 