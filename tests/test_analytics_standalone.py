#!/usr/bin/env python3
"""
Standalone test script for Analytics Engine

This script tests the core analytics engine functionality including real-time KPI calculations,
event-driven data collection, and session-based storage.
"""

import sys
import os
import time
import json
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analytics.analytics_engine import AnalyticsEngine, MetricData, KPICalculation


def test_analytics_engine_basic():
    """Test basic analytics engine functionality."""
    print("🧪 Testing basic analytics engine functionality...")
    
    # Create analytics engine
    analytics = AnalyticsEngine()
    
    # Test metric recording
    success = analytics.record_metric("test_metric", 42.0, "test_category")
    assert success, "Metric recording should succeed"
    print("  ✅ Metric recording works")
    
    # Test KPI retrieval
    kpi = analytics.get_kpi("test_category.test_metric")
    assert kpi is not None, "KPI should be available"
    assert kpi.value == 42.0, "KPI value should match recorded metric"
    print("  ✅ KPI retrieval works")
    
    # Test multiple metrics
    for i in range(5):
        analytics.record_metric("test_metric", float(i), "test_category")
    
    kpi = analytics.get_kpi("test_category.test_metric")
    assert kpi.value == 2.0, "KPI should be average of 0,1,2,3,4"
    print("  ✅ Multiple metrics averaging works")
    
    analytics.shutdown()
    print("✅ Basic analytics engine tests passed")


def test_analytics_engine_performance():
    """Test analytics engine performance."""
    print("🧪 Testing analytics engine performance...")
    
    analytics = AnalyticsEngine()
    
    # Record many metrics quickly
    start_time = time.time()
    for i in range(100):
        analytics.record_metric(f"metric_{i}", float(i), "performance_test")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Should complete quickly (less than 1 second)
    assert duration < 1.0, f"Performance test took too long: {duration:.2f}s"
    print(f"  ✅ Performance test completed in {duration:.3f}s")
    
    # Check memory usage
    stats = analytics.get_performance_stats()
    assert stats["total_metrics"] >= 100, "Should have recorded all metrics"
    print(f"  ✅ Recorded {stats['total_metrics']} metrics")
    
    analytics.shutdown()
    print("✅ Performance tests passed")


def test_analytics_engine_event_handlers():
    """Test analytics engine event handlers."""
    print("🧪 Testing analytics engine event handlers...")
    
    analytics = AnalyticsEngine()
    
    # Test order event handlers
    order_data = {"order_id": "ORDER_001", "items": ["ITEM_A1", "ITEM_B2"]}
    analytics._handle_order_created(order_data)
    
    # Check that order metric was recorded
    order_metric = analytics.get_kpi("order_processing.order_created")
    assert order_metric is not None, "Order created metric should be recorded"
    print("  ✅ Order event handler works")
    
    # Test robot event handlers
    robot_data = {"robot_id": "ROBOT_001", "distance": 15.5}
    analytics._handle_robot_movement(robot_data)
    
    # Check that robot metric was recorded
    robot_metric = analytics.get_kpi("robot_performance.robot_movement")
    assert robot_metric is not None, "Robot movement metric should be recorded"
    print("  ✅ Robot event handler works")
    
    # Test inventory event handlers
    inventory_data = {"item_id": "ITEM_A1", "quantity": 95.0}
    analytics._handle_inventory_update(inventory_data)
    
    # Check that inventory metric was recorded
    inventory_metric = analytics.get_kpi("inventory_management.inventory_update")
    assert inventory_metric is not None, "Inventory update metric should be recorded"
    print("  ✅ Inventory event handler works")
    
    analytics.shutdown()
    print("✅ Event handler tests passed")


def test_analytics_engine_kpi_calculations():
    """Test KPI calculation functionality."""
    print("🧪 Testing KPI calculation functionality...")
    
    analytics = AnalyticsEngine()
    
    # Test orders per hour calculation
    for i in range(10):
        analytics.record_metric("order_completed", 1.0, "order_processing")
    
    orders_per_hour = analytics.calculate_orders_per_hour()
    assert orders_per_hour > 0, "Orders per hour should be positive"
    print(f"  ✅ Orders per hour: {orders_per_hour:.2f}")
    
    # Test robot utilization calculation
    for i in range(5):
        analytics.record_metric("active_time", 10.0, "robot_performance")
        analytics.record_metric("total_time", 20.0, "robot_performance")
    
    utilization = analytics.calculate_robot_utilization()
    assert 45.0 <= utilization <= 55.0, f"Utilization should be around 50%, got {utilization}"
    print(f"  ✅ Robot utilization: {utilization:.1f}%")
    
    analytics.shutdown()
    print("✅ KPI calculation tests passed")


