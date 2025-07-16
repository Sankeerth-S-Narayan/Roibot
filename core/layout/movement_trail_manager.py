"""
Movement Trail Visualization System for Phase 4 Bidirectional Navigation.

Handles movement trail system, short-distance trail tracking, trail update mechanism,
integration with GridVisualizer, trail cleanup and management, and trail configuration options.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .coordinate import Coordinate


class TrailType(Enum):
    """Types of movement trails."""
    RECENT_PATH = "recent_path"      # Recent movement path
    COMPLETE_PATH = "complete_path"   # Complete planned path
    HIGHLIGHT = "highlight"          # Highlighted positions
    DEBUG = "debug"                  # Debug information


@dataclass
class TrailPoint:
    """Represents a point in the movement trail."""
    position: Coordinate
    timestamp: float
    trail_type: TrailType
    intensity: float = 1.0  # 0.0 to 1.0 for fade effect


@dataclass
class TrailConfig:
    """Configuration for movement trail visualization."""
    max_trail_length: int = 20  # Maximum number of trail points
    trail_duration: float = 10.0  # How long trail points last (seconds)
    fade_rate: float = 0.1  # Rate at which trail fades (per second)
    update_interval: float = 0.1  # How often to update trail (seconds)
    show_recent_path: bool = True
    show_complete_path: bool = False
    show_highlights: bool = True
    show_debug: bool = False


class MovementTrailManager:
    """
    Manages movement trail visualization for robot navigation.
    
    Features:
    - Movement trail system with configurable length
    - Short-distance trail tracking
    - Trail update mechanism
    - Integration with GridVisualizer
    - Trail cleanup and management
    - Trail configuration options
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize movement trail manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = TrailConfig()
        self.trail_points: List[TrailPoint] = []
        self.last_update_time: float = 0.0
        self.current_position: Optional[Coordinate] = None
        
        # Trail statistics
        self.total_points_added: int = 0
        self.total_points_removed: int = 0
        self.trail_start_time: float = time.time()
        
        if config:
            self.load_config(config)
        
        print("✅ MovementTrailManager initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the trail manager with settings from config.
        
        Args:
            config: Configuration dictionary
        """
        self.load_config(config)
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """
        Load trail configuration from dictionary.
        
        Args:
            config: Configuration dictionary
        """
        trail_config = config.get("trail", {})
        
        self.config.max_trail_length = trail_config.get("max_trail_length", 20)
        self.config.trail_duration = trail_config.get("trail_duration", 10.0)
        self.config.fade_rate = trail_config.get("fade_rate", 0.1)
        self.config.update_interval = trail_config.get("update_interval", 0.1)
        self.config.show_recent_path = trail_config.get("show_recent_path", True)
        self.config.show_complete_path = trail_config.get("show_complete_path", False)
        self.config.show_highlights = trail_config.get("show_highlights", True)
        self.config.show_debug = trail_config.get("show_debug", False)
        
        print(f"✅ Trail config loaded: {self.config.max_trail_length} max points, {self.config.trail_duration}s duration")
    
    def add_trail_point(self, position: Coordinate, trail_type: TrailType = TrailType.RECENT_PATH) -> None:
        """
        Add a new point to the movement trail.
        
        Args:
            position: Robot position
            trail_type: Type of trail point
        """
        current_time = time.time()
        
        # Create new trail point
        trail_point = TrailPoint(
            position=position,
            timestamp=current_time,
            trail_type=trail_type,
            intensity=1.0
        )
        
        # Add to trail
        self.trail_points.append(trail_point)
        self.total_points_added += 1
        
        # Update current position
        self.current_position = position
        
        # Clean up old points if needed
        self._cleanup_old_points()
        
        # Limit trail length
        if len(self.trail_points) > self.config.max_trail_length:
            removed_point = self.trail_points.pop(0)
            self.total_points_removed += 1
    
    def update_trail(self, current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Update trail visualization (fade old points, etc.).
        
        Args:
            current_time: Current time (defaults to time.time())
            
        Returns:
            Dictionary with update information
        """
        if current_time is None:
            current_time = time.time()
        
        # Check if we should update
        if current_time - self.last_update_time < self.config.update_interval:
            return {"status": "no_update_needed"}
        
        self.last_update_time = current_time
        
        # Update point intensities (fade effect)
        points_updated = 0
        points_removed = 0
        
        for i in range(len(self.trail_points) - 1, -1, -1):
            point = self.trail_points[i]
            age = current_time - point.timestamp
            
            # Remove points that are too old
            if age > self.config.trail_duration:
                self.trail_points.pop(i)
                points_removed += 1
                self.total_points_removed += 1
                continue
            
            # Fade point intensity
            fade_amount = age * self.config.fade_rate
            point.intensity = max(0.0, 1.0 - fade_amount)
            points_updated += 1
        
        return {
            "status": "updated",
            "points_updated": points_updated,
            "points_removed": points_removed,
            "total_points": len(self.trail_points),
            "current_position": self.current_position
        }
    
    def get_trail_points(self, trail_type: Optional[TrailType] = None) -> List[TrailPoint]:
        """
        Get trail points, optionally filtered by type.
        
        Args:
            trail_type: Optional trail type filter
            
        Returns:
            List of trail points
        """
        if trail_type is None:
            return self.trail_points.copy()
        
        return [point for point in self.trail_points if point.trail_type == trail_type]
    
    def get_recent_path(self, max_points: Optional[int] = None) -> List[Coordinate]:
        """
        Get recent movement path as coordinates.
        
        Args:
            max_points: Maximum number of points to return
            
        Returns:
            List of recent coordinates
        """
        recent_points = self.get_trail_points(TrailType.RECENT_PATH)
        
        if max_points:
            recent_points = recent_points[-max_points:]
        
        return [point.position for point in recent_points]
    
    def add_complete_path(self, path_coordinates: List[Coordinate]) -> None:
        """
        Add complete planned path to trail.
        
        Args:
            path_coordinates: List of path coordinates
        """
        if not self.config.show_complete_path:
            return
        
        current_time = time.time()
        
        for coord in path_coordinates:
            trail_point = TrailPoint(
                position=coord,
                timestamp=current_time,
                trail_type=TrailType.COMPLETE_PATH,
                intensity=0.5  # Lower intensity for planned path
            )
            self.trail_points.append(trail_point)
        
        print(f"✅ Added complete path with {len(path_coordinates)} points")
    
    def add_highlight(self, position: Coordinate, intensity: float = 1.0) -> None:
        """
        Add a highlight point to the trail.
        
        Args:
            position: Position to highlight
            intensity: Highlight intensity
        """
        if not self.config.show_highlights:
            return
        
        trail_point = TrailPoint(
            position=position,
            timestamp=time.time(),
            trail_type=TrailType.HIGHLIGHT,
            intensity=intensity
        )
        self.trail_points.append(trail_point)
    
    def add_debug_point(self, position: Coordinate, debug_info: str = "") -> None:
        """
        Add a debug point to the trail.
        
        Args:
            position: Debug position
            debug_info: Debug information
        """
        if not self.config.show_debug:
            return
        
        trail_point = TrailPoint(
            position=position,
            timestamp=time.time(),
            trail_type=TrailType.DEBUG,
            intensity=0.8
        )
        self.trail_points.append(trail_point)
    
    def clear_trail(self, trail_type: Optional[TrailType] = None) -> int:
        """
        Clear trail points, optionally by type.
        
        Args:
            trail_type: Optional trail type to clear
            
        Returns:
            Number of points removed
        """
        if trail_type is None:
            # Clear all points
            removed_count = len(self.trail_points)
            self.trail_points.clear()
            self.total_points_removed += removed_count
            return removed_count
        
        # Clear specific type
        original_count = len(self.trail_points)
        self.trail_points = [point for point in self.trail_points if point.trail_type != trail_type]
        removed_count = original_count - len(self.trail_points)
        self.total_points_removed += removed_count
        
        return removed_count
    
    def get_trail_statistics(self) -> Dict[str, Any]:
        """Get trail statistics for analytics."""
        current_time = time.time()
        
        # Count points by type
        type_counts = {}
        for trail_type in TrailType:
            type_counts[trail_type.value] = len(self.get_trail_points(trail_type))
        
        return {
            "total_points": len(self.trail_points),
            "type_counts": type_counts,
            "total_points_added": self.total_points_added,
            "total_points_removed": self.total_points_removed,
            "trail_age": current_time - self.trail_start_time,
            "current_position": str(self.current_position) if self.current_position else None,
            "config": {
                "max_trail_length": self.config.max_trail_length,
                "trail_duration": self.config.trail_duration,
                "fade_rate": self.config.fade_rate
            }
        }
    
    def export_trail_for_visualization(self) -> Dict[str, Any]:
        """
        Export trail data for GridVisualizer integration.
        
        Returns:
            Dictionary with trail data for visualization
        """
        trail_data = {
            "recent_path": [],
            "complete_path": [],
            "highlights": [],
            "debug_points": []
        }
        
        for point in self.trail_points:
            coord_data = {
                "position": (point.position.aisle, point.position.rack),
                "intensity": point.intensity,
                "age": time.time() - point.timestamp
            }
            
            if point.trail_type == TrailType.RECENT_PATH:
                trail_data["recent_path"].append(coord_data)
            elif point.trail_type == TrailType.COMPLETE_PATH:
                trail_data["complete_path"].append(coord_data)
            elif point.trail_type == TrailType.HIGHLIGHT:
                trail_data["highlights"].append(coord_data)
            elif point.trail_type == TrailType.DEBUG:
                trail_data["debug_points"].append(coord_data)
        
        return trail_data
    
    def _cleanup_old_points(self) -> None:
        """Clean up old trail points based on duration."""
        current_time = time.time()
        
        # Remove points older than trail duration
        original_count = len(self.trail_points)
        self.trail_points = [
            point for point in self.trail_points
            if current_time - point.timestamp <= self.config.trail_duration
        ]
        
        removed_count = original_count - len(self.trail_points)
        if removed_count > 0:
            self.total_points_removed += removed_count 