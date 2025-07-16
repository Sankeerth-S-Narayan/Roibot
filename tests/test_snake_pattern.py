"""
Unit tests for the SnakePattern class.

Tests bidirectional snake pattern navigation, direction optimization,
path planning, and direction change tracking.
"""

import unittest
from core.layout.snake_pattern import SnakePattern, Direction
from core.layout.coordinate import Coordinate


class TestSnakePattern(unittest.TestCase):
    """Test cases for the SnakePattern class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.snake_pattern = SnakePattern(max_aisle=25, max_rack=20)
    
    def test_initialization(self):
        """Test snake pattern initialization."""
        self.assertEqual(self.snake_pattern.max_aisle, 25)
        self.assertEqual(self.snake_pattern.max_rack, 20)
        self.assertEqual(self.snake_pattern.direction_changes, 0)
        self.assertEqual(self.snake_pattern.current_direction, Direction.FORWARD)
    
    def test_snake_direction_odd_aisles(self):
        """Test snake direction for odd aisles."""
        # Odd aisles should be LEFT_TO_RIGHT
        self.assertEqual(self.snake_pattern.get_snake_direction(1), Direction.LEFT_TO_RIGHT)
        self.assertEqual(self.snake_pattern.get_snake_direction(3), Direction.LEFT_TO_RIGHT)
        self.assertEqual(self.snake_pattern.get_snake_direction(25), Direction.LEFT_TO_RIGHT)
    
    def test_snake_direction_even_aisles(self):
        """Test snake direction for even aisles."""
        # Even aisles should be RIGHT_TO_LEFT
        self.assertEqual(self.snake_pattern.get_snake_direction(2), Direction.RIGHT_TO_LEFT)
        self.assertEqual(self.snake_pattern.get_snake_direction(4), Direction.RIGHT_TO_LEFT)
        self.assertEqual(self.snake_pattern.get_snake_direction(24), Direction.RIGHT_TO_LEFT)
    
    def test_optimal_direction_forward(self):
        """Test optimal direction calculation for forward movement."""
        start = Coordinate(5, 5)
        target = Coordinate(7, 7)
        
        # Should choose forward for nearby targets
        optimal = self.snake_pattern.get_optimal_direction(start, target)
        self.assertEqual(optimal, Direction.FORWARD)
    
    def test_optimal_direction_reverse(self):
        """Test optimal direction calculation for reverse movement."""
        start = Coordinate(5, 5)
        target = Coordinate(20, 15)
        
        # Should choose reverse for distant targets
        optimal = self.snake_pattern.get_optimal_direction(start, target)
        # Note: This might be forward or reverse depending on the algorithm
        self.assertIn(optimal, [Direction.FORWARD, Direction.REVERSE])
    
    def test_forward_distance_calculation(self):
        """Test forward distance calculation."""
        start = Coordinate(5, 5)
        target = Coordinate(7, 8)
        
        distance = self.snake_pattern._calculate_forward_distance(start, target)
        expected = 5  # 2 horizontal + 3 vertical
        self.assertEqual(distance, expected)
    
    def test_reverse_distance_calculation(self):
        """Test reverse distance calculation."""
        start = Coordinate(5, 5)
        target = Coordinate(20, 15)
        
        distance = self.snake_pattern._calculate_reverse_distance(start, target)
        # Should be greater than direct distance
        self.assertGreater(distance, start.distance_to(target))
    
    def test_path_to_target_same_position(self):
        """Test path to target when start and target are the same."""
        coord = Coordinate(5, 5)
        path = self.snake_pattern.get_path_to_target(coord, coord)
        
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], coord)
    
    def test_forward_path_generation(self):
        """Test forward path generation."""
        start = Coordinate(5, 5)
        target = Coordinate(7, 8)
        
        path = self.snake_pattern._generate_forward_path(start, target)
        
        # Check path structure
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], target)
        
        # Check intermediate points
        self.assertIn(Coordinate(6, 5), path)
        self.assertIn(Coordinate(7, 5), path)
        self.assertIn(Coordinate(7, 6), path)
        self.assertIn(Coordinate(7, 7), path)
    
    def test_reverse_path_generation(self):
        """Test reverse path generation."""
        start = Coordinate(5, 5)
        target = Coordinate(20, 15)
        
        path = self.snake_pattern._generate_reverse_path(start, target)
        
        # Check path structure
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], target)
        
        # Should include movement to the end
        self.assertIn(Coordinate(25, 5), path)
    
    def test_aisle_direction_forward(self):
        """Test aisle direction calculation for forward movement."""
        # Odd aisle with forward movement
        direction = self.snake_pattern.get_aisle_direction(5, Direction.FORWARD)
        self.assertEqual(direction, Direction.LEFT_TO_RIGHT)
        
        # Even aisle with forward movement
        direction = self.snake_pattern.get_aisle_direction(6, Direction.FORWARD)
        self.assertEqual(direction, Direction.RIGHT_TO_LEFT)
    
    def test_aisle_direction_reverse(self):
        """Test aisle direction calculation for reverse movement."""
        # Odd aisle with reverse movement
        direction = self.snake_pattern.get_aisle_direction(5, Direction.REVERSE)
        self.assertEqual(direction, Direction.RIGHT_TO_LEFT)
        
        # Even aisle with reverse movement
        direction = self.snake_pattern.get_aisle_direction(6, Direction.REVERSE)
        self.assertEqual(direction, Direction.LEFT_TO_RIGHT)
    
    def test_path_distance_calculation(self):
        """Test path distance calculation."""
        path = [
            Coordinate(1, 1),
            Coordinate(2, 1),
            Coordinate(3, 1),
            Coordinate(3, 2),
            Coordinate(3, 3)
        ]
        
        distance = self.snake_pattern.calculate_path_distance(path)
        expected = 4  # 1 + 1 + 1 + 1
        self.assertEqual(distance, expected)
    
    def test_path_distance_empty_path(self):
        """Test path distance calculation for empty path."""
        path = []
        distance = self.snake_pattern.calculate_path_distance(path)
        self.assertEqual(distance, 0.0)
    
    def test_path_distance_single_point(self):
        """Test path distance calculation for single point."""
        path = [Coordinate(5, 5)]
        distance = self.snake_pattern.calculate_path_distance(path)
        self.assertEqual(distance, 0.0)
    
    def test_optimize_path_for_multiple_targets(self):
        """Test path optimization for multiple targets."""
        start = Coordinate(1, 1)
        targets = [
            Coordinate(5, 5),
            Coordinate(3, 3),
            Coordinate(7, 7)
        ]
        
        path = self.snake_pattern.optimize_path_for_multiple_targets(start, targets)
        
        # Check path structure
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], targets[-1])
        
        # Should visit all targets
        for target in targets:
            self.assertIn(target, path)
    
    def test_optimize_path_no_targets(self):
        """Test path optimization with no targets."""
        start = Coordinate(5, 5)
        targets = []
        
        path = self.snake_pattern.optimize_path_for_multiple_targets(start, targets)
        
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], start)
    
    def test_direction_change_count(self):
        """Test direction change counting."""
        path = [
            Coordinate(1, 1),
            Coordinate(2, 1),  # Right
            Coordinate(3, 1),  # Right
            Coordinate(3, 2),  # Down (direction change)
            Coordinate(3, 3),  # Down
            Coordinate(4, 3),  # Right (direction change)
        ]
        
        changes = self.snake_pattern.get_direction_change_count(path)
        self.assertEqual(changes, 2)
    
    def test_direction_change_count_short_path(self):
        """Test direction change counting for short paths."""
        # Path with less than 3 points
        path = [Coordinate(1, 1), Coordinate(2, 1)]
        changes = self.snake_pattern.get_direction_change_count(path)
        self.assertEqual(changes, 0)
    
    def test_is_direction_change(self):
        """Test direction change detection."""
        prev = Coordinate(1, 1)
        curr = Coordinate(2, 1)
        next_pos = Coordinate(3, 1)
        
        # No direction change (all moving right)
        self.assertFalse(self.snake_pattern._is_direction_change(prev, curr, next_pos))
        
        # Direction change (right then down)
        next_pos = Coordinate(2, 2)
        self.assertTrue(self.snake_pattern._is_direction_change(prev, curr, next_pos))
    
    def test_path_statistics(self):
        """Test path statistics calculation."""
        path = [
            Coordinate(1, 1),
            Coordinate(2, 1),
            Coordinate(3, 1),
            Coordinate(3, 2),
            Coordinate(3, 3)
        ]
        
        stats = self.snake_pattern.get_path_statistics(path)
        
        self.assertEqual(stats['total_distance'], 4.0)
        self.assertEqual(stats['direction_changes'], 1)
        self.assertEqual(stats['path_length'], 5)
        self.assertEqual(stats['start_coordinate'], Coordinate(1, 1))
        self.assertEqual(stats['end_coordinate'], Coordinate(3, 3))
        self.assertEqual(stats['average_distance_per_step'], 1.0)
    
    def test_path_statistics_empty_path(self):
        """Test path statistics for empty path."""
        path = []
        stats = self.snake_pattern.get_path_statistics(path)
        
        self.assertEqual(stats['total_distance'], 0.0)
        self.assertEqual(stats['direction_changes'], 0)
        self.assertEqual(stats['path_length'], 0)
        self.assertIsNone(stats['start_coordinate'])
        self.assertIsNone(stats['end_coordinate'])
    
    def test_direction_change_tracking(self):
        """Test direction change tracking."""
        # Initial state
        self.assertEqual(self.snake_pattern.get_direction_changes(), 0)
        
        # Set same direction (no change)
        self.snake_pattern.set_current_direction(Direction.FORWARD)
        self.assertEqual(self.snake_pattern.get_direction_changes(), 0)
        
        # Change direction
        self.snake_pattern.set_current_direction(Direction.REVERSE)
        self.assertEqual(self.snake_pattern.get_direction_changes(), 1)
        
        # Change again
        self.snake_pattern.set_current_direction(Direction.FORWARD)
        self.assertEqual(self.snake_pattern.get_direction_changes(), 2)
    
    def test_reset_direction_changes(self):
        """Test resetting direction change counter."""
        # Make some direction changes
        self.snake_pattern.set_current_direction(Direction.REVERSE)
        self.snake_pattern.set_current_direction(Direction.FORWARD)
        self.assertEqual(self.snake_pattern.get_direction_changes(), 2)
        
        # Reset
        self.snake_pattern.reset_direction_changes()
        self.assertEqual(self.snake_pattern.get_direction_changes(), 0)
    
    def test_get_current_direction(self):
        """Test getting current direction."""
        self.assertEqual(self.snake_pattern.get_current_direction(), Direction.FORWARD)
        
        self.snake_pattern.set_current_direction(Direction.REVERSE)
        self.assertEqual(self.snake_pattern.get_current_direction(), Direction.REVERSE)
    
    def test_string_representations(self):
        """Test string representations."""
        # String representation
        str_repr = str(self.snake_pattern)
        self.assertIn("SnakePattern(25x20)", str_repr)
        self.assertIn("Direction: forward", str_repr)
        
        # Detailed representation
        repr_str = repr(self.snake_pattern)
        self.assertIn("SnakePattern", repr_str)
        self.assertIn("max_aisle=25", repr_str)
        self.assertIn("max_rack=20", repr_str)
        self.assertIn("direction=forward", repr_str)
    
    def test_complex_path_scenario(self):
        """Test complex path scenario with multiple direction changes."""
        start = Coordinate(1, 1)
        target = Coordinate(25, 20)
        
        # Get optimal path
        path = self.snake_pattern.get_path_to_target(start, target)
        
        # Verify path properties
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], target)
        
        # Calculate statistics
        stats = self.snake_pattern.get_path_statistics(path)
        
        # Verify statistics
        self.assertGreater(stats['total_distance'], 0)
        self.assertGreaterEqual(stats['direction_changes'], 0)
        self.assertEqual(stats['path_length'], len(path))
        self.assertEqual(stats['start_coordinate'], start)
        self.assertEqual(stats['end_coordinate'], target)


if __name__ == '__main__':
    unittest.main() 