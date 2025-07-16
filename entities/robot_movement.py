from typing import Optional, Tuple
import time
from core.layout.coordinate import Coordinate

class RobotMovement:
    """
    Handles smooth movement physics and interpolation for the robot.
    """
    
    def __init__(self, robot, config=None):
        self.robot = robot
        self.target_position: Optional[Coordinate] = None
        self.start_position: Optional[Coordinate] = None
        self.movement_start_time: Optional[float] = None
        self.movement_duration: float = 10.0  # seconds per aisle (configurable)
        self.is_moving: bool = False
        self.progress: float = 0.0  # 0.0 to 1.0
        
        if config:
            self.load_config(config)
    
    def load_config(self, config):
        """Load movement configuration."""
        self.movement_duration = config.get('movement_speed', 10.0)
    
    def set_target(self, target: Coordinate):
        """Set a new target position and start movement."""
        if not self.is_valid_position(target):
            raise ValueError(f"Invalid target position: {target}")
        
        self.target_position = target
        self.start_position = Coordinate(*self.robot.position) if self.robot.position else Coordinate(1, 1)
        self.movement_start_time = time.time()
        self.is_moving = True
        self.progress = 0.0
    
    def update(self, current_time: float):
        """Update movement progress based on elapsed time."""
        if not self.is_moving or not self.movement_start_time:
            return
        
        elapsed = current_time - self.movement_start_time
        distance = self.calculate_distance(self.start_position, self.target_position)
        total_duration = distance * self.movement_duration
        
        # Handle case where distance is 0 (same start and end position)
        if total_duration <= 0:
            self.progress = 1.0
            self.robot.position = (self.target_position.aisle, self.target_position.rack)
            self.is_moving = False
            return
        
        self.progress = min(elapsed / total_duration, 1.0)
        
        # Update robot position with interpolation
        if self.progress < 1.0:
            self.robot.position = self.interpolate_position(
                self.start_position, self.target_position, self.progress
            )
        else:
            # Movement complete
            self.robot.position = (self.target_position.aisle, self.target_position.rack)
            self.is_moving = False
            self.progress = 1.0
    
    def interpolate_position(self, start: Coordinate, end: Coordinate, progress: float) -> Tuple[int, int]:
        """Interpolate between two positions using linear interpolation."""
        aisle = start.aisle + (end.aisle - start.aisle) * progress
        rack = start.rack + (end.rack - start.rack) * progress
        return (int(aisle), int(rack))
    
    def calculate_distance(self, start: Coordinate, end: Coordinate) -> float:
        """Calculate Manhattan distance between two positions."""
        return abs(end.aisle - start.aisle) + abs(end.rack - start.rack)
    
    def is_valid_position(self, position: Coordinate) -> bool:
        """Validate position is within warehouse bounds."""
        return (1 <= position.aisle <= 25 and 1 <= position.rack <= 20)
    
    def is_complete(self) -> bool:
        """Check if movement is complete."""
        return not self.is_moving and self.progress >= 1.0
    
    def get_progress(self) -> float:
        """Get current movement progress (0.0 to 1.0)."""
        return self.progress
    
    def stop_movement(self):
        """Stop current movement."""
        self.is_moving = False
        self.progress = 0.0 