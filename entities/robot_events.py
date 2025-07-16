from typing import Dict, Any, Optional, Tuple
from core.events import EventSystem, EventType, EventPriority
from core.layout.coordinate import Coordinate

class RobotEvents:
    """
    Handles robot event emission and integration with the EventSystem.
    """
    
    def __init__(self, robot, event_system: EventSystem):
        self.robot = robot
        self.event_system = event_system
        self.last_position: Optional[Tuple[int, int]] = None
        self.last_state = None
        self.last_collection_progress: float = 0.0
    
    async def emit_state_change(self, old_state, new_state):
        """Emit robot state change event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_STATE_CHANGED,
            data={
                'robot_id': self.robot.robot_id,
                'old_state': str(old_state),
                'new_state': str(new_state),
                'timestamp': self.robot.movement.movement_start_time
            },
            source='robot',
            priority=EventPriority.MEDIUM
        )
    
    async def emit_position_update(self, position: Tuple[int, int], progress: float = None):
        """Emit robot position update event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_MOVED,
            data={
                'robot_id': self.robot.robot_id,
                'position': position,
                'progress': progress,
                'direction': self.robot.direction,
                'is_moving': self.robot.movement.is_moving
            },
            source='robot',
            priority=EventPriority.LOW
        )
    
    async def emit_item_collection_start(self, item_id: str, position: Tuple[int, int]):
        """Emit item collection start event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_STATE_CHANGED,
            data={
                'robot_id': self.robot.robot_id,
                'event': 'collection_start',
                'item_id': item_id,
                'position': position,
                'items_held': len(self.robot.items_held),
                'max_capacity': self.robot.collection.max_items
            },
            source='robot',
            priority=EventPriority.MEDIUM
        )
    
    async def emit_item_collection_complete(self, item_id: str, position: Tuple[int, int]):
        """Emit item collection complete event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_STATE_CHANGED,
            data={
                'robot_id': self.robot.robot_id,
                'event': 'collection_complete',
                'item_id': item_id,
                'position': position,
                'items_held': len(self.robot.items_held),
                'collection_time': self.robot.collection.collection_time
            },
            source='robot',
            priority=EventPriority.MEDIUM
        )
    
    async def emit_order_assigned(self, order):
        """Emit order assignment event."""
        await self.event_system.emit(
            event_type=EventType.ORDER_ASSIGNED,
            data={
                'robot_id': self.robot.robot_id,
                'order_id': order.order_id,
                'item_count': len(order.item_ids),
                'item_positions': order.item_positions,
                'timestamp': order.timestamp_assigned
            },
            source='robot',
            priority=EventPriority.MEDIUM
        )
    
    async def emit_order_completed(self, order):
        """Emit order completion event."""
        await self.event_system.emit(
            event_type=EventType.ORDER_COMPLETED,
            data={
                'robot_id': self.robot.robot_id,
                'order_id': order.order_id,
                'total_distance': order.total_distance,
                'efficiency_score': order.efficiency_score,
                'completion_time': order.timestamp_completed - order.timestamp_assigned if order.timestamp_completed and order.timestamp_assigned else None,
                'items_collected': order.items_collected
            },
            source='robot',
            priority=EventPriority.MEDIUM
        )
    
    async def emit_movement_progress(self, progress: float, target_position: Tuple[int, int]):
        """Emit movement progress event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_MOVED,
            data={
                'robot_id': self.robot.robot_id,
                'progress': progress,
                'target_position': target_position,
                'current_position': self.robot.position,
                'movement_duration': self.robot.movement.movement_duration
            },
            source='robot',
            priority=EventPriority.LOW
        )
    
    async def emit_path_update(self, path: list, current_target: Coordinate):
        """Emit path update event."""
        await self.event_system.emit(
            event_type=EventType.ROBOT_MOVED,
            data={
                'robot_id': self.robot.robot_id,
                'path_length': len(path),
                'current_target': (current_target.aisle, current_target.rack) if current_target else None,
                'remaining_items': len(self.robot.navigation.get_remaining_items()),
                'collected_items': len(self.robot.navigation.get_collected_items())
            },
            source='robot',
            priority=EventPriority.LOW
        )
    
    async def emit_robot_stats(self):
        """Emit robot statistics event."""
        collection_stats = self.robot.get_collection_stats()
        order_stats = self.robot.get_order_stats()
        
        await self.event_system.emit(
            event_type=EventType.ROBOT_STATE_CHANGED,
            data={
                'robot_id': self.robot.robot_id,
                'event': 'stats_update',
                'state': str(self.robot.state),
                'position': self.robot.position,
                'items_held': len(self.robot.items_held),
                'collection_stats': collection_stats,
                'order_stats': order_stats,
                'is_available': self.robot.is_available_for_order()
            },
            source='robot',
            priority=EventPriority.LOW
        )
    
    async def emit_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Emit robot error event."""
        await self.event_system.emit(
            event_type=EventType.SYSTEM_ERROR,
            data={
                'robot_id': self.robot.robot_id,
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {},
                'state': str(self.robot.state),
                'position': self.robot.position
            },
            source='robot',
            priority=EventPriority.HIGH
        )
    
    def should_emit_position_update(self, current_position: Tuple[int, int]) -> bool:
        """Check if position update should be emitted (avoid spam)."""
        if self.last_position != current_position:
            self.last_position = current_position
            return True
        return False
    
    def should_emit_state_update(self, current_state) -> bool:
        """Check if state update should be emitted."""
        if self.last_state != current_state:
            self.last_state = current_state
            return True
        return False
    
    def should_emit_collection_progress(self, current_progress: float) -> bool:
        """Check if collection progress should be emitted (throttle updates)."""
        # Emit every 10% progress or significant changes
        if abs(current_progress - self.last_collection_progress) >= 0.1:
            self.last_collection_progress = current_progress
            return True
        return False 