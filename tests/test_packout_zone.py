"""
Unit tests for the PackoutZoneManager class.

Tests packout zone functionality, special zone validation,
robot start/return logic, and distance calculations.
"""

import unittest
from core.layout.packout_zone import PackoutZoneManager, PackoutZoneType
from core.layout.warehouse_layout import WarehouseLayoutManager
from core.layout.coordinate import Coordinate


class TestPackoutZoneManager(unittest.TestCase):
    """Test cases for the PackoutZoneManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.warehouse_layout = WarehouseLayoutManager()
        self.warehouse_layout.reset_grid()
        self.packout_manager = PackoutZoneManager(self.warehouse_layout)
    
    def test_initialization(self):
        """Test packout zone manager initialization."""
        self.assertEqual(self.packout_manager.packout_location, Coordinate(1, 1))
        self.assertIsInstance(self.packout_manager.restricted_zones, list)
        self.assertIsInstance(self.packout_manager.transit_zones, list)
        self.assertEqual(self.packout_manager.warehouse_layout, self.warehouse_layout)
    
    def test_packout_location(self):
        """Test packout location functionality."""
        packout = self.packout_manager.get_packout_location()
        self.assertEqual(packout, Coordinate(1, 1))
        
        # Test packout location identification
        self.assertTrue(self.packout_manager.is_packout_location(Coordinate(1, 1)))
        self.assertFalse(self.packout_manager.is_packout_location(Coordinate(2, 2)))
    
    def test_restricted_zones(self):
        """Test restricted zone functionality."""
        # Test restricted zone identification
        self.assertTrue(self.packout_manager.is_restricted_zone(Coordinate(1, 2)))
        self.assertTrue(self.packout_manager.is_restricted_zone(Coordinate(2, 1)))
        self.assertTrue(self.packout_manager.is_restricted_zone(Coordinate(2, 2)))
        
        # Test non-restricted zones
        self.assertFalse(self.packout_manager.is_restricted_zone(Coordinate(3, 3)))
        self.assertFalse(self.packout_manager.is_restricted_zone(Coordinate(1, 1)))  # Packout is not restricted
    
    def test_zone_type_detection(self):
        """Test zone type detection."""
        # Packout zone
        self.assertEqual(self.packout_manager.get_zone_type(Coordinate(1, 1)), PackoutZoneType.PACKOUT)
        
        # Restricted zones
        self.assertEqual(self.packout_manager.get_zone_type(Coordinate(1, 2)), PackoutZoneType.RESTRICTED)
        self.assertEqual(self.packout_manager.get_zone_type(Coordinate(2, 1)), PackoutZoneType.RESTRICTED)
        
        # Transit zones (regular positions)
        self.assertEqual(self.packout_manager.get_zone_type(Coordinate(3, 3)), PackoutZoneType.TRANSIT)
    
    def test_item_pickup_validation(self):
        """Test item pickup validation."""
        # Cannot pickup at packout location
        self.assertFalse(self.packout_manager.can_pickup_item_at(Coordinate(1, 1)))
        
        # Cannot pickup at restricted zones
        self.assertFalse(self.packout_manager.can_pickup_item_at(Coordinate(1, 2)))
        self.assertFalse(self.packout_manager.can_pickup_item_at(Coordinate(2, 1)))
        
        # Can pickup at regular positions
        self.assertTrue(self.packout_manager.can_pickup_item_at(Coordinate(3, 3)))
        self.assertTrue(self.packout_manager.can_pickup_item_at(Coordinate(25, 20)))
    
    def test_item_placement_validation(self):
        """Test item placement validation."""
        # Can only place at packout location
        self.assertTrue(self.packout_manager.can_place_item_at(Coordinate(1, 1)))
        
        # Cannot place at other locations
        self.assertFalse(self.packout_manager.can_place_item_at(Coordinate(2, 2)))
        self.assertFalse(self.packout_manager.can_place_item_at(Coordinate(25, 20)))
    
    def test_distance_calculations(self):
        """Test distance calculations from packout."""
        # Distance to packout itself
        self.assertEqual(self.packout_manager.get_distance_from_packout(Coordinate(1, 1)), 0)
        
        # Distance to nearby positions
        self.assertEqual(self.packout_manager.get_distance_from_packout(Coordinate(2, 1)), 1)
        self.assertEqual(self.packout_manager.get_distance_from_packout(Coordinate(1, 2)), 1)
        self.assertEqual(self.packout_manager.get_distance_from_packout(Coordinate(2, 2)), 2)
        
        # Distance to far positions
        self.assertEqual(self.packout_manager.get_distance_from_packout(Coordinate(25, 20)), 43)  # 24 + 19
    
    def test_euclidean_distance_calculations(self):
        """Test Euclidean distance calculations from packout."""
        # Distance to packout itself
        self.assertEqual(self.packout_manager.get_euclidean_distance_from_packout(Coordinate(1, 1)), 0.0)
        
        # Distance to nearby positions
        self.assertEqual(self.packout_manager.get_euclidean_distance_from_packout(Coordinate(2, 1)), 1.0)
        self.assertEqual(self.packout_manager.get_euclidean_distance_from_packout(Coordinate(1, 2)), 1.0)
        self.assertAlmostEqual(self.packout_manager.get_euclidean_distance_from_packout(Coordinate(2, 2)), 1.4142135623730951)
    
    def test_robot_position_validation(self):
        """Test robot position validation."""
        # Valid robot positions
        self.assertTrue(self.packout_manager.is_valid_robot_position(Coordinate(1, 1)))
        self.assertTrue(self.packout_manager.is_valid_robot_position(Coordinate(25, 20)))
        self.assertTrue(self.packout_manager.is_valid_robot_position(Coordinate(13, 10)))
        
        # Invalid robot positions - create invalid coordinates by directly setting attributes
        class InvalidCoordinate:
            def __init__(self, aisle, rack):
                self.aisle = aisle
                self.rack = rack
        
        self.assertFalse(self.packout_manager.is_valid_robot_position(InvalidCoordinate(0, 1)))
        self.assertFalse(self.packout_manager.is_valid_robot_position(InvalidCoordinate(26, 1)))
        self.assertFalse(self.packout_manager.is_valid_robot_position(InvalidCoordinate(1, 0)))
        self.assertFalse(self.packout_manager.is_valid_robot_position(InvalidCoordinate(1, 21)))
    
    def test_robot_start_return_positions(self):
        """Test robot start and return positions."""
        start_pos = self.packout_manager.get_robot_start_position()
        return_pos = self.packout_manager.get_robot_return_position()
        
        self.assertEqual(start_pos, Coordinate(1, 1))
        self.assertEqual(return_pos, Coordinate(1, 1))
        self.assertEqual(start_pos, return_pos)
    
    def test_packout_zone_statistics(self):
        """Test packout zone statistics."""
        stats = self.packout_manager.get_packout_zone_statistics()
        
        # Verify required fields
        self.assertIn('packout_location', stats)
        self.assertIn('restricted_zones_count', stats)
        self.assertIn('transit_zones_count', stats)
        self.assertIn('total_positions', stats)
        self.assertIn('available_pickup_positions', stats)
        self.assertIn('available_placement_positions', stats)
        self.assertIn('restricted_zone_positions', stats)
        
        # Verify values
        self.assertEqual(stats['packout_location'], {'aisle': 1, 'rack': 1})
        self.assertEqual(stats['restricted_zones_count'], 3)
        self.assertEqual(stats['total_positions'], 500)  # 25 * 20
        self.assertEqual(stats['available_placement_positions'], 1)  # Only packout
        self.assertEqual(len(stats['restricted_zone_positions']), 3)
    
    def test_packout_zone_visualization(self):
        """Test packout zone visualization."""
        # Visualization without robot
        viz = self.packout_manager.get_packout_zone_visualization()
        
        self.assertIn("Packout Zone Visualization", viz)
        self.assertIn("Packout Location: (1, 1)", viz)
        self.assertIn("Restricted Zones: 3", viz)
        
        # Visualization with robot
        robot_pos = Coordinate(5, 5)
        viz_with_robot = self.packout_manager.get_packout_zone_visualization(robot_pos)
        
        self.assertIn("Robot Position: (5, 5)", viz_with_robot)
        self.assertIn("Distance from Packout: 8", viz_with_robot)
    
    def test_order_pickup_validation(self):
        """Test order pickup location validation."""
        # Valid pickup locations
        valid_locations = [Coordinate(3, 3), Coordinate(5, 5), Coordinate(10, 10)]
        is_valid, errors = self.packout_manager.validate_order_pickup_locations(valid_locations)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid pickup locations
        invalid_locations = [Coordinate(1, 1), Coordinate(3, 3)]  # Packout + valid
        is_valid, errors = self.packout_manager.validate_order_pickup_locations(invalid_locations)
        
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Cannot pickup item at (1, 1)", errors[0])
    
    def test_order_placement_validation(self):
        """Test order placement location validation."""
        # Valid placement locations (only packout)
        valid_locations = [Coordinate(1, 1)]
        is_valid, errors = self.packout_manager.validate_order_placement_locations(valid_locations)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid placement locations
        invalid_locations = [Coordinate(1, 1), Coordinate(2, 2)]  # Packout + invalid
        is_valid, errors = self.packout_manager.validate_order_placement_locations(invalid_locations)
        
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Cannot place item at (2, 2)", errors[0])
    
    def test_optimal_pickup_route(self):
        """Test optimal pickup route generation."""
        pickup_locations = [Coordinate(3, 3), Coordinate(5, 5)]
        
        route = self.packout_manager.get_optimal_pickup_route(Coordinate(1, 1), pickup_locations)
        
        # Verify route structure
        self.assertEqual(route[0], Coordinate(1, 1))  # Start at packout
        self.assertIn(Coordinate(3, 3), route)
        self.assertIn(Coordinate(5, 5), route)
        
        # Verify route includes intermediate points
        self.assertIn(Coordinate(2, 1), route)
        self.assertIn(Coordinate(3, 1), route)
        self.assertIn(Coordinate(3, 2), route)
    
    def test_optimal_pickup_route_empty(self):
        """Test optimal pickup route with empty locations."""
        route = self.packout_manager.get_optimal_pickup_route(Coordinate(1, 1), [])
        
        self.assertEqual(len(route), 1)
        self.assertEqual(route[0], Coordinate(1, 1))
    
    def test_optimal_pickup_route_invalid_locations(self):
        """Test optimal pickup route with invalid locations."""
        invalid_locations = [Coordinate(1, 1)]  # Packout location
        
        with self.assertRaises(ValueError):
            self.packout_manager.get_optimal_pickup_route(Coordinate(1, 1), invalid_locations)
    
    def test_return_route(self):
        """Test return route generation."""
        current = Coordinate(5, 5)
        route = self.packout_manager.get_return_route(current)
        
        # Verify route structure
        self.assertEqual(route[0], current)
        self.assertEqual(route[-1], Coordinate(1, 1))  # End at packout
        
        # Verify route includes intermediate points
        self.assertIn(Coordinate(4, 5), route)
        self.assertIn(Coordinate(3, 5), route)
        self.assertIn(Coordinate(2, 5), route)
        self.assertIn(Coordinate(1, 5), route)
        self.assertIn(Coordinate(1, 4), route)
        self.assertIn(Coordinate(1, 3), route)
        self.assertIn(Coordinate(1, 2), route)
    
    def test_return_route_from_packout(self):
        """Test return route when already at packout."""
        route = self.packout_manager.get_return_route(Coordinate(1, 1))
        
        self.assertEqual(len(route), 1)
        self.assertEqual(route[0], Coordinate(1, 1))
    
    def test_total_pickup_distance(self):
        """Test total pickup distance calculation."""
        pickup_locations = [Coordinate(3, 3), Coordinate(5, 5)]
        
        distance = self.packout_manager.calculate_total_pickup_distance(pickup_locations)
        
        # Should be greater than 0
        self.assertGreater(distance, 0)
        
        # Should be at least the sum of distances to each location
        min_distance = (Coordinate(1, 1).distance_to(Coordinate(3, 3)) + 
                       Coordinate(3, 3).distance_to(Coordinate(5, 5)))
        self.assertGreaterEqual(distance, min_distance)
    
    def test_total_pickup_distance_empty(self):
        """Test total pickup distance with empty locations."""
        distance = self.packout_manager.calculate_total_pickup_distance([])
        
        self.assertEqual(distance, 0.0)
    
    def test_total_return_distance(self):
        """Test total return distance calculation."""
        current = Coordinate(5, 5)
        distance = self.packout_manager.calculate_total_return_distance(current)
        
        expected = Coordinate(1, 1).distance_to(current)
        self.assertEqual(distance, expected)
    
    def test_string_representations(self):
        """Test string representations."""
        # String representation
        str_repr = str(self.packout_manager)
        self.assertIn("PackoutZoneManager", str_repr)
        self.assertIn("Packout: (1, 1)", str_repr)
        self.assertIn("Restricted: 3", str_repr)
        
        # Detailed representation
        repr_str = repr(self.packout_manager)
        self.assertIn("PackoutZoneManager", repr_str)
        self.assertIn("packout_location=(1, 1)", repr_str)
        self.assertIn("restricted_zones=3", repr_str)
    
    def test_complex_scenario(self):
        """Test complex packout zone scenario."""
        # Simulate robot movement and order fulfillment
        robot_start = self.packout_manager.get_robot_start_position()
        self.assertEqual(robot_start, Coordinate(1, 1))
        
        # Pickup locations for an order
        pickup_locations = [Coordinate(3, 3), Coordinate(7, 5), Coordinate(12, 8)]
        
        # Validate pickup locations
        is_valid, errors = self.packout_manager.validate_order_pickup_locations(pickup_locations)
        self.assertTrue(is_valid)
        
        # Calculate pickup route
        pickup_route = self.packout_manager.get_optimal_pickup_route(robot_start, pickup_locations)
        pickup_distance = self.packout_manager.calculate_total_pickup_distance(pickup_locations)
        
        # Verify route properties
        self.assertGreater(len(pickup_route), 1)
        self.assertGreater(pickup_distance, 0)
        
        # Simulate robot at last pickup location
        last_pickup = pickup_locations[-1]
        return_route = self.packout_manager.get_return_route(last_pickup)
        return_distance = self.packout_manager.calculate_total_return_distance(last_pickup)
        
        # Verify return route
        self.assertEqual(return_route[0], last_pickup)
        self.assertEqual(return_route[-1], Coordinate(1, 1))
        self.assertEqual(return_distance, last_pickup.distance_to(Coordinate(1, 1)))


if __name__ == '__main__':
    unittest.main() 