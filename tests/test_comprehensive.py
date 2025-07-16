"""
Comprehensive testing suite for warehouse layout system.

This module provides comprehensive tests for all warehouse layout components
including boundary conditions, error handling, performance testing, and
integration scenarios.
"""

import unittest
import time
import random
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from core.layout.coordinate import Coordinate, CoordinateError
from core.layout.warehouse_layout import WarehouseLayoutManager, GridState
from core.layout.snake_pattern import SnakePattern, Direction
from core.layout.packout_zone import PackoutZoneManager
from core.layout.distance_tracker import DistanceTracker, DistanceEventType
from core.layout.grid_visualizer import GridVisualizer, GridCellType
from core.layout.integration import LayoutIntegrationManager, LayoutEvent


class TestComprehensiveCoordinateSystem(unittest.TestCase):
    """Comprehensive tests for coordinate system."""
    
    def test_coordinate_bounds_validation_edge_cases(self):
        """Test coordinate bounds validation with edge cases."""
        # Test valid edge cases
        edge_coords = [
            Coordinate(1, 1),    # Minimum valid
            Coordinate(25, 20),  # Maximum valid
            Coordinate(1, 20),   # Min aisle, max rack
            Coordinate(25, 1),   # Max aisle, min rack
            Coordinate(13, 10),  # Middle coordinates
        ]
        
        for coord in edge_coords:
            with self.subTest(coord=coord):
                self.assertTrue(coord.is_valid())
        
        # Test invalid edge cases
        invalid_coords = [
            (0, 1),    # Zero aisle
            (1, 0),    # Zero rack
            (26, 1),   # Aisle too high
            (1, 21),   # Rack too high
            (-1, 1),   # Negative aisle
            (1, -1),   # Negative rack
            (30, 30),  # Both too high
        ]
        
        for aisle, rack in invalid_coords:
            with self.subTest(aisle=aisle, rack=rack):
                with self.assertRaises(CoordinateError):
                    Coordinate(aisle, rack)
    
    def test_coordinate_operations_edge_cases(self):
        """Test coordinate operations with edge cases."""
        # Test distance calculations
        coord1 = Coordinate(1, 1)
        coord2 = Coordinate(25, 20)
        
        # Manhattan distance should be 43 (24 + 19)
        self.assertEqual(coord1.distance_to(coord2), 43)
        self.assertEqual(coord2.distance_to(coord1), 43)
        
        # Test same coordinate distance
        self.assertEqual(coord1.distance_to(coord1), 0)
        
        # Test packout location detection
        packout = Coordinate(1, 1)
        self.assertTrue(packout.is_packout_location())
        
        non_packout = Coordinate(2, 2)
        self.assertFalse(non_packout.is_packout_location())
    
    def test_coordinate_serialization_edge_cases(self):
        """Test coordinate serialization with edge cases."""
        # Test to_dict
        coord = Coordinate(13, 7)
        coord_dict = coord.to_dict()
        self.assertEqual(coord_dict['aisle'], 13)
        self.assertEqual(coord_dict['rack'], 7)
        
        # Test from_dict
        new_coord = Coordinate.from_dict(coord_dict)
        self.assertEqual(new_coord, coord)
        
        # Test string representation
        coord_str = str(coord)
        self.assertIn("13", coord_str)
        self.assertIn("7", coord_str)


