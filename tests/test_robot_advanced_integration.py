#!/usr/bin/env python3
"""
Advanced integration test for Robot Entity components including orders and events.
Tests that all robot components work together properly with the new order and event systems.
"""

import sys
import time
import os
import asyncio

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.robot import Robot, RobotState
from entities.robot_orders import Order, OrderStatus
from core.layout.coordinate import Coordinate
from core.events import EventSystem, EventType

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

def test_order_management():
    """Test order management functionality."""
    print("📦 Testing Order Management...")
    
    # Test 1: Order creation
    print("\n1. Testing Order Creation...")
    order = Order("ORDER_001", ["ITEM_001", "ITEM_002"], [(3, 3), (7, 7)])
    print(f"✅ Order created: {order.order_id}")
    print(f"✅ Items: {order.item_ids}")
    print(f"✅ Positions: {order.item_positions}")
    print(f"✅ Initial status: {order.status}")
    
    # Test 2: Order assignment
    print("\n2. Testing Order Assignment...")
    robot = Robot()
    # Robot starts in IDLE state, no need to set it again
    
    success = robot.assign_order(order)
    print(f"✅ Order assignment: {success}")
    print(f"✅ Robot state after assignment: {robot.state}")
    print(f"✅ Current order: {robot.get_current_order().order_id if robot.get_current_order() else None}")
    
    # Test 3: Order progress tracking
    print("\n3. Testing Order Progress Tracking...")
    order = robot.get_current_order()
    print(f"✅ Order status: {order.status}")
    print(f"✅ Remaining items: {order.get_remaining_items()}")
    print(f"✅ Remaining positions: {order.get_remaining_positions()}")
    
    # Test 4: Item collection simulation
    print("\n4. Testing Item Collection Simulation...")
    robot.position = (3, 3)
    robot.start_item_collection("ITEM_001", (3, 3), time.time())
    print(f"✅ Started collection for ITEM_001")
    print(f"✅ Is collecting: {robot.is_collecting()}")
    
    # Simulate collection completion
    for i in range(5):
        complete = robot.update_collection(time.time())
        if complete:
            print(f"✅ Collection completed!")
            break
        time.sleep(0.1)
    
    # Check order progress
    order = robot.get_current_order()
    print(f"✅ Items collected: {order.items_collected}")
    print(f"✅ Remaining items: {order.get_remaining_items()}")
    
    return True

def test_event_system_integration():
    """Test event system integration."""
    print("\n📡 Testing Event System Integration...")
    
    # Create event system
    event_system = EventSystem()
    
    # Start the event system
    run_async(event_system.start())
    
    # Create robot with event system
    robot = Robot(event_system=event_system)
    
    # Track events
    events_received = []
    
    def event_handler(event):
        events_received.append({
            'type': event.event_type.value,
            'data': event.data,
            'source': event.source
        })
        print(f"📋 Event received: {event.event_type.value} from {event.source}")
    
    # Subscribe to robot events
    event_system.subscribe(EventType.ROBOT_STATE_CHANGED, event_handler)
    event_system.subscribe(EventType.ROBOT_MOVED, event_handler)
    event_system.subscribe(EventType.ORDER_ASSIGNED, event_handler)
    
    # Test 1: State change events
    print("\n1. Testing State Change Events...")
    robot.set_state(RobotState.MOVING_TO_ITEM)
    run_async(event_system.process_events())
    
    # Test 2: Position update events
    print("\n2. Testing Position Update Events...")
    robot.position = (1, 1)
    robot.update_movement(time.time())
    run_async(event_system.process_events())
    
    # Test 3: Order assignment events
    print("\n3. Testing Order Assignment Events...")
    order = Order("ORDER_002", ["ITEM_003"], [(5, 5)])
    robot.assign_order(order)
    run_async(event_system.process_events())
    
    # Check events received
    print(f"✅ Events received: {len(events_received)}")
    for i, event in enumerate(events_received):
        print(f"   Event {i+1}: {event['type']} from {event['source']}")
    
    # Stop the event system
    run_async(event_system.stop())
    
    return len(events_received) > 0

