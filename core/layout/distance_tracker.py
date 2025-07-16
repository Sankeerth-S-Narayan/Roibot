"""
Distance tracking and KPI integration for warehouse robot simulation.

This module provides comprehensive distance tracking for robot movements,
individual orders, and KPI calculations with EventSystem integration.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import math
from enum import Enum

from .coordinate import Coordinate
from .warehouse_layout import WarehouseLayoutManager
from .snake_pattern import SnakePattern, Direction
from .packout_zone import PackoutZoneManager


class DistanceEventType(Enum):
    """Types of distance tracking events."""
    ROBOT_MOVE = "robot_move"
    ORDER_START = "order_start"
    ORDER_COMPLETE = "order_complete"
    PICKUP_ITEM = "pickup_item"
    DELIVER_TO_PACKOUT = "deliver_to_packout"
    RETURN_TO_START = "return_to_start"


@dataclass
class DistanceEvent:
    """Represents a distance tracking event."""
    event_type: DistanceEventType
    from_coord: Coordinate
    to_coord: Coordinate
    distance: float
    timestamp: datetime
    order_id: Optional[str] = None
    robot_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DistanceTracker:
    """
    Comprehensive distance tracking for warehouse robot simulation.
    
    Tracks total distance, per-order distance, and provides KPI calculations
    with EventSystem integration.
    """
    
    def __init__(self):
        """Initialize the distance tracker."""
        self._total_distance: float = 0.0
        self._order_distances: Dict[str, float] = {}
        self._robot_distances: Dict[str, float] = {}
        self._events: List[DistanceEvent] = []
        self._current_positions: Dict[str, Coordinate] = {}
        
        # Get required managers
        self._layout_manager = WarehouseLayoutManager()
        self._snake_navigator = SnakePattern()
        self._packout_manager = PackoutZoneManager(self._layout_manager)
    
    @property
    def total_distance(self) -> float:
        """Get total distance traveled by all robots."""
        return self._total_distance
    
    @property
    def order_distances(self) -> Dict[str, float]:
        """Get distance traveled for each order."""
        return self._order_distances.copy()
    
    @property
    def robot_distances(self) -> Dict[str, float]:
        """Get distance traveled by each robot."""
        return self._robot_distances.copy()
    
    @property
    def events(self) -> List[DistanceEvent]:
        """Get all distance tracking events."""
        return self._events.copy()
    
    def get_order_distance(self, order_id: str) -> float:
        """Get distance traveled for a specific order."""
        return self._order_distances.get(order_id, 0.0)
    
    def get_robot_distance(self, robot_id: str) -> float:
        """Get distance traveled by a specific robot."""
        return self._robot_distances.get(robot_id, 0.0)
    
    def get_current_position(self, robot_id: str) -> Optional[Coordinate]:
        """Get current position of a robot."""
        return self._current_positions.get(robot_id)
    
    def calculate_distance(self, from_coord: Coordinate, to_coord: Coordinate) -> float:
        """
        Calculate Manhattan distance between two coordinates.
        
        Args:
            from_coord: Starting coordinate
            to_coord: Ending coordinate
            
        Returns:
            Manhattan distance between coordinates
        """
        return abs(from_coord.aisle - to_coord.aisle) + abs(from_coord.rack - to_coord.rack)
    
    def calculate_optimal_path_distance(self, from_coord: Coordinate, to_coord: Coordinate, 
                                     direction: Direction = Direction.FORWARD) -> float:
        """
        Calculate optimal path distance using snake pattern navigation.
        
        Args:
            from_coord: Starting coordinate
            to_coord: Ending coordinate
            direction: Robot movement direction
            
        Returns:
            Optimal path distance using snake pattern
        """

        path = self._snake_navigator.get_path_to_target(from_coord, to_coord)
        return len(path) - 1  # Distance is number of moves, not number of positions
    
    def track_robot_move(self, robot_id: str, from_coord: Coordinate, to_coord: Coordinate,
                        direction: Direction = Direction.FORWARD) -> float:
        """
        Track a robot movement and calculate distance.
        
        Args:
            robot_id: ID of the robot
            from_coord: Starting coordinate
            to_coord: Ending coordinate
            direction: Robot movement direction
            
        Returns:
            Distance traveled in this move
        """
        # Validate coordinates
        if not self._layout_manager.is_valid_coordinate(from_coord):
            raise ValueError(f"Invalid from_coordinate: {from_coord}")
        if not self._layout_manager.is_valid_coordinate(to_coord):
            raise ValueError(f"Invalid to_coordinate: {to_coord}")
        
        # Calculate distance using optimal path
        distance = self.calculate_optimal_path_distance(from_coord, to_coord, direction)
        
        # Update tracking
        self._total_distance += distance
        self._robot_distances[robot_id] = self._robot_distances.get(robot_id, 0.0) + distance
        self._current_positions[robot_id] = to_coord
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.ROBOT_MOVE,
            from_coord=from_coord,
            to_coord=to_coord,
            distance=distance,
            timestamp=datetime.now(),
            robot_id=robot_id
        )
        self._events.append(event)
        
        return distance
    
    def track_order_start(self, order_id: str, robot_id: str, start_coord: Coordinate) -> None:
        """
        Track the start of an order.
        
        Args:
            order_id: ID of the order
            robot_id: ID of the robot handling the order
            start_coord: Starting coordinate for the order
        """
        # Initialize order distance tracking
        self._order_distances[order_id] = 0.0
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.ORDER_START,
            from_coord=start_coord,
            to_coord=start_coord,
            distance=0.0,
            timestamp=datetime.now(),
            order_id=order_id,
            robot_id=robot_id
        )
        self._events.append(event)
    
    def track_pickup_item(self, order_id: str, robot_id: str, from_coord: Coordinate, 
                         to_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float:
        """
        Track item pickup movement for an order.
        
        Args:
            order_id: ID of the order
            robot_id: ID of the robot
            from_coord: Starting coordinate
            to_coord: Item pickup coordinate
            direction: Robot movement direction
            
        Returns:
            Distance traveled for this pickup
        """
        distance = self.track_robot_move(robot_id, from_coord, to_coord, direction)
        
        # Add to order distance
        self._order_distances[order_id] = self._order_distances.get(order_id, 0.0) + distance
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.PICKUP_ITEM,
            from_coord=from_coord,
            to_coord=to_coord,
            distance=distance,
            timestamp=datetime.now(),
            order_id=order_id,
            robot_id=robot_id
        )
        self._events.append(event)
        
        return distance
    
    def track_deliver_to_packout(self, order_id: str, robot_id: str, from_coord: Coordinate,
                                direction: Direction = Direction.FORWARD) -> float:
        """
        Track delivery to packout location.
        
        Args:
            order_id: ID of the order
            robot_id: ID of the robot
            from_coord: Starting coordinate
            direction: Robot movement direction
            
        Returns:
            Distance traveled to packout
        """
        packout_coord = self._packout_manager.packout_location
        
        distance = self.track_robot_move(robot_id, from_coord, packout_coord, direction)
        
        # Add to order distance
        self._order_distances[order_id] = self._order_distances.get(order_id, 0.0) + distance
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.DELIVER_TO_PACKOUT,
            from_coord=from_coord,
            to_coord=packout_coord,
            distance=distance,
            timestamp=datetime.now(),
            order_id=order_id,
            robot_id=robot_id
        )
        self._events.append(event)
        
        return distance
    
    def track_return_to_start(self, robot_id: str, from_coord: Coordinate,
                             start_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float:
        """
        Track robot return to start position.
        
        Args:
            robot_id: ID of the robot
            from_coord: Current coordinate
            start_coord: Start coordinate to return to
            direction: Robot movement direction
            
        Returns:
            Distance traveled to return to start
        """
        distance = self.track_robot_move(robot_id, from_coord, start_coord, direction)
        
        # Add to robot distance (track_robot_move already adds to total)
        # No need to add again since track_robot_move handles it
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.RETURN_TO_START,
            from_coord=from_coord,
            to_coord=start_coord,
            distance=distance,
            timestamp=datetime.now(),
            robot_id=robot_id
        )
        self._events.append(event)
        
        return distance
    
    def track_order_complete(self, order_id: str, robot_id: str, final_coord: Coordinate) -> float:
        """
        Track order completion.
        
        Args:
            order_id: ID of the order
            robot_id: ID of the robot
            final_coord: Final coordinate after order completion
            
        Returns:
            Total distance for this order
        """
        total_order_distance = self._order_distances.get(order_id, 0.0)
        
        # Create and store event
        event = DistanceEvent(
            event_type=DistanceEventType.ORDER_COMPLETE,
            from_coord=final_coord,
            to_coord=final_coord,
            distance=total_order_distance,
            timestamp=datetime.now(),
            order_id=order_id,
            robot_id=robot_id,
            metadata={"total_order_distance": total_order_distance}
        )
        self._events.append(event)
        
        return total_order_distance
    
    def get_kpi_metrics(self) -> Dict[str, Any]:
        """
        Calculate KPI metrics based on distance tracking.
        
        Returns:
            Dictionary containing various KPI metrics
        """
        if not self._events:
            return {
                "total_distance": 0.0,
                "average_order_distance": 0.0,
                "total_orders": 0,
                "average_robot_distance": 0.0,
                "total_robots": 0,
                "efficiency_score": 0.0
            }
        
        # Calculate metrics
        total_orders = len(self._order_distances)
        total_robots = len(self._robot_distances)
        
        avg_order_distance = (sum(self._order_distances.values()) / total_orders 
                            if total_orders > 0 else 0.0)
        avg_robot_distance = (sum(self._robot_distances.values()) / total_robots 
                             if total_robots > 0 else 0.0)
        
        # Calculate efficiency score (lower is better)
        # Based on average distance per order
        efficiency_score = 1.0 / (avg_order_distance + 1.0)  # Avoid division by zero
        
        return {
            "total_distance": self._total_distance,
            "average_order_distance": avg_order_distance,
            "total_orders": total_orders,
            "average_robot_distance": avg_robot_distance,
            "total_robots": total_robots,
            "efficiency_score": efficiency_score
        }
    
    def get_events_by_type(self, event_type: DistanceEventType) -> List[DistanceEvent]:
        """
        Get events filtered by type.
        
        Args:
            event_type: Type of events to filter
            
        Returns:
            List of events of the specified type
        """
        return [event for event in self._events if event.event_type == event_type]
    
    def get_events_by_order(self, order_id: str) -> List[DistanceEvent]:
        """
        Get events for a specific order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            List of events for the specified order
        """
        return [event for event in self._events if event.order_id == order_id]
    
    def get_events_by_robot(self, robot_id: str) -> List[DistanceEvent]:
        """
        Get events for a specific robot.
        
        Args:
            robot_id: ID of the robot
            
        Returns:
            List of events for the specified robot
        """
        return [event for event in self._events if event.robot_id == robot_id]
    
    def reset(self) -> None:
        """Reset all distance tracking data."""
        self._total_distance = 0.0
        self._order_distances.clear()
        self._robot_distances.clear()
        self._events.clear()
        self._current_positions.clear()
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export distance tracking data for persistence.
        
        Returns:
            Dictionary containing all tracking data
        """
        return {
            "total_distance": self._total_distance,
            "order_distances": self._order_distances.copy(),
            "robot_distances": self._robot_distances.copy(),
            "events": [
                {
                    "event_type": event.event_type.value,
                    "from_coord": (event.from_coord.aisle, event.from_coord.rack),
                    "to_coord": (event.to_coord.aisle, event.to_coord.rack),
                    "distance": event.distance,
                    "timestamp": event.timestamp.isoformat(),
                    "order_id": event.order_id,
                    "robot_id": event.robot_id,
                    "metadata": event.metadata
                }
                for event in self._events
            ],
            "current_positions": {
                robot_id: (coord.aisle, coord.rack)
                for robot_id, coord in self._current_positions.items()
            }
        }
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """
        Import distance tracking data from persistence.
        
        Args:
            data: Dictionary containing tracking data
        """
        self.reset()
        
        self._total_distance = data.get("total_distance", 0.0)
        self._order_distances = data.get("order_distances", {})
        self._robot_distances = data.get("robot_distances", {})
        
        # Import events
        for event_data in data.get("events", []):
            event = DistanceEvent(
                event_type=DistanceEventType(event_data["event_type"]),
                from_coord=Coordinate(event_data["from_coord"][0], event_data["from_coord"][1]),
                to_coord=Coordinate(event_data["to_coord"][0], event_data["to_coord"][1]),
                distance=event_data["distance"],
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                order_id=event_data.get("order_id"),
                robot_id=event_data.get("robot_id"),
                metadata=event_data.get("metadata", {})
            )
            self._events.append(event)
        
        # Import current positions
        for robot_id, coord_data in data.get("current_positions", {}).items():
            self._current_positions[robot_id] = Coordinate(coord_data[0], coord_data[1]) 