class TestComprehensiveSnakePattern(unittest.TestCase):
    """Comprehensive tests for snake pattern navigation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.snake = SnakePattern()
    
    def test_snake_pattern_edge_cases(self):
        """Test snake pattern with edge cases."""
        # Test same start and target
        coord = Coordinate(10, 10)
        path = self.snake.get_path_to_target(coord, coord)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], coord)
        
        # Test packout to packout
        packout = Coordinate(1, 1)
        path = self.snake.get_path_to_target(packout, packout)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], packout)
        
        # Test corner to corner
        corner1 = Coordinate(1, 1)
        corner2 = Coordinate(25, 20)
        path = self.snake.get_path_to_target(corner1, corner2)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], corner1)
        self.assertEqual(path[-1], corner2)
    
    def test_snake_pattern_direction_optimization(self):
        """Test snake pattern direction optimization."""
        # Test forward direction optimization
        start = Coordinate(1, 1)
        target = Coordinate(5, 5)
        
        forward_path = self.snake.get_path_to_target(start, target)
        forward_distance = len(forward_path) - 1
        
        # Test reverse direction
        reverse_path = self.snake.get_path_to_target(target, start)
        reverse_distance = len(reverse_path) - 1
        
        # Both should be optimal for their respective directions
        self.assertGreater(forward_distance, 0)
        self.assertGreater(reverse_distance, 0)
    
    def test_snake_pattern_complex_scenarios(self):
        """Test snake pattern with complex scenarios."""
        # Test zigzag pattern
        path = self.snake.get_path_to_target(Coordinate(1, 1), Coordinate(25, 20))
        
        # Verify path properties
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], Coordinate(1, 1))
        self.assertEqual(path[-1], Coordinate(25, 20))
        
        # Verify no duplicate coordinates
        path_set = set(path)
        self.assertEqual(len(path), len(path_set))
        
        # Verify consecutive coordinates are adjacent
        for i in range(len(path) - 1):
            curr = path[i]
            next_coord = path[i + 1]
            distance = abs(curr.aisle - next_coord.aisle) + abs(curr.rack - next_coord.rack)
            self.assertEqual(distance, 1)
    
    def test_snake_pattern_performance(self):
        """Test snake pattern performance with large coordinate sets."""
        # Generate random coordinate pairs
        random.seed(42)  # For reproducible tests
        test_cases = []
        
        for _ in range(100):
            start = Coordinate(random.randint(1, 25), random.randint(1, 20))
            target = Coordinate(random.randint(1, 25), random.randint(1, 20))
            test_cases.append((start, target))
        
        # Measure performance
        start_time = time.time()
        
        for start, target in test_cases:
            path = self.snake.get_path_to_target(start, target)
            # Verify path is valid
            self.assertGreaterEqual(len(path), 1)
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], target)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(execution_time, 5.0)  # 5 seconds max
        
        print(f"Snake pattern performance test: {len(test_cases)} paths in {execution_time:.3f}s")


class TestComprehensivePackoutZone(unittest.TestCase):
    """Comprehensive tests for packout zone management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.layout_manager = WarehouseLayoutManager()
        self.packout_manager = PackoutZoneManager(self.layout_manager)
    
    def test_packout_location_special_handling(self):
        """Test packout location special handling."""
        packout = self.packout_manager.packout_location
        
        # Test packout location is correct
        self.assertEqual(packout, Coordinate(1, 1))
        
        # Test packout zone identification
        self.assertTrue(self.packout_manager.is_packout_location(packout))
        self.assertFalse(self.packout_manager.is_packout_location(Coordinate(2, 2)))
        
        # Test packout zone restrictions
        self.assertTrue(self.packout_manager.is_restricted_zone(packout))
        
        # Test distance to packout
        test_coord = Coordinate(10, 10)
        distance = self.packout_manager.calculate_distance_to_packout(test_coord)
        self.assertGreater(distance, 0)
    
    def test_packout_zone_route_optimization(self):
        """Test packout zone route optimization."""
        # Test routes from various locations to packout
        test_locations = [
            Coordinate(25, 20),  # Far corner
            Coordinate(13, 10),  # Middle
            Coordinate(1, 20),   # Same aisle
            Coordinate(25, 1),   # Same rack
        ]
        
        for location in test_locations:
            with self.subTest(location=location):
                # Test optimal route calculation
                route = self.packout_manager.calculate_optimal_route_to_packout(location)
                
                # Verify route properties
                self.assertGreater(len(route), 0)
                self.assertEqual(route[0], location)
                self.assertEqual(route[-1], self.packout_manager.packout_location)
                
                # Verify route distance
                route_distance = len(route) - 1
                expected_distance = location.distance_to(self.packout_manager.packout_location)
                self.assertGreaterEqual(route_distance, expected_distance)
    
    def test_packout_zone_validation_edge_cases(self):
        """Test packout zone validation with edge cases."""
        # Test valid coordinates
        valid_coords = [
            Coordinate(1, 1),    # Packout itself
            Coordinate(2, 2),    # Near packout
            Coordinate(25, 20),  # Far corner
        ]
        
        for coord in valid_coords:
            with self.subTest(coord=coord):
                self.assertTrue(self.packout_manager.is_valid_coordinate(coord))
        
        # Test invalid coordinates (these will raise CoordinateError)
        invalid_coords = [
            (0, 1),    # Invalid aisle
            (1, 0),    # Invalid rack
            (26, 1),   # Aisle too high
            (1, 21),   # Rack too high
        ]
        
        for aisle, rack in invalid_coords:
            with self.subTest(aisle=aisle, rack=rack):
                with self.assertRaises(CoordinateError):
                    Coordinate(aisle, rack)


