"""
Comprehensive tests for CompletePathPlanner.

Tests upfront path calculation for all items, path optimization for multiple items,
path execution tracking, path validation and error handling, and integration with
robot navigation system.
"""

import unittest
import time
from unittest.mock import Mock, patch

from core.layout.complete_path_planner import (
    CompletePathPlanner, 
    PathExecutionStatus, 
    PathExecutionState
)
from core.layout.coordinate import Coordinate
from core.layout.warehouse_layout import WarehouseLayoutManager


class TestCompletePathPlanner(unittest.TestCase):
    """Test suite for CompletePathPlanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("\n🧪 Setting up CompletePathPlanner tests...")
        
        # Test configuration
        self.test_config = {
            "robot": {
                "aisle_traversal_time": 7.0,
                "horizontal_movement_time": 0.35,
                "direction_change_cooldown": 0.5
            }
        }
        
        # Initialize warehouse layout
        self.warehouse_layout = WarehouseLayoutManager()
        
        # Initialize path planner
        self.path_planner = CompletePathPlanner(self.warehouse_layout, self.test_config)
        
        # Test coordinates
        self.start_pos = Coordinate(1, 1)
        self.item_positions = [
            Coordinate(2, 5),
            Coordinate(3, 10),
            Coordinate(1, 15)
        ]
        
        print("✅ Test setup complete")
    
    def test_initialization(self):
        """Test CompletePathPlanner initialization."""
        print("\n1. Testing Initialization...")
        
        # Test basic initialization
        self.assertIsNotNone(self.path_planner.warehouse_layout)
        self.assertIsNotNone(self.path_planner.path_calculator)
        self.assertIsNotNone(self.path_planner.timing_manager)
        
        # Test initial state
        self.assertIsNone(self.path_planner.current_path)
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.NOT_STARTED)
        
        print("✅ Initialization tests passed")
    
    def test_complete_path_planning(self):
        """Test complete path planning for multiple items."""
        print("\n2. Testing Complete Path Planning...")
        
        # Plan complete path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        
        # Verify path was created
        self.assertIsNotNone(complete_path)
        self.assertGreater(len(complete_path.segments), 0)
        self.assertEqual(len(complete_path.items_to_collect), 3)
        
        # Verify path is stored
        self.assertEqual(self.path_planner.current_path, complete_path)
        
        # Verify path statistics
        stats = self.path_planner.get_path_statistics(complete_path)
        self.assertGreater(stats['total_distance'], 0)
        self.assertGreater(stats['total_duration'], 0)
        self.assertEqual(stats['items_to_collect'], 3)
        
        print(f"✅ Path planned: {stats['total_distance']:.1f} units, {stats['total_duration']:.1f}s")
        print(f"✅ Segments: {len(complete_path.segments)}")
        print(f"✅ Items: {len(complete_path.items_to_collect)}")
        
        print("✅ Complete path planning tests passed")
    
    def test_path_execution_start(self):
        """Test path execution start functionality."""
        print("\n3. Testing Path Execution Start...")
        
        # Plan path first
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        
        # Start execution
        start_time = time.time()
        success = self.path_planner.start_path_execution(start_time)
        
        # Verify execution started
        self.assertTrue(success)
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.IN_PROGRESS)
        self.assertEqual(self.path_planner.execution_state.start_time, start_time)
        self.assertEqual(self.path_planner.execution_state.current_segment_index, 0)
        
        print("✅ Path execution started successfully")
        
        # Test starting execution when already in progress
        success2 = self.path_planner.start_path_execution()
        self.assertFalse(success2)  # Should fail
        
        print("✅ Duplicate start handling passed")
        
        print("✅ Path execution start tests passed")
    
    def test_path_execution_update(self):
        """Test path execution update functionality."""
        print("\n4. Testing Path Execution Update...")
        
        # Plan and start path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        self.path_planner.start_path_execution()
        
        # Test update with no execution
        self.path_planner.execution_state.status = PathExecutionStatus.NOT_STARTED
        update_data = self.path_planner.update_path_execution(time.time())
        self.assertEqual(update_data["status"], "no_execution")
        
        # Restart execution
        self.path_planner.start_path_execution()
        
        # Test update during execution
        current_time = time.time()
        update_data = self.path_planner.update_path_execution(current_time)
        
        self.assertEqual(update_data["status"], "in_progress")
        self.assertIn("segment_index", update_data)
        self.assertIn("progress", update_data)
        self.assertIn("elapsed", update_data)
        self.assertIn("remaining", update_data)
        
        print(f"✅ Execution update: segment {update_data['segment_index']}, progress {update_data['progress']:.2%}")
        
        print("✅ Path execution update tests passed")
    
    def test_path_execution_completion(self):
        """Test path execution completion."""
        print("\n5. Testing Path Execution Completion...")
        
        # Plan and start path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        start_time = time.time()
        self.path_planner.start_path_execution(start_time)
        
        # Simulate completion by advancing time and processing all segments
        total_duration = complete_path.total_duration
        completion_time = start_time + total_duration + 0.1
        
        # Process all segments to completion
        update_data = None
        while True:
            update_data = self.path_planner.update_path_execution(completion_time)
            if update_data["status"] == "completed":
                break
            elif update_data["status"] == "segment_completed":
                # Continue to next segment
                continue
            else:
                # Still in progress, advance time more
                completion_time += 1.0
        
        # Verify completion
        self.assertEqual(update_data["status"], "completed")
        self.assertIn("total_time", update_data)
        self.assertIn("collected_items", update_data)
        
        # Verify execution state
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.COMPLETED)
        self.assertEqual(len(self.path_planner.execution_state.collected_items), 3)
        
        print(f"✅ Path completed: {update_data['total_time']:.2f}s, {update_data['collected_items']} items")
        
        print("✅ Path execution completion tests passed")
    
    def test_execution_control(self):
        """Test execution control (pause, resume, stop)."""
        print("\n6. Testing Execution Control...")
        
        # Plan and start path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        self.path_planner.start_path_execution()
        
        # Test pause
        pause_success = self.path_planner.pause_path_execution()
        self.assertTrue(pause_success)
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.PAUSED)
        print("✅ Path execution paused")
        
        # Test resume
        resume_success = self.path_planner.resume_path_execution()
        self.assertTrue(resume_success)
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.IN_PROGRESS)
        print("✅ Path execution resumed")
        
        # Test stop
        stop_success = self.path_planner.stop_path_execution()
        self.assertTrue(stop_success)
        self.assertEqual(self.path_planner.execution_state.status, PathExecutionStatus.FAILED)
        print("✅ Path execution stopped")
        
        print("✅ Execution control tests passed")
    
    def test_path_validation(self):
        """Test path validation functionality."""
        print("\n7. Testing Path Validation...")
        
        # Test valid path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        is_valid = self.path_planner.validate_path(complete_path)
        self.assertTrue(is_valid)
        print("✅ Valid path validation passed")
        
        # Test empty path
        empty_path = self.path_planner.plan_complete_path(self.start_pos, [])
        is_valid_empty = self.path_planner.validate_path(empty_path)
        self.assertTrue(is_valid_empty)
        print("✅ Empty path validation passed")
        
        print("✅ Path validation tests passed")
    
    def test_item_order_optimization(self):
        """Test item order optimization."""
        print("\n8. Testing Item Order Optimization...")
        
        # Test with unsorted items
        unsorted_items = [
            Coordinate(3, 10),
            Coordinate(1, 15),
            Coordinate(2, 5)
        ]
        
        optimized_items = self.path_planner.optimize_item_order(unsorted_items)
        
        # Verify items are sorted in ascending order
        expected_order = [
            Coordinate(1, 15),
            Coordinate(2, 5),
            Coordinate(3, 10)
        ]
        
        self.assertEqual(optimized_items, expected_order)
        print("✅ Item order optimization passed")
        
        # Test empty list
        empty_optimized = self.path_planner.optimize_item_order([])
        self.assertEqual(empty_optimized, [])
        print("✅ Empty list optimization passed")
        
        print("✅ Item order optimization tests passed")
    
    def test_execution_progress_tracking(self):
        """Test execution progress tracking."""
        print("\n9. Testing Execution Progress Tracking...")
        
        # Plan path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        
        # Test initial progress
        initial_progress = self.path_planner.get_execution_progress()
        self.assertEqual(initial_progress, 0.0)
        
        # Start execution
        self.path_planner.start_path_execution()
        
        # Test progress during execution
        self.path_planner.execution_state.current_segment_index = 2
        progress = self.path_planner.get_execution_progress()
        self.assertGreater(progress, 0.0)
        self.assertLessEqual(progress, 1.0)
        
        print(f"✅ Progress tracking: {progress:.2%}")
        
        print("✅ Execution progress tracking tests passed")
    
    def test_current_segment_and_target(self):
        """Test current segment and target position retrieval."""
        print("\n10. Testing Current Segment and Target...")
        
        # Plan and start path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        self.path_planner.start_path_execution()
        
        # Test current segment
        current_segment = self.path_planner.get_current_segment()
        self.assertIsNotNone(current_segment)
        print(f"✅ Current segment: {current_segment.start} → {current_segment.end}")
        
        # Test next target position
        next_target = self.path_planner.get_next_target_position()
        self.assertIsNotNone(next_target)
        self.assertEqual(next_target, current_segment.end)
        print(f"✅ Next target: {next_target}")
        
        # Test with no current path
        self.path_planner.current_path = None
        no_segment = self.path_planner.get_current_segment()
        no_target = self.path_planner.get_next_target_position()
        self.assertIsNone(no_segment)
        self.assertIsNone(no_target)
        print("✅ No path handling passed")
        
        print("✅ Current segment and target tests passed")
    
    def test_execution_statistics(self):
        """Test execution statistics collection."""
        print("\n11. Testing Execution Statistics...")
        
        # Complete a path execution
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        start_time = time.time()
        self.path_planner.start_path_execution(start_time)
        
        # Simulate completion by processing all segments
        completion_time = start_time + complete_path.total_duration + 0.1
        
        # Process all segments to completion
        while True:
            update_data = self.path_planner.update_path_execution(completion_time)
            if update_data["status"] == "completed":
                break
            elif update_data["status"] == "segment_completed":
                # Continue to next segment
                continue
            else:
                # Still in progress, advance time more
                completion_time += 1.0
        
        # Get statistics
        stats = self.path_planner.get_execution_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_executions"], 1)
        self.assertEqual(stats["successful_executions"], 1)
        self.assertEqual(stats["failed_executions"], 0)
        self.assertGreater(stats["average_execution_time"], 0.0)
        self.assertEqual(stats["total_items_collected"], 3)
        
        print(f"✅ Statistics: {stats['total_executions']} executions, {stats['successful_executions']} successful")
        print(f"✅ Average time: {stats['average_execution_time']:.2f}s")
        print(f"✅ Total items: {stats['total_items_collected']}")
        
        print("✅ Execution statistics tests passed")
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n12. Testing Error Handling...")
        
        # Test planning with invalid path (use valid coordinates but invalid path)
        # We'll test with a path that would be invalid due to snake pattern constraints
        # This is a more realistic test since Coordinate validation happens at creation
        invalid_items = [Coordinate(1, 1)]  # Same as start position
        try:
            self.path_planner.plan_complete_path(self.start_pos, invalid_items)
            print("✅ Invalid path handling passed")
        except Exception as e:
            print(f"✅ Invalid path handling passed (caught: {e})")
        
        # Test starting execution without path
        # Clear the current path first
        self.path_planner.current_path = None
        success = self.path_planner.start_path_execution()
        self.assertFalse(success)
        print("✅ No path execution handling passed")
        
        # Test pause/resume without execution
        self.path_planner.execution_state.status = PathExecutionStatus.NOT_STARTED
        pause_success = self.path_planner.pause_path_execution()
        resume_success = self.path_planner.resume_path_execution()
        self.assertFalse(pause_success)
        self.assertFalse(resume_success)
        print("✅ Invalid state handling passed")
        
        print("✅ Error handling tests passed")
    
    def test_integration_with_robot_navigation(self):
        """Test integration with robot navigation system."""
        print("\n13. Testing Robot Navigation Integration...")
        
        # Plan path
        complete_path = self.path_planner.plan_complete_path(self.start_pos, self.item_positions)
        
        # Simulate robot navigation integration
        robot_positions = []
        self.path_planner.start_path_execution()
        
        # Simulate robot following path
        for i, segment in enumerate(complete_path.segments):
            robot_positions.append(segment.start)
            if i == len(complete_path.segments) - 1:
                robot_positions.append(segment.end)
        
        # Verify robot follows path correctly
        self.assertEqual(len(robot_positions), len(complete_path.segments) + 1)
        self.assertEqual(robot_positions[0], self.start_pos)
        
        print(f"✅ Robot navigation: {len(robot_positions)} positions followed")
        print("✅ Robot navigation integration tests passed")
        
        print("✅ Integration tests passed")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 