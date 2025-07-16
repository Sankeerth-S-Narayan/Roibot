"""
Packout zone management for warehouse robot simulation.

This module provides packout zone functionality including special zone validation,
robot start/return logic, and distance calculations from packout location.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum

from .coordinate import Coordinate, CoordinateError
from .warehouse_layout import WarehouseLayoutManager, GridState


class PackoutZoneType(Enum):
    """Enumeration for packout zone types."""
    PACKOUT = "packout"
    RESTRICTED = "restricted"
    TRANSIT = "transit"


class PackoutZoneManager:
    """
    Manages packout zone functionality and special zone validation.
    
    Handles packout location (1,1), robot start/return logic,
    and distance calculations from packout to any location.
    """
    
    def __init__(self, warehouse_layout: WarehouseLayoutManager):
        """
        Initialize packout zone manager.
        
        Args:
            warehouse_layout: Warehouse layout manager instance
        """
        self.warehouse_layout = warehouse_layout
        self.packout_location = Coordinate(1, 1)
        self.restricted_zones: List[Coordinate] = []
        self.transit_zones: List[Coordinate] = []
        
        # Initialize restricted zones (adjacent to packout)
        self._initialize_restricted_zones()
    
    def _initialize_restricted_zones(self):
        """Initialize restricted zones around packout location."""
        # Add adjacent positions as restricted zones
        adjacent_positions = [
            Coordinate(1, 2),  # Above packout
            Coordinate(2, 1),  # Right of packout
            Coordinate(2, 2),  # Diagonal to packout
        ]
        
        for pos in adjacent_positions:
            if self.warehouse_layout.is_valid_coordinate(pos):
                self.restricted_zones.append(pos)
    
    def get_packout_location(self) -> Coordinate:
        """
        Get the packout location coordinate.
        
        Returns:
            Packout location coordinate (1, 1)
        """
        return self.packout_location
    
    def is_packout_location(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is the packout location.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if coordinate is packout location, False otherwise
        """
        return coord == self.packout_location
    
    def is_restricted_zone(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is in a restricted zone.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if coordinate is in restricted zone, False otherwise
        """
        return coord in self.restricted_zones or self.is_packout_location(coord)
    
    def is_transit_zone(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is in a transit zone.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if coordinate is in transit zone, False otherwise
        """
        return coord in self.transit_zones
    
    def get_zone_type(self, coord: Coordinate) -> PackoutZoneType:
        """
        Get the zone type for a coordinate.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            Zone type for the coordinate
        """
        if self.is_packout_location(coord):
            return PackoutZoneType.PACKOUT
        elif self.is_restricted_zone(coord):
            return PackoutZoneType.RESTRICTED
        elif self.is_transit_zone(coord):
            return PackoutZoneType.TRANSIT
        else:
            return PackoutZoneType.TRANSIT  # Default for regular positions
    
    def can_pickup_item_at(self, coord: Coordinate) -> bool:
        """
        Check if item pickup is allowed at the coordinate.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if pickup is allowed, False otherwise
        """
        # No pickup at packout location or restricted zones
        return not (self.is_packout_location(coord) or self.is_restricted_zone(coord))
    
    def can_place_item_at(self, coord: Coordinate) -> bool:
        """
        Check if item placement is allowed at the coordinate.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if placement is allowed, False otherwise
        """
        # Only packout location allows item placement
        return self.is_packout_location(coord)
    
    def get_distance_from_packout(self, coord: Coordinate) -> float:
        """
        Calculate distance from packout location to any coordinate.
        
        Args:
            coord: Target coordinate
            
        Returns:
            Manhattan distance from packout to coordinate
        """
        return self.packout_location.distance_to(coord)
    
    def get_euclidean_distance_from_packout(self, coord: Coordinate) -> float:
        """
        Calculate Euclidean distance from packout location to any coordinate.
        
        Args:
            coord: Target coordinate
            
        Returns:
            Euclidean distance from packout to coordinate
        """
        return self.packout_location.euclidean_distance_to(coord)
    
    def get_robot_start_position(self) -> Coordinate:
        """
        Get the robot start position (packout location).
        
        Returns:
            Robot start position coordinate
        """
        return self.packout_location
    
    def get_robot_return_position(self) -> Coordinate:
        """
        Get the robot return position (packout location).
        
        Returns:
            Robot return position coordinate
        """
        return self.packout_location
    
    def is_valid_robot_position(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is a valid robot position.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if valid robot position, False otherwise
        """
        return self.warehouse_layout.is_valid_coordinate(coord)
    
    def is_valid_coordinate(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is valid within warehouse bounds.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if coordinate is valid, False otherwise
        """
        return self.warehouse_layout.is_valid_coordinate(coord)
    
    def calculate_optimal_route_to_packout(self, start: Coordinate) -> List[Coordinate]:
        """
        Calculate optimal route from start position to packout.
        
        Args:
            start: Starting coordinate
            
        Returns:
            List of coordinates representing the optimal route
        """
        # Use snake pattern for optimal route
        from .snake_pattern import SnakePattern
        snake = SnakePattern()
        return snake.get_path_to_target(start, self.packout_location)
    
    def calculate_distance_to_packout(self, coord: Coordinate) -> float:
        """
        Calculate distance from coordinate to packout location.
        
        Args:
            coord: Starting coordinate
            
        Returns:
            Manhattan distance to packout
        """
        return self.packout_location.distance_to(coord)
    
    def get_packout_zone_statistics(self) -> Dict[str, any]:
        """
        Get statistics about packout zone and related areas.
        
        Returns:
            Dictionary with packout zone statistics
        """
        total_positions = self.warehouse_layout.get_grid_dimensions()[0] * self.warehouse_layout.get_grid_dimensions()[1]
        
        return {
            'packout_location': self.packout_location.to_dict(),
            'restricted_zones_count': len(self.restricted_zones),
            'transit_zones_count': len(self.transit_zones),
            'total_positions': total_positions,
            'available_pickup_positions': total_positions - len(self.restricted_zones) - 1,  # -1 for packout
            'available_placement_positions': 1,  # Only packout
            'restricted_zone_positions': [pos.to_dict() for pos in self.restricted_zones]
        }
    
    def get_packout_zone_visualization(self, robot_position: Optional[Coordinate] = None) -> str:
        """
        Create a text-based visualization of the packout zone.
        
        Args:
            robot_position: Optional robot position to highlight
            
        Returns:
            String representation of the packout zone
        """
        visualization = []
        visualization.append("Packout Zone Visualization")
        visualization.append("=" * 40)
        
        # Show packout location
        visualization.append(f"Packout Location: {self.packout_location}")
        visualization.append(f"Restricted Zones: {len(self.restricted_zones)}")
        visualization.append(f"Transit Zones: {len(self.transit_zones)}")
        visualization.append("")
        
        # Show restricted zones
        if self.restricted_zones:
            visualization.append("Restricted Zones:")
            for zone in self.restricted_zones:
                visualization.append(f"  - {zone}")
        
        # Show robot position if provided
        if robot_position:
            visualization.append(f"Robot Position: {robot_position}")
            distance = self.get_distance_from_packout(robot_position)
            visualization.append(f"Distance from Packout: {distance}")
        
        return "\n".join(visualization)
    
    def validate_order_pickup_locations(self, pickup_locations: List[Coordinate]) -> Tuple[bool, List[str]]:
        """
        Validate that all pickup locations are valid for item pickup.
        
        Args:
            pickup_locations: List of coordinates for item pickup
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid = True
        error_messages = []
        
        for coord in pickup_locations:
            if not self.can_pickup_item_at(coord):
                is_valid = False
                error_messages.append(f"Cannot pickup item at {coord}: {self.get_zone_type(coord).value} zone")
        
        return is_valid, error_messages
    
    def validate_order_placement_locations(self, placement_locations: List[Coordinate]) -> Tuple[bool, List[str]]:
        """
        Validate that all placement locations are valid for item placement.
        
        Args:
            placement_locations: List of coordinates for item placement
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid = True
        error_messages = []
        
        for coord in placement_locations:
            if not self.can_place_item_at(coord):
                is_valid = False
                error_messages.append(f"Cannot place item at {coord}: {self.get_zone_type(coord).value} zone")
        
        return is_valid, error_messages
    
    def get_optimal_pickup_route(self, start: Coordinate, pickup_locations: List[Coordinate]) -> List[Coordinate]:
        """
        Get optimal route for picking up items from multiple locations.
        
        Args:
            start: Starting coordinate (usually packout)
            pickup_locations: List of pickup coordinates
            
        Returns:
            List of coordinates representing the optimal route
        """
        if not pickup_locations:
            return [start]
        
        # Validate pickup locations
        is_valid, errors = self.validate_order_pickup_locations(pickup_locations)
        if not is_valid:
            raise ValueError(f"Invalid pickup locations: {'; '.join(errors)}")
        
        # Sort locations by distance from start for simple optimization
        sorted_locations = sorted(pickup_locations, key=lambda coord: start.distance_to(coord))
        
        # Build route
        route = [start]
        current = start
        
        for location in sorted_locations:
            # Add path to pickup location
            if current != location:
                # Simple path: move horizontally then vertically
                if current.aisle != location.aisle:
                    step = 1 if location.aisle > current.aisle else -1
                    while current.aisle != location.aisle:
                        current = Coordinate(current.aisle + step, current.rack)
                        route.append(current)
                
                if current.rack != location.rack:
                    step = 1 if location.rack > current.rack else -1
                    while current.rack != location.rack:
                        current = Coordinate(current.aisle, current.rack + step)
                        route.append(current)
        
        return route
    
    def get_return_route(self, current: Coordinate) -> List[Coordinate]:
        """
        Get route from current position back to packout.
        
        Args:
            current: Current coordinate
            
        Returns:
            List of coordinates representing the return route
        """
        if current == self.packout_location:
            return [current]
        
        # Simple return route: move to packout location
        route = [current]
        
        # Move horizontally to packout aisle
        if current.aisle != self.packout_location.aisle:
            step = 1 if self.packout_location.aisle > current.aisle else -1
            while current.aisle != self.packout_location.aisle:
                current = Coordinate(current.aisle + step, current.rack)
                route.append(current)
        
        # Move vertically to packout rack
        if current.rack != self.packout_location.rack:
            step = 1 if self.packout_location.rack > current.rack else -1
            while current.rack != self.packout_location.rack:
                current = Coordinate(current.aisle, current.rack + step)
                route.append(current)
        
        return route
    
    def calculate_total_pickup_distance(self, pickup_locations: List[Coordinate]) -> float:
        """
        Calculate total distance for pickup route from packout.
        
        Args:
            pickup_locations: List of pickup coordinates
            
        Returns:
            Total distance for pickup route
        """
        if not pickup_locations:
            return 0.0
        
        route = self.get_optimal_pickup_route(self.packout_location, pickup_locations)
        
        # Calculate total distance
        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += route[i].distance_to(route[i + 1])
        
        return total_distance
    
    def calculate_total_return_distance(self, current: Coordinate) -> float:
        """
        Calculate distance from current position back to packout.
        
        Args:
            current: Current coordinate
            
        Returns:
            Distance to packout
        """
        return self.get_distance_from_packout(current)
    
    def __str__(self) -> str:
        """String representation of packout zone manager."""
        stats = self.get_packout_zone_statistics()
        return f"PackoutZoneManager - Packout: {self.packout_location}, Restricted: {stats['restricted_zones_count']}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"PackoutZoneManager(packout_location={self.packout_location}, restricted_zones={len(self.restricted_zones)})" 