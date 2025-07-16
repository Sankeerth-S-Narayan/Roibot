"""
Robot Order Assignment System for Phase 5: Order Management System

This module provides the RobotOrderAssigner class that handles robot assignment
logic with single robot support and automatic order assignment when robot becomes
available. Manages order processing state and completion detection.

Key Features:
- Single robot assignment (ROBOT_001)
- Automatic order assignment when robot available
- Order processing state management
- Order completion detection
- Assignment validation and error handling
- Integration with existing robot state machine

Author: Roibot Development Team
Version: 1.0
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

from .robot_orders import Order, OrderStatus
from .order_queue_manager import OrderQueueManager
from entities.robot_state import RobotState


class AssignmentStatus(Enum):
    """Enumeration for assignment status."""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class AssignmentStatistics:
    """Statistics for robot order assignment."""
    total_assignments: int = 0
    total_completions: int = 0
    total_failures: int = 0
    average_assignment_time: float = 0.0
    average_completion_time: float = 0.0
    current_assignment_duration: float = 0.0
    robot_utilization_rate: float = 0.0


class RobotOrderAssigner:
    """
    Handles robot assignment logic with single robot support and automatic order assignment.
    
    Manages order assignment to ROBOT_001, tracks assignment state, and handles
    order completion detection. Integrates with existing robot state machine.
    """
    
    def __init__(self, robot_id: str = "ROBOT_001"):
        """
        Initialize the robot order assigner.
        
        Args:
            robot_id: ID of the robot to assign orders to
        """
        self.robot_id = robot_id
        self.current_assignment: Optional[Order] = None
        self.assignment_start_time: Optional[float] = None
        self.assignment_history: List[Dict[str, Any]] = []
        
        # Statistics tracking
        self.statistics = AssignmentStatistics()
        self.assigner_start_time = time.time()
        
        # Performance tracking
        self.assignment_times: List[float] = []
        self.completion_times: List[float] = []
        
        print(f"🤖 RobotOrderAssigner initialized for {robot_id}")
    
    def is_robot_available(self, robot_state: RobotState) -> bool:
        """
        Check if robot is available for order assignment.
        
        Args:
            robot_state: Current robot state
            
        Returns:
            True if robot is available, False otherwise
        """
        # Robot is available if it's IDLE and has no current assignment
        return (robot_state == RobotState.IDLE and 
                self.current_assignment is None)
    
    def assign_order_to_robot(self, order: Order, robot_state: RobotState) -> bool:
        """
        Assign an order to the robot.
        
        Args:
            order: Order object to assign
            robot_state: Current robot state
            
        Returns:
            True if assignment successful, False otherwise
        """
        try:
            # Check if robot is available
            if not self.is_robot_available(robot_state):
                print(f"⚠️  Robot {self.robot_id} is not available (state: {robot_state.value})")
                return False
            
            # Check if order is valid for assignment
            if not self._validate_order_for_assignment(order):
                print(f"❌ Order {order.order_id} is not valid for assignment")
                return False
            
            # Assign order to robot
            self.current_assignment = order
            self.assignment_start_time = time.time()
            
            # Update order status
            order.status = OrderStatus.IN_PROGRESS
            order.assigned_robot_id = self.robot_id
            order.timestamp_assigned = time.time()
            
            # Update statistics
            self.statistics.total_assignments += 1
            
            # Add to assignment history
            assignment_record = {
                'order_id': order.order_id,
                'robot_id': self.robot_id,
                'assignment_time': time.time(),
                'robot_state': robot_state.value,
                'order_items': len(order.item_ids)
            }
            self.assignment_history.append(assignment_record)
            
            print(f"🎯 Assigned order {order.order_id} to {self.robot_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error assigning order to robot: {e}")
            return False
    
    def get_next_order_for_robot(self, queue_manager: OrderQueueManager, robot_state: RobotState) -> Optional[Order]:
        """
        Get the next order for robot assignment.
        
        Args:
            queue_manager: Order queue manager
            robot_state: Current robot state
            
        Returns:
            Next order for assignment or None if no assignment possible
        """
        # Check if robot is available
        if not self.is_robot_available(robot_state):
            return None
        
        # Get next order from queue
        next_order = queue_manager.get_next_order()
        
        if next_order is None:
            return None
        
        # Try to assign the order
        if self.assign_order_to_robot(next_order, robot_state):
            return next_order
        else:
            return None
    
    def update_assignment_progress(self, robot_state: RobotState, collected_items: List[str]) -> bool:
        """
        Update assignment progress based on robot state and collected items.
        
        Args:
            robot_state: Current robot state
            collected_items: List of items collected by robot
            
        Returns:
            True if assignment updated successfully, False otherwise
        """
        if self.current_assignment is None:
            return False
        
        try:
            # Update order with collected items
            for item_id in collected_items:
                if item_id in self.current_assignment.item_ids:
                    self.current_assignment.mark_item_collected(item_id)
            
            # Check if order is complete
            if self.current_assignment.is_complete():
                return self._complete_current_assignment()
            
            # Update assignment duration
            if self.assignment_start_time:
                self.statistics.current_assignment_duration = time.time() - self.assignment_start_time
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating assignment progress: {e}")
            return False
    
    def _complete_current_assignment(self) -> bool:
        """
        Complete the current assignment.
        
        Returns:
            True if completion successful, False otherwise
        """
        if self.current_assignment is None:
            return False
        
        try:
            # Calculate assignment time
            assignment_time = 0.0
            if self.assignment_start_time:
                assignment_time = time.time() - self.assignment_start_time
            
            # Update statistics
            self.statistics.total_completions += 1
            self.assignment_times.append(assignment_time)
            self.statistics.average_assignment_time = sum(self.assignment_times) / len(self.assignment_times)
            
            # Update order completion
            self.current_assignment.complete_order(
                time.time(),
                self.current_assignment.total_distance,
                self.current_assignment.efficiency_score
            )
            
            # Clear current assignment
            completed_order = self.current_assignment
            self.current_assignment = None
            self.assignment_start_time = None
            self.statistics.current_assignment_duration = 0.0
            
            print(f"✅ Completed assignment for order {completed_order.order_id} (time: {assignment_time:.2f}s)")
            return True
            
        except Exception as e:
            print(f"❌ Error completing assignment: {e}")
            return False
    
    def fail_current_assignment(self) -> bool:
        """
        Fail the current assignment.
        
        Returns:
            True if failure successful, False otherwise
        """
        if self.current_assignment is None:
            return False
        
        try:
            # Update statistics
            self.statistics.total_failures += 1
            
            # Update order failure
            self.current_assignment.fail_order()
            
            # Clear current assignment
            failed_order = self.current_assignment
            self.current_assignment = None
            self.assignment_start_time = None
            self.statistics.current_assignment_duration = 0.0
            
            print(f"❌ Failed assignment for order {failed_order.order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error failing assignment: {e}")
            return False
    
    def get_assignment_status(self) -> AssignmentStatus:
        """
        Get the current assignment status.
        
        Returns:
            AssignmentStatus enum value
        """
        if self.current_assignment is None:
            return AssignmentStatus.AVAILABLE
        else:
            return AssignmentStatus.ASSIGNED
    
    def get_current_assignment(self) -> Optional[Order]:
        """
        Get the current assignment.
        
        Returns:
            Current order assignment or None
        """
        return self.current_assignment
    
    def get_assignment_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive assignment statistics.
        
        Returns:
            Dictionary with assignment statistics
        """
        total_time = time.time() - self.assigner_start_time
        utilization_rate = 0.0
        if total_time > 0:
            utilization_rate = (self.statistics.current_assignment_duration / total_time) * 100
        
        return {
            'assignment_status': self.get_assignment_status().value,
            'robot_id': self.robot_id,
            'current_assignment': self.current_assignment.order_id if self.current_assignment else None,
            'assignment_duration': self.statistics.current_assignment_duration,
            'statistics': {
                'total_assignments': self.statistics.total_assignments,
                'total_completions': self.statistics.total_completions,
                'total_failures': self.statistics.total_failures,
                'average_assignment_time': self.statistics.average_assignment_time,
                'average_completion_time': self.statistics.average_completion_time,
                'robot_utilization_rate': utilization_rate
            }
        }
    
    def _validate_order_for_assignment(self, order: Order) -> bool:
        """
        Validate an order for assignment.
        
        Args:
            order: Order object to validate
            
        Returns:
            True if order is valid for assignment, False otherwise
        """
        try:
            # Check if order has required attributes
            if not hasattr(order, 'order_id') or not order.order_id:
                return False
            
            if not hasattr(order, 'item_ids') or not order.item_ids:
                return False
            
            if not hasattr(order, 'item_positions') or not order.item_positions:
                return False
            
            # Check if order is in a valid state for assignment
            if order.status not in [OrderStatus.PENDING]:
                return False
            
            # Check if robot is already assigned to this order
            if hasattr(order, 'assigned_robot_id') and order.assigned_robot_id:
                return False
            
            return True
            
        except Exception:
            return False
    
    def clear_assignment(self):
        """Clear the current assignment."""
        if self.current_assignment:
            print(f"🧹 Cleared assignment for order {self.current_assignment.order_id}")
        
        self.current_assignment = None
        self.assignment_start_time = None
        self.statistics.current_assignment_duration = 0.0
    
    def reset_statistics(self):
        """Reset assignment statistics."""
        self.statistics = AssignmentStatistics()
        self.assignment_times.clear()
        self.completion_times.clear()
        self.assigner_start_time = time.time()
        
        print("📊 Assignment statistics reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information for the assigner.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'assigner_status': self.get_assignment_statistics(),
            'current_assignment': {
                'order_id': self.current_assignment.order_id if self.current_assignment else None,
                'status': self.current_assignment.status.value if self.current_assignment else None,
                'items': len(self.current_assignment.item_ids) if self.current_assignment else 0,
                'collected_items': len(self.current_assignment.items_collected) if self.current_assignment else 0
            },
            'assignment_history': self.assignment_history[-5:] if self.assignment_history else [],  # Last 5 assignments
            'assigner_timing': {
                'assigner_start_time': self.assigner_start_time,
                'current_time': time.time(),
                'assigner_duration': time.time() - self.assigner_start_time
            }
        } 