#!/usr/bin/env python3
"""
Standalone test script for OrderAnalytics functionality.

This script demonstrates the order processing analytics capabilities
with realistic order processing scenarios and comprehensive reporting.
"""

import time
import json
from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.order_analytics import OrderAnalytics, OrderStatus


def main():
    """Main test function for OrderAnalytics."""
    print("🔄 Initializing OrderAnalytics Test...")
    
    # Initialize analytics engine
    config_data = {
        "rolling_window_seconds": 60,
        "max_metrics_per_category": 1000,
        "calculation_interval_seconds": 5,
        "memory_management": {
            "max_metrics_per_category": 1000,
            "cleanup_interval_seconds": 300
        }
    }
    
    analytics_engine = AnalyticsEngine()
    # Override config with test data
    analytics_engine.config = config_data
    analytics_engine.rolling_window_seconds = config_data.get("rolling_window_seconds", 60)
    
    # Initialize order analytics
    order_analytics = OrderAnalytics(analytics_engine)
    
    print("✅ Analytics Engine initialized")
    print("📊 OrderAnalytics ready for testing")
    print()
    
    # Test Scenario 1: Basic Order Processing
    print("=" * 60)
    print("📋 SCENARIO 1: Basic Order Processing")
    print("=" * 60)
    
    # Create orders
    orders = [
        ("ORDER_001", ["ITEM_A1", "ITEM_B2", "ITEM_C3"], 1),
        ("ORDER_002", ["ITEM_D4", "ITEM_E5"], 2),
        ("ORDER_003", ["ITEM_F6"], 1),
        ("ORDER_004", ["ITEM_G7", "ITEM_H8", "ITEM_I9", "ITEM_J10"], 3)
    ]
    
    print("📝 Creating orders...")
    for order_id, items, priority in orders:
        order_analytics.track_order_created(order_id, items, priority)
        print(f"   ✅ Created {order_id} with {len(items)} items (priority: {priority})")
    
    print(f"\n📊 Current Status:")
    print(f"   Total Orders: {len(order_analytics.orders)}")
    print(f"   Queue Length: {len(order_analytics.order_queue)}")
    print(f"   Created: {order_analytics.status_counts[OrderStatus.CREATED]}")
    
    # Assign orders to robots
    print("\n🤖 Assigning orders to robots...")
    assignments = [
        ("ORDER_001", "ROBOT_001"),
        ("ORDER_002", "ROBOT_002"),
        ("ORDER_003", "ROBOT_001"),
        ("ORDER_004", "ROBOT_003")
    ]
    
    for order_id, robot_id in assignments:
        time.sleep(0.1)  # Simulate assignment delay
        order_analytics.track_order_assigned(order_id, robot_id)
        print(f"   ✅ Assigned {order_id} to {robot_id}")
    
    print(f"\n📊 After Assignment:")
    print(f"   Queue Length: {len(order_analytics.order_queue)}")
    print(f"   Assigned: {order_analytics.status_counts[OrderStatus.ASSIGNED]}")
    
    # Start processing orders
    print("\n⚡ Starting order processing...")
    for order_id, _ in assignments:
        order_analytics.track_order_started(order_id)
        print(f"   ✅ Started processing {order_id}")
    
    print(f"\n📊 After Starting:")
    print(f"   In Progress: {order_analytics.status_counts[OrderStatus.IN_PROGRESS]}")
    
    # Complete orders with different processing times
    print("\n✅ Completing orders...")
    completion_times = [0.2, 0.3, 0.15, 0.4]
    for (order_id, _), processing_time in zip(assignments, completion_times):
        time.sleep(processing_time)
        order_analytics.track_order_completed(order_id)
        print(f"   ✅ Completed {order_id} (processing time: {processing_time:.2f}s)")
    
    # Test Scenario 2: Order Cancellations and Failures
    print("\n" + "=" * 60)
    print("📋 SCENARIO 2: Order Cancellations and Failures")
    print("=" * 60)
    
    # Create additional orders
    additional_orders = [
        ("ORDER_005", ["ITEM_K11", "ITEM_L12"], 1),
        ("ORDER_006", ["ITEM_M13"], 2),
        ("ORDER_007", ["ITEM_N14", "ITEM_O15"], 1)
    ]
    
    print("📝 Creating additional orders...")
    for order_id, items, priority in additional_orders:
        order_analytics.track_order_created(order_id, items, priority)
        print(f"   ✅ Created {order_id} with {len(items)} items")
    
    # Cancel one order
    print("\n❌ Cancelling order...")
    order_analytics.track_order_cancelled("ORDER_005", "Out of stock")
    print("   ❌ Cancelled ORDER_005 (Out of stock)")
    
    # Assign and fail another order
    print("\n🤖 Assigning and failing order...")
    order_analytics.track_order_assigned("ORDER_006", "ROBOT_001")
    order_analytics.track_order_failed("ORDER_006", "Robot malfunction")
    print("   ❌ Failed ORDER_006 (Robot malfunction)")
    
    # Complete the remaining order
    print("\n✅ Completing remaining order...")
    order_analytics.track_order_assigned("ORDER_007", "ROBOT_002")
    order_analytics.track_order_started("ORDER_007")
    time.sleep(0.25)
    order_analytics.track_order_completed("ORDER_007")
    print("   ✅ Completed ORDER_007")
    
    # Generate Comprehensive Analytics Report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE ANALYTICS REPORT")
    print("=" * 60)
    
    # Get all analytics data
    summary = order_analytics.get_order_analytics_summary()
    
    print(f"\n📈 ORDER SUMMARY:")
    print(f"   Total Orders: {summary['total_orders']}")
    print(f"   Completion Rate: {summary['completion_rate']:.1f}%")
    print(f"   Orders per Hour: {summary['orders_per_hour']:.1f}")
    print(f"   Average Items per Order: {summary['items_per_order']:.1f}")
    
    print(f"\n📊 STATUS DISTRIBUTION:")
    for status, count in summary['status_distribution'].items():
        print(f"   {status.title()}: {count}")
    
    print(f"\n⏱️ QUEUE ANALYTICS:")
    queue_analytics = summary['queue_analytics']
    print(f"   Current Queue Length: {queue_analytics['queue_length']}")
    print(f"   Average Queue Time: {queue_analytics['average_queue_time']:.2f}s")
    print(f"   Max Queue Time: {queue_analytics['max_queue_time']:.2f}s")
    print(f"   Total Queued: {queue_analytics['total_queued']}")
    
    print(f"\n⚡ PROCESSING ANALYTICS:")
    processing_analytics = summary['processing_analytics']
    print(f"   Average Processing Time: {processing_analytics['average_processing_time']:.2f}s")
    print(f"   Min Processing Time: {processing_analytics['min_processing_time']:.2f}s")
    print(f"   Max Processing Time: {processing_analytics['max_processing_time']:.2f}s")
    print(f"   Total Processed: {processing_analytics['total_processed']}")
    
    # Get KPI data
    print(f"\n🎯 KEY PERFORMANCE INDICATORS:")
    kpis = analytics_engine.get_all_kpis()
    for kpi in kpis:
        if kpi.category == "order_processing":
            print(f"   {kpi.name}: {kpi.value} {kpi.unit}")
    
    # Export analytics data
    print(f"\n📤 EXPORTING ANALYTICS DATA...")
    export_data = analytics_engine.export_analytics_data()
    
    # Save to file
    with open("order_analytics_export.json", "w") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print("   ✅ Analytics data exported to 'order_analytics_export.json'")
    
    # Performance statistics
    print(f"\n📊 PERFORMANCE STATISTICS:")
    perf_stats = analytics_engine.get_performance_stats()
    for key, value in perf_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ ORDER ANALYTICS TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Cleanup
    order_analytics.clear_analytics_data()
    analytics_engine.shutdown()
    print("🧹 Cleanup completed")


if __name__ == "__main__":
    main() 