def test_analytics_engine_data_export():
    """Test analytics data export functionality."""
    print("🧪 Testing analytics data export functionality...")
    
    analytics = AnalyticsEngine()
    
    # Record some test data
    analytics.record_metric("test_metric", 42.0, "test_category")
    analytics.record_metric("another_metric", 100.0, "test_category")
    
    # Export data
    export_data = analytics.export_analytics_data()
    
    # Check export structure
    assert "session_info" in export_data, "Export should have session info"
    assert "kpis" in export_data, "Export should have KPIs"
    assert "performance_stats" in export_data, "Export should have performance stats"
    
    # Check session info
    session_info = export_data["session_info"]
    assert "start_time" in session_info, "Session info should have start time"
    assert "duration_seconds" in session_info, "Session info should have duration"
    assert "config" in session_info, "Session info should have config"
    
    # Check KPIs
    kpis = export_data["kpis"]
    assert len(kpis) >= 2, "Should have exported KPIs"
    
    print(f"  ✅ Exported {len(kpis)} KPIs")
    print("  ✅ Export structure is correct")
    
    analytics.shutdown()
    print("✅ Data export tests passed")


def test_analytics_engine_configuration():
    """Test analytics engine configuration loading."""
    print("🧪 Testing analytics engine configuration...")
    
    # Test default configuration
    analytics = AnalyticsEngine("nonexistent.json")
    assert analytics.config is not None, "Should load default config"
    assert analytics.rolling_window_seconds == 300, "Should use default rolling window"
    print("  ✅ Default configuration loading works")
    
    analytics.shutdown()
    
    # Test custom configuration
    config_data = {
        "rolling_window_seconds": 120,
        "enable_debug_mode": True,
        "categories": {
            "test_category": {
                "enabled": True,
                "metrics": ["test_metric"]
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(config_data, f)
        config_file = f.name
    
    try:
        analytics = AnalyticsEngine(config_file)
        assert analytics.rolling_window_seconds == 120, "Should use custom rolling window"
        assert analytics.config["enable_debug_mode"] == True, "Should use custom debug mode"
        print("  ✅ Custom configuration loading works")
        
        analytics.shutdown()
        
    finally:
        os.unlink(config_file)
    
    print("✅ Configuration tests passed")


def test_analytics_engine_session_management():
    """Test analytics engine session management."""
    print("🧪 Testing analytics engine session management...")
    
    analytics = AnalyticsEngine()
    
    # Record some data
    analytics.record_metric("test_metric", 42.0, "test_category")
    
    # Verify data exists
    assert len(analytics.metrics) > 0, "Should have recorded metrics"
    assert len(analytics.kpi_cache) > 0, "Should have calculated KPIs"
    
    # Clear session data
    analytics.clear_session_data()
    
    # Verify data is cleared
    assert len(analytics.metrics) == 0, "Metrics should be cleared"
    assert len(analytics.kpi_cache) == 0, "KPI cache should be cleared"
    
    print("  ✅ Session data clearing works")
    
    analytics.shutdown()
    print("✅ Session management tests passed")


def main():
    """Run all analytics engine tests."""
    print("🚀 Starting Analytics Engine tests...")
    print("=" * 60)
    
    try:
        test_analytics_engine_basic()
        print()
        
        test_analytics_engine_performance()
        print()
        
        test_analytics_engine_event_handlers()
        print()
        
        test_analytics_engine_kpi_calculations()
        print()
        
        test_analytics_engine_data_export()
        print()
        
        test_analytics_engine_configuration()
        print()
        
        test_analytics_engine_session_management()
        print()
        
        print("=" * 60)
        print("🎉 All Analytics Engine tests passed!")
        print("✅ Basic functionality")
        print("✅ Performance")
        print("✅ Event handlers")
        print("✅ KPI calculations")
        print("✅ Data export")
        print("✅ Configuration")
        print("✅ Session management")
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 