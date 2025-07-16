from enum import Enum, auto
from typing import List, Optional, Tuple
from .robot_movement import RobotMovement
from .robot_navigation import RobotNavigation
from .robot_collection import RobotCollection
from .robot_orders import RobotOrders, Order
from .robot_events import RobotEvents
from .robot_state import RobotState

class Robot:
    """
    Represents a warehouse robot entity with a unique identifier and state machine.
    """
    _id_counter = 1

    def __init__(self, config=None, event_system=None):
        self.robot_id = f"ROBOT_{Robot._id_counter:03d}"
        Robot._id_counter += 1
        self.state = RobotState.IDLE
        self.position: Optional[Tuple[int, int]] = None  # (aisle, rack)
        self.items_held: List[str] = []
        self.direction: str = "FORWARD"  # or "REVERSE"
        self.order_assignment = None
        
        # Initialize movement, navigation, collection, orders, and events components
        self.movement = RobotMovement(self, config)
        self.navigation = RobotNavigation(self)
        self.collection = RobotCollection(self, config)
        self.orders = RobotOrders(self)
        self.events = RobotEvents(self, event_system) if event_system else None

    def set_state(self, new_state: RobotState):
        """
        Transition to a new state, validating allowed transitions.
        """
        old_state = self.state
        
        # Allow setting the same state (no-op)
        if new_state == self.state:
            return
        
        allowed = {
            RobotState.IDLE: [RobotState.MOVING_TO_ITEM],
            RobotState.MOVING_TO_ITEM: [RobotState.COLLECTING_ITEM, RobotState.RETURNING],
            RobotState.COLLECTING_ITEM: [RobotState.MOVING_TO_ITEM, RobotState.RETURNING],
            RobotState.RETURNING: [RobotState.IDLE],
        }
        if new_state in allowed[self.state]:
            self.state = new_state
            # Emit state change event if events system is available
            if self.events and self.events.should_emit_state_update(new_state):
                self._emit_event_safe(self.events.emit_state_change(old_state, new_state))
        else:
            raise ValueError(f"Invalid state transition: {self.state} -> {new_state}. Allowed transitions from {self.state}: {allowed[self.state]}")
    
    def _emit_event_safe(self, coro):
        """Safely emit an async event, handling both async and sync contexts."""
        import asyncio
        try:
            # Try to create task in existing event loop
            asyncio.create_task(coro)
        except RuntimeError:
            # No event loop running, try to run in new event loop
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(coro)
                loop.close()
            except Exception:
                # If all else fails, skip event emission silently
                pass

    def update_movement(self, current_time: float):
        """Update robot movement in the simulation loop."""
        self.movement.update(current_time)
        
        # Emit position update if events system is available
        if self.events and self.position and self.events.should_emit_position_update(self.position):
            self._emit_event_safe(self.events.emit_position_update(
                self.position, 
                self.movement.get_progress()
            ))

    def update_collection(self, current_time: float) -> bool:
        """Update collection progress and return True if collection is complete."""
        result = self.collection.update_collection(current_time)
        
        # Emit collection progress if events system is available
        if self.events and self.collection.is_collecting():
            progress = self.collection.get_collection_progress()
            if self.events.should_emit_collection_progress(progress):
                self._emit_event_safe(self.events.emit_movement_progress(
                    progress, 
                    self.position or (0, 0)
                ))
        
        return result

    def update_order_progress(self, current_time: float):
        """Update order progress based on robot state and actions."""
        self.orders.update_order_progress(current_time)

    def assign_order(self, order: Order) -> bool:
        """Assign an order to the robot."""
        result = self.orders.assign_order(order)
        
        # Emit order assignment event if successful
        if result and self.events:
            self._emit_event_safe(self.events.emit_order_assigned(order))
        
        return result

    def set_item_targets(self, item_positions: List[Tuple[int, int]]):
        """Set target items for collection in ascending order."""
        self.navigation.set_item_targets(item_positions)

    def set_collection_targets(self, item_ids: List[str]):
        """Set target item IDs for collection."""
        self.collection.set_target_items(item_ids)

    def start_item_collection(self, item_id: str, item_position: Tuple[int, int], current_time: float):
        """Start collecting an item at the specified position."""
        self.collection.start_collection(item_id, item_position, current_time)
        
        # Emit collection start event if events system is available
        if self.events:
            self._emit_event_safe(self.events.emit_item_collection_start(item_id, item_position))

    def get_next_target(self):
        """Get the next target item position."""
        return self.navigation.get_next_target()

    def calculate_path_to_next_item(self):
        """Calculate optimal path to the next item using snake pattern."""
        return self.navigation.calculate_path_to_next_item()

    def is_all_items_collected(self) -> bool:
        """Check if all target items have been processed."""
        return self.navigation.is_all_items_collected()

    def is_collecting(self) -> bool:
        """Check if robot is currently collecting an item."""
        return self.collection.is_collecting()

    def get_collection_progress(self) -> float:
        """Get collection progress as a percentage."""
        return self.collection.get_collection_progress()

    def get_collection_stats(self):
        """Get collection statistics."""
        return self.collection.get_collection_stats()

    def get_current_order(self):
        """Get the currently assigned order."""
        return self.orders.get_current_order()

    def is_available_for_order(self) -> bool:
        """Check if robot is available for new order assignment."""
        return self.orders.is_available_for_order()

    def get_order_stats(self):
        """Get order statistics."""
        return self.orders.get_order_stats()

    def reset(self):
        """
        Reset the robot to its default state (IDLE, no items, no order, default direction).
        """
        self.state = RobotState.IDLE
        self.position = None
        self.items_held.clear()
        self.direction = "FORWARD"
        self.order_assignment = None
        self.movement.stop_movement()
        self.navigation.reset_navigation()
        self.collection.reset_collection()
        self.orders.reset_orders()

    def load_config(self, config):
        """
        Load robot configuration from a config dictionary or object.
        """
        self.movement.load_config(config.get('movement', {}))
        self.collection.load_config(config.get('collection', {})) 