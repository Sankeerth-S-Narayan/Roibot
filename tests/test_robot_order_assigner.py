"""
Comprehensive tests for RobotOrderAssigner class.

Tests robot assignment logic, order processing state management,
assignment validation, completion detection, and integration with
robot state machine.

Author: Roibot Development Team
Version: 1.0
"""

import unittest
import time
from unittest.mock import Mock, patch

from entities.robot_order_assigner import RobotOrderAssigner, AssignmentStatus, AssignmentStatistics
from entities.robot_orders import Order, OrderStatus
from entities.order_queue_manager import OrderQueueManager
from entities.robot_state import RobotState


class TestRobotOrderAssigner(unittest.TestCase):
    """Test cases for RobotOrderAssigner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.assigner = RobotOrderAssigner(robot_id="ROBOT_001")
        self.queue_manager = OrderQueueManager(max_queue_size=10)
        
        # Create test orders
        self.order1 = Order("ORD_001", ["ITEM_A1", "ITEM_B2"], [(1, 1), (2, 2)])
        self.order2 = Order("ORD_002", ["ITEM_C3"], [(3, 3)])
        self.order3 = Order("ORD_003", ["ITEM_D4", "ITEM_E5", "ITEM_F6"], [(4, 4), (5, 5), (6, 6)])
    
    def test_initialization(self):
        """Test RobotOrderAssigner initialization."""
        self.assertEqual(self.assigner.robot_id, "ROBOT_001")
        self.assertIsNone(self.assigner.current_assignment)
        self.assertIsNone(self.assigner.assignment_start_time)
        self.assertEqual(len(self.assigner.assignment_history), 0)
        self.assertIsInstance(self.assigner.statistics, AssignmentStatistics)
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
        self.assertEqual(self.assigner.statistics.total_completions, 0)
        self.assertEqual(self.assigner.statistics.total_failures, 0)
    
    def test_is_robot_available_idle_no_assignment(self):
        """Test robot availability when IDLE with no assignment."""
        result = self.assigner.is_robot_available(RobotState.IDLE)
        self.assertTrue(result)
    
    def test_is_robot_available_idle_with_assignment(self):
        """Test robot availability when IDLE but has assignment."""
        self.assigner.current_assignment = self.order1
        result = self.assigner.is_robot_available(RobotState.IDLE)
        self.assertFalse(result)
    
    def test_is_robot_available_not_idle(self):
        """Test robot availability when not IDLE."""
        result = self.assigner.is_robot_available(RobotState.MOVING_TO_ITEM)
        self.assertFalse(result)
        
        result = self.assigner.is_robot_available(RobotState.COLLECTING_ITEM)
        self.assertFalse(result)
        
        result = self.assigner.is_robot_available(RobotState.RETURNING)
        self.assertFalse(result)
    
    def test_assign_order_to_robot_success(self):
        """Test successful order assignment to robot."""
        result = self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        self.assertTrue(result)
        self.assertEqual(self.assigner.current_assignment, self.order1)
        self.assertIsNotNone(self.assigner.assignment_start_time)
        self.assertEqual(self.order1.status, OrderStatus.IN_PROGRESS)
        self.assertEqual(self.order1.assigned_robot_id, "ROBOT_001")
        self.assertIsNotNone(self.order1.timestamp_assigned)
        self.assertEqual(self.assigner.statistics.total_assignments, 1)
        self.assertEqual(len(self.assigner.assignment_history), 1)
    
    def test_assign_order_to_robot_not_available(self):
        """Test order assignment when robot is not available."""
        result = self.assigner.assign_order_to_robot(self.order1, RobotState.MOVING_TO_ITEM)
        
        self.assertFalse(result)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertIsNone(self.assigner.assignment_start_time)
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
    
    def test_assign_order_to_robot_already_assigned(self):
        """Test order assignment when robot already has assignment."""
        # Assign first order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        # Try to assign second order
        result = self.assigner.assign_order_to_robot(self.order2, RobotState.IDLE)
        
        self.assertFalse(result)
        self.assertEqual(self.assigner.current_assignment, self.order1)
        self.assertEqual(self.assigner.statistics.total_assignments, 1)
    
    def test_assign_order_to_robot_invalid_order(self):
        """Test order assignment with invalid order."""
        # Create invalid order (already in progress)
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.status = OrderStatus.IN_PROGRESS
        
        result = self.assigner.assign_order_to_robot(invalid_order, RobotState.IDLE)
        
        self.assertFalse(result)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
    
    def test_get_next_order_for_robot_success(self):
        """Test getting next order for robot assignment."""
        # Add order to queue
        self.queue_manager.add_order(self.order1)
        
        result = self.assigner.get_next_order_for_robot(self.queue_manager, RobotState.IDLE)
        
        self.assertEqual(result, self.order1)
        self.assertEqual(self.assigner.current_assignment, self.order1)
        self.assertEqual(self.assigner.statistics.total_assignments, 1)
    
    def test_get_next_order_for_robot_not_available(self):
        """Test getting next order when robot is not available."""
        # Add order to queue
        self.queue_manager.add_order(self.order1)
        
        result = self.assigner.get_next_order_for_robot(self.queue_manager, RobotState.MOVING_TO_ITEM)
        
        self.assertIsNone(result)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
    
    def test_get_next_order_for_robot_empty_queue(self):
        """Test getting next order when queue is empty."""
        result = self.assigner.get_next_order_for_robot(self.queue_manager, RobotState.IDLE)
        
        self.assertIsNone(result)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
    
    def test_update_assignment_progress_no_assignment(self):
        """Test updating assignment progress with no current assignment."""
        result = self.assigner.update_assignment_progress(RobotState.COLLECTING_ITEM, ["ITEM_A1"])
        
        self.assertFalse(result)
    
    def test_update_assignment_progress_partial_completion(self):
        """Test updating assignment progress with partial completion."""
        # Assign order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        # Update with one item collected
        result = self.assigner.update_assignment_progress(RobotState.COLLECTING_ITEM, ["ITEM_A1"])
        
        self.assertTrue(result)
        self.assertEqual(len(self.order1.items_collected), 1)
        self.assertIn("ITEM_A1", self.order1.items_collected)
        self.assertFalse(self.order1.is_complete())
        self.assertIsNotNone(self.assigner.current_assignment)
    
    def test_update_assignment_progress_completion(self):
        """Test updating assignment progress with order completion."""
        # Assign order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        # Update with all items collected
        result = self.assigner.update_assignment_progress(RobotState.COLLECTING_ITEM, ["ITEM_A1", "ITEM_B2"])
        
        self.assertTrue(result)
        self.assertEqual(len(self.order1.items_collected), 2)
        self.assertTrue(self.order1.is_complete())
        self.assertIsNone(self.assigner.current_assignment)  # Assignment cleared
        self.assertEqual(self.assigner.statistics.total_completions, 1)
    
    def test_complete_current_assignment_success(self):
        """Test successful completion of current assignment."""
        # Assign order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        result = self.assigner._complete_current_assignment()
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.COMPLETED)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertIsNone(self.assigner.assignment_start_time)
        self.assertEqual(self.assigner.statistics.total_completions, 1)
        self.assertEqual(self.assigner.statistics.current_assignment_duration, 0.0)
    
    def test_complete_current_assignment_no_assignment(self):
        """Test completing assignment when no current assignment."""
        result = self.assigner._complete_current_assignment()
        
        self.assertFalse(result)
        self.assertEqual(self.assigner.statistics.total_completions, 0)
    
    def test_fail_current_assignment_success(self):
        """Test successful failure of current assignment."""
        # Assign order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        result = self.assigner.fail_current_assignment()
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.FAILED)
        self.assertIsNone(self.assigner.current_assignment)
        self.assertIsNone(self.assigner.assignment_start_time)
        self.assertEqual(self.assigner.statistics.total_failures, 1)
        self.assertEqual(self.assigner.statistics.current_assignment_duration, 0.0)
    
    def test_fail_current_assignment_no_assignment(self):
        """Test failing assignment when no current assignment."""
        result = self.assigner.fail_current_assignment()
        
        self.assertFalse(result)
        self.assertEqual(self.assigner.statistics.total_failures, 0)
    
    def test_get_assignment_status_available(self):
        """Test assignment status when available."""
        status = self.assigner.get_assignment_status()
        self.assertEqual(status, AssignmentStatus.AVAILABLE)
    
    def test_get_assignment_status_assigned(self):
        """Test assignment status when assigned."""
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        status = self.assigner.get_assignment_status()
        self.assertEqual(status, AssignmentStatus.ASSIGNED)
    
    def test_get_current_assignment(self):
        """Test getting current assignment."""
        self.assertIsNone(self.assigner.get_current_assignment())
        
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        current = self.assigner.get_current_assignment()
        self.assertEqual(current, self.order1)
    
    def test_get_assignment_statistics(self):
        """Test getting assignment statistics."""
        stats = self.assigner.get_assignment_statistics()
        
        self.assertIn('assignment_status', stats)
        self.assertIn('robot_id', stats)
        self.assertIn('current_assignment', stats)
        self.assertIn('assignment_duration', stats)
        self.assertIn('statistics', stats)
        
        self.assertEqual(stats['assignment_status'], AssignmentStatus.AVAILABLE.value)
        self.assertEqual(stats['robot_id'], "ROBOT_001")
        self.assertIsNone(stats['current_assignment'])
        self.assertEqual(stats['assignment_duration'], 0.0)
    
    def test_validate_order_for_assignment_valid(self):
        """Test order validation with valid order."""
        result = self.assigner._validate_order_for_assignment(self.order1)
        self.assertTrue(result)
    
    def test_validate_order_for_assignment_invalid_missing_order_id(self):
        """Test order validation with missing order ID."""
        invalid_order = Order("", ["ITEM_A1"], [(1, 1)])
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_invalid_missing_item_ids(self):
        """Test order validation with missing item IDs."""
        invalid_order = Order("ORD_INVALID", None, [(1, 1)])
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_invalid_missing_positions(self):
        """Test order validation with missing positions."""
        # Create order with valid positions first, then modify to None
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.item_positions = None
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_already_in_progress(self):
        """Test order validation with order already in progress."""
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.status = OrderStatus.IN_PROGRESS
        
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_already_completed(self):
        """Test order validation with order already completed."""
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.status = OrderStatus.COMPLETED
        
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_already_failed(self):
        """Test order validation with order already failed."""
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.status = OrderStatus.FAILED
        
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_for_assignment_already_assigned(self):
        """Test order validation with order already assigned to robot."""
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.assigned_robot_id = "ROBOT_002"
        
        result = self.assigner._validate_order_for_assignment(invalid_order)
        self.assertFalse(result)
    
    def test_clear_assignment(self):
        """Test clearing current assignment."""
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        self.assigner.clear_assignment()
        
        self.assertIsNone(self.assigner.current_assignment)
        self.assertIsNone(self.assigner.assignment_start_time)
        self.assertEqual(self.assigner.statistics.current_assignment_duration, 0.0)
    
    def test_reset_statistics(self):
        """Test resetting assignment statistics."""
        # Add some activity
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        self.assigner._complete_current_assignment()
        
        self.assigner.reset_statistics()
        
        self.assertEqual(self.assigner.statistics.total_assignments, 0)
        self.assertEqual(self.assigner.statistics.total_completions, 0)
        self.assertEqual(self.assigner.statistics.total_failures, 0)
        self.assertEqual(len(self.assigner.assignment_times), 0)
        self.assertEqual(len(self.assigner.completion_times), 0)
    
    def test_get_debug_info(self):
        """Test get_debug_info method."""
        debug_info = self.assigner.get_debug_info()
        
        self.assertIn('assigner_status', debug_info)
        self.assertIn('current_assignment', debug_info)
        self.assertIn('assignment_history', debug_info)
        self.assertIn('assigner_timing', debug_info)
        
        self.assertIsInstance(debug_info['current_assignment'], dict)
        self.assertIsInstance(debug_info['assignment_history'], list)
        self.assertIsInstance(debug_info['assigner_timing'], dict)
    
    def test_assignment_timing_tracking(self):
        """Test assignment timing tracking."""
        # Assign order
        self.assigner.assign_order_to_robot(self.order1, RobotState.IDLE)
        
        # Simulate some time passing
        time.sleep(0.1)
        
        # Complete assignment
        self.assigner._complete_current_assignment()
        
        self.assertGreater(len(self.assigner.assignment_times), 0)
        self.assertGreater(self.assigner.statistics.average_assignment_time, 0)
        self.assertEqual(self.assigner.statistics.total_completions, 1)


if __name__ == '__main__':
    unittest.main() 