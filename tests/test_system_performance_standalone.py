"""
Standalone test script for SystemPerformanceMonitor.

This script demonstrates comprehensive system performance monitoring functionality
including performance tracking, health monitoring, threshold management, and data export.
"""

import time
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.system_performance import SystemPerformanceMonitor


def test_system_performance_monitoring():
    """Demonstrate comprehensive system performance monitoring."""
    print("🚀 Starting SystemPerformanceMonitor Standalone Test")
    print("=" * 60)
    
    # Initialize analytics engine
    print("📊 Initializing Analytics Engine...")
    analytics_engine = AnalyticsEngine()
    
    # Initialize system performance monitor
    print("🔧 Initializing SystemPerformanceMonitor...")
    system_monitor = SystemPerformanceMonitor(analytics_engine)
    
    print("✅ SystemPerformanceMonitor initialized successfully")
    print()
    
    # Test 1: Basic operation tracking
    print("📈 Test 1: Basic Operation Tracking")
    print("-" * 40)
    
    # Track various operations
    operations = [
        ("database_query", 150.0, True),
        ("api_request", 300.0, True),
        ("file_upload", 800.0, False),  # Failed operation
        ("cache_lookup", 50.0, True),
        ("data_processing", 1200.0, True),
        ("network_request", 450.0, True),
        ("database_write", 200.0, False),  # Failed operation
        ("image_processing", 600.0, True)
    ]
    
    for op_name, response_time, success in operations:
        system_monitor.track_operation(op_name, response_time, success)
        print(f"  ✅ Tracked: {op_name} ({response_time}ms, success={success})")
    
    print(f"  📊 Total operations: {system_monitor._total_operations}")
    print(f"  📊 Total errors: {system_monitor._total_errors}")
    print(f"  📊 Error rate: {(system_monitor._total_errors / system_monitor._total_operations * 100):.1f}%")
    print()
    
    # Test 2: System health monitoring
    print("🏥 Test 2: System Health Monitoring")
    print("-" * 40)
    
    # Mock system monitoring to avoid psutil hanging
    from unittest.mock import patch
    
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
                            
                            # Start system monitoring
                            system_monitor.start_system_monitoring()
                            print("  ✅ Started system monitoring")
                            
                            # Get system health
                            health_score = system_monitor.get_health_score()
                            is_healthy = system_monitor.is_system_healthy()
                            alerts = system_monitor.get_performance_alerts()
                            
                            print(f"  📊 Health Score: {health_score:.1f}/100")
                            print(f"  📊 System Healthy: {is_healthy}")
                            print(f"  📊 Active Alerts: {len(alerts)}")
                            
                            if alerts:
                                for alert in alerts:
                                    print(f"    ⚠️  {alert}")
                            else:
                                print("    ✅ No active alerts")
    print()
    
    # Test 3: Performance summary
    print("📋 Test 3: Performance Summary")
    print("-" * 40)
    
    # Mock system metrics for summary
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
                            
                            summary = system_monitor.get_system_performance_summary()
    
    # Display throughput stats
    throughput_stats = summary["throughput_stats"]
    print(f"  📊 Throughput Stats:")
    print(f"    Current: {throughput_stats['current_throughput']:.1f} ops/sec")
    print(f"    Average: {throughput_stats['average_throughput']:.1f} ops/sec")
    print(f"    Max: {throughput_stats['max_throughput']:.1f} ops/sec")
    print(f"    Min: {throughput_stats['min_throughput']:.1f} ops/sec")
    
    # Display response time stats
    response_time_stats = summary["response_time_stats"]
    print(f"  📊 Response Time Stats:")
    print(f"    Current: {response_time_stats['current_response_time']:.1f} ms")
    print(f"    Average: {response_time_stats['average_response_time']:.1f} ms")
    print(f"    Max: {response_time_stats['max_response_time']:.1f} ms")
    print(f"    Min: {response_time_stats['min_response_time']:.1f} ms")
    
    # Display system resources
    system_resources = summary["system_resources"]
    print(f"  📊 System Resources:")
    print(f"    Memory Usage: {system_resources['memory_usage']:.1f}%")
    print(f"    CPU Utilization: {system_resources['cpu_utilization']:.1f}%")
    print(f"    Disk I/O: {system_resources['disk_io']:.1f} MB/s")
    print(f"    Network I/O: {system_resources['network_io']:.1f} MB/s")
    print(f"    System Load: {system_resources['system_load']:.1f}")
    print(f"    Process Count: {system_resources['process_count']}")
    print(f"    Thread Count: {system_resources['thread_count']}")
    print()
    
    # Test 4: Threshold management
    print("⚙️  Test 4: Threshold Management")
    print("-" * 40)
    
    # Get current thresholds
    current_thresholds = system_monitor.get_thresholds()
    print("  📊 Current Thresholds:")
    for metric, threshold in current_thresholds.items():
        print(f"    {metric}: Warning={threshold.warning_threshold}{threshold.unit}, Critical={threshold.critical_threshold}{threshold.unit}")
    
    # Update thresholds
    print("  🔧 Updating thresholds...")
    system_monitor.update_thresholds(
        throughput=(120.0, 60.0),  # More lenient
        response_time=(800.0, 1500.0),  # More lenient
        memory_usage=85.0,  # More lenient
        cpu_utilization=85.0  # More lenient
    )
    
    # Get updated thresholds
    updated_thresholds = system_monitor.get_thresholds()
    print("  📊 Updated Thresholds:")
    for metric, threshold in updated_thresholds.items():
        if metric in ["throughput", "response_time", "memory_usage", "cpu_utilization"]:
            print(f"    {metric}: Warning={threshold.warning_threshold}{threshold.unit}, Critical={threshold.critical_threshold}{threshold.unit}")
    print()
    
    # Test 5: Performance history
    print("📜 Test 5: Performance History")
    print("-" * 40)
    
    # Get performance history
    performance_history = system_monitor.get_performance_history()
    print(f"  📊 Performance History Records: {len(performance_history)}")
    
    if performance_history:
        latest_record = performance_history[-1]
        print(f"  📊 Latest Record:")
        print(f"    Timestamp: {latest_record.timestamp}")
        print(f"    Metric Type: {latest_record.metric_type.value}")
        print(f"    Value: {latest_record.value} {latest_record.unit}")
        print(f"    Operation: {latest_record.metadata.get('operation', 'N/A')}")
        print(f"    Success: {latest_record.metadata.get('success', 'N/A')}")
    
    # Get health history
    health_history = system_monitor.get_health_history()
    print(f"  📊 Health History Records: {len(health_history)}")
    
    if health_history:
        latest_health = health_history[-1]
        print(f"  📊 Latest Health Snapshot:")
        print(f"    Timestamp: {latest_health.timestamp}")
        print(f"    Health Score: {latest_health.health_score:.1f}")
        print(f"    Is Healthy: {latest_health.is_healthy}")
        print(f"    Throughput: {latest_health.throughput_ops_per_sec:.1f} ops/sec")
        print(f"    Response Time: {latest_health.average_response_time:.1f} ms")
        print(f"    Memory Usage: {latest_health.memory_usage_percent:.1f}%")
        print(f"    CPU Utilization: {latest_health.cpu_utilization_percent:.1f}%")
        print(f"    Error Rate: {latest_health.error_rate_percent:.1f}%")
        print(f"    Alerts: {len(latest_health.alerts)}")
    print()
    
    # Test 6: Data export
    print("📤 Test 6: Data Export")
    print("-" * 40)
    
    # Mock system metrics for export
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
                            
                            # Export to JSON
                            print("  📤 Exporting to JSON...")
                            json_data = system_monitor.export_performance_data("json")
    
    # Parse and display export summary
    export_data = json.loads(json_data)
    print(f"  📊 Export Summary:")
    print(f"    Export Timestamp: {export_data['export_timestamp']}")
    print(f"    Performance Records: {len(export_data['performance_data'])}")
    print(f"    Health Snapshots: {len(export_data['health_snapshots'])}")
    print(f"    Summary Included: {'summary' in export_data}")
    
    # Export to CSV
    print("  📤 Exporting to CSV...")
    csv_data = system_monitor.export_performance_data("csv")
    csv_lines = csv_data.strip().split('\n')
    print(f"  📊 CSV Export:")
    print(f"    Total Lines: {len(csv_lines)}")
    print(f"    Header: {csv_lines[0] if csv_lines else 'None'}")
    print(f"    Data Rows: {len(csv_lines) - 1 if len(csv_lines) > 1 else 0}")
    print()
    
    # Test 7: Stress testing
    print("💪 Test 7: Stress Testing")
    print("-" * 40)
    
    # Add many operations quickly
    print("  🔄 Adding 100 operations...")
    start_time = time.time()
    
    for i in range(100):
        system_monitor.track_operation(f"stress_op_{i}", 100.0 + (i % 50), success=(i % 10 != 0))
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"  ✅ Added 100 operations in {processing_time:.3f} seconds")
    print(f"  📊 Operations per second: {100 / processing_time:.1f}")
    print(f"  📊 Total operations: {system_monitor._total_operations}")
    print(f"  📊 Total errors: {system_monitor._total_errors}")
    print(f"  📊 Error rate: {(system_monitor._total_errors / system_monitor._total_operations * 100):.1f}%")
    print()
    
    # Test 8: Cleanup and final summary
    print("🧹 Test 8: Cleanup and Final Summary")
    print("-" * 40)
    
    # Get final summary
    final_summary = system_monitor.get_system_performance_summary()
    
    print("  📊 Final Performance Summary:")
    print(f"    Total Operations: {final_summary['performance_metrics']['total_operations']}")
    print(f"    Total Errors: {final_summary['performance_metrics']['total_errors']}")
    print(f"    Error Rate: {final_summary['performance_metrics']['error_rate']:.1f}%")
    print(f"    Current Throughput: {final_summary['performance_metrics']['throughput']:.1f} ops/sec")
    print(f"    Average Response Time: {final_summary['performance_metrics']['response_time']:.1f} ms")
    print(f"    Health Score: {final_summary['system_health']['current_score']:.1f}/100")
    print(f"    System Healthy: {final_summary['system_health']['is_healthy']}")
    print(f"    Active Alerts: {final_summary['system_health']['alert_count']}")
    
    # Clear data
    print("  🧹 Clearing performance data...")
    system_monitor.clear_performance_data()
    
    # Verify cleanup
    print(f"  ✅ Performance data cleared:")
    print(f"    Performance records: {len(system_monitor.performance_data)}")
    print(f"    Health snapshots: {len(system_monitor.health_snapshots)}")
    print(f"    Throughput history: {len(system_monitor.throughput_history)}")
    print(f"    Response time history: {len(system_monitor.response_time_history)}")
    print(f"    Error count history: {len(system_monitor.error_count_history)}")
    print()
    
    # Cleanup
    print("🔄 Shutting down analytics engine...")
    analytics_engine.shutdown()
    print("✅ Analytics engine shutdown complete")
    print()
    
    print("🎉 SystemPerformanceMonitor Standalone Test Completed Successfully!")
    print("=" * 60)


def main():
    """Main function to run the standalone test."""
    try:
        test_system_performance_monitoring()
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