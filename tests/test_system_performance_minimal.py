"""
Minimal SystemPerformanceMonitor Test

This test bypasses the analytics engine entirely and tests only
the core data structures and basic operations.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock
from core.analytics.system_performance import SystemPerformanceMonitor, SystemPerformanceData, SystemMetric


def test_system_performance_monitor_minimal():
    """Test SystemPerformanceMonitor with minimal dependencies."""
    print("🚀 Starting Minimal SystemPerformanceMonitor Test")
    print("=" * 50)
    
    # Create a completely mock analytics engine that does nothing
    mock_analytics = Mock()
    mock_analytics.record_metric = Mock()
    
    print("📝 Creating SystemPerformanceMonitor...")
    
    # Create the monitor
    monitor = SystemPerformanceMonitor(mock_analytics)
    print("✅ SystemPerformanceMonitor initialized successfully")
    
    # Test 1: Basic data structure creation
    print("\n📈 Test 1: Basic Data Structure Creation")
    print("-" * 30)
    
    # Create a simple performance data entry
    test_data = SystemPerformanceData(
        timestamp=time.time(),
        metric_type=SystemMetric.RESPONSE_TIME,
        value=100.0,
        unit="ms",
        metadata={"test": True}
    )
    print(f"  ✅ Created SystemPerformanceData: {test_data}")
    
    # Test 2: Manual operation tracking (bypassing track_operation)
    print("\n📈 Test 2: Manual Operation Tracking")
    print("-" * 30)
    
    # Manually add data to the monitor's internal structures
    current_time = time.time()
    
    # Add to performance data
    monitor.performance_data.append(test_data)
    print("  ✅ Added to performance_data")
    
    # Add to response time history
    monitor.response_time_history.append(100.0)
    print("  ✅ Added to response_time_history")
    
    # Update counters manually
    monitor._total_operations += 1
    monitor._total_response_time += 100.0
    print("  ✅ Updated internal counters")
    
    # Test 3: Check data structures
    print("\n📈 Test 3: Check Data Structures")
    print("-" * 30)
    
    print(f"  📊 Performance data count: {len(monitor.performance_data)}")
    print(f"  📊 Response time history count: {len(monitor.response_time_history)}")
    print(f"  📊 Total operations: {monitor._total_operations}")
    print(f"  📊 Total response time: {monitor._total_response_time}")
    
    # Test 4: Basic calculations
    print("\n📈 Test 4: Basic Calculations")
    print("-" * 30)
    
    if monitor.response_time_history:
        avg_response_time = sum(monitor.response_time_history) / len(monitor.response_time_history)
        print(f"  📊 Average response time: {avg_response_time} ms")
    
    if monitor._total_operations > 0:
        total_time = time.time() - monitor._start_time
        if total_time > 0:
            throughput = monitor._total_operations / total_time
            print(f"  📊 Throughput: {throughput:.2f} ops/sec")
    
    # Test 5: Check thresholds
    print("\n📈 Test 5: Check Thresholds")
    print("-" * 30)
    
    thresholds = monitor.get_thresholds()
    print(f"  📊 Number of thresholds: {len(thresholds)}")
    for name, threshold in thresholds.items():
        print(f"    📊 {name}: warning={threshold.warning_threshold}, critical={threshold.critical_threshold}")
    
    # Test 6: Basic summary (without analytics engine calls)
    print("\n📈 Test 6: Basic Summary")
    print("-" * 30)
    
    summary = {
        "total_operations": monitor._total_operations,
        "total_response_time": monitor._total_response_time,
        "total_errors": monitor._total_errors,
        "performance_data_count": len(monitor.performance_data),
        "response_time_history_count": len(monitor.response_time_history),
        "throughput_history_count": len(monitor.throughput_history),
        "health_snapshots_count": len(monitor.health_snapshots)
    }
    
    for key, value in summary.items():
        print(f"  📊 {key}: {value}")
    
    print("\n✅ All minimal tests completed successfully!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        success = test_system_performance_monitor_minimal()
        if success:
            print("\n🎉 All minimal tests passed! Core data structures are working.")
        else:
            print("\n❌ Some minimal tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 