"""
Direction Optimizer for Phase 4 Task 2

Handles advanced direction optimization, snake pattern integration,
smooth direction changes, and direction state tracking.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time

from .coordinate import Coordinate
from .snake_pattern import SnakePattern, Direction
from .warehouse_layout import WarehouseLayoutManager


class DirectionState(Enum):
    """Enumeration for direction states."""
    FORWARD = "forward"
    REVERSE = "reverse"
    CHANGING = "changing"
    IDLE = "idle"


@dataclass
class DirectionChange:
    """Represents a direction change event."""
    from_direction: Direction
    to_direction: Direction
    timestamp: float
    position: Coordinate
    reason: str


class DirectionOptimizer:
    """
    Advanced direction optimizer with snake pattern integration.
    
    Features:
    - Direction choice based on shortest path
    - Snake pattern integrity maintenance
    - Smooth direction change logic
    - Direction state tracking
    - Integration with robot movement
    - Direction change event emission
    """
    
    def __init__(self, warehouse_layout: WarehouseLayoutManager, snake_pattern: SnakePattern):
        self.warehouse_layout = warehouse_layout
        self.snake_pattern = snake_pattern
        self.current_direction = Direction.FORWARD
        self.direction_state = DirectionState.IDLE
        self.direction_changes: List[DirectionChange] = []
        self.last_change_time = 0.0
        self.change_cooldown = 0.1  # seconds
        
    def optimize_direction_for_path(self, current_pos: Coordinate, target_pos: Coordinate, 
                                  path_coords: List[Coordinate]) -> Direction:
        """
        Optimize direction based on shortest path and snake pattern rules.
        
        Args:
            current_pos: Current robot position
            target_pos: Target position
            path_coords: Calculated path coordinates
            
        Returns:
            Optimal direction for the path
        """
        # If same aisle, use snake pattern rules
        if current_pos.aisle == target_pos.aisle:
            return self._get_snake_pattern_direction(current_pos, target_pos)
        
        # For different aisles, calculate optimal direction
        return self._calculate_optimal_direction(current_pos, target_pos, path_coords)
    
    def _get_snake_pattern_direction(self, current_pos: Coordinate, target_pos: Coordinate) -> Direction:
        """
        Get direction based on snake pattern rules.
        
        Args:
            current_pos: Current position
            target_pos: Target position
            
        Returns:
            Direction based on snake pattern
        """
        aisle = current_pos.aisle
        
        if aisle % 2 == 1:  # Odd aisle - left to right
            if target_pos.rack > current_pos.rack:
                return Direction.FORWARD
            else:
                return Direction.REVERSE
        else:  # Even aisle - right to left
            if target_pos.rack < current_pos.rack:
                return Direction.REVERSE
            else:
                return Direction.FORWARD
    
    def _calculate_optimal_direction(self, current_pos: Coordinate, target_pos: Coordinate,
                                   path_coords: List[Coordinate]) -> Direction:
        """
        Calculate optimal direction for cross-aisle movement.
        
        Args:
            current_pos: Current position
            target_pos: Target position
            path_coords: Path coordinates
            
        Returns:
            Optimal direction
        """
        # Calculate forward and reverse distances
        forward_distance = self._calculate_forward_distance(current_pos, target_pos)
        reverse_distance = self._calculate_reverse_distance(current_pos, target_pos)
        
        # Consider current direction to minimize changes
        direction_penalty = 0.0
        if self.current_direction == Direction.REVERSE:
            direction_penalty = 2.0  # Penalty for changing direction
        
        # Choose direction with shortest total distance
        if forward_distance <= reverse_distance + direction_penalty:
            return Direction.FORWARD
        else:
            return Direction.REVERSE
    
    def _calculate_forward_distance(self, start: Coordinate, target: Coordinate) -> float:
        """Calculate forward distance using Manhattan distance."""
        return abs(target.aisle - start.aisle) + abs(target.rack - start.rack)
    
    def _calculate_reverse_distance(self, start: Coordinate, target: Coordinate) -> float:
        """Calculate reverse distance considering warehouse bounds."""
        # For reverse, go to opposite end and then to target
        if start.aisle <= 12:  # First half
            reverse_start = Coordinate(25, start.rack)
        else:  # Second half
            reverse_start = Coordinate(1, start.rack)
        
        distance_to_reverse = abs(reverse_start.aisle - start.aisle) + abs(reverse_start.rack - start.rack)
        distance_from_reverse = abs(target.aisle - reverse_start.aisle) + abs(target.rack - reverse_start.rack)
        
        return distance_to_reverse + distance_from_reverse
    
    def change_direction(self, new_direction: Direction, position: Coordinate, reason: str = "") -> bool:
        """
        Change direction with smooth transition logic.
        
        Args:
            new_direction: New direction to change to
            position: Current position
            reason: Reason for direction change
            
        Returns:
            True if direction change successful, False otherwise
        """
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_change_time < self.change_cooldown:
            return False
        
        # Don't change if already in that direction
        if new_direction == self.current_direction:
            return True
        
        # Set direction state to changing
        self.direction_state = DirectionState.CHANGING
        
        # Record direction change
        direction_change = DirectionChange(
            from_direction=self.current_direction,
            to_direction=new_direction,
            timestamp=current_time,
            position=position,
            reason=reason
        )
        self.direction_changes.append(direction_change)
        
        # Update current direction
        self.current_direction = new_direction
        self.last_change_time = current_time
        
        # Set direction state back to normal
        self.direction_state = DirectionState.IDLE
        
        return True
    
    def get_direction_state(self) -> DirectionState:
        """Get current direction state."""
        return self.direction_state
    
    def get_current_direction(self) -> Direction:
        """Get current direction."""
        return self.current_direction
    
    def get_direction_changes(self) -> List[DirectionChange]:
        """Get list of direction changes."""
        return self.direction_changes.copy()
    
    def get_direction_statistics(self) -> Dict[str, Any]:
        """
        Get direction optimization statistics.
        
        Returns:
            Dictionary with direction statistics
        """
        if not self.direction_changes:
            return {
                'total_changes': 0,
                'forward_changes': 0,
                'reverse_changes': 0,
                'average_changes_per_minute': 0.0,
                'current_direction': self.current_direction.value,
                'direction_state': self.direction_state.value
            }
        
        forward_changes = sum(1 for change in self.direction_changes 
                            if change.to_direction == Direction.FORWARD)
        reverse_changes = sum(1 for change in self.direction_changes 
                             if change.to_direction == Direction.REVERSE)
        
        # Calculate average changes per minute
        if self.direction_changes:
            time_span = self.direction_changes[-1].timestamp - self.direction_changes[0].timestamp
            if time_span > 0:
                avg_changes_per_minute = (len(self.direction_changes) / time_span) * 60
            else:
                avg_changes_per_minute = 0.0
        else:
            avg_changes_per_minute = 0.0
        
        return {
            'total_changes': len(self.direction_changes),
            'forward_changes': forward_changes,
            'reverse_changes': reverse_changes,
            'average_changes_per_minute': avg_changes_per_minute,
            'current_direction': self.current_direction.value,
            'direction_state': self.direction_state.value
        }
    
    def reset_direction_changes(self):
        """Reset direction change history."""
        self.direction_changes.clear()
        self.last_change_time = 0.0
    
    def set_change_cooldown(self, cooldown_seconds: float):
        """Set the direction change cooldown period."""
        self.change_cooldown = cooldown_seconds
    
    def get_change_cooldown(self) -> float:
        """Get the current direction change cooldown."""
        return self.change_cooldown
    
    def is_direction_change_allowed(self) -> bool:
        """Check if direction change is allowed (not in cooldown)."""
        current_time = time.time()
        return current_time - self.last_change_time >= self.change_cooldown 