class TestComprehensiveDistanceTracking(unittest.TestCase):
    """Comprehensive tests for distance tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = DistanceTracker()
    
    def test_distance_calculation_accuracy(self):
        """Test distance calculation accuracy."""
        # Test Manhattan distance calculations
        test_cases = [
            (Coordinate(1, 1), Coordinate(5, 5), 8),    # 4 + 4
            (Coordinate(1, 1), Coordinate(1, 10), 9),   # 0 + 9
            (Coordinate(1, 1), Coordinate(10, 1), 9),   # 9 + 0
            (Coordinate(1, 1), Coordinate(1, 1), 0),    # Same coordinate
        ]
        
        for start, target, expected in test_cases:
            with self.subTest(start=start, target=target):
                distance = self.tracker.calculate_distance(start, target)
                self.assertEqual(distance, expected)
    
    def test_distance_tracking_complex_scenarios(self):
        """Test distance tracking with complex scenarios."""
        # Simulate complete order workflow
        order_id = "order_001"
        robot_id = "robot_001"
        start_coord = Coordinate(5, 5)  # Different from packout location
        item_coord = Coordinate(10, 10)
        
        # Start order
        self.tracker.track_order_start(order_id, robot_id, start_coord)
        
        # Move to item (this includes the robot move)
        pickup_distance = self.tracker.track_pickup_item(
            order_id, robot_id, start_coord, item_coord
        )
        
        # Deliver to packout (this includes the robot move)
        delivery_distance = self.tracker.track_deliver_to_packout(
            order_id, robot_id, item_coord
        )
        
        # Return to start (this is a separate robot move)
        # Robot is currently at packout location after delivery
        packout_pos = self.tracker.get_current_position(robot_id)
        
        # If robot is already at start position, no return distance needed
        if packout_pos == start_coord:
            return_distance = 0.0
        else:
            return_distance = self.tracker.track_return_to_start(
                robot_id, packout_pos, start_coord
            )
        
        # Complete order
        total_order_distance = self.tracker.track_order_complete(
            order_id, robot_id, start_coord
        )
        
        # Verify distances
        self.assertGreater(pickup_distance, 0)
        self.assertGreater(delivery_distance, 0)
        self.assertGreater(return_distance, 0)
        
        # Verify order distance
        expected_order_distance = pickup_distance + delivery_distance
        self.assertEqual(self.tracker.get_order_distance(order_id), expected_order_distance)
        
        # Verify robot distance
        expected_robot_distance = pickup_distance + delivery_distance + return_distance
        self.assertEqual(self.tracker.get_robot_distance(robot_id), expected_robot_distance)
    
    def test_distance_tracking_performance(self):
        """Test distance tracking performance with large datasets."""
        # Generate large number of events
        num_events = 1000
        start_time = time.time()
        
        for i in range(num_events):
            order_id = f"order_{i:03d}"
            robot_id = f"robot_{i % 5:03d}"
            start_coord = Coordinate(random.randint(1, 25), random.randint(1, 20))
            target_coord = Coordinate(random.randint(1, 25), random.randint(1, 20))
            
            self.tracker.track_order_start(order_id, robot_id, start_coord)
            self.tracker.track_pickup_item(order_id, robot_id, start_coord, target_coord)
            self.tracker.track_order_complete(order_id, robot_id, target_coord)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 10.0)  # 10 seconds max
        
        # Verify data integrity
        self.assertEqual(len(self.tracker.order_distances), num_events)
        self.assertEqual(len(self.tracker.robot_distances), 5)  # 5 robots
        
        print(f"Distance tracking performance test: {num_events} events in {execution_time:.3f}s")


class TestComprehensiveGridVisualization(unittest.TestCase):
    """Comprehensive tests for grid visualization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = GridVisualizer()
    
    def test_grid_visualization_edge_cases(self):
        """Test grid visualization with edge cases."""
        # Test empty grid
        rendered = self.visualizer.render_grid()
        self.assertIn("WAREHOUSE GRID VISUALIZATION", rendered)
        self.assertIn("GRID STATISTICS", rendered)
        
        # Test grid with all robot positions
        for i in range(5):
            robot_id = f"robot_{i:03d}"
            coord = Coordinate(i + 1, i + 1)
            self.visualizer.set_robot_position(robot_id, coord)
        
        rendered = self.visualizer.render_grid()
        self.assertIn("ROBOT POSITIONS", rendered)
        
        # Test grid with path
        path = [Coordinate(1, 1), Coordinate(5, 5), Coordinate(10, 10)]
        self.visualizer.set_path(path)
        rendered = self.visualizer.render_grid()
        self.assertIn("Path", rendered)
    
    def test_grid_visualization_cell_priority(self):
        """Test grid visualization cell priority order."""
        coord = Coordinate(5, 5)
        
        # Test priority: robot > target > start > path > highlight > packout > occupied > empty
        
        # Robot should have highest priority
        self.visualizer.set_robot_position("robot_001", coord)
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.ROBOT)
        
        # Clear robot and test target
        self.visualizer.remove_robot_position("robot_001")
        self.visualizer.set_target_cell(coord)
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.TARGET)
        
        # Clear target and test start
        self.visualizer.clear_start_target()
        self.visualizer.set_start_cell(coord)
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.START)
        
        # Clear start and test path
        self.visualizer.clear_start_target()
        self.visualizer.set_path([coord])
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.PATH)
        
        # Clear path and test highlight
        self.visualizer.clear_path()
        self.visualizer.highlight_cell(coord)
        cell_type = self.visualizer.get_cell_type(coord)
        self.assertEqual(cell_type, GridCellType.HIGHLIGHT)
        
        # Clear highlight and test packout
        self.visualizer.clear_highlights()
        packout_coord = Coordinate(1, 1)
        cell_type = self.visualizer.get_cell_type(packout_coord)
        self.assertEqual(cell_type, GridCellType.PACKOUT)
    
    def test_grid_visualization_performance(self):
        """Test grid visualization performance."""
        # Test rendering performance with complex state
        start_time = time.time()
        
        # Add many elements
        for i in range(10):
            robot_id = f"robot_{i:03d}"
            coord = Coordinate(i + 1, i + 1)
            self.visualizer.set_robot_position(robot_id, coord)
        
        # Add path
        path = [Coordinate(i, i) for i in range(1, 21)]
        self.visualizer.set_path(path)
        
        # Add highlights
        for i in range(5):
            coord = Coordinate(i + 10, i + 10)
            self.visualizer.highlight_cell(coord)
        
        # Render grid
        rendered = self.visualizer.render_grid()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 2.0)  # 2 seconds max
        
        # Verify content
        self.assertIn("WAREHOUSE GRID VISUALIZATION", rendered)
        self.assertIn("ROBOT POSITIONS", rendered)
        
        print(f"Grid visualization performance test: complex state in {execution_time:.3f}s")


