"""
Unit tests for the WarehouseLayoutManager class.

Tests singleton pattern, grid management, coordinate validation, and state management.
"""

import unittest
from core.layout.warehouse_layout import (
    WarehouseLayoutManager, GridState, warehouse_layout
)
from core.layout.coordinate import Coordinate, CoordinateError


class TestWarehouseLayoutManager(unittest.TestCase):
    """Test cases for the WarehouseLayoutManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset the warehouse layout for each test
        self.layout_manager = WarehouseLayoutManager()
        self.layout_manager.reset_grid()
    
    def test_singleton_pattern(self):
        """Test that WarehouseLayoutManager follows singleton pattern."""
        manager1 = WarehouseLayoutManager()
        manager2 = WarehouseLayoutManager()
        
        # Should be the same instance
        self.assertIs(manager1, manager2)
        self.assertIs(manager1, warehouse_layout)
    
    def test_grid_dimensions(self):
        """Test grid dimensions are correct."""
        max_aisle, max_rack = self.layout_manager.get_grid_dimensions()
        self.assertEqual(max_aisle, 25)
        self.assertEqual(max_rack, 20)
    
    def test_valid_coordinate_validation(self):
        """Test coordinate validation with valid coordinates."""
        # Valid coordinates
        self.assertTrue(self.layout_manager.is_valid_coordinate(Coordinate(1, 1)))
        self.assertTrue(self.layout_manager.is_valid_coordinate(Coordinate(25, 20)))
        self.assertTrue(self.layout_manager.is_valid_coordinate(Coordinate(13, 10)))
    
    def test_invalid_coordinate_validation(self):
        """Test coordinate validation with invalid coordinates."""
        # Create invalid coordinates by directly setting attributes
        class InvalidCoordinate:
            def __init__(self, aisle, rack):
                self.aisle = aisle
                self.rack = rack
        
        # Invalid coordinates
        self.assertFalse(self.layout_manager.is_valid_coordinate(InvalidCoordinate(0, 1)))
        self.assertFalse(self.layout_manager.is_valid_coordinate(InvalidCoordinate(26, 1)))
        self.assertFalse(self.layout_manager.is_valid_coordinate(InvalidCoordinate(1, 0)))
        self.assertFalse(self.layout_manager.is_valid_coordinate(InvalidCoordinate(1, 21)))
    
    def test_get_grid_state(self):
        """Test getting grid state for different positions."""
        # Packout location
        packout = Coordinate(1, 1)
        self.assertEqual(self.layout_manager.get_grid_state(packout), GridState.PACKOUT)
        
        # Empty position
        empty = Coordinate(2, 2)
        self.assertEqual(self.layout_manager.get_grid_state(empty), GridState.EMPTY)
    
    def test_set_grid_state(self):
        """Test setting grid state."""
        coord = Coordinate(5, 5)
        
        # Initially empty
        self.assertEqual(self.layout_manager.get_grid_state(coord), GridState.EMPTY)
        self.assertFalse(self.layout_manager.is_position_occupied(coord))
        
        # Set to occupied
        self.assertTrue(self.layout_manager.set_grid_state(coord, GridState.OCCUPIED))
        self.assertEqual(self.layout_manager.get_grid_state(coord), GridState.OCCUPIED)
        self.assertTrue(self.layout_manager.is_position_occupied(coord))
        
        # Set back to empty
        self.assertTrue(self.layout_manager.set_grid_state(coord, GridState.EMPTY))
        self.assertEqual(self.layout_manager.get_grid_state(coord), GridState.EMPTY)
        self.assertFalse(self.layout_manager.is_position_occupied(coord))
    
    def test_invalid_coordinate_operations(self):
        """Test operations with invalid coordinates raise errors."""
        # Create invalid coordinate that passes validation but is out of bounds
        class InvalidCoordinate:
            def __init__(self, aisle, rack):
                self.aisle = aisle
                self.rack = rack
        
        invalid_coord = InvalidCoordinate(0, 0)
        
        # These should raise CoordinateError because the coordinate is invalid
        with self.assertRaises(CoordinateError):
            self.layout_manager.get_grid_state(invalid_coord)
        
        with self.assertRaises(CoordinateError):
            self.layout_manager.set_grid_state(invalid_coord, GridState.OCCUPIED)
    
    def test_packout_location(self):
        """Test packout location identification."""
        packout = Coordinate(1, 1)
        other = Coordinate(1, 2)
        
        self.assertTrue(self.layout_manager.is_packout_location(packout))
        self.assertFalse(self.layout_manager.is_packout_location(other))
        
        # Get packout location
        retrieved_packout = self.layout_manager.get_packout_location()
        self.assertEqual(retrieved_packout, packout)
    
    def test_available_positions(self):
        """Test getting available positions."""
        available = self.layout_manager.get_available_positions()
        
        # Should include all positions except packout
        expected_count = 25 * 20 - 1  # Total - packout
        self.assertEqual(len(available), expected_count)
        
        # Packout should not be in available positions
        packout = Coordinate(1, 1)
        self.assertNotIn(packout, available)
    
    def test_occupied_positions(self):
        """Test getting occupied positions."""
        # Initially only packout is occupied
        occupied = self.layout_manager.get_occupied_positions()
        self.assertEqual(len(occupied), 1)
        self.assertIn(Coordinate(1, 1), occupied)
        
        # Add another occupied position
        coord = Coordinate(5, 5)
        self.layout_manager.set_grid_state(coord, GridState.OCCUPIED)
        
        occupied = self.layout_manager.get_occupied_positions()
        self.assertEqual(len(occupied), 2)
        self.assertIn(Coordinate(1, 1), occupied)
        self.assertIn(coord, occupied)
    
    def test_grid_statistics(self):
        """Test grid statistics calculation."""
        stats = self.layout_manager.get_grid_statistics()
        
        self.assertEqual(stats['total_positions'], 500)  # 25 * 20
        self.assertEqual(stats['occupied_positions'], 1)  # Only packout
        self.assertEqual(stats['empty_positions'], 499)  # Total - occupied (packout is included in occupied)
        self.assertEqual(stats['packout_position'], 1)
        self.assertEqual(stats['max_aisle'], 25)
        self.assertEqual(stats['max_rack'], 20)
    
    def test_coordinate_bounds_validation(self):
        """Test coordinate bounds validation."""
        # Valid bounds
        self.assertTrue(self.layout_manager.validate_coordinate_bounds(1, 1))
        self.assertTrue(self.layout_manager.validate_coordinate_bounds(25, 20))
        self.assertTrue(self.layout_manager.validate_coordinate_bounds(13, 10))
        
        # Invalid bounds
        self.assertFalse(self.layout_manager.validate_coordinate_bounds(0, 1))
        self.assertFalse(self.layout_manager.validate_coordinate_bounds(26, 1))
        self.assertFalse(self.layout_manager.validate_coordinate_bounds(1, 0))
        self.assertFalse(self.layout_manager.validate_coordinate_bounds(1, 21))
    
    def test_grid_snapshot(self):
        """Test grid snapshot creation and loading."""
        # Create snapshot
        snapshot = self.layout_manager.get_grid_snapshot()
        
        # Verify snapshot structure
        self.assertIn('dimensions', snapshot)
        self.assertIn('grid_state', snapshot)
        self.assertIn('occupied_positions', snapshot)
        self.assertIn('statistics', snapshot)
        
        # Verify dimensions
        self.assertEqual(snapshot['dimensions']['max_aisle'], 25)
        self.assertEqual(snapshot['dimensions']['max_rack'], 20)
        
        # Verify packout location
        self.assertEqual(snapshot['packout_location'], {'aisle': 1, 'rack': 1})
        
        # Load snapshot
        self.assertTrue(self.layout_manager.load_grid_snapshot(snapshot))
        
        # Verify state is preserved
        new_stats = self.layout_manager.get_grid_statistics()
        self.assertEqual(new_stats['occupied_positions'], 1)  # Only packout
    
    def test_invalid_snapshot_loading(self):
        """Test loading invalid snapshots."""
        # Invalid snapshot structure
        invalid_snapshot = {'invalid': 'data'}
        self.assertFalse(self.layout_manager.load_grid_snapshot(invalid_snapshot))
    
    def test_grid_reset(self):
        """Test grid reset functionality."""
        # Modify grid state
        coord = Coordinate(5, 5)
        self.layout_manager.set_grid_state(coord, GridState.OCCUPIED)
        
        # Verify modification
        self.assertTrue(self.layout_manager.is_position_occupied(coord))
        
        # Reset grid
        self.layout_manager.reset_grid()
        
        # Verify reset
        self.assertFalse(self.layout_manager.is_position_occupied(coord))
        self.assertEqual(self.layout_manager.get_grid_state(coord), GridState.EMPTY)
    
    def test_grid_visualization(self):
        """Test grid visualization creation."""
        # Create visualization without robot
        viz = self.layout_manager.get_grid_visualization()
        
        # Verify visualization contains expected elements
        self.assertIn("Warehouse Grid (25x20)", viz)
        self.assertIn("Legend:", viz)
        self.assertIn("P=Packout", viz)
        self.assertIn("X=Occupied", viz)
        self.assertIn(".=Empty", viz)
        
        # Create visualization with robot
        robot_pos = Coordinate(5, 5)
        viz_with_robot = self.layout_manager.get_grid_visualization(robot_pos)
        
        # Verify robot position is highlighted
        self.assertIn("R=Robot", viz_with_robot)
    
    def test_string_representations(self):
        """Test string representations."""
        # String representation
        str_repr = str(self.layout_manager)
        self.assertIn("WarehouseLayoutManager(25x20)", str_repr)
        self.assertIn("Occupied:", str_repr)
        self.assertIn("Empty:", str_repr)
        
        # Detailed representation
        repr_str = repr(self.layout_manager)
        self.assertIn("WarehouseLayoutManager", repr_str)
        self.assertIn("dimensions=(25, 20)", repr_str)
    
    def test_multiple_state_changes(self):
        """Test multiple state changes and their effects."""
        coord1 = Coordinate(5, 5)
        coord2 = Coordinate(10, 10)
        
        # Set multiple positions to occupied
        self.layout_manager.set_grid_state(coord1, GridState.OCCUPIED)
        self.layout_manager.set_grid_state(coord2, GridState.OCCUPIED)
        
        # Verify both are occupied
        self.assertTrue(self.layout_manager.is_position_occupied(coord1))
        self.assertTrue(self.layout_manager.is_position_occupied(coord2))
        
        # Verify statistics
        stats = self.layout_manager.get_grid_statistics()
        self.assertEqual(stats['occupied_positions'], 3)  # packout + coord1 + coord2
        self.assertEqual(stats['empty_positions'], 497)  # 500 - 3 (packout + coord1 + coord2)
        
        # Set one back to empty
        self.layout_manager.set_grid_state(coord1, GridState.EMPTY)
        
        # Verify updated state
        self.assertFalse(self.layout_manager.is_position_occupied(coord1))
        self.assertTrue(self.layout_manager.is_position_occupied(coord2))
        
        # Verify updated statistics
        stats = self.layout_manager.get_grid_statistics()
        self.assertEqual(stats['occupied_positions'], 2)  # packout + coord2
        self.assertEqual(stats['empty_positions'], 498)  # 500 - 2 (packout + coord2)


if __name__ == '__main__':
    unittest.main() 