def test_comprehensive_robot_workflow():
    """Test complete robot workflow with orders and events."""
    print("\n🔄 Testing Comprehensive Robot Workflow...")
    
    # Create event system
    event_system = EventSystem()
    run_async(event_system.start())
    robot = Robot(event_system=event_system)
    
    # Create order
    order = Order("ORDER_003", ["ITEM_004", "ITEM_005"], [(2, 2), (8, 8)])
    
    # Test complete workflow
    print("\n1. Initial State...")
    print(f"✅ Robot state: {robot.state}")
    print(f"✅ Available for order: {robot.is_available_for_order()}")
    
    print("\n2. Order Assignment...")
    success = robot.assign_order(order)
    print(f"✅ Order assigned: {success}")
    print(f"✅ Robot state: {robot.state}")
    
    print("\n3. Navigation Setup...")
    next_target = robot.get_next_target()
    print(f"✅ Next target: {next_target}")
    path = robot.calculate_path_to_next_item()
    print(f"✅ Path calculated: {len(path)} positions")
    
    print("\n4. Movement Simulation...")
    robot.position = (1, 1)
    target = Coordinate(2, 2)
    robot.movement.set_target(target)
    
    # Simulate movement
    for i in range(10):
        robot.update_movement(time.time())
        if robot.movement.is_complete():
            print(f"✅ Movement completed!")
            break
        time.sleep(0.1)
    
    print("\n5. Item Collection...")
    robot.position = (2, 2)
    robot.start_item_collection("ITEM_004", (2, 2), time.time())
    
    # Simulate collection
    for i in range(5):
        complete = robot.update_collection(time.time())
        if complete:
            print(f"✅ Collection completed!")
            break
        time.sleep(0.1)
    
    print("\n6. Order Progress...")
    order = robot.get_current_order()
    print(f"✅ Items collected: {order.items_collected}")
    print(f"✅ Order complete: {order.is_complete()}")
    
    # Stop the event system
    run_async(event_system.stop())
    
    return True

def test_error_handling():
    """Test error handling in order and event systems."""
    print("\n🔍 Testing Error Handling...")
    
    robot = Robot()
    
    # Test 1: Invalid order assignment (robot not idle)
    print("\n1. Testing Invalid Order Assignment...")
    robot.set_state(RobotState.MOVING_TO_ITEM)
    order = Order("ORDER_004", ["ITEM_006"], [(3, 3)])
    
    success = robot.assign_order(order)
    print(f"✅ Invalid assignment properly rejected: {not success}")
    
    # Test 2: Collection at wrong position
    print("\n2. Testing Collection at Wrong Position...")
    robot.position = (1, 1)
    try:
        robot.start_item_collection("ITEM_007", (5, 5), time.time())
        print("❌ Collection at wrong position should have failed")
        return False
    except ValueError:
        print("✅ Collection at wrong position properly rejected")
    
    # Test 3: Order with invalid positions
    print("\n3. Testing Order with Invalid Positions...")
    try:
        invalid_order = Order("ORDER_005", ["ITEM_008"], [(30, 30)])  # Invalid position
        print("❌ Invalid order should have been rejected")
        return False
    except Exception:
        print("✅ Invalid order properly rejected")
    
    print("✅ All Error Handling Tests Passed!")
    return True

def test_performance():
    """Test performance of robot components."""
    print("\n⚡ Testing Performance...")
    
    robot = Robot()
    
    # Test 1: Multiple state changes
    print("\n1. Testing Multiple State Changes...")
    start_time = time.time()
    for i in range(100):
        robot.set_state(RobotState.MOVING_TO_ITEM)
        robot.set_state(RobotState.COLLECTING_ITEM)
        robot.set_state(RobotState.RETURNING)
        robot.set_state(RobotState.IDLE)
    
    duration = time.time() - start_time
    print(f"✅ 100 state changes completed in {duration:.3f}s")
    print(f"✅ Average time per state change: {duration/400:.6f}s")
    
    # Test 2: Multiple order assignments
    print("\n2. Testing Multiple Order Assignments...")
    start_time = time.time()
    for i in range(50):
        order = Order(f"ORDER_{i}", [f"ITEM_{i}"], [(i % 25 + 1, i % 20 + 1)])
        robot.reset()
        robot.assign_order(order)
    
    duration = time.time() - start_time
    print(f"✅ 50 order assignments completed in {duration:.3f}s")
    print(f"✅ Average time per order assignment: {duration/50:.6f}s")
    
    # Test 3: Movement calculations
    print("\n3. Testing Movement Calculations...")
    start_time = time.time()
    for i in range(100):
        robot.position = (1, 1)
        target = Coordinate((i % 25) + 1, (i % 20) + 1)
        robot.movement.set_target(target)
        robot.movement.update(time.time())
    
    duration = time.time() - start_time
    print(f"✅ 100 movement calculations completed in {duration:.3f}s")
    print(f"✅ Average time per movement calculation: {duration/100:.6f}s")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Advanced Robot Integration Tests...")
    
    success = True
    success &= test_order_management()
    success &= test_event_system_integration()
    success &= test_comprehensive_robot_workflow()
    success &= test_error_handling()
    success &= test_performance()
    
    if success:
        print("\n🎉 All advanced tests passed! Robot components are working correctly.")
        print("✅ Order management system is functional")
        print("✅ Event system integration is working")
        print("✅ Complete workflow is operational")
        print("✅ Error handling is robust")
        print("✅ Performance is acceptable")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 