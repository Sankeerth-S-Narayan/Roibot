from typing import List, Optional, Tuple, Dict
import time
from core.layout.coordinate import Coordinate

class CollectionState:
    """Enumeration for collection states."""
    IDLE = "idle"
    COLLECTING = "collecting"
    COMPLETED = "completed"

class RobotCollection:
    """
    Handles item collection mechanics and state management for the robot.
    """
    
    def __init__(self, robot, config=None):
        self.robot = robot
        self.collection_time: float = 3.0  # seconds (configurable)
        self.collection_start_time: Optional[float] = None
        self.current_collection_state = CollectionState.IDLE
        self.target_items: List[str] = []  # Item IDs to collect
        self.collected_items: List[str] = []  # Item IDs already collected
        self.current_item_id: Optional[str] = None
        self.max_items: int = 5  # Maximum items robot can hold
        
        if config:
            self.load_config(config)
    
    def load_config(self, config):
        """Load collection configuration."""
        self.collection_time = config.get('collection_time', 3.0)
        self.max_items = config.get('max_items', 5)
    
    def start_collection(self, item_id: str, item_position: Tuple[int, int], current_time: float):
        """
        Start collecting an item at the specified position.
        
        Args:
            item_id: ID of the item to collect
            item_position: (aisle, rack) position of the item
            current_time: Current simulation time
        """
        # Validate robot is at the correct position
        if not self._is_at_correct_position(item_position):
            raise ValueError(f"Robot not at correct position for item {item_id}")
        
        # Check if robot has capacity
        if len(self.robot.items_held) >= self.max_items:
            raise ValueError(f"Robot at maximum capacity ({self.max_items} items)")
        
        # Check if item is in target list
        if item_id not in self.target_items:
            raise ValueError(f"Item {item_id} not in target list")
        
        # Check if item already collected
        if item_id in self.collected_items:
            raise ValueError(f"Item {item_id} already collected")
        
        self.current_item_id = item_id
        self.collection_start_time = current_time
        self.current_collection_state = CollectionState.COLLECTING
    
    def update_collection(self, current_time: float) -> bool:
        """
        Update collection progress and return True if collection is complete.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            True if collection is complete, False otherwise
        """
        if self.current_collection_state != CollectionState.COLLECTING:
            return False
        
        if not self.collection_start_time:
            return False
        
        elapsed = current_time - self.collection_start_time
        
        if elapsed >= self.collection_time:
            # Collection complete
            self._complete_collection()
            return True
        
        return False
    
    def _complete_collection(self):
        """Complete the current item collection."""
        if self.current_item_id:
            # Add item to robot's held items
            self.robot.items_held.append(self.current_item_id)
            self.collected_items.append(self.current_item_id)
            
            # Remove from target list
            if self.current_item_id in self.target_items:
                self.target_items.remove(self.current_item_id)
            
            self.current_collection_state = CollectionState.COMPLETED
            self.current_item_id = None
            self.collection_start_time = None
    
    def _is_at_correct_position(self, item_position: Tuple[int, int]) -> bool:
        """Check if robot is at the correct position for item collection."""
        if not self.robot.position:
            return False
        
        robot_pos = self.robot.position
        return robot_pos == item_position
    
    def set_target_items(self, item_ids: List[str]):
        """Set the list of items to collect."""
        self.target_items = item_ids.copy()
        self.collected_items.clear()
        self.current_collection_state = CollectionState.IDLE
    
    def get_collection_progress(self) -> float:
        """Get collection progress as a percentage (0.0 to 1.0)."""
        if self.current_collection_state != CollectionState.COLLECTING:
            return 0.0
        
        if not self.collection_start_time:
            return 0.0
        
        elapsed = time.time() - self.collection_start_time
        return min(elapsed / self.collection_time, 1.0)
    
    def is_collecting(self) -> bool:
        """Check if robot is currently collecting an item."""
        return self.current_collection_state == CollectionState.COLLECTING
    
    def is_collection_complete(self) -> bool:
        """Check if current collection is complete."""
        return self.current_collection_state == CollectionState.COMPLETED
    
    def get_remaining_items(self) -> List[str]:
        """Get list of remaining items to collect."""
        return [item for item in self.target_items if item not in self.collected_items]
    
    def get_collected_items(self) -> List[str]:
        """Get list of already collected items."""
        return self.collected_items.copy()
    
    def get_collection_stats(self) -> Dict[str, any]:
        """Get collection statistics."""
        return {
            'total_targets': len(self.target_items) + len(self.collected_items),
            'collected': len(self.collected_items),
            'remaining': len(self.get_remaining_items()),
            'robot_capacity': len(self.robot.items_held),
            'max_capacity': self.max_items,
            'is_collecting': self.is_collecting(),
            'collection_progress': self.get_collection_progress()
        }
    
    def reset_collection(self):
        """Reset collection state."""
        self.current_collection_state = CollectionState.IDLE
        self.current_item_id = None
        self.collection_start_time = None
        self.target_items.clear()
        self.collected_items.clear() 