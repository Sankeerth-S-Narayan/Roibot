"""
Grid visualization and debug utilities for warehouse layout.

This module provides console-based grid visualization, robot position display,
path visualization, and debugging utilities for the warehouse layout system.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import os
import sys

from .coordinate import Coordinate
from .warehouse_layout import WarehouseLayoutManager
from .snake_pattern import Direction


class GridCellType(Enum):
    """Types of grid cells for visualization."""
    EMPTY = " "
    OCCUPIED = "█"
    PACKOUT = "P"
    ROBOT = "R"
    PATH = "·"
    HIGHLIGHT = "★"
    START = "S"
    TARGET = "T"


@dataclass
class VisualCell:
    """Represents a cell in the grid visualization."""
    cell_type: GridCellType
    content: str = ""
    color: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GridVisualizer:
    """
    Console-based grid visualization for warehouse layout.
    
    Provides comprehensive visualization of the warehouse grid including
    robot positions, paths, highlights, and debugging information.
    """
    
    def __init__(self, warehouse_layout: Optional[WarehouseLayoutManager] = None):
        """
        Initialize grid visualizer.
        
        Args:
            warehouse_layout: Warehouse layout manager instance
        """
        self.warehouse_layout = warehouse_layout or WarehouseLayoutManager()
        self.robot_positions: Dict[str, Coordinate] = {}
        self.highlighted_cells: Set[Coordinate] = set()
        self.path_cells: Set[Coordinate] = set()
        self.start_cells: Set[Coordinate] = set()
        self.target_cells: Set[Coordinate] = set()
        
        # Visualization settings
        self.show_coordinates = True
        self.show_legend = True
        self.compact_mode = False
        self.max_width = 120  # Terminal width limit
    
    def set_robot_position(self, robot_id: str, position: Coordinate) -> None:
        """
        Set robot position for visualization.
        
        Args:
            robot_id: ID of the robot
            position: Current position of the robot
        """
        self.robot_positions[robot_id] = position
    
    def remove_robot_position(self, robot_id: str) -> None:
        """
        Remove robot position from visualization.
        
        Args:
            robot_id: ID of the robot to remove
        """
        if robot_id in self.robot_positions:
            del self.robot_positions[robot_id]
    
    def highlight_cell(self, coordinate: Coordinate) -> None:
        """
        Highlight a specific cell.
        
        Args:
            coordinate: Coordinate to highlight
        """
        self.highlighted_cells.add(coordinate)
    
    def clear_highlights(self) -> None:
        """Clear all highlighted cells."""
        self.highlighted_cells.clear()
    
    def set_path(self, path: List[Coordinate]) -> None:
        """
        Set path for visualization.
        
        Args:
            path: List of coordinates representing the path
        """
        self.path_cells = set(path)
    
    def clear_path(self) -> None:
        """Clear current path visualization."""
        self.path_cells.clear()
    
    def set_start_cell(self, coordinate: Coordinate) -> None:
        """
        Set start cell for visualization.
        
        Args:
            coordinate: Start coordinate
        """
        self.start_cells.add(coordinate)
    
    def set_target_cell(self, coordinate: Coordinate) -> None:
        """
        Set target cell for visualization.
        
        Args:
            coordinate: Target coordinate
        """
        self.target_cells.add(coordinate)
    
    def clear_start_target(self) -> None:
        """Clear start and target cells."""
        self.start_cells.clear()
        self.target_cells.clear()
    
    def get_cell_type(self, coordinate: Coordinate) -> GridCellType:
        """
        Determine cell type for visualization.
        
        Args:
            coordinate: Coordinate to check
            
        Returns:
            Cell type for visualization
        """
        # Check priority order: robot > target > start > path > highlight > packout > occupied > empty
        
        # Check if robot is at this position
        for robot_id, pos in self.robot_positions.items():
            if pos == coordinate:
                return GridCellType.ROBOT
        
        # Check if it's a target cell
        if coordinate in self.target_cells:
            return GridCellType.TARGET
        
        # Check if it's a start cell
        if coordinate in self.start_cells:
            return GridCellType.START
        
        # Check if it's part of a path
        if coordinate in self.path_cells:
            return GridCellType.PATH
        
        # Check if it's highlighted
        if coordinate in self.highlighted_cells:
            return GridCellType.HIGHLIGHT
        
        # Check if it's packout location
        if coordinate == Coordinate(1, 1):
            return GridCellType.PACKOUT
        
        # Check if it's occupied (from warehouse layout)
        if self.warehouse_layout.is_position_occupied(coordinate):
            return GridCellType.OCCUPIED
        
        # Default to empty
        return GridCellType.EMPTY
    
    def get_cell_symbol(self, coordinate: Coordinate) -> str:
        """
        Get symbol for a cell.
        
        Args:
            coordinate: Coordinate to get symbol for
            
        Returns:
            Symbol string for the cell
        """
        cell_type = self.get_cell_type(coordinate)
        
        # Check if robot is at this position for special symbol
        for robot_id, pos in self.robot_positions.items():
            if pos == coordinate:
                return f"R{robot_id[-1]}"  # Use last character of robot ID
        
        return cell_type.value
    
    def render_grid(self) -> str:
        """
        Render the complete grid as a string.
        
        Returns:
            Formatted grid string
        """
        if self.compact_mode:
            return self._render_compact_grid()
        else:
            return self._render_full_grid()
    
    def _render_full_grid(self) -> str:
        """Render full grid with coordinates and legend."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("WAREHOUSE GRID VISUALIZATION")
        lines.append("=" * 80)
        
        # Grid content
        grid_lines = self._generate_grid_lines()
        lines.extend(grid_lines)
        
        # Legend
        if self.show_legend:
            lines.append("")
            lines.append("LEGEND:")
            lines.append(f"  {GridCellType.EMPTY.value} = Empty")
            lines.append(f"  {GridCellType.OCCUPIED.value} = Occupied")
            lines.append(f"  {GridCellType.PACKOUT.value} = Packout Location")
            lines.append(f"  {GridCellType.ROBOT.value} = Robot Position")
            lines.append(f"  {GridCellType.PATH.value} = Path")
            lines.append(f"  {GridCellType.HIGHLIGHT.value} = Highlighted")
            lines.append(f"  {GridCellType.START.value} = Start")
            lines.append(f"  {GridCellType.TARGET.value} = Target")
        
        # Robot positions
        if self.robot_positions:
            lines.append("")
            lines.append("ROBOT POSITIONS:")
            for robot_id, pos in self.robot_positions.items():
                lines.append(f"  {robot_id}: {pos}")
        
        # Statistics
        lines.append("")
        lines.append("GRID STATISTICS:")
        stats = self.warehouse_layout.get_grid_statistics()
        lines.append(f"  Total Cells: {stats['total_positions']}")
        lines.append(f"  Empty Cells: {stats['empty_positions']}")
        lines.append(f"  Occupied Cells: {stats['occupied_positions']}")
        lines.append(f"  Robots: {len(self.robot_positions)}")
        lines.append(f"  Highlighted: {len(self.highlighted_cells)}")
        lines.append(f"  Path Cells: {len(self.path_cells)}")
        
        return "\n".join(lines)
    
    def _render_compact_grid(self) -> str:
        """Render compact grid without extra information."""
        return "\n".join(self._generate_grid_lines())
    
    def _generate_grid_lines(self) -> List[str]:
        """Generate grid lines for visualization."""
        lines = []
        
        # Column headers
        if self.show_coordinates:
            header = "    "  # Space for row numbers
            for rack in range(1, 21):
                header += f" {rack:2d}"
            lines.append(header)
            lines.append("    " + "-" * 60)  # Separator
        
        # Grid rows
        for aisle in range(1, 26):
            if self.show_coordinates:
                line = f"{aisle:2d} |"
            else:
                line = "|"
            
            for rack in range(1, 21):
                coord = Coordinate(aisle, rack)
                symbol = self.get_cell_symbol(coord)
                line += f" {symbol}"
            
            line += " |"
            lines.append(line)
        
        return lines
    
    def print_grid(self) -> None:
        """Print the grid to console."""
        print(self.render_grid())
    
    def visualize_path(self, path: List[Coordinate], start: Optional[Coordinate] = None,
                      target: Optional[Coordinate] = None) -> str:
        """
        Visualize a specific path.
        
        Args:
            path: List of coordinates representing the path
            start: Optional start coordinate
            target: Optional target coordinate
            
        Returns:
            Formatted path visualization
        """
        # Clear previous path and set new one
        self.clear_path()
        self.clear_start_target()
        
        if start:
            self.set_start_cell(start)
        if target:
            self.set_target_cell(target)
        
        self.set_path(path)
        
        return self.render_grid()
    
    def print_path_visualization(self, path: List[Coordinate], start: Optional[Coordinate] = None,
                                target: Optional[Coordinate] = None) -> None:
        """
        Print path visualization to console.
        
        Args:
            path: List of coordinates representing the path
            start: Optional start coordinate
            target: Optional target coordinate
        """
        print(self.visualize_path(path, start, target))
    
    def export_grid_state(self) -> Dict[str, Any]:
        """
        Export current grid state for debugging.
        
        Returns:
            Dictionary containing grid state information
        """
        return {
            "robot_positions": {
                robot_id: (pos.aisle, pos.rack)
                for robot_id, pos in self.robot_positions.items()
            },
            "highlighted_cells": [
                (coord.aisle, coord.rack) for coord in self.highlighted_cells
            ],
            "path_cells": [
                (coord.aisle, coord.rack) for coord in self.path_cells
            ],
            "start_cells": [
                (coord.aisle, coord.rack) for coord in self.start_cells
            ],
            "target_cells": [
                (coord.aisle, coord.rack) for coord in self.target_cells
            ],
            "warehouse_stats": self.warehouse_layout.get_grid_statistics()
        }
    
    def import_grid_state(self, state: Dict[str, Any]) -> None:
        """
        Import grid state from exported data.
        
        Args:
            state: Dictionary containing grid state information
        """
        # Clear current state
        self.robot_positions.clear()
        self.highlighted_cells.clear()
        self.path_cells.clear()
        self.start_cells.clear()
        self.target_cells.clear()
        
        # Import robot positions
        for robot_id, pos_data in state.get("robot_positions", {}).items():
            self.robot_positions[robot_id] = Coordinate(pos_data[0], pos_data[1])
        
        # Import highlighted cells
        for coord_data in state.get("highlighted_cells", []):
            self.highlighted_cells.add(Coordinate(coord_data[0], coord_data[1]))
        
        # Import path cells
        for coord_data in state.get("path_cells", []):
            self.path_cells.add(Coordinate(coord_data[0], coord_data[1]))
        
        # Import start cells
        for coord_data in state.get("start_cells", []):
            self.start_cells.add(Coordinate(coord_data[0], coord_data[1]))
        
        # Import target cells
        for coord_data in state.get("target_cells", []):
            self.target_cells.add(Coordinate(coord_data[0], coord_data[1]))
    
    def get_grid_summary(self) -> str:
        """
        Get a summary of the current grid state.
        
        Returns:
            Summary string
        """
        stats = self.warehouse_layout.get_grid_statistics()
        summary_lines = [
            "GRID SUMMARY:",
            f"  Dimensions: 25x20 ({stats['total_positions']} total cells)",
            f"  Empty: {stats['empty_positions']}",
            f"  Occupied: {stats['occupied_positions']}",
            f"  Packout: (1, 1)",
            f"  Robots: {len(self.robot_positions)}",
            f"  Highlighted: {len(self.highlighted_cells)}",
            f"  Path Length: {len(self.path_cells)}",
            f"  Start Points: {len(self.start_cells)}",
            f"  Target Points: {len(self.target_cells)}"
        ]
        
        if self.robot_positions:
            summary_lines.append("  Robot Positions:")
            for robot_id, pos in self.robot_positions.items():
                summary_lines.append(f"    {robot_id}: {pos}")
        
        return "\n".join(summary_lines)
    
    def print_summary(self) -> None:
        """Print grid summary to console."""
        print(self.get_grid_summary())
    
    def clear_all(self) -> None:
        """Clear all visualization data."""
        self.robot_positions.clear()
        self.highlighted_cells.clear()
        self.path_cells.clear()
        self.start_cells.clear()
        self.target_cells.clear()
    
    def set_visualization_options(self, show_coordinates: bool = None, 
                                 show_legend: bool = None, 
                                 compact_mode: bool = None) -> None:
        """
        Set visualization options.
        
        Args:
            show_coordinates: Whether to show coordinate labels
            show_legend: Whether to show legend
            compact_mode: Whether to use compact mode
        """
        if show_coordinates is not None:
            self.show_coordinates = show_coordinates
        if show_legend is not None:
            self.show_legend = show_legend
        if compact_mode is not None:
            self.compact_mode = compact_mode 