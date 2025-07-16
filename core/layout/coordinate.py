"""
Grid coordinate system for warehouse layout.

This module provides the Coordinate class for representing warehouse grid positions
with 1-based indexing (Aisle 1-25, Rack 1-20) and comprehensive validation.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, Union
import math


class CoordinateError(Exception):
    """Exception raised for coordinate validation errors."""
    pass


@dataclass(frozen=True)
class Coordinate:
    """
    Represents a warehouse grid coordinate with 1-based indexing.
    
    Attributes:
        aisle: Aisle number (1-25)
        rack: Rack number (1-20)
    """
    
    aisle: int
    rack: int
    
    def __post_init__(self):
        """Validate coordinate bounds after initialization."""
        self._validate_bounds()
    
    def _validate_bounds(self):
        """Validate that coordinate is within warehouse bounds."""
        if not (1 <= self.aisle <= 25):
            raise CoordinateError(f"Aisle must be between 1 and 25, got {self.aisle}")
        if not (1 <= self.rack <= 20):
            raise CoordinateError(f"Rack must be between 1 and 20, got {self.rack}")
    
    @classmethod
    def from_tuple(cls, coord_tuple: Tuple[int, int]) -> 'Coordinate':
        """Create coordinate from tuple (aisle, rack)."""
        if len(coord_tuple) != 2:
            raise CoordinateError(f"Coordinate tuple must have 2 elements, got {len(coord_tuple)}")
        return cls(coord_tuple[0], coord_tuple[1])
    
    @classmethod
    def from_dict(cls, coord_dict: dict) -> 'Coordinate':
        """Create coordinate from dictionary {'aisle': x, 'rack': y}."""
        if 'aisle' not in coord_dict or 'rack' not in coord_dict:
            raise CoordinateError("Coordinate dictionary must contain 'aisle' and 'rack' keys")
        return cls(coord_dict['aisle'], coord_dict['rack'])
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert coordinate to tuple (aisle, rack)."""
        return (self.aisle, self.rack)
    
    def to_dict(self) -> dict:
        """Convert coordinate to dictionary {'aisle': x, 'rack': y}."""
        return {'aisle': self.aisle, 'rack': self.rack}
    
    def distance_to(self, other: 'Coordinate') -> float:
        """
        Calculate Manhattan distance to another coordinate.
        
        Args:
            other: Target coordinate
            
        Returns:
            Manhattan distance between coordinates
        """
        return abs(self.aisle - other.aisle) + abs(self.rack - other.rack)
    
    def euclidean_distance_to(self, other: 'Coordinate') -> float:
        """
        Calculate Euclidean distance to another coordinate.
        
        Args:
            other: Target coordinate
            
        Returns:
            Euclidean distance between coordinates
        """
        return math.sqrt((self.aisle - other.aisle) ** 2 + (self.rack - other.rack) ** 2)
    
    def is_adjacent(self, other: 'Coordinate') -> bool:
        """
        Check if this coordinate is adjacent to another.
        
        Args:
            other: Coordinate to check adjacency with
            
        Returns:
            True if coordinates are adjacent (Manhattan distance = 1)
        """
        return self.distance_to(other) == 1
    
    def is_same_aisle(self, other: 'Coordinate') -> bool:
        """Check if coordinates are in the same aisle."""
        return self.aisle == other.aisle
    
    def is_same_rack(self, other: 'Coordinate') -> bool:
        """Check if coordinates are in the same rack."""
        return self.rack == other.rack
    
    def is_valid(self) -> bool:
        """Check if this coordinate is valid (within bounds)."""
        return 1 <= self.aisle <= 25 and 1 <= self.rack <= 20
    
    def is_packout_location(self) -> bool:
        """Check if this coordinate is the packout location (1, 1)."""
        return self.aisle == 1 and self.rack == 1
    
    def is_boundary(self) -> bool:
        """Check if this coordinate is on the warehouse boundary."""
        return (self.aisle == 1 or self.aisle == 25 or 
                self.rack == 1 or self.rack == 20)
    
    def is_corner(self) -> bool:
        """Check if this coordinate is a corner of the warehouse."""
        return ((self.aisle == 1 or self.aisle == 25) and 
                (self.rack == 1 or self.rack == 20))
    
    def __str__(self) -> str:
        """String representation: (aisle, rack)."""
        return f"({self.aisle}, {self.rack})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Coordinate(aisle={self.aisle}, rack={self.rack})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Coordinate):
            return False
        return self.aisle == other.aisle and self.rack == other.rack
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((self.aisle, self.rack))


@dataclass
class SmoothCoordinate:
    """
    Represents a warehouse grid coordinate with floating-point precision for smooth movement.
    
    Attributes:
        aisle: Aisle number (float for smooth interpolation)
        rack: Rack number (float for smooth interpolation)
    """
    
    aisle: float
    rack: float
    
    def __post_init__(self):
        """Validate coordinate bounds after initialization."""
        self._validate_bounds()
    
    def _validate_bounds(self):
        """Validate that coordinate is within warehouse bounds."""
        if not (1.0 <= self.aisle <= 25.0):
            raise CoordinateError(f"Aisle must be between 1.0 and 25.0, got {self.aisle}")
        if not (1.0 <= self.rack <= 20.0):
            raise CoordinateError(f"Rack must be between 1.0 and 20.0, got {self.rack}")
    
    def to_coordinate(self) -> Coordinate:
        """Convert to integer Coordinate for grid operations."""
        return Coordinate(int(self.aisle), int(self.rack))
    
    def distance_to(self, other: 'SmoothCoordinate') -> float:
        """Calculate Manhattan distance to another coordinate."""
        return abs(self.aisle - other.aisle) + abs(self.rack - other.rack)
    
    def __str__(self) -> str:
        """String representation: (aisle, rack)."""
        return f"({self.aisle:.2f}, {self.rack:.2f})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SmoothCoordinate(aisle={self.aisle:.2f}, rack={self.rack:.2f})"


def create_coordinate(aisle: int, rack: int) -> Coordinate:
    """
    Factory function to create a validated coordinate.
    
    Args:
        aisle: Aisle number (1-25)
        rack: Rack number (1-20)
        
    Returns:
        Validated Coordinate object
        
    Raises:
        CoordinateError: If coordinate is invalid
    """
    return Coordinate(aisle, rack)


def validate_coordinate_tuple(coord_tuple: Tuple[int, int]) -> bool:
    """
    Validate a coordinate tuple without creating an object.
    
    Args:
        coord_tuple: Tuple (aisle, rack) to validate
        
    Returns:
        True if coordinate is valid, False otherwise
    """
    try:
        Coordinate.from_tuple(coord_tuple)
        return True
    except CoordinateError:
        return False


def get_warehouse_bounds() -> Tuple[int, int]:
    """
    Get warehouse dimensions.
    
    Returns:
        Tuple of (max_aisle, max_rack)
    """
    return (25, 20)


def is_valid_aisle(aisle: int) -> bool:
    """Check if aisle number is valid."""
    return 1 <= aisle <= 25


def is_valid_rack(rack: int) -> bool:
    """Check if rack number is valid."""
    return 1 <= rack <= 20 