class TestComprehensiveIntegration(unittest.TestCase):
    """Comprehensive tests for system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = LayoutIntegrationManager()
    
    def test_integration_boundary_conditions(self):
        """Test integration with boundary conditions."""
        # Test with None external systems
        result = self.integration.initialize_integration()
        self.assertTrue(result)
        
        # Test with mock systems
        mock_sim_engine = Mock()
        mock_event_system = Mock()
        mock_config_manager = Mock()
        
        result = self.integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        
        self.assertTrue(result)
        self.assertTrue(self.integration._initialized)
    
    def test_integration_error_handling(self):
        """Test integration error handling."""
        # Test with systems that raise exceptions
        mock_sim_engine = Mock()
        mock_event_system = Mock()
        mock_config_manager = Mock()
        
        # Make event system raise exception
        mock_event_system.register_handler.side_effect = Exception("Test error")
        
        # Should still initialize successfully (exceptions are caught)
        result = self.integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        
        self.assertTrue(result)
    
    def test_integration_performance(self):
        """Test integration performance."""
        # Test with large number of events
        start_time = time.time()
        
        # Initialize integration
        mock_sim_engine = Mock()
        mock_event_system = Mock()
        mock_config_manager = Mock()
        
        self.integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        
        # Process many events
        num_events = 100
        for i in range(num_events):
            event_data = {
                'robot_id': f'robot_{i % 5:03d}',
                'from_coordinate': Coordinate(i % 25 + 1, i % 20 + 1),
                'to_coordinate': Coordinate((i + 1) % 25 + 1, (i + 1) % 20 + 1),
                'direction': 'forward'
            }
            self.integration._handle_robot_move(event_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 5.0)  # 5 seconds max
        
        # Verify data integrity
        self.assertEqual(len(self.integration.grid_visualizer.robot_positions), 5)
        
        print(f"Integration performance test: {num_events} events in {execution_time:.3f}s")
    
    def test_integration_data_persistence(self):
        """Test integration data persistence."""
        # Initialize integration
        mock_config_manager = Mock()
        self.integration.initialize_integration(config_manager=mock_config_manager)
        
        # Add some data
        self.integration.grid_visualizer.set_robot_position("robot_001", Coordinate(5, 5))
        self.integration.distance_tracker.track_robot_move(
            "robot_001", Coordinate(1, 1), Coordinate(5, 5)
        )
        
        # Export state
        state = self.integration.get_layout_state()
        
        # Verify state structure
        self.assertIn('warehouse_layout', state)
        self.assertIn('distance_tracker', state)
        self.assertIn('grid_visualizer', state)
        self.assertIn('packout_manager', state)
        
        # Import state
        result = self.integration.load_layout_state(state)
        self.assertTrue(result)
    
    def test_integration_validation(self):
        """Test integration validation."""
        # Initialize integration
        self.integration.initialize_integration()
        
        # Get validation results
        validation = self.integration.validate_grid_integrity()
        
        # Verify validation structure
        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)
        self.assertIn('statistics', validation)
        
        # Should be valid by default
        self.assertTrue(validation['valid'])
    
    def test_integration_extension_points(self):
        """Test integration extension points."""
        # Initialize integration
        self.integration.initialize_integration()
        
        # Get extension points
        extension_points = self.integration.create_extension_points()
        
        # Verify all components are accessible
        self.assertIsNotNone(extension_points['warehouse_layout'])
        self.assertIsNotNone(extension_points['snake_pattern'])
        self.assertIsNotNone(extension_points['packout_manager'])
        self.assertIsNotNone(extension_points['distance_tracker'])
        self.assertIsNotNone(extension_points['grid_visualizer'])
        self.assertIsNotNone(extension_points['integration_manager'])
        self.assertIsInstance(extension_points['event_handlers'], dict)


class TestComprehensiveEndToEnd(unittest.TestCase):
    """Comprehensive end-to-end tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = LayoutIntegrationManager()
        self.integration.initialize_integration()
    
    def test_complete_warehouse_workflow(self):
        """Test complete warehouse workflow."""
        # Simulate complete warehouse operation
        order_id = "order_001"
        robot_id = "robot_001"
        start_coord = Coordinate(1, 1)
        item_coord = Coordinate(10, 10)
        
        # 1. Start order
        self.integration._handle_order_start({
            'order_id': order_id,
            'robot_id': robot_id,
            'start_coordinate': start_coord
        })
        
        # 2. Move to item
        self.integration._handle_robot_move({
            'robot_id': robot_id,
            'from_coordinate': start_coord,
            'to_coordinate': item_coord,
            'direction': 'forward'
        })
        
        # 3. Pickup item
        self.integration._handle_item_pickup({
            'order_id': order_id,
            'robot_id': robot_id,
            'from_coordinate': item_coord,
            'to_coordinate': item_coord
        })
        
        # 4. Deliver to packout
        self.integration._handle_item_delivery({
            'order_id': order_id,
            'robot_id': robot_id,
            'from_coordinate': item_coord
        })
        
        # 5. Return to start
        self.integration._handle_robot_move({
            'robot_id': robot_id,
            'from_coordinate': self.integration.packout_manager.packout_location,
            'to_coordinate': start_coord,
            'direction': 'forward'
        })
        
        # 6. Complete order
        self.integration._handle_order_complete({
            'order_id': order_id,
            'robot_id': robot_id,
            'final_coordinate': start_coord
        })
        
        # Verify workflow results
        self.assertGreater(self.integration.distance_tracker.get_order_distance(order_id), 0)
        self.assertGreater(self.integration.distance_tracker.get_robot_distance(robot_id), 0)
        self.assertIn(robot_id, self.integration.grid_visualizer.robot_positions)
        
        # Verify KPI metrics
        metrics = self.integration.distance_tracker.get_kpi_metrics()
        self.assertEqual(metrics['total_orders'], 1)
        self.assertEqual(metrics['total_robots'], 1)
        self.assertGreater(metrics['efficiency_score'], 0)
    
    def test_multiple_orders_concurrent(self):
        """Test multiple orders running concurrently."""
        # Simulate multiple orders
        num_orders = 5
        orders = []
        
        for i in range(num_orders):
            order_id = f"order_{i:03d}"
            robot_id = f"robot_{i % 3:03d}"
            start_coord = Coordinate(i + 1, i + 1)
            item_coord = Coordinate(i + 10, i + 10)
            
            # Start order
            self.integration._handle_order_start({
                'order_id': order_id,
                'robot_id': robot_id,
                'start_coordinate': start_coord
            })
            
            # Move to item
            self.integration._handle_robot_move({
                'robot_id': robot_id,
                'from_coordinate': start_coord,
                'to_coordinate': item_coord,
                'direction': 'forward'
            })
            
            # Pickup item
            self.integration._handle_item_pickup({
                'order_id': order_id,
                'robot_id': robot_id,
                'from_coordinate': start_coord,
                'to_coordinate': item_coord
            })
            
            # Deliver to packout
            self.integration._handle_item_delivery({
                'order_id': order_id,
                'robot_id': robot_id,
                'from_coordinate': item_coord
            })
            
            # Complete order
            self.integration._handle_order_complete({
                'order_id': order_id,
                'robot_id': robot_id,
                'final_coordinate': self.integration.packout_manager.packout_location
            })
            
            orders.append(order_id)
        
        # Verify results
        for order_id in orders:
            self.assertGreater(self.integration.distance_tracker.get_order_distance(order_id), 0)
        
        # Verify KPI metrics
        metrics = self.integration.distance_tracker.get_kpi_metrics()
        self.assertEqual(metrics['total_orders'], num_orders)
        self.assertEqual(metrics['total_robots'], 3)
        self.assertGreater(metrics['efficiency_score'], 0)
    
    def test_system_stress_test(self):
        """Test system under stress conditions."""
        # Generate many rapid events
        num_events = 500
        start_time = time.time()
        
        for i in range(num_events):
            order_id = f"order_{i:03d}"
            robot_id = f"robot_{i % 10:03d}"
            coord1 = Coordinate(random.randint(1, 25), random.randint(1, 20))
            coord2 = Coordinate(random.randint(1, 25), random.randint(1, 20))
            
            # Random event types
            event_type = random.choice(['robot_move', 'order_start', 'item_pickup'])
            
            if event_type == 'robot_move':
                self.integration._handle_robot_move({
                    'robot_id': robot_id,
                    'from_coordinate': coord1,
                    'to_coordinate': coord2,
                    'direction': 'forward'
                })
            elif event_type == 'order_start':
                self.integration._handle_order_start({
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'start_coordinate': coord1
                })
            elif event_type == 'item_pickup':
                self.integration._handle_item_pickup({
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'from_coordinate': coord1,
                    'to_coordinate': coord2
                })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 15.0)  # 15 seconds max
        
        # Verify system integrity
        self.assertGreater(len(self.integration.distance_tracker.events), 0)
        self.assertGreater(self.integration.distance_tracker.total_distance, 0)
        
        print(f"System stress test: {num_events} events in {execution_time:.3f}s")


if __name__ == "__main__":
    unittest.main() 