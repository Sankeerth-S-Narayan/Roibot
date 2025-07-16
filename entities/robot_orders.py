from typing import List, Optional, Dict, Any
from enum import Enum
import time
from .robot_state import RobotState

class OrderStatus(Enum):
    """Enumeration for order status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Order:
    """Represents an order with items to be collected."""
    
    def __init__(self, order_id: str, item_ids: List[str], item_positions: List[tuple]):
        self.order_id = order_id
        self.item_ids = item_ids
        self.item_positions = item_positions  # List of (aisle, rack) tuples
        
        # Validate positions
        self._validate_positions()
        
        self.status = OrderStatus.PENDING
        self.assigned_robot_id: Optional[str] = None
        self.timestamp_assigned: Optional[float] = None
        self.timestamp_completed: Optional[float] = None
        self.items_collected: List[str] = []
        self.total_distance: float = 0.0
        self.efficiency_score: float = 0.0
    
    def _validate_positions(self):
        """Validate that all item positions are within warehouse bounds."""
        if self.item_positions is None:
            raise ValueError("Item positions cannot be None")
            
        for i, position in enumerate(self.item_positions):
            if not isinstance(position, tuple) or len(position) != 2:
                raise ValueError(f"Invalid position format at index {i}: {position}")
            
            aisle, rack = position
            if not (1 <= aisle <= 25 and 1 <= rack <= 20):
                raise ValueError(f"Position {position} is outside warehouse bounds (1-25, 1-20)")
    
    def assign_to_robot(self, robot_id: str, timestamp: float):
        """Assign this order to a robot."""
        self.assigned_robot_id = robot_id
        self.timestamp_assigned = timestamp
        self.status = OrderStatus.IN_PROGRESS
    
    def mark_item_collected(self, item_id: str) -> bool:
        """Mark an item as collected."""
        if item_id in self.item_ids and item_id not in self.items_collected:
            self.items_collected.append(item_id)
            return True
        return False
    
    def is_complete(self) -> bool:
        """Check if all items in the order have been collected."""
        return len(self.items_collected) == len(self.item_ids)
    
    def get_remaining_items(self) -> List[str]:
        """Get list of remaining items to collect."""
        return [item for item in self.item_ids if item not in self.items_collected]
    
    def get_remaining_positions(self) -> List[tuple]:
        """Get positions of remaining items to collect."""
        remaining_items = self.get_remaining_items()
        remaining_positions = []
        for item_id in remaining_items:
            if item_id in self.item_ids:
                index = self.item_ids.index(item_id)
                if index < len(self.item_positions):
                    remaining_positions.append(self.item_positions[index])
        return remaining_positions
    
    def complete_order(self, timestamp: float, total_distance: float, efficiency_score: float):
        """Mark order as completed."""
        self.status = OrderStatus.COMPLETED
        self.timestamp_completed = timestamp
        self.total_distance = total_distance
        self.efficiency_score = efficiency_score
    
    def fail_order(self):
        """Mark order as failed."""
        self.status = OrderStatus.FAILED
    
    def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics."""
        return {
            'order_id': self.order_id,
            'status': self.status.value,
            'total_items': len(self.item_ids),
            'collected_items': len(self.items_collected),
            'remaining_items': len(self.get_remaining_items()),
            'assigned_robot': self.assigned_robot_id,
            'total_distance': self.total_distance,
            'efficiency_score': self.efficiency_score,
            'completion_time': self.timestamp_completed - self.timestamp_assigned if self.timestamp_completed and self.timestamp_assigned else None
        }

