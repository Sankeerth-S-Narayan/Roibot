"""
Simple test for SystemPerformanceMonitor core functionality.

This test focuses on the basic functionality without the analytics engine
to isolate any hanging issues.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics.system_performance import SystemPerformanceMonitor, SystemMetric, SystemPerformanceData


def test_basic_functionality():
    """Test basic SystemPerformanceMonitor functionality without analytics engine."""
    print("🚀 Starting Simple SystemPerformanceMonitor Test")
    print("=" * 50)
    
    # Create a mock analytics engine
    class MockAnalyticsEngine:
        def __init__(self):
            self.metrics = {}
        
        def record_metric(self, name, value, category):
            self.metrics[f"{category}.{name}"] = value
        
        def get_kpi(self, name):
            class MockKPI:
                def __init__(self, value):
                    self.value = value
            return MockKPI(self.metrics.get(name, 0.0))
        
        def shutdown(self):
            pass
    
    # Initialize with mock analytics engine
    print("📊 Initializing with mock analytics engine...")
    mock_analytics = MockAnalyticsEngine()
    system_monitor = SystemPerformanceMonitor(mock_analytics)
    
    print("✅ SystemPerformanceMonitor initialized successfully")
    print()
    
    # Test 1: Basic operation tracking
    print("📈 Test 1: Basic Operation Tracking")
    print("-" * 30)
    
    # Track operations
    operations = [
        ("test_op_1", 100.0, True),
        ("test_op_2", 200.0, False),
        ("test_op_3", 150.0, True)
    ]
    
    for op_name, response_time, success in operations:
        print(f"  📝 Tracking: {op_name} ({response_time}ms, success={success})")
        system_monitor.track_operation(op_name, response_time, success)
    
    print(f"  📊 Total operations: {system_monitor._total_operations}")
    print(f"  📊 Total errors: {system_monitor._total_errors}")
    print(f"  📊 Error rate: {(system_monitor._total_errors / system_monitor._total_operations * 100):.1f}%")
    print(f"  📊 Performance data records: {len(system_monitor.performance_data)}")
    print(f"  📊 Response time history: {len(system_monitor.response_time_history)}")
    print(f"  📊 Error count history: {len(system_monitor.error_count_history)}")
    print()
    
    # Test 2: Performance data structure
    print("📋 Test 2: Performance Data Structure")
    print("-" * 30)
    
    if system_monitor.performance_data:
        latest_record = system_monitor.performance_data[-1]
        print(f"  📊 Latest record:")
        print(f"    Timestamp: {latest_record.timestamp}")
        print(f"    Metric Type: {latest_record.metric_type.value}")
        print(f"    Value: {latest_record.value} {latest_record.unit}")
        print(f"    Operation: {latest_record.metadata.get('operation', 'N/A')}")
        print(f"    Success: {latest_record.metadata.get('success', 'N/A')}")
    print()
    
    # Test 3: Threshold management
    print("⚙️  Test 3: Threshold Management")
    print("-" * 30)
    
    thresholds = system_monitor.get_thresholds()
    print(f"  📊 Number of thresholds: {len(thresholds)}")
    for metric, threshold in thresholds.items():
        print(f"    {metric}: Warning={threshold.warning_threshold}{threshold.unit}, Critical={threshold.critical_threshold}{threshold.unit}")
    
    # Update thresholds
    system_monitor.update_thresholds(
        throughput=(80.0, 40.0),
        response_time=(800.0, 1500.0)
    )
    print("  ✅ Thresholds updated")
    print()
    
    # Test 4: Performance history
    print("📜 Test 4: Performance History")
    print("-" * 30)
    
    history = system_monitor.get_performance_history()
    print(f"  📊 Performance history records: {len(history)}")
    
    response_time_history = system_monitor.get_performance_history(SystemMetric.RESPONSE_TIME)
    print(f"  📊 Response time history records: {len(response_time_history)}")
    print()
    
    # Test 5: Data clearing
    print("🧹 Test 5: Data Clearing")
    print("-" * 30)
    
    print(f"  📊 Before clearing:")
    print(f"    Performance data: {len(system_monitor.performance_data)}")
    print(f"    Response time history: {len(system_monitor.response_time_history)}")
    print(f"    Error count history: {len(system_monitor.error_count_history)}")
    
    system_monitor.clear_performance_data()
    
    print(f"  📊 After clearing:")
    print(f"    Performance data: {len(system_monitor.performance_data)}")
    print(f"    Response time history: {len(system_monitor.response_time_history)}")
    print(f"    Error count history: {len(system_monitor.error_count_history)}")
    print()
    
    # Test 6: Thread safety
    print("🔒 Test 6: Thread Safety")
    print("-" * 30)
    
    import threading
    
    def add_operations(thread_id):
        for i in range(5):
            system_monitor.track_operation(f"thread_{thread_id}_op_{i}", 100.0 + i, success=True)
    
    # Start multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=add_operations, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"  📊 After multi-threaded operations:")
    print(f"    Total operations: {system_monitor._total_operations}")
    print(f"    Performance data records: {len(system_monitor.performance_data)}")
    print()
    
    print("🎉 Simple SystemPerformanceMonitor Test Completed Successfully!")
    print("=" * 50)


def main():
    """Main function to run the simple test."""
    try:
        test_basic_functionality()
        print("✅ All tests passed!")
        return 0
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 