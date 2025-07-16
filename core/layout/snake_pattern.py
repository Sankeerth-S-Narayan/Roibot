"""
Bidirectional snake pattern navigation for warehouse robot movement.

This module provides the SnakePattern class for implementing bidirectional
snake path navigation with direction optimization and path planning.
"""

from typing import List, Tuple, Optional, Dict
from enum import Enum
import math

from .coordinate import Coordinate, CoordinateError


class Direction(Enum):
    """Enumeration for movement directions."""
    FORWARD = "forward"
    REVERSE = "reverse"
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"


class SnakePattern:
    """
    Bidirectional snake pattern navigation system.
    
    Implements snake pattern navigation with direction optimization
    based on robot movement and target positions.
    """
    
    def __init__(self, max_aisle: int = 25, max_rack: int = 20):
        """
        Initialize snake pattern with warehouse dimensions.
        
        Args:
            max_aisle: Maximum aisle number
            max_rack: Maximum rack number
        """
        self.max_aisle = max_aisle
        self.max_rack = max_rack
        self.direction_changes = 0
        self.current_direction = Direction.FORWARD
    
    def get_snake_direction(self, aisle: int) -> Direction:
        """
        Get the snake direction for a specific aisle.
        
        Args:
            aisle: Aisle number (1-25)
            
        Returns:
            Direction for the aisle (LEFT_TO_RIGHT or RIGHT_TO_LEFT)
        """
        if aisle % 2 == 1:  # Odd aisles
            return Direction.LEFT_TO_RIGHT
        else:  # Even aisles
            return Direction.RIGHT_TO_LEFT
    
    def get_optimal_direction(self, start: Coordinate, target: Coordinate) -> Direction:
        """
        Determine optimal movement direction based on start and target positions.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            Optimal direction (FORWARD or REVERSE)
        """
        # Calculate distances for both directions
        forward_distance = self._calculate_forward_distance(start, target)
        reverse_distance = self._calculate_reverse_distance(start, target)
        
        # Choose direction with shorter distance
        if forward_distance <= reverse_distance:
            return Direction.FORWARD
        else:
            return Direction.REVERSE
    
    def _calculate_forward_distance(self, start: Coordinate, target: Coordinate) -> float:
        """
        Calculate distance using forward snake pattern.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            Total distance using forward pattern
        """
        distance = 0
        current = start
        
        # Move to target aisle
        if current.aisle != target.aisle:
            distance += abs(current.aisle - target.aisle)
            current = Coordinate(target.aisle, current.rack)
        
        # Move to target rack
        if current.rack != target.rack:
            distance += abs(current.rack - target.rack)
        
        return distance
    
    def _calculate_reverse_distance(self, start: Coordinate, target: Coordinate) -> float:
        """
        Calculate distance using reverse snake pattern.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            Total distance using reverse pattern
        """
        # For reverse, we need to consider the snake pattern direction
        # and calculate the path that goes in the opposite direction
        
        # Calculate distance to the opposite end of the warehouse
        if start.aisle <= self.max_aisle // 2:
            # Start is in first half, reverse means going to the end
            reverse_start = Coordinate(self.max_aisle, start.rack)
        else:
            # Start is in second half, reverse means going to the beginning
            reverse_start = Coordinate(1, start.rack)
        
        # Calculate distance to reverse start point
        distance_to_reverse = start.distance_to(reverse_start)
        
        # Calculate distance from reverse start to target
        distance_from_reverse = reverse_start.distance_to(target)
        
        return distance_to_reverse + distance_from_reverse
    
    def get_path_to_target(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Get the optimal path from start to target using snake pattern.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            List of coordinates representing the path
        """
        if start == target:
            return [start]
        
        # Determine optimal direction
        optimal_direction = self.get_optimal_direction(start, target)
        
        # Generate path based on direction
        if optimal_direction == Direction.FORWARD:
            return self._generate_forward_path(start, target)
        else:
            return self._generate_reverse_path(start, target)
    
    def _generate_forward_path(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Generate forward path from start to target.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            List of coordinates for forward path
        """
        path = [start]
        current = start
        
        # Move vertically to target aisle first (correct coordinate system)
        if current.aisle != target.aisle:
            step = 1 if target.aisle > current.aisle else -1
            while current.aisle != target.aisle:
                current = Coordinate(current.aisle + step, current.rack)
                path.append(current)
        
        # Move horizontally to target rack (correct coordinate system)
        if current.rack != target.rack:
            step = 1 if target.rack > current.rack else -1
            while current.rack != target.rack:
                current = Coordinate(current.aisle, current.rack + step)
                path.append(current)
        
        return path
    
    def _generate_reverse_path(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Generate reverse path from start to target.
        
        Args:
            start: Starting coordinate
            target: Target coordinate
            
        Returns:
            List of coordinates for reverse path
        """
        path = [start]
        current = start
        
        # For reverse, we need to consider the snake pattern
        # First, move to the opposite end of the warehouse
        if current.aisle <= self.max_aisle // 2:
            # Move to the end
            while current.aisle < self.max_aisle:
                current = Coordinate(current.aisle + 1, current.rack)
                path.append(current)
        else:
            # Move to the beginning
            while current.aisle > 1:
                current = Coordinate(current.aisle - 1, current.rack)
                path.append(current)
        
        # Now move to target
        target_path = self._generate_forward_path(current, target)
        path.extend(target_path[1:])  # Skip the first point as it's already in path
        
        return path
    
    def get_aisle_direction(self, aisle: int, movement_direction: Direction) -> Direction:
        """
        Get the direction within an aisle based on movement direction.
        
        Args:
            aisle: Aisle number
            movement_direction: Overall movement direction
            
        Returns:
            Direction within the aisle
        """
        base_direction = self.get_snake_direction(aisle)
        
        if movement_direction == Direction.FORWARD:
            return base_direction
        else:  # REVERSE
            if base_direction == Direction.LEFT_TO_RIGHT:
                return Direction.RIGHT_TO_LEFT
            else:
                return Direction.LEFT_TO_RIGHT
    
    def calculate_path_distance(self, path: List[Coordinate]) -> float:
        """
        Calculate total distance of a path.
        
        Args:
            path: List of coordinates representing the path
            
        Returns:
            Total distance of the path
        """
        if len(path) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            total_distance += path[i].distance_to(path[i + 1])
        
        return total_distance
    
    def optimize_path_for_multiple_targets(self, start: Coordinate, targets: List[Coordinate]) -> List[Coordinate]:
        """
        Optimize path for multiple targets using snake pattern.
        
        Args:
            start: Starting coordinate
            targets: List of target coordinates
            
        Returns:
            Optimized path visiting all targets
        """
        if not targets:
            return [start]
        
        # Sort targets by aisle to follow snake pattern
        sorted_targets = sorted(targets, key=lambda coord: coord.aisle)
        
        # Generate path visiting all targets
        path = [start]
        current = start
        
        for target in sorted_targets:
            # Get path to next target
            target_path = self.get_path_to_target(current, target)
            path.extend(target_path[1:])  # Skip first point as it's already in path
            current = target
        
        return path
    
    def get_direction_change_count(self, path: List[Coordinate]) -> int:
        """
        Count direction changes in a path.
        
        Args:
            path: List of coordinates representing the path
            
        Returns:
            Number of direction changes
        """
        if len(path) < 3:
            return 0
        
        changes = 0
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_pos = path[i + 1]
            
            # Check if direction changed
            if self._is_direction_change(prev, curr, next_pos):
                changes += 1
        
        return changes
    
    def _is_direction_change(self, prev: Coordinate, curr: Coordinate, next_pos: Coordinate) -> bool:
        """
        Check if there's a direction change between three consecutive points.
        
        Args:
            prev: Previous coordinate
            curr: Current coordinate
            next_pos: Next coordinate
            
        Returns:
            True if direction changed, False otherwise
        """
        # Calculate movement vectors
        dx1 = curr.aisle - prev.aisle
        dy1 = curr.rack - prev.rack
        dx2 = next_pos.aisle - curr.aisle
        dy2 = next_pos.rack - curr.rack
        
        # Check if movement direction changed
        return (dx1 != dx2) or (dy1 != dy2)
    
    def get_path_statistics(self, path: List[Coordinate]) -> Dict[str, any]:
        """
        Get comprehensive statistics about a path.
        
        Args:
            path: List of coordinates representing the path
            
        Returns:
            Dictionary with path statistics
        """
        if not path:
            return {
                'total_distance': 0.0,
                'direction_changes': 0,
                'path_length': 0,
                'start_coordinate': None,
                'end_coordinate': None
            }
        
        total_distance = self.calculate_path_distance(path)
        direction_changes = self.get_direction_change_count(path)
        
        return {
            'total_distance': total_distance,
            'direction_changes': direction_changes,
            'path_length': len(path),
            'start_coordinate': path[0],
            'end_coordinate': path[-1],
            'average_distance_per_step': total_distance / max(len(path) - 1, 1)
        }
    
    def reset_direction_changes(self):
        """Reset direction change counter."""
        self.direction_changes = 0
    
    def get_direction_changes(self) -> int:
        """Get current direction change count."""
        return self.direction_changes
    
    def set_current_direction(self, direction: Direction):
        """Set current movement direction."""
        if self.current_direction != direction:
            self.direction_changes += 1
        self.current_direction = direction
    
    def get_current_direction(self) -> Direction:
        """Get current movement direction."""
        return self.current_direction
    
    def __str__(self) -> str:
        """String representation of snake pattern."""
        return f"SnakePattern({self.max_aisle}x{self.max_rack}) - Direction: {self.current_direction.value}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SnakePattern(max_aisle={self.max_aisle}, max_rack={self.max_rack}, direction={self.current_direction.value})" 