class RobotOrders:
    """
    Handles order assignment and management for the robot.
    """
    
    def __init__(self, robot):
        self.robot = robot
        self.current_order: Optional[Order] = None
        self.order_queue: List[Order] = []
        self.completed_orders: List[Order] = []
        self.failed_orders: List[Order] = []
    
    def assign_order(self, order: Order) -> bool:
        """
        Assign an order to the robot.
        
        Args:
            order: Order object to assign
            
        Returns:
            True if assignment successful, False otherwise
        """
        # Check if robot is available (IDLE state)
        if self.robot.state != RobotState.IDLE:
            return False
        
        # Check if robot already has an order
        if self.current_order is not None:
            return False
        
        # Assign order to robot
        order.assign_to_robot(self.robot.robot_id, time.time())
        self.current_order = order
        
        # Set up robot for order execution
        self._setup_robot_for_order(order)
        
        return True
    
    def _setup_robot_for_order(self, order: Order):
        """Set up robot components for order execution."""
        # Set item targets for navigation
        self.robot.set_item_targets(order.item_positions)
        
        # Set collection targets
        self.robot.set_collection_targets(order.item_ids)
        
        # Change robot state to start moving
        self.robot.set_state(RobotState.MOVING_TO_ITEM)
    
    def update_order_progress(self, current_time: float):
        """
        Update order progress based on robot state and actions.
        
        Args:
            current_time: Current simulation time
        """
        if not self.current_order:
            return
        
        # Update order based on robot state
        if self.robot.state == RobotState.COLLECTING_ITEM:
            # Check if collection is complete
            if self.robot.update_collection(current_time):
                # Item collection completed
                if self.robot.is_collecting():
                    # Get the current item being collected
                    current_item = self._get_current_collecting_item()
                    if current_item:
                        self.current_order.mark_item_collected(current_item)
                
                # Check if all items collected
                if self.current_order.is_complete():
                    self._complete_current_order(current_time)
                else:
                    # Move to next item
                    self.robot.set_state(RobotState.MOVING_TO_ITEM)
    
    def _get_current_collecting_item(self) -> Optional[str]:
        """Get the item ID currently being collected."""
        # This is a simplified implementation
        # In a real system, you'd track which specific item is being collected
        remaining_items = self.current_order.get_remaining_items()
        if remaining_items:
            return remaining_items[0]
        return None
    
    def _complete_current_order(self, current_time: float):
        """Complete the current order."""
        if not self.current_order:
            return
        
        # Calculate order statistics
        total_distance = self._calculate_order_distance()
        efficiency_score = self._calculate_efficiency_score()
        
        # Mark order as completed
        self.current_order.complete_order(current_time, total_distance, efficiency_score)
        
        # Move order to completed list
        self.completed_orders.append(self.current_order)
        
        # Reset robot for next order
        self.robot.set_state(RobotState.RETURNING)
        self.current_order = None
    
    def _calculate_order_distance(self) -> float:
        """Calculate total distance traveled for the order."""
        # This is a simplified calculation
        # In a real system, you'd track actual distance traveled
        return len(self.current_order.item_ids) * 10.0  # Simplified distance
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score for the order."""
        # This is a simplified calculation
        # In a real system, you'd use actual metrics
        if self.current_order:
            collected = len(self.current_order.items_collected)
            total = len(self.current_order.item_ids)
            return collected / total if total > 0 else 0.0
        return 0.0
    
    def get_current_order(self) -> Optional[Order]:
        """Get the currently assigned order."""
        return self.current_order
    
    def get_order_queue(self) -> List[Order]:
        """Get the order queue."""
        return self.order_queue.copy()
    
    def get_completed_orders(self) -> List[Order]:
        """Get list of completed orders."""
        return self.completed_orders.copy()
    
    def get_failed_orders(self) -> List[Order]:
        """Get list of failed orders."""
        return self.failed_orders.copy()
    
    def add_to_queue(self, order: Order):
        """Add an order to the queue."""
        self.order_queue.append(order)
    
    def get_next_queued_order(self) -> Optional[Order]:
        """Get the next order from the queue."""
        if self.order_queue:
            return self.order_queue.pop(0)
        return None
    
    def is_available_for_order(self) -> bool:
        """Check if robot is available for new order assignment."""
        return (self.robot.state == RobotState.IDLE and 
                self.current_order is None)
    
    def get_order_stats(self) -> Dict[str, Any]:
        """Get comprehensive order statistics."""
        return {
            'current_order': self.current_order.get_order_stats() if self.current_order else None,
            'queue_length': len(self.order_queue),
            'completed_count': len(self.completed_orders),
            'failed_count': len(self.failed_orders),
            'is_available': self.is_available_for_order()
        }
    
    def reset_orders(self):
        """Reset all order state."""
        self.current_order = None
        self.order_queue.clear()
        self.completed_orders.clear()
        self.failed_orders.clear() 