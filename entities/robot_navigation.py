from typing import List, Optional, Tuple
from core.layout.snake_pattern import SnakePattern, Direction
from core.layout.coordinate import Coordinate

class RobotNavigation:
    """
    Handles snake pattern navigation and path planning for the robot.
    Integrates with existing SnakePattern logic for optimal path calculation.
    """
    
    def __init__(self, robot):
        self.robot = robot
        self.snake_pattern = SnakePattern(max_aisle=25, max_rack=20)
        self.target_items: List[Coordinate] = []
        self.current_target_index: int = 0
        self.path: List[Coordinate] = []
        self.current_path_index: int = 0
        self.is_navigating: bool = False
        
    def set_item_targets(self, item_positions: List[Tuple[int, int]]):
        """
        Set target items for collection in ascending order.
        
        Args:
            item_positions: List of (aisle, rack) tuples for items to collect
        """
        # Convert to Coordinate objects and sort in ascending order
        coordinates = [Coordinate(aisle, rack) for aisle, rack in item_positions]
        self.target_items = sorted(coordinates, key=lambda coord: (coord.aisle, coord.rack))
        self.current_target_index = 0
        self.is_navigating = True
        
    def get_next_target(self) -> Optional[Coordinate]:
        """Get the next target item position."""
        if self.current_target_index < len(self.target_items):
            return self.target_items[self.current_target_index]
        return None
    
    def calculate_path_to_next_item(self) -> List[Coordinate]:
        """
        Calculate optimal path to the next item using snake pattern.
        
        Returns:
            List of coordinates representing the path
        """
        if not self.is_navigating or self.current_target_index >= len(self.target_items):
            return []
        
        current_pos = Coordinate(*self.robot.position) if self.robot.position else Coordinate(1, 1)
        target = self.target_items[self.current_target_index]
        
        # Use snake pattern to calculate optimal path
        path = self.snake_pattern.get_path_to_target(current_pos, target)
        self.path = path
        self.current_path_index = 0
        
        return path
    
    def get_next_path_position(self) -> Optional[Coordinate]:
        """Get the next position in the current path."""
        if self.current_path_index < len(self.path):
            return self.path[self.current_path_index]
        return None
    
    def advance_path(self):
        """Move to the next position in the current path."""
        if self.current_path_index < len(self.path):
            self.current_path_index += 1
    
    def advance_target(self):
        """Move to the next target item."""
        if self.current_target_index < len(self.target_items):
            self.current_target_index += 1
            self.current_path_index = 0  # Reset path for new target
    
    def is_path_complete(self) -> bool:
        """Check if the current path is complete."""
        return self.current_path_index >= len(self.path)
    
    def is_all_items_collected(self) -> bool:
        """Check if all target items have been processed."""
        return self.current_target_index >= len(self.target_items)
    
    def get_optimal_direction(self, start: Coordinate, target: Coordinate) -> Direction:
        """Get optimal movement direction using snake pattern."""
        return self.snake_pattern.get_optimal_direction(start, target)
    
    def calculate_path_distance(self, path: List[Coordinate]) -> float:
        """Calculate total distance for a path."""
        return self.snake_pattern.calculate_path_distance(path)
    
    def get_path_statistics(self, path: List[Coordinate]) -> dict:
        """Get statistics for a path (distance, direction changes, etc.)."""
        return self.snake_pattern.get_path_statistics(path)
    
    def reset_navigation(self):
        """Reset navigation state."""
        self.target_items.clear()
        self.current_target_index = 0
        self.path.clear()
        self.current_path_index = 0
        self.is_navigating = False
    
    def get_remaining_items(self) -> List[Coordinate]:
        """Get list of remaining items to collect."""
        return self.target_items[self.current_target_index:]
    
    def get_collected_items(self) -> List[Coordinate]:
        """Get list of already collected items."""
        return self.target_items[:self.current_target_index] 