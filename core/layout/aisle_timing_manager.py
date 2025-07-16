"""
Aisle Traversal Timing Manager for Phase 4 Bidirectional Navigation.

Handles configurable 7-second aisle traversal timing with different movement types,
timing validation, and event emission for analytics.
"""

import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

from .coordinate import Coordinate


class MovementType(Enum):
    """Types of movement for timing calculations."""
    HORIZONTAL = "horizontal"  # Same aisle, different rack
    VERTICAL = "vertical"      # Different aisle, same rack
    DIAGONAL = "diagonal"      # Different aisle and rack


@dataclass
class TimingConfig:
    """Configuration for aisle traversal timing."""
    aisle_traversal_time: float = 7.0  # seconds per aisle
    horizontal_movement_time: float = 0.35  # seconds per rack movement
    direction_change_cooldown: float = 0.5  # seconds
    max_timing_variance: float = 0.1  # 10% variance allowed


@dataclass
class MovementTiming:
    """Timing information for a movement segment."""
    start_time: float
    end_time: float
    duration: float
    movement_type: MovementType
    start_position: Coordinate
    end_position: Coordinate
    is_completed: bool = False


class AisleTimingManager:
    """
    Manages aisle traversal timing with configurable settings.
    
    Features:
    - 7-second aisle traversal timing (configurable)
    - Different timing for horizontal vs vertical movement
    - Timing validation and error handling
    - Event emission for analytics
    - Movement interpolation integration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize aisle timing manager.
        
        Args:
            config: Configuration dictionary with timing settings
        """
        self.config = TimingConfig()
        self.current_movement: Optional[MovementTiming] = None
        self.movement_history: List[MovementTiming] = []
        self.last_direction_change: float = 0.0
        self.total_movement_time: float = 0.0
        self.aisles_traversed: int = 0
        self.racks_traversed: int = 0
        
        if config:
            self.load_config(config)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the timing manager with settings from config.
        
        Args:
            config: Configuration dictionary
        """
        self.load_config(config)
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """
        Load timing configuration from dictionary.
        
        Args:
            config: Configuration dictionary
        """
        robot_config = config.get("robot", {})
        
        self.config.aisle_traversal_time = robot_config.get("aisle_traversal_time", 7.0)
        self.config.horizontal_movement_time = robot_config.get("horizontal_movement_time", 0.35)
        self.config.direction_change_cooldown = robot_config.get("direction_change_cooldown", 0.5)
        self.config.max_timing_variance = robot_config.get("max_timing_variance", 0.1)
        
        print(f"✅ AisleTimingManager loaded: {self.config.aisle_traversal_time}s per aisle")
    
    def calculate_movement_timing(self, start_pos: Coordinate, end_pos: Coordinate) -> MovementTiming:
        """
        Calculate timing for movement between two positions.
        
        Args:
            start_pos: Starting position
            end_pos: Ending position
            
        Returns:
            MovementTiming object with calculated timing
        """
        current_time = time.time()
        
        # Determine movement type
        movement_type = self._determine_movement_type(start_pos, end_pos)
        
        # Calculate duration based on movement type
        duration = self._calculate_duration(start_pos, end_pos, movement_type)
        
        # Validate timing
        self._validate_timing(duration, movement_type)
        
        return MovementTiming(
            start_time=current_time,
            end_time=current_time + duration,
            duration=duration,
            movement_type=movement_type,
            start_position=start_pos,
            end_position=end_pos
        )
    
    def start_movement(self, start_pos: Coordinate, end_pos: Coordinate) -> MovementTiming:
        """
        Start a new movement with timing.
        
        Args:
            start_pos: Starting position
            end_pos: Ending position
            
        Returns:
            MovementTiming object for the new movement
        """
        # Check direction change cooldown
        current_time = time.time()
        if current_time - self.last_direction_change < self.config.direction_change_cooldown:
            print(f"⚠️  Direction change cooldown active: {self.config.direction_change_cooldown}s")
        
        # Calculate timing
        movement = self.calculate_movement_timing(start_pos, end_pos)
        self.current_movement = movement
        
        # Update direction change time if this is a direction change
        if self._is_direction_change(start_pos, end_pos):
            self.last_direction_change = current_time
        
        print(f"🚀 Starting movement: {start_pos} → {end_pos} ({movement.duration:.2f}s)")
        return movement
    
    def update_movement(self, current_time: float) -> Optional[Dict[str, Any]]:
        """
        Update current movement progress.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Movement update data or None if no movement
        """
        if not self.current_movement:
            return None
        
        # Check if movement is complete
        if current_time >= self.current_movement.end_time:
            self._complete_movement()
            return {
                "type": "movement_complete",
                "movement": self.current_movement,
                "total_time": self.total_movement_time
            }
        
        # Calculate progress
        elapsed = current_time - self.current_movement.start_time
        progress = min(elapsed / self.current_movement.duration, 1.0)
        
        return {
            "type": "movement_progress",
            "progress": progress,
            "elapsed": elapsed,
            "remaining": self.current_movement.duration - elapsed
        }
    
    def get_movement_progress(self) -> float:
        """Get current movement progress (0.0 to 1.0)."""
        if not self.current_movement:
            return 0.0
        
        current_time = time.time()
        elapsed = current_time - self.current_movement.start_time
        return min(elapsed / self.current_movement.duration, 1.0)
    
    def get_aisle_traversal_time(self) -> float:
        """Get configured aisle traversal time."""
        return self.config.aisle_traversal_time
    
    def set_aisle_traversal_time(self, time_seconds: float) -> None:
        """
        Set aisle traversal time.
        
        Args:
            time_seconds: New aisle traversal time in seconds
        """
        if time_seconds <= 0:
            raise ValueError("Aisle traversal time must be positive")
        
        self.config.aisle_traversal_time = time_seconds
        print(f"⚙️  Aisle traversal time updated to: {time_seconds}s")
    
    def get_timing_statistics(self) -> Dict[str, Any]:
        """Get timing statistics for analytics."""
        if not self.movement_history:
            return {
                "total_movements": 0,
                "total_time": 0.0,
                "average_movement_time": 0.0,
                "aisles_traversed": 0,
                "racks_traversed": 0
            }
        
        total_movements = len(self.movement_history)
        total_time = sum(m.duration for m in self.movement_history)
        avg_time = total_time / total_movements if total_movements > 0 else 0.0
        
        return {
            "total_movements": total_movements,
            "total_time": total_time,
            "average_movement_time": avg_time,
            "aisles_traversed": self.aisles_traversed,
            "racks_traversed": self.racks_traversed,
            "current_aisle_traversal_time": self.config.aisle_traversal_time
        }
    
    def _determine_movement_type(self, start_pos: Coordinate, end_pos: Coordinate) -> MovementType:
        """Determine the type of movement between two positions."""
        aisle_diff = abs(end_pos.aisle - start_pos.aisle)
        rack_diff = abs(end_pos.rack - start_pos.rack)
        
        if aisle_diff == 0 and rack_diff > 0:
            return MovementType.HORIZONTAL
        elif rack_diff == 0 and aisle_diff > 0:
            return MovementType.VERTICAL
        else:
            return MovementType.DIAGONAL
    
    def _calculate_duration(self, start_pos: Coordinate, end_pos: Coordinate, movement_type: MovementType) -> float:
        """Calculate movement duration based on type and distance."""
        aisle_diff = abs(end_pos.aisle - start_pos.aisle)
        rack_diff = abs(end_pos.rack - start_pos.rack)
        
        # Handle zero distance movement (same position)
        if aisle_diff == 0 and rack_diff == 0:
            return 0.1  # Minimum duration for same position
        
        if movement_type == MovementType.HORIZONTAL:
            # Horizontal movement: rack to rack within same aisle
            return rack_diff * self.config.horizontal_movement_time
        elif movement_type == MovementType.VERTICAL:
            # Vertical movement: aisle to aisle
            return aisle_diff * self.config.aisle_traversal_time
        else:
            # Diagonal movement: combine both
            horizontal_time = rack_diff * self.config.horizontal_movement_time
            vertical_time = aisle_diff * self.config.aisle_traversal_time
            return horizontal_time + vertical_time
    
    def _validate_timing(self, duration: float, movement_type: MovementType) -> None:
        """Validate calculated timing against configuration."""
        if duration <= 0:
            raise ValueError("Movement duration must be positive")
        
        # Only validate variance for vertical movements (aisle traversal)
        if movement_type == MovementType.VERTICAL:
            expected_time = self.config.aisle_traversal_time
            variance = abs(duration - expected_time) / expected_time
            
            if variance > self.config.max_timing_variance:
                print(f"⚠️  Timing variance exceeds limit: {variance:.2%} > {self.config.max_timing_variance:.2%}")
    
    def _is_direction_change(self, start_pos: Coordinate, end_pos: Coordinate) -> bool:
        """Check if this movement represents a direction change."""
        if not self.current_movement:
            return False
        
        # Compare with previous movement direction
        prev_start = self.current_movement.start_position
        prev_end = self.current_movement.end_position
        
        prev_direction = (prev_end.aisle - prev_start.aisle, prev_end.rack - prev_start.rack)
        current_direction = (end_pos.aisle - start_pos.aisle, end_pos.rack - start_pos.rack)
        
        return prev_direction != current_direction
    
    def _complete_movement(self) -> None:
        """Complete the current movement and update statistics."""
        if not self.current_movement:
            return
        
        # Mark as completed
        self.current_movement.is_completed = True
        
        # Add to history
        self.movement_history.append(self.current_movement)
        
        # Update statistics
        self.total_movement_time += self.current_movement.duration
        
        # Update traversal counts
        aisle_diff = abs(self.current_movement.end_position.aisle - self.current_movement.start_position.aisle)
        rack_diff = abs(self.current_movement.end_position.rack - self.current_movement.start_position.rack)
        
        self.aisles_traversed += aisle_diff
        self.racks_traversed += rack_diff
        
        print(f"✅ Movement completed: {self.current_movement.duration:.2f}s")
        
        # Clear current movement
        self.current_movement = None 