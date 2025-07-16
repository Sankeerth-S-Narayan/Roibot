"""
Tests for grid visualization and debug utilities.

Tests the GridVisualizer class functionality including grid rendering,
robot position display, path visualization, and debugging utilities.
"""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from core.layout.grid_visualizer import GridVisualizer, GridCellType, VisualCell
from core.layout.coordinate import Coordinate
from core.layout.warehouse_layout import WarehouseLayoutManager


class TestGridVisualizer(unittest.TestCase):
    """Test cases for GridVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = GridVisualizer()
        self.coord1 = Coordinate(1, 1)
        self.coord2 = Coordinate(5, 5)
        self.coord3 = Coordinate(10, 10)
        self.coord4 = Coordinate(15, 15)
    
    def test_initialization(self):
        """Test GridVisualizer initialization."""
        self.assertIsNotNone(self.visualizer.warehouse_layout)
        self.assertEqual(len(self.visualizer.robot_positions), 0)
        self.assertEqual(len(self.visualizer.highlighted_cells), 0)
        self.assertEqual(len(self.visualizer.path_cells), 0)
        self.assertTrue(self.visualizer.show_coordinates)
        self.assertTrue(self.visualizer.show_legend)
        self.assertFalse(self.visualizer.compact_mode)
    
    def test_set_robot_position(self):
        """Test setting robot position."""
        robot_id = "robot_001"
        
        self.visualizer.set_robot_position(robot_id, self.coord1)
        
        self.assertIn(robot_id, self.visualizer.robot_positions)
        self.assertEqual(self.visualizer.robot_positions[robot_id], self.coord1)
    
    def test_remove_robot_position(self):
        """Test removing robot position."""
        robot_id = "robot_001"
        
        # Set position
        self.visualizer.set_robot_position(robot_id, self.coord1)
        self.assertIn(robot_id, self.visualizer.robot_positions)
        
        # Remove position
        self.visualizer.remove_robot_position(robot_id)
        self.assertNotIn(robot_id, self.visualizer.robot_positions)
    
    def test_highlight_cell(self):
        """Test highlighting a cell."""
        self.visualizer.highlight_cell(self.coord1)
        
        self.assertIn(self.coord1, self.visualizer.highlighted_cells)
    
    def test_clear_highlights(self):
        """Test clearing highlights."""
        self.visualizer.highlight_cell(self.coord1)
        self.visualizer.highlight_cell(self.coord2)
        
        self.assertEqual(len(self.visualizer.highlighted_cells), 2)
        
        self.visualizer.clear_highlights()
        
        self.assertEqual(len(self.visualizer.highlighted_cells), 0)
    
    def test_set_path(self):
        """Test setting path for visualization."""
        path = [self.coord1, self.coord2, self.coord3]
        
        self.visualizer.set_path(path)
        
        self.assertEqual(len(self.visualizer.path_cells), 3)
        for coord in path:
            self.assertIn(coord, self.visualizer.path_cells)
    
    def test_clear_path(self):
        """Test clearing path."""
        path = [self.coord1, self.coord2]
        self.visualizer.set_path(path)
        
        self.assertEqual(len(self.visualizer.path_cells), 2)
        
        self.visualizer.clear_path()
        
        self.assertEqual(len(self.visualizer.path_cells), 0)
    
    def test_set_start_target_cells(self):
        """Test setting start and target cells."""
        self.visualizer.set_start_cell(self.coord1)
        self.visualizer.set_target_cell(self.coord2)
        
        self.assertIn(self.coord1, self.visualizer.start_cells)
        self.assertIn(self.coord2, self.visualizer.target_cells)
    
    def test_clear_start_target(self):
        """Test clearing start and target cells."""
        self.visualizer.set_start_cell(self.coord1)
        self.visualizer.set_target_cell(self.coord2)
        
        self.assertEqual(len(self.visualizer.start_cells), 1)
        self.assertEqual(len(self.visualizer.target_cells), 1)
        
        self.visualizer.clear_start_target()
        
        self.assertEqual(len(self.visualizer.start_cells), 0)
        self.assertEqual(len(self.visualizer.target_cells), 0)
    
    def test_get_cell_type_empty(self):
        """Test getting cell type for empty cell."""
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.EMPTY)
    
    def test_get_cell_type_packout(self):
        """Test getting cell type for packout location."""
        cell_type = self.visualizer.get_cell_type(self.coord1)  # (1, 1) is packout
        self.assertEqual(cell_type, GridCellType.PACKOUT)
    
    def test_get_cell_type_robot(self):
        """Test getting cell type for robot position."""
        robot_id = "robot_001"
        self.visualizer.set_robot_position(robot_id, self.coord2)
        
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.ROBOT)
    
    def test_get_cell_type_target(self):
        """Test getting cell type for target cell."""
        self.visualizer.set_target_cell(self.coord2)
        
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.TARGET)
    
    def test_get_cell_type_start(self):
        """Test getting cell type for start cell."""
        self.visualizer.set_start_cell(self.coord2)
        
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.START)
    
    def test_get_cell_type_path(self):
        """Test getting cell type for path cell."""
        path = [self.coord2]
        self.visualizer.set_path(path)
        
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.PATH)
    
    def test_get_cell_type_highlight(self):
        """Test getting cell type for highlighted cell."""
        self.visualizer.highlight_cell(self.coord2)
        
        cell_type = self.visualizer.get_cell_type(self.coord2)
        self.assertEqual(cell_type, GridCellType.HIGHLIGHT)
    
    def test_get_cell_symbol_robot(self):
        """Test getting cell symbol for robot."""
        robot_id = "robot_001"
        self.visualizer.set_robot_position(robot_id, self.coord2)
        
        symbol = self.visualizer.get_cell_symbol(self.coord2)
        self.assertEqual(symbol, "R1")  # Last character of robot_001
    
    def test_get_cell_symbol_default(self):
        """Test getting default cell symbol."""
        symbol = self.visualizer.get_cell_symbol(self.coord2)
        self.assertEqual(symbol, GridCellType.EMPTY.value)
    
    def test_render_grid(self):
        """Test grid rendering."""
        rendered = self.visualizer.render_grid()
        
        # Should contain grid content
        self.assertIn("WAREHOUSE GRID VISUALIZATION", rendered)
        self.assertIn("LEGEND:", rendered)
        self.assertIn("GRID STATISTICS:", rendered)
    
    def test_render_compact_grid(self):
        """Test compact grid rendering."""
        self.visualizer.compact_mode = True
        rendered = self.visualizer.render_grid()
        
        # Should not contain extra information
        self.assertNotIn("WAREHOUSE GRID VISUALIZATION", rendered)
        self.assertNotIn("LEGEND:", rendered)
        self.assertNotIn("GRID STATISTICS:", rendered)
    
    def test_visualize_path(self):
        """Test path visualization."""
        path = [self.coord1, self.coord2, self.coord3]
        start = self.coord1
        target = self.coord3
        
        rendered = self.visualizer.visualize_path(path, start, target)
        
        # Should contain path visualization
        self.assertIn("WAREHOUSE GRID VISUALIZATION", rendered)
        self.assertIn("Path", rendered)
    
    def test_export_grid_state(self):
        """Test grid state export."""
        # Add some data
        self.visualizer.set_robot_position("robot_001", self.coord1)
        self.visualizer.highlight_cell(self.coord2)
        self.visualizer.set_path([self.coord3])
        
        state = self.visualizer.export_grid_state()
        
        # Verify export structure
        self.assertIn("robot_positions", state)
        self.assertIn("highlighted_cells", state)
        self.assertIn("path_cells", state)
        self.assertIn("warehouse_stats", state)
        
        # Verify data integrity
        self.assertIn("robot_001", state["robot_positions"])
        self.assertEqual(len(state["highlighted_cells"]), 1)
        self.assertEqual(len(state["path_cells"]), 1)
    
    def test_import_grid_state(self):
        """Test grid state import."""
        # Create test state
        test_state = {
            "robot_positions": {"robot_001": (5, 5)},
            "highlighted_cells": [(10, 10)],
            "path_cells": [(15, 15)],
            "start_cells": [(1, 1)],
            "target_cells": [(20, 20)]
        }
        
        # Import state
        self.visualizer.import_grid_state(test_state)
        
        # Verify import
        self.assertIn("robot_001", self.visualizer.robot_positions)
        self.assertEqual(self.visualizer.robot_positions["robot_001"], Coordinate(5, 5))
        self.assertIn(Coordinate(10, 10), self.visualizer.highlighted_cells)
        self.assertIn(Coordinate(15, 15), self.visualizer.path_cells)
        self.assertIn(Coordinate(1, 1), self.visualizer.start_cells)
        self.assertIn(Coordinate(20, 20), self.visualizer.target_cells)
    
    def test_get_grid_summary(self):
        """Test grid summary generation."""
        # Add some data
        self.visualizer.set_robot_position("robot_001", self.coord1)
        self.visualizer.highlight_cell(self.coord2)
        
        summary = self.visualizer.get_grid_summary()
        
        # Verify summary content
        self.assertIn("GRID SUMMARY:", summary)
        self.assertIn("Dimensions: 25x20", summary)
        self.assertIn("Robots: 1", summary)
        self.assertIn("Highlighted: 1", summary)
        self.assertIn("robot_001:", summary)
    
    def test_clear_all(self):
        """Test clearing all visualization data."""
        # Add some data
        self.visualizer.set_robot_position("robot_001", self.coord1)
        self.visualizer.highlight_cell(self.coord2)
        self.visualizer.set_path([self.coord3])
        self.visualizer.set_start_cell(self.coord4)
        self.visualizer.set_target_cell(self.coord1)
        
        # Verify data exists
        self.assertEqual(len(self.visualizer.robot_positions), 1)
        self.assertEqual(len(self.visualizer.highlighted_cells), 1)
        self.assertEqual(len(self.visualizer.path_cells), 1)
        self.assertEqual(len(self.visualizer.start_cells), 1)
        self.assertEqual(len(self.visualizer.target_cells), 1)
        
        # Clear all
        self.visualizer.clear_all()
        
        # Verify all cleared
        self.assertEqual(len(self.visualizer.robot_positions), 0)
        self.assertEqual(len(self.visualizer.highlighted_cells), 0)
        self.assertEqual(len(self.visualizer.path_cells), 0)
        self.assertEqual(len(self.visualizer.start_cells), 0)
        self.assertEqual(len(self.visualizer.target_cells), 0)
    
    def test_set_visualization_options(self):
        """Test setting visualization options."""
        # Test setting options
        self.visualizer.set_visualization_options(
            show_coordinates=False,
            show_legend=False,
            compact_mode=True
        )
        
        self.assertFalse(self.visualizer.show_coordinates)
        self.assertFalse(self.visualizer.show_legend)
        self.assertTrue(self.visualizer.compact_mode)
    
    def test_cell_priority_order(self):
        """Test cell type priority order."""
        # Set up all types for the same coordinate
        coord = self.coord2
        self.visualizer.set_robot_position("robot_001", coord)
        self.visualizer.set_target_cell(coord)
        self.visualizer.set_start_cell(coord)
        self.visualizer.set_path([coord])
        self.visualizer.highlight_cell(coord)
        
        # Robot should have highest priority
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.ROBOT)
    
    def test_multiple_robots(self):
        """Test multiple robot positions."""
        self.visualizer.set_robot_position("robot_001", self.coord1)
        self.visualizer.set_robot_position("robot_002", self.coord2)
        
        self.assertEqual(len(self.visualizer.robot_positions), 2)
        self.assertEqual(self.visualizer.robot_positions["robot_001"], self.coord1)
        self.assertEqual(self.visualizer.robot_positions["robot_002"], self.coord2)
    
    def test_path_visualization_with_start_target(self):
        """Test path visualization with start and target."""
        path = [self.coord1, self.coord2, self.coord3]
        start = self.coord1
        target = self.coord3
        
        rendered = self.visualizer.visualize_path(path, start, target)
        
        # Should show start and target
        self.assertIn("Start", rendered)
        self.assertIn("Target", rendered)
        self.assertIn("Path", rendered)
    
    def test_grid_statistics(self):
        """Test grid statistics in rendered output."""
        rendered = self.visualizer.render_grid()
        
        # Should contain statistics
        self.assertIn("Total Cells:", rendered)
        self.assertIn("Empty Cells:", rendered)
        self.assertIn("Occupied Cells:", rendered)
        self.assertIn("Robots:", rendered)
        self.assertIn("Highlighted:", rendered)
        self.assertIn("Path Cells:", rendered)


class TestGridCellType(unittest.TestCase):
    """Test cases for GridCellType enum."""
    
    def test_cell_types(self):
        """Test all cell types have values."""
        self.assertEqual(GridCellType.EMPTY.value, " ")
        self.assertEqual(GridCellType.OCCUPIED.value, "█")
        self.assertEqual(GridCellType.PACKOUT.value, "P")
        self.assertEqual(GridCellType.ROBOT.value, "R")
        self.assertEqual(GridCellType.PATH.value, "·")
        self.assertEqual(GridCellType.HIGHLIGHT.value, "★")
        self.assertEqual(GridCellType.START.value, "S")
        self.assertEqual(GridCellType.TARGET.value, "T")


class TestVisualCell(unittest.TestCase):
    """Test cases for VisualCell dataclass."""
    
    def test_visual_cell_creation(self):
        """Test VisualCell creation."""
        cell = VisualCell(GridCellType.EMPTY, "test", "red")
        
        self.assertEqual(cell.cell_type, GridCellType.EMPTY)
        self.assertEqual(cell.content, "test")
        self.assertEqual(cell.color, "red")
        self.assertIsInstance(cell.metadata, dict)
    
    def test_visual_cell_defaults(self):
        """Test VisualCell default values."""
        cell = VisualCell(GridCellType.ROBOT)
        
        self.assertEqual(cell.cell_type, GridCellType.ROBOT)
        self.assertEqual(cell.content, "")
        self.assertIsNone(cell.color)
        self.assertIsInstance(cell.metadata, dict)


if __name__ == "__main__":
    unittest.main() 