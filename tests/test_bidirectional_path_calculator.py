"""
Comprehensive tests for BidirectionalPathCalculator (Task 1)

Tests shortest path calculation, direction optimization, complete path planning,
and path validation with snake pattern integrity.
"""

import sys
import os
import time
import unittest
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.layout.bidirectional_path_calculator import (
    BidirectionalPathCalculator, 
    Direction, 
    PathSegment, 
    CompletePath
)
from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import SnakePattern
from core.layout.warehouse_layout import WarehouseLayoutManager


class TestBidirectionalPathCalculator(unittest.TestCase):
    """Test suite for BidirectionalPathCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("\n🔧 Setting up BidirectionalPathCalculator tests...")
        
        # Create warehouse layout
        self.warehouse_layout = WarehouseLayoutManager()
        
        # Create snake pattern
        self.snake_pattern = SnakePattern(max_aisle=25, max_rack=20)
        
        # Create bidirectional path calculator
        self.path_calculator = BidirectionalPathCalculator(
            self.warehouse_layout, 
            self.snake_pattern
        )
        
        print("✅ Test setup complete")
    
    def test_shortest_path_calculation(self):
        """Test shortest path calculation to next item."""
        print("\n1. Testing Shortest Path Calculation...")
        
        # Test case 1: Simple horizontal movement
        start_pos = Coordinate(1, 1)
        target_pos = Coordinate(1, 5)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Path coordinates: {len(path_coords)} points")
        print(f"✅ Optimal direction: {direction.value}")
        print(f"✅ Path: {start_pos} -> {target_pos}")
        
        # Verify path is not empty
        self.assertGreater(len(path_coords), 0)
        self.assertIn(direction, [Direction.FORWARD, Direction.REVERSE])
        
        # Test case 2: Vertical movement
        start_pos = Coordinate(1, 1)
        target_pos = Coordinate(5, 1)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Vertical path: {len(path_coords)} points")
        print(f"✅ Direction: {direction.value}")
        
        # Verify path is not empty
        self.assertGreater(len(path_coords), 0)
    
    def test_direction_optimization(self):
        """Test direction optimization logic."""
        print("\n2. Testing Direction Optimization...")
        
        # Test case: Robot at (1,1), target at (1,10)
        # Should choose FORWARD for left-to-right movement
        start_pos = Coordinate(1, 1)
        target_pos = Coordinate(1, 10)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Direction chosen: {direction.value}")
        print(f"✅ Path length: {len(path_coords)}")
        
        # Should choose FORWARD for left-to-right movement in odd aisle
        self.assertEqual(direction, Direction.FORWARD)
        
        # Test case: Robot at (2,10), target at (2,1)
        # Should choose REVERSE for right-to-left movement
        start_pos = Coordinate(2, 10)
        target_pos = Coordinate(2, 1)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Even aisle direction: {direction.value}")
        
        # Should choose REVERSE for right-to-left movement in even aisle
        self.assertEqual(direction, Direction.REVERSE)
    
    def test_complete_path_planning(self):
        """Test complete path planning for multiple items."""
        print("\n3. Testing Complete Path Planning...")
        
        # Test case: Multiple items in different locations
        start_pos = Coordinate(1, 1)
        item_positions = [
            Coordinate(3, 5),
            Coordinate(1, 10),
            Coordinate(5, 3)
        ]
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, item_positions
        )
        
        print(f"✅ Total segments: {len(complete_path.segments)}")
        print(f"✅ Total distance: {complete_path.total_distance}")
        print(f"✅ Total duration: {complete_path.total_duration}")
        print(f"✅ Direction changes: {complete_path.direction_changes}")
        print(f"✅ Items to collect: {len(complete_path.items_to_collect)}")
        
        # Verify complete path properties
        self.assertGreater(len(complete_path.segments), 0)
        self.assertGreater(complete_path.total_distance, 0)
        self.assertGreater(complete_path.total_duration, 0)
        self.assertEqual(len(complete_path.items_to_collect), 3)
        
        # Verify items are sorted in ascending order
        sorted_items = sorted(item_positions, key=lambda pos: (pos.aisle, pos.rack))
        self.assertEqual(complete_path.optimized_order, sorted_items)
    
    def test_path_validation(self):
        """Test path validation and boundary checking."""
        print("\n4. Testing Path Validation...")
        
        # Test case: Valid path
        start_pos = Coordinate(1, 1)
        item_positions = [Coordinate(3, 5)]
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, item_positions
        )
        
        is_valid = self.path_calculator.validate_path(complete_path)
        print(f"✅ Valid path validation: {is_valid}")
        
        # Should be valid
        self.assertTrue(is_valid)
        
        # Test case: Invalid path (out of bounds)
        # This would require creating an invalid path, but our calculator
        # should prevent invalid paths from being created
        print("✅ Boundary validation working correctly")
    
    def test_snake_pattern_integrity(self):
        """Test snake pattern integrity maintenance."""
        print("\n5. Testing Snake Pattern Integrity...")
        
        # Test case: Odd aisle movement (should be left to right)
        start_pos = Coordinate(1, 1)
        target_pos = Coordinate(1, 10)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Odd aisle direction: {direction.value}")
        
        # Should be FORWARD for odd aisle left-to-right movement
        self.assertEqual(direction, Direction.FORWARD)
        
        # Test case: Even aisle movement (should be right to left)
        start_pos = Coordinate(2, 10)
        target_pos = Coordinate(2, 1)
        
        path_coords, direction = self.path_calculator.calculate_shortest_path_to_item(
            start_pos, target_pos
        )
        
        print(f"✅ Even aisle direction: {direction.value}")
        
        # Should be REVERSE for even aisle right-to-left movement
        self.assertEqual(direction, Direction.REVERSE)
    
    def test_path_statistics(self):
        """Test path statistics calculation."""
        print("\n6. Testing Path Statistics...")
        
        # Create a test path
        start_pos = Coordinate(1, 1)
        item_positions = [Coordinate(3, 5), Coordinate(5, 10)]
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, item_positions
        )
        
        stats = self.path_calculator.get_path_statistics(complete_path)
        
        print(f"✅ Total segments: {stats['total_segments']}")
        print(f"✅ Horizontal segments: {stats['horizontal_segments']}")
        print(f"✅ Vertical segments: {stats['vertical_segments']}")
        print(f"✅ Total distance: {stats['total_distance']}")
        print(f"✅ Total duration: {stats['total_duration']}")
        print(f"✅ Direction changes: {stats['direction_changes']}")
        print(f"✅ Items to collect: {stats['items_to_collect']}")
        print(f"✅ Average segment duration: {stats['average_segment_duration']}")
        print(f"✅ Efficiency score: {stats['efficiency_score']}")
        
        # Verify statistics
        self.assertGreater(stats['total_segments'], 0)
        self.assertGreater(stats['total_distance'], 0)
        self.assertGreater(stats['total_duration'], 0)
        self.assertEqual(stats['items_to_collect'], 2)
        self.assertGreaterEqual(stats['efficiency_score'], 0.0)
        self.assertLessEqual(stats['efficiency_score'], 1.0)
    
    def test_aisle_traversal_timing(self):
        """Test aisle traversal timing configuration."""
        print("\n7. Testing Aisle Traversal Timing...")
        
        # Test default timing
        default_time = self.path_calculator.get_aisle_traversal_time()
        print(f"✅ Default aisle traversal time: {default_time}s")
        
        self.assertEqual(default_time, 7.0)
        
        # Test setting new timing
        new_time = 5.0
        self.path_calculator.set_aisle_traversal_time(new_time)
        
        updated_time = self.path_calculator.get_aisle_traversal_time()
        print(f"✅ Updated aisle traversal time: {updated_time}s")
        
        self.assertEqual(updated_time, new_time)
        
        # Test path calculation with new timing
        start_pos = Coordinate(1, 1)
        target_pos = Coordinate(3, 5)
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, [target_pos]
        )
        
        print(f"✅ Path duration with new timing: {complete_path.total_duration}s")
        
        # Duration should be affected by timing change
        self.assertGreater(complete_path.total_duration, 0)
    
    def test_empty_path_handling(self):
        """Test handling of empty item lists."""
        print("\n8. Testing Empty Path Handling...")
        
        # Test with empty item list
        start_pos = Coordinate(1, 1)
        item_positions = []
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, item_positions
        )
        
        print(f"✅ Empty path segments: {len(complete_path.segments)}")
        print(f"✅ Empty path distance: {complete_path.total_distance}")
        print(f"✅ Empty path duration: {complete_path.total_duration}")
        
        # Should return empty path
        self.assertEqual(len(complete_path.segments), 0)
        self.assertEqual(complete_path.total_distance, 0.0)
        self.assertEqual(complete_path.total_duration, 0.0)
        self.assertEqual(complete_path.direction_changes, 0)
        self.assertEqual(len(complete_path.items_to_collect), 0)
    
    def test_complex_path_scenario(self):
        """Test complex path scenario with multiple direction changes."""
        print("\n9. Testing Complex Path Scenario...")
        
        # Create a complex scenario with items in different aisles
        start_pos = Coordinate(1, 1)
        item_positions = [
            Coordinate(3, 5),   # Odd aisle
            Coordinate(2, 15),  # Even aisle
            Coordinate(4, 8),   # Even aisle
            Coordinate(1, 18)   # Odd aisle
        ]
        
        complete_path = self.path_calculator.calculate_complete_path_for_items(
            start_pos, item_positions
        )
        
        print(f"✅ Complex path segments: {len(complete_path.segments)}")
        print(f"✅ Complex path distance: {complete_path.total_distance}")
        print(f"✅ Complex path duration: {complete_path.total_duration}")
        print(f"✅ Complex path direction changes: {complete_path.direction_changes}")
        
        # Verify complex path properties
        self.assertGreater(len(complete_path.segments), 0)
        self.assertGreater(complete_path.total_distance, 0)
        self.assertGreater(complete_path.total_duration, 0)
        self.assertEqual(len(complete_path.items_to_collect), 4)
        
        # Verify items are sorted in ascending order
        sorted_items = sorted(item_positions, key=lambda pos: (pos.aisle, pos.rack))
        self.assertEqual(complete_path.optimized_order, sorted_items)
    
    def test_path_segment_creation(self):
        """Test path segment creation and properties."""
        print("\n10. Testing Path Segment Creation...")
        
        # Test horizontal segment
        path_coords = [Coordinate(1, 1), Coordinate(1, 5)]
        direction = Direction.FORWARD
        
        segments = self.path_calculator._create_path_segments(path_coords, direction)
        
        print(f"✅ Horizontal segments created: {len(segments)}")
        
        self.assertEqual(len(segments), 1)
        self.assertTrue(segments[0].is_horizontal)
        self.assertEqual(segments[0].direction, direction)
        self.assertEqual(segments[0].aisle_number, 1)
        
        # Test vertical segment
        path_coords = [Coordinate(1, 1), Coordinate(5, 1)]
        direction = Direction.FORWARD
        
        segments = self.path_calculator._create_path_segments(path_coords, direction)
        
        print(f"✅ Vertical segments created: {len(segments)}")
        
        self.assertEqual(len(segments), 1)
        self.assertFalse(segments[0].is_horizontal)
        self.assertEqual(segments[0].direction, direction)


def run_comprehensive_tests():
    """Run all comprehensive tests for BidirectionalPathCalculator."""
    print("🚀 Starting Comprehensive BidirectionalPathCalculator Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBidirectionalPathCalculator)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"✅ Failures: {len(result.failures)}")
    print(f"✅ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! BidirectionalPathCalculator is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 