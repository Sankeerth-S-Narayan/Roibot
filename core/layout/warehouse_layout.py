"""
Warehouse layout manager for grid system management.

This module provides the WarehouseLayoutManager singleton class for managing
the 25x20 warehouse grid, coordinate validation, and grid state management.
"""

from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import json

from .coordinate import Coordinate, CoordinateError, get_warehouse_bounds


class GridState(Enum):
    """Enumeration for grid cell states."""
    EMPTY = "empty"
    OCCUPIED = "occupied"
    PACKOUT = "packout"
    RESERVED = "reserved"


class WarehouseLayoutManager:
    """
    Singleton class for managing warehouse grid layout and state.
    
    Manages the 25x20 warehouse grid with coordinate validation,
    grid state tracking, and integration with existing systems.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure singleton pattern - only one instance exists."""
        if cls._instance is None:
            cls._instance = super(WarehouseLayoutManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize warehouse layout manager (only once)."""
        if not self._initialized:
            self._initialize_grid()
            self._initialized = True
    
    def _initialize_grid(self):
        """Initialize the warehouse grid and state."""
        self.max_aisle, self.max_rack = get_warehouse_bounds()
        self.grid_state: Dict[Coordinate, GridState] = {}
        self.occupied_positions: Set[Coordinate] = set()
        self.packout_location = Coordinate(1, 1)
        
        # Initialize all grid positions as empty
        for aisle in range(1, self.max_aisle + 1):
            for rack in range(1, self.max_rack + 1):
                coord = Coordinate(aisle, rack)
                if coord.is_packout_location():
                    self.grid_state[coord] = GridState.PACKOUT
                else:
                    self.grid_state[coord] = GridState.EMPTY
        
        # Mark packout as occupied
        self.occupied_positions.add(self.packout_location)
    
    def get_grid_dimensions(self) -> Tuple[int, int]:
        """
        Get warehouse grid dimensions.
        
        Returns:
            Tuple of (max_aisle, max_rack)
        """
        return (self.max_aisle, self.max_rack)
    
    def is_valid_coordinate(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is within warehouse bounds.
        
        Args:
            coord: Coordinate to validate
            
        Returns:
            True if coordinate is valid, False otherwise
        """
        try:
            # Validate bounds directly without creating new object
            return (1 <= coord.aisle <= self.max_aisle and 
                    1 <= coord.rack <= self.max_rack)
        except AttributeError:
            return False
    
    def get_grid_state(self, coord: Coordinate) -> GridState:
        """
        Get the state of a grid position.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            GridState of the position
            
        Raises:
            CoordinateError: If coordinate is invalid
        """
        if not self.is_valid_coordinate(coord):
            raise CoordinateError(f"Invalid coordinate: {coord}")
        
        return self.grid_state.get(coord, GridState.EMPTY)
    
    def set_grid_state(self, coord: Coordinate, state: GridState) -> bool:
        """
        Set the state of a grid position.
        
        Args:
            coord: Coordinate to update
            state: New state for the position
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            CoordinateError: If coordinate is invalid
        """
        if not self.is_valid_coordinate(coord):
            raise CoordinateError(f"Invalid coordinate: {coord}")
        
        # Update grid state
        self.grid_state[coord] = state
        
        # Update occupied positions set
        if state == GridState.OCCUPIED:
            self.occupied_positions.add(coord)
        elif state == GridState.EMPTY:
            self.occupied_positions.discard(coord)
        
        return True
    
    def is_position_occupied(self, coord: Coordinate) -> bool:
        """
        Check if a position is occupied.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if position is occupied, False otherwise
        """
        return coord in self.occupied_positions
    
    def is_packout_location(self, coord: Coordinate) -> bool:
        """
        Check if coordinate is the packout location.
        
        Args:
            coord: Coordinate to check
            
        Returns:
            True if coordinate is packout location, False otherwise
        """
        return coord.is_packout_location()
    
    def get_packout_location(self) -> Coordinate:
        """
        Get the packout location coordinate.
        
        Returns:
            Packout location coordinate (1, 1)
        """
        return self.packout_location
    
    def get_available_positions(self) -> List[Coordinate]:
        """
        Get all available (empty) positions in the warehouse.
        
        Returns:
            List of available coordinates
        """
        available = []
        for coord, state in self.grid_state.items():
            if state == GridState.EMPTY:
                available.append(coord)
        return available
    
    def get_occupied_positions(self) -> List[Coordinate]:
        """
        Get all occupied positions in the warehouse.
        
        Returns:
            List of occupied coordinates
        """
        return list(self.occupied_positions)
    
    def get_grid_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the warehouse grid.
        
        Returns:
            Dictionary with grid statistics
        """
        total_positions = self.max_aisle * self.max_rack
        occupied_count = len(self.occupied_positions)
        empty_count = total_positions - occupied_count  # Don't subtract packout again
        
        return {
            'total_positions': total_positions,
            'occupied_positions': occupied_count,
            'empty_positions': empty_count,
            'packout_position': 1,
            'max_aisle': self.max_aisle,
            'max_rack': self.max_rack
        }
    
    def validate_coordinate_bounds(self, aisle: int, rack: int) -> bool:
        """
        Validate coordinate bounds without creating object.
        
        Args:
            aisle: Aisle number to validate
            rack: Rack number to validate
            
        Returns:
            True if coordinates are within bounds, False otherwise
        """
        return (1 <= aisle <= self.max_aisle and 
                1 <= rack <= self.max_rack)
    
    def get_grid_snapshot(self) -> Dict[str, any]:
        """
        Get a snapshot of the current grid state for persistence.
        
        Returns:
            Dictionary representation of grid state
        """
        snapshot = {
            'dimensions': {
                'max_aisle': self.max_aisle,
                'max_rack': self.max_rack
            },
            'packout_location': self.packout_location.to_dict(),
            'grid_state': {},
            'occupied_positions': [],
            'statistics': self.get_grid_statistics()
        }
        
        # Convert grid state to serializable format
        for coord, state in self.grid_state.items():
            coord_str = f"{coord.aisle},{coord.rack}"
            snapshot['grid_state'][coord_str] = state.value
        
        # Convert occupied positions to serializable format
        for coord in self.occupied_positions:
            snapshot['occupied_positions'].append(coord.to_dict())
        
        return snapshot
    
    def load_grid_snapshot(self, snapshot: Dict[str, any]) -> bool:
        """
        Load grid state from a snapshot.
        
        Args:
            snapshot: Grid state snapshot to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate snapshot structure
            if 'dimensions' not in snapshot or 'grid_state' not in snapshot:
                return False
            
            # Reset grid state
            self._initialize_grid()
            
            # Load grid state
            for coord_str, state_value in snapshot['grid_state'].items():
                aisle, rack = map(int, coord_str.split(','))
                coord = Coordinate(aisle, rack)
                state = GridState(state_value)
                self.set_grid_state(coord, state)
            
            return True
        except (ValueError, KeyError, CoordinateError):
            return False
    
    def reset_grid(self):
        """Reset the grid to initial state."""
        self._initialize_grid()
    
    def get_grid_visualization(self, robot_position: Optional[Coordinate] = None) -> str:
        """
        Create a text-based visualization of the warehouse grid.
        
        Args:
            robot_position: Optional robot position to highlight
            
        Returns:
            String representation of the grid
        """
        visualization = []
        visualization.append(f"Warehouse Grid ({self.max_aisle}x{self.max_rack})")
        visualization.append("=" * 50)
        
        # Header row
        header = "    "
        for rack in range(1, self.max_rack + 1):
            header += f"{rack:2d} "
        visualization.append(header)
        visualization.append("")
        
        # Grid rows
        for aisle in range(1, self.max_aisle + 1):
            row = f"{aisle:2d} |"
            for rack in range(1, self.max_rack + 1):
                coord = Coordinate(aisle, rack)
                
                if robot_position and coord == robot_position:
                    row += " R "  # Robot
                elif coord.is_packout_location():
                    row += " P "  # Packout
                elif self.is_position_occupied(coord):
                    row += " X "  # Occupied
                else:
                    row += " . "  # Empty
            
            visualization.append(row)
        
        # Legend
        visualization.append("")
        visualization.append("Legend: R=Robot, P=Packout, X=Occupied, .=Empty")
        
        return "\n".join(visualization)
    
    def __str__(self) -> str:
        """String representation of warehouse layout manager."""
        stats = self.get_grid_statistics()
        return (f"WarehouseLayoutManager({self.max_aisle}x{self.max_rack}) - "
                f"Occupied: {stats['occupied_positions']}, "
                f"Empty: {stats['empty_positions']}")
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"WarehouseLayoutManager(dimensions=({self.max_aisle}, {self.max_rack}))"


# Global instance for easy access
warehouse_layout = WarehouseLayoutManager() 