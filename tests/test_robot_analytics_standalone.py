#!/usr/bin/env python3
"""
Standalone RobotAnalytics Test Script

This script demonstrates and tests the RobotAnalytics functionality
without requiring the full test suite. It provides comprehensive
testing of robot performance analytics features.
"""

import sys
import time
import statistics
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.analytics.analytics_engine import AnalyticsEngine
from core.analytics.robot_analytics import RobotAnalytics, RobotState


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


def test_robot_analytics_basic():
    """Test basic robot analytics functionality."""
    print("=== Testing Basic Robot Analytics ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create robot analytics
    robot_analytics = RobotAnalytics(analytics_engine)
    
    # Test robot creation
    print("1. Testing robot creation...")
    robot_id = "ROBOT_001"
    initial_position = (10, 15)
    metadata = {"model": "AGV-2000", "capacity": 50}
    
    robot_analytics.track_robot_created(robot_id, initial_position, metadata)
    
    # Verify robot was created
    assert robot_id in robot_analytics.robots
    robot_data = robot_analytics.robots[robot_id]
    assert robot_data.robot_id == robot_id
    assert robot_data.current_state == RobotState.IDLE
    assert robot_data.current_position == initial_position
    assert robot_data.metadata == metadata
    print("   ✅ Robot creation successful")
    
    # Test state change
    print("2. Testing robot state change...")
    time.sleep(0.1)  # Simulate idle time
    new_position = (12, 17)
    robot_analytics.track_robot_state_change(robot_id, RobotState.MOVING, new_position)
    
    # Verify state change
    assert robot_data.current_state == RobotState.MOVING
    assert robot_data.current_position == new_position
    assert robot_data.idle_time > 0
    assert len(robot_analytics.state_transitions) == 1
    print("   ✅ State change successful")
    
    # Test movement tracking
    print("3. Testing movement tracking...")
    distance = 15.5
    path_savings = 2.3
    robot_analytics.track_robot_movement(robot_id, distance, path_savings)
    
    # Verify movement tracking
    assert robot_data.total_distance_moved == distance
    assert robot_data.path_optimization_savings == path_savings
    assert len(robot_analytics.movement_distances) == 1
    assert len(robot_analytics.path_optimizations) == 1
    print("   ✅ Movement tracking successful")
    
    # Test item collection
    print("4. Testing item collection...")
    item_id = "ITEM_A1"
    collection_time = 2.5
    robot_analytics.track_item_collected(robot_id, item_id, collection_time)
    
    # Verify item collection
    assert robot_data.total_items_collected == 1
    assert robot_analytics._total_items_collected == 1
    print("   ✅ Item collection successful")
    
    # Test order completion
    print("5. Testing order completion...")
    order_id = "ORDER_001"
    completion_time = 30.5
    robot_analytics.track_order_completed(robot_id, order_id, completion_time)
    
    # Verify order completion
    assert robot_data.total_orders_completed == 1
    print("   ✅ Order completion successful")
    
    print("✅ All basic tests passed!")
    return robot_analytics


def test_multiple_robots():
    """Test multiple robots processing."""
    print("\n=== Testing Multiple Robots ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create robot analytics
    robot_analytics = RobotAnalytics(analytics_engine)
    
    # Create multiple robots
    robots = [
        ("ROBOT_001", (10, 15), {"model": "AGV-2000"}),
        ("ROBOT_002", (20, 25), {"model": "AGV-3000"}),
        ("ROBOT_003", (30, 35), {"model": "AGV-1000"})
    ]
    
    print("1. Creating multiple robots...")
    for robot_id, position, metadata in robots:
        robot_analytics.track_robot_created(robot_id, position, metadata)
    
    # Verify all robots created
    assert len(robot_analytics.robots) == 3
    assert robot_analytics._total_robots == 3
    assert robot_analytics._idle_robots == 3
    assert robot_analytics._active_robots == 0
    print("   ✅ Multiple robots created")
    
    # Activate robots
    print("2. Activating robots...")
    robot_analytics.track_robot_state_change("ROBOT_001", RobotState.MOVING)
    robot_analytics.track_robot_state_change("ROBOT_002", RobotState.COLLECTING)
    
    # Verify robot counts
    assert robot_analytics._idle_robots == 1
    assert robot_analytics._active_robots == 2
    print("   ✅ Robots activated")
    
    # Test state distribution
    print("3. Testing state distribution...")
    distribution = robot_analytics.get_robot_state_distribution()
    assert distribution.get("idle", 0) == 1
    assert distribution.get("moving", 0) == 1
    assert distribution.get("collecting", 0) == 1
    print("   ✅ State distribution correct")
    
    print("✅ Multiple robots test passed!")
    return robot_analytics


def test_analytics_summaries():
    """Test analytics summary generation."""
    print("\n=== Testing Analytics Summaries ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create robot analytics
    robot_analytics = RobotAnalytics(analytics_engine)
    
    # Create robot and add activity
    robot_id = "ROBOT_001"
    initial_position = (10, 15)
    
    robot_analytics.track_robot_created(robot_id, initial_position)
    time.sleep(0.1)
    robot_analytics.track_robot_state_change(robot_id, RobotState.MOVING)
    robot_analytics.track_robot_movement(robot_id, 15.5, 2.3)
    robot_analytics.track_robot_movement(robot_id, 8.2, 1.1)
    robot_analytics.track_item_collected(robot_id, "ITEM_A1", 2.5)
    robot_analytics.track_order_completed(robot_id, "ORDER_001", 30.5)
    
    # Test performance summary
    print("1. Testing performance summary...")
    summary = robot_analytics.get_robot_performance_summary()
    
    assert summary["total_robots"] == 1
    assert summary["active_robots"] == 1
    assert summary["idle_robots"] == 0
    assert summary["total_distance_moved"] == 23.7  # 15.5 + 8.2
    assert summary["total_items_collected"] == 1
    assert summary["total_path_savings"] == 3.4  # 2.3 + 1.1
    print("   ✅ Performance summary generated")
    
    # Test individual robot analytics
    print("2. Testing individual robot analytics...")
    analytics = robot_analytics.get_robot_analytics(robot_id)
    
    assert analytics is not None
    assert analytics["robot_id"] == robot_id
    assert analytics["current_state"] == "moving"
    assert analytics["total_distance_moved"] == 23.7
    assert analytics["total_items_collected"] == 1
    assert analytics["total_orders_completed"] == 1
    assert analytics["path_optimization_savings"] == 3.4
    assert analytics["idle_time"] > 0
    assert analytics["moving_time"] > 0
    assert analytics["total_time"] > 0
    assert analytics["utilization_rate"] > 0
    print("   ✅ Individual robot analytics generated")
    
    # Test movement analytics
    print("3. Testing movement analytics...")
    movement_analytics = robot_analytics.get_movement_analytics()
    
    assert movement_analytics["total_distance"] == 23.7
    assert movement_analytics["average_movement"] == 11.85  # 23.7 / 2
    assert movement_analytics["max_movement"] == 15.5
    assert movement_analytics["min_movement"] == 8.2
    assert movement_analytics["total_movements"] == 2
    print("   ✅ Movement analytics generated")
    
    # Test path optimization analytics
    print("4. Testing path optimization analytics...")
    optimization_analytics = robot_analytics.get_path_optimization_analytics()
    
    assert optimization_analytics["total_savings"] == 3.4
    assert optimization_analytics["average_savings"] == 1.7  # 3.4 / 2
    assert optimization_analytics["max_savings"] == 2.3
    assert optimization_analytics["total_optimizations"] == 2
    print("   ✅ Path optimization analytics generated")
    
    print("✅ All analytics summaries test passed!")
    return robot_analytics


def test_complex_scenario():
    """Test complex robot scenario with multiple activities."""
    print("\n=== Testing Complex Robot Scenario ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create robot analytics
    robot_analytics = RobotAnalytics(analytics_engine)
    
    # Create robot
    robot_id = "ROBOT_001"
    initial_position = (10, 15)
    
    print("1. Creating robot and simulating complex workflow...")
    robot_analytics.track_robot_created(robot_id, initial_position)
    
    # Simulate complex workflow
    time.sleep(0.1)  # Idle time
    robot_analytics.track_robot_state_change(robot_id, RobotState.MOVING, (12, 17))
    
    time.sleep(0.1)  # Moving time
    robot_analytics.track_robot_movement(robot_id, 15.5, 2.3)
    robot_analytics.track_robot_state_change(robot_id, RobotState.COLLECTING, (15, 20))
    
    time.sleep(0.1)  # Collecting time
    robot_analytics.track_item_collected(robot_id, "ITEM_A1", 2.5)
    robot_analytics.track_item_collected(robot_id, "ITEM_B2", 1.8)
    robot_analytics.track_robot_state_change(robot_id, RobotState.MOVING, (18, 22))
    
    time.sleep(0.1)  # More moving time
    robot_analytics.track_robot_movement(robot_id, 8.2, 1.1)
    robot_analytics.track_order_completed(robot_id, "ORDER_001", 30.5)
    robot_analytics.track_robot_state_change(robot_id, RobotState.RETURNING, (20, 25))
    
    time.sleep(0.1)  # Returning time
    robot_analytics.track_robot_movement(robot_id, 12.7, 0.5)
    robot_analytics.track_robot_state_change(robot_id, RobotState.IDLE, (10, 15))
    
    print("2. Verifying complex scenario results...")
    
    # Get robot analytics
    analytics = robot_analytics.get_robot_analytics(robot_id)
    
    # Verify comprehensive data
    assert analytics["total_distance_moved"] == 36.4  # 15.5 + 8.2 + 12.7
    assert analytics["total_items_collected"] == 2
    assert analytics["total_orders_completed"] == 1
    assert analytics["path_optimization_savings"] == 3.9  # 2.3 + 1.1 + 0.5
    assert analytics["idle_time"] > 0
    assert analytics["moving_time"] > 0
    assert analytics["collecting_time"] > 0
    assert analytics["utilization_rate"] > 0
    
    # Check state transitions
    assert len(robot_analytics.state_transitions) == 5
    
    # Check movement data
    assert len(robot_analytics.movement_distances) == 3
    assert len(robot_analytics.path_optimizations) == 3
    
    print("   ✅ Complex scenario verification successful")
    
    # Test performance summary
    summary = robot_analytics.get_robot_performance_summary()
    assert summary["total_robots"] == 1
    assert summary["total_distance_moved"] == 36.4
    assert summary["total_items_collected"] == 2
    assert summary["total_path_savings"] == 3.9
    
    print("   ✅ Performance summary verification successful")
    
    print("✅ Complex scenario test passed!")
    return robot_analytics


def test_data_clearing():
    """Test data clearing functionality."""
    print("\n=== Testing Data Clearing ===")
    
    # Create analytics engine
    config = create_test_config()
    analytics_engine = AnalyticsEngine()
    analytics_engine.config = config
    analytics_engine.rolling_window_seconds = config.get("rolling_window_seconds", 60)
    
    # Create robot analytics
    robot_analytics = RobotAnalytics(analytics_engine)
    
    # Create some robots and add activity
    print("1. Creating robots and adding activity...")
    robot_analytics.track_robot_created("ROBOT_001", (10, 15))
    robot_analytics.track_robot_state_change("ROBOT_001", RobotState.MOVING)
    robot_analytics.track_robot_movement("ROBOT_001", 15.5, 2.3)
    
    # Verify data exists
    assert len(robot_analytics.robots) == 1
    assert len(robot_analytics.state_transitions) == 1
    assert len(robot_analytics.movement_distances) == 1
    assert len(robot_analytics.path_optimizations) == 1
    print("   ✅ Data created successfully")
    
    # Clear data
    print("2. Clearing analytics data...")
    robot_analytics.clear_analytics_data()
    
    # Verify data is cleared
    assert len(robot_analytics.robots) == 0
    assert len(robot_analytics.state_transitions) == 0
    assert len(robot_analytics.movement_distances) == 0
    assert len(robot_analytics.path_optimizations) == 0
    
    # Check internal counters are reset
    assert robot_analytics._total_robots == 0
    assert robot_analytics._active_robots == 0
    assert robot_analytics._idle_robots == 0
    assert robot_analytics._total_distance == 0.0
    assert robot_analytics._total_items_collected == 0
    assert robot_analytics._total_path_savings == 0.0
    print("   ✅ Data cleared successfully")
    
    print("✅ Data clearing test passed!")


def main():
    """Run all robot analytics tests."""
    print("🤖 RobotAnalytics Standalone Test Suite")
    print("=" * 50)
    
    try:
        # Run all tests
        test_robot_analytics_basic()
        test_multiple_robots()
        test_analytics_summaries()
        test_complex_scenario()
        test_data_clearing()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! RobotAnalytics is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 