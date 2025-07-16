"""
Unit tests for the Coordinate class and coordinate system.

Tests coordinate validation, distance calculations, and coordinate conversions.
"""

import unittest
from core.layout.coordinate import (
    Coordinate, CoordinateError, create_coordinate, 
    validate_coordinate_tuple, get_warehouse_bounds,
    is_valid_aisle, is_valid_rack
)


class TestCoordinate(unittest.TestCase):
    """Test cases for the Coordinate class."""
    
    def test_valid_coordinate_creation(self):
        """Test creating valid coordinates."""
        # Test basic coordinate creation
        coord = Coordinate(1, 1)
        self.assertEqual(coord.aisle, 1)
        self.assertEqual(coord.rack, 1)
        
        # Test boundary coordinates
        coord = Coordinate(25, 20)
        self.assertEqual(coord.aisle, 25)
        self.assertEqual(coord.rack, 20)
        
        # Test middle coordinates
        coord = Coordinate(13, 10)
        self.assertEqual(coord.aisle, 13)
        self.assertEqual(coord.rack, 10)
    
    def test_invalid_coordinate_creation(self):
        """Test that invalid coordinates raise CoordinateError."""
        # Test out of bounds aisle
        with self.assertRaises(CoordinateError):
            Coordinate(0, 1)
        
        with self.assertRaises(CoordinateError):
            Coordinate(26, 1)
        
        # Test out of bounds rack
        with self.assertRaises(CoordinateError):
            Coordinate(1, 0)
        
        with self.assertRaises(CoordinateError):
            Coordinate(1, 21)
        
        # Test both out of bounds
        with self.assertRaises(CoordinateError):
            Coordinate(0, 0)
        
        with self.assertRaises(CoordinateError):
            Coordinate(26, 21)
    
    def test_from_tuple(self):
        """Test creating coordinates from tuples."""
        # Valid tuple
        coord = Coordinate.from_tuple((5, 10))
        self.assertEqual(coord.aisle, 5)
        self.assertEqual(coord.rack, 10)
        
        # Invalid tuple length
        with self.assertRaises(CoordinateError):
            Coordinate.from_tuple((5,))
        
        with self.assertRaises(CoordinateError):
            Coordinate.from_tuple((5, 10, 15))
    
    def test_from_dict(self):
        """Test creating coordinates from dictionaries."""
        # Valid dictionary
        coord = Coordinate.from_dict({'aisle': 5, 'rack': 10})
        self.assertEqual(coord.aisle, 5)
        self.assertEqual(coord.rack, 10)
        
        # Missing keys
        with self.assertRaises(CoordinateError):
            Coordinate.from_dict({'aisle': 5})
        
        with self.assertRaises(CoordinateError):
            Coordinate.from_dict({'rack': 10})
    
    def test_to_tuple(self):
        """Test converting coordinate to tuple."""
        coord = Coordinate(5, 10)
        coord_tuple = coord.to_tuple()
        self.assertEqual(coord_tuple, (5, 10))
        self.assertIsInstance(coord_tuple, tuple)
    
    def test_to_dict(self):
        """Test converting coordinate to dictionary."""
        coord = Coordinate(5, 10)
        coord_dict = coord.to_dict()
        self.assertEqual(coord_dict, {'aisle': 5, 'rack': 10})
        self.assertIsInstance(coord_dict, dict)
    
    def test_distance_calculations(self):
        """Test distance calculation methods."""
        coord1 = Coordinate(1, 1)
        coord2 = Coordinate(5, 5)
        coord3 = Coordinate(1, 5)
        
        # Manhattan distance
        self.assertEqual(coord1.distance_to(coord2), 8)  # 4 + 4
        self.assertEqual(coord1.distance_to(coord3), 4)  # 0 + 4
        self.assertEqual(coord1.distance_to(coord1), 0)  # Same coordinate
        
        # Euclidean distance
        self.assertAlmostEqual(coord1.euclidean_distance_to(coord2), 5.656854249492381)
        self.assertEqual(coord1.euclidean_distance_to(coord3), 4.0)
        self.assertEqual(coord1.euclidean_distance_to(coord1), 0.0)
    
    def test_adjacency_checking(self):
        """Test adjacency checking."""
        coord1 = Coordinate(5, 5)
        
        # Adjacent coordinates
        self.assertTrue(coord1.is_adjacent(Coordinate(5, 6)))
        self.assertTrue(coord1.is_adjacent(Coordinate(5, 4)))
        self.assertTrue(coord1.is_adjacent(Coordinate(6, 5)))
        self.assertTrue(coord1.is_adjacent(Coordinate(4, 5)))
        
        # Non-adjacent coordinates
        self.assertFalse(coord1.is_adjacent(Coordinate(5, 7)))
        self.assertFalse(coord1.is_adjacent(Coordinate(7, 5)))
        self.assertFalse(coord1.is_adjacent(Coordinate(6, 6)))
        self.assertFalse(coord1.is_adjacent(coord1))  # Same coordinate
    
    def test_same_aisle_rack_checking(self):
        """Test same aisle and rack checking."""
        coord1 = Coordinate(5, 10)
        coord2 = Coordinate(5, 15)
        coord3 = Coordinate(10, 10)
        
        # Same aisle
        self.assertTrue(coord1.is_same_aisle(coord2))
        self.assertFalse(coord1.is_same_aisle(coord3))
        
        # Same rack
        self.assertTrue(coord1.is_same_rack(coord3))
        self.assertFalse(coord1.is_same_rack(coord2))
    
    def test_packout_location(self):
        """Test packout location identification."""
        packout = Coordinate(1, 1)
        other = Coordinate(1, 2)
        
        self.assertTrue(packout.is_packout_location())
        self.assertFalse(other.is_packout_location())
    
    def test_boundary_checking(self):
        """Test boundary and corner checking."""
        # Boundary coordinates
        self.assertTrue(Coordinate(1, 10).is_boundary())
        self.assertTrue(Coordinate(25, 10).is_boundary())
        self.assertTrue(Coordinate(10, 1).is_boundary())
        self.assertTrue(Coordinate(10, 20).is_boundary())
        
        # Non-boundary coordinates
        self.assertFalse(Coordinate(10, 10).is_boundary())
        
        # Corner coordinates
        self.assertTrue(Coordinate(1, 1).is_corner())
        self.assertTrue(Coordinate(1, 20).is_corner())
        self.assertTrue(Coordinate(25, 1).is_corner())
        self.assertTrue(Coordinate(25, 20).is_corner())
        
        # Non-corner coordinates
        self.assertFalse(Coordinate(10, 10).is_corner())
        self.assertFalse(Coordinate(1, 10).is_corner())
    
    def test_string_representations(self):
        """Test string representations."""
        coord = Coordinate(5, 10)
        
        # String representation
        self.assertEqual(str(coord), "(5, 10)")
        
        # Detailed representation
        self.assertEqual(repr(coord), "Coordinate(aisle=5, rack=10)")
    
    def test_equality_and_hashing(self):
        """Test equality comparison and hashing."""
        coord1 = Coordinate(5, 10)
        coord2 = Coordinate(5, 10)
        coord3 = Coordinate(5, 11)
        
        # Equality
        self.assertEqual(coord1, coord2)
        self.assertNotEqual(coord1, coord3)
        self.assertNotEqual(coord1, "not a coordinate")
        
        # Hashing
        coord_set = {coord1, coord2, coord3}
        self.assertEqual(len(coord_set), 2)  # coord1 and coord2 are equal
    
    def test_factory_function(self):
        """Test the create_coordinate factory function."""
        coord = create_coordinate(5, 10)
        self.assertEqual(coord.aisle, 5)
        self.assertEqual(coord.rack, 10)
        
        # Should raise error for invalid coordinates
        with self.assertRaises(CoordinateError):
            create_coordinate(0, 10)
    
    def test_validation_functions(self):
        """Test validation utility functions."""
        # Valid coordinates
        self.assertTrue(validate_coordinate_tuple((5, 10)))
        self.assertTrue(validate_coordinate_tuple((1, 1)))
        self.assertTrue(validate_coordinate_tuple((25, 20)))
        
        # Invalid coordinates
        self.assertFalse(validate_coordinate_tuple((0, 10)))
        self.assertFalse(validate_coordinate_tuple((26, 10)))
        self.assertFalse(validate_coordinate_tuple((5, 0)))
        self.assertFalse(validate_coordinate_tuple((5, 21)))
        
        # Invalid tuple length
        self.assertFalse(validate_coordinate_tuple((5,)))
        self.assertFalse(validate_coordinate_tuple((5, 10, 15)))
    
    def test_warehouse_bounds(self):
        """Test warehouse bounds function."""
        max_aisle, max_rack = get_warehouse_bounds()
        self.assertEqual(max_aisle, 25)
        self.assertEqual(max_rack, 20)
    
    def test_validation_utility_functions(self):
        """Test aisle and rack validation functions."""
        # Valid aisles
        self.assertTrue(is_valid_aisle(1))
        self.assertTrue(is_valid_aisle(13))
        self.assertTrue(is_valid_aisle(25))
        
        # Invalid aisles
        self.assertFalse(is_valid_aisle(0))
        self.assertFalse(is_valid_aisle(26))
        
        # Valid racks
        self.assertTrue(is_valid_rack(1))
        self.assertTrue(is_valid_rack(10))
        self.assertTrue(is_valid_rack(20))
        
        # Invalid racks
        self.assertFalse(is_valid_rack(0))
        self.assertFalse(is_valid_rack(21))


if __name__ == '__main__':
    unittest.main() 