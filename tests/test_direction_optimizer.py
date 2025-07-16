"""
Comprehensive tests for DirectionOptimizer (Task 2)

Tests direction optimization, snake pattern integration, smooth direction changes,
direction state tracking, and integration with robot movement system.
"""

import sys
import os
import time
import unittest
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.layout.direction_optimizer import (
    DirectionOptimizer, 
    DirectionState, 
    DirectionChange
)
from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import SnakePattern, Direction
from core.layout.warehouse_layout import WarehouseLayoutManager


class TestDirectionOptimizer(unittest.TestCase):
    """Test suite for DirectionOptimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("\n🔧 Setting up DirectionOptimizer tests...")
        
        # Create warehouse layout
        self.warehouse_layout = WarehouseLayoutManager()
        
        # Create snake pattern
        self.snake_pattern = SnakePattern(max_aisle=25, max_rack=20)
        
        # Create direction optimizer
        self.direction_optimizer = DirectionOptimizer(
            self.warehouse_layout, 
            self.snake_pattern
        )
        
        print("✅ Test setup complete")
    
    def test_direction_optimization_for_same_aisle(self):
        """Test direction optimization for same aisle movement."""
        print("\n1. Testing Direction Optimization for Same Aisle...")
        
        # Test case 1: Odd aisle - left to right
        current_pos = Coordinate(1, 1)
        target_pos = Coordinate(1, 10)
        path_coords = [Coordinate(1, i) for i in range(1, 11)]
        
        direction = self.direction_optimizer.optimize_direction_for_path(
            current_pos, target_pos, path_coords
        )
        
        print(f"✅ Odd aisle direction: {direction.value}")
        
        # Should be FORWARD for left-to-right movement in odd aisle
        self.assertEqual(direction, Direction.FORWARD)
        
        # Test case 2: Even aisle - right to left
        current_pos = Coordinate(2, 10)
        target_pos = Coordinate(2, 1)
        path_coords = [Coordinate(2, i) for i in range(10, 0, -1)]
        
        direction = self.direction_optimizer.optimize_direction_for_path(
            current_pos, target_pos, path_coords
        )
        
        print(f"✅ Even aisle direction: {direction.value}")
        
        # Should be REVERSE for right-to-left movement in even aisle
        self.assertEqual(direction, Direction.REVERSE)
    
    def test_direction_optimization_for_different_aisles(self):
        """Test direction optimization for cross-aisle movement."""
        print("\n2. Testing Direction Optimization for Different Aisles...")
        
        # Test case: Cross-aisle movement
        current_pos = Coordinate(1, 1)
        target_pos = Coordinate(5, 10)
        path_coords = [Coordinate(i, j) for i in range(1, 6) for j in range(1, 11)]
        
        direction = self.direction_optimizer.optimize_direction_for_path(
            current_pos, target_pos, path_coords
        )
        
        print(f"✅ Cross-aisle direction: {direction.value}")
        
        # Should return a valid direction
        self.assertIn(direction, [Direction.FORWARD, Direction.REVERSE])
    
    def test_smooth_direction_change(self):
        """Test smooth direction change logic."""
        print("\n3. Testing Smooth Direction Change...")
        
        # Test initial direction
        initial_direction = self.direction_optimizer.get_current_direction()
        print(f"✅ Initial direction: {initial_direction.value}")
        
        self.assertEqual(initial_direction, Direction.FORWARD)
        
        # Test direction change
        current_pos = Coordinate(1, 1)
        success = self.direction_optimizer.change_direction(
            Direction.REVERSE, current_pos, "Test direction change"
        )
        
        print(f"✅ Direction change successful: {success}")
        
        # Should be successful
        self.assertTrue(success)
        
        # Check new direction
        new_direction = self.direction_optimizer.get_current_direction()
        print(f"✅ New direction: {new_direction.value}")
        
        self.assertEqual(new_direction, Direction.REVERSE)
        
        # Test direction change cooldown
        success = self.direction_optimizer.change_direction(
            Direction.FORWARD, current_pos, "Immediate change"
        )
        
        print(f"✅ Immediate change allowed: {success}")
        
        # Should be blocked by cooldown
        self.assertFalse(success)
    
    def test_direction_state_tracking(self):
        """Test direction state tracking."""
        print("\n4. Testing Direction State Tracking...")
        
        # Test initial state
        initial_state = self.direction_optimizer.get_direction_state()
        print(f"✅ Initial state: {initial_state.value}")
        
        self.assertEqual(initial_state, DirectionState.IDLE)
        
        # Test state during direction change
        current_pos = Coordinate(1, 1)
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        
        # State should be IDLE after change
        state = self.direction_optimizer.get_direction_state()
        print(f"✅ State after change: {state.value}")
        
        self.assertEqual(state, DirectionState.IDLE)
    
    def test_direction_change_history(self):
        """Test direction change history tracking."""
        print("\n5. Testing Direction Change History...")
        
        # Make some direction changes
        current_pos = Coordinate(1, 1)
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos, "First change")
        time.sleep(0.2)  # Wait for cooldown
        self.direction_optimizer.change_direction(Direction.FORWARD, current_pos, "Second change")
        
        # Get direction changes
        changes = self.direction_optimizer.get_direction_changes()
        print(f"✅ Total direction changes: {len(changes)}")
        
        # Should have 2 changes
        self.assertEqual(len(changes), 2)
        
        # Check first change
        first_change = changes[0]
        print(f"✅ First change: {first_change.from_direction.value} -> {first_change.to_direction.value}")
        
        self.assertEqual(first_change.from_direction, Direction.FORWARD)
        self.assertEqual(first_change.to_direction, Direction.REVERSE)
        self.assertEqual(first_change.reason, "First change")
        
        # Check second change
        second_change = changes[1]
        print(f"✅ Second change: {second_change.from_direction.value} -> {second_change.to_direction.value}")
        
        self.assertEqual(second_change.from_direction, Direction.REVERSE)
        self.assertEqual(second_change.to_direction, Direction.FORWARD)
        self.assertEqual(second_change.reason, "Second change")
    
    def test_direction_statistics(self):
        """Test direction statistics calculation."""
        print("\n6. Testing Direction Statistics...")
        
        # Reset and make some changes
        self.direction_optimizer.reset_direction_changes()
        current_pos = Coordinate(1, 1)
        
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        time.sleep(0.2)
        self.direction_optimizer.change_direction(Direction.FORWARD, current_pos)
        time.sleep(0.2)
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        
        # Get statistics
        stats = self.direction_optimizer.get_direction_statistics()
        
        print(f"✅ Total changes: {stats['total_changes']}")
        print(f"✅ Forward changes: {stats['forward_changes']}")
        print(f"✅ Reverse changes: {stats['reverse_changes']}")
        print(f"✅ Current direction: {stats['current_direction']}")
        print(f"✅ Direction state: {stats['direction_state']}")
        
        # Verify statistics
        self.assertEqual(stats['total_changes'], 3)
        self.assertEqual(stats['forward_changes'], 1)
        self.assertEqual(stats['reverse_changes'], 2)
        self.assertEqual(stats['current_direction'], 'reverse')
        self.assertEqual(stats['direction_state'], 'idle')
    
    def test_cooldown_management(self):
        """Test direction change cooldown management."""
        print("\n7. Testing Cooldown Management...")
        
        # Test default cooldown
        default_cooldown = self.direction_optimizer.get_change_cooldown()
        print(f"✅ Default cooldown: {default_cooldown}s")
        
        self.assertEqual(default_cooldown, 0.1)
        
        # Test setting new cooldown
        new_cooldown = 0.5
        self.direction_optimizer.set_change_cooldown(new_cooldown)
        
        updated_cooldown = self.direction_optimizer.get_change_cooldown()
        print(f"✅ Updated cooldown: {updated_cooldown}s")
        
        self.assertEqual(updated_cooldown, new_cooldown)
        
        # Test cooldown check
        current_pos = Coordinate(1, 1)
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        
        # Should not be allowed immediately
        allowed = self.direction_optimizer.is_direction_change_allowed()
        print(f"✅ Direction change allowed: {allowed}")
        
        self.assertFalse(allowed)
        
        # Wait for cooldown
        time.sleep(0.6)
        
        # Should be allowed now
        allowed = self.direction_optimizer.is_direction_change_allowed()
        print(f"✅ Direction change allowed after wait: {allowed}")
        
        self.assertTrue(allowed)
    
    def test_snake_pattern_integration(self):
        """Test snake pattern integration."""
        print("\n8. Testing Snake Pattern Integration...")
        
        # Test odd aisle movement
        current_pos = Coordinate(3, 1)
        target_pos = Coordinate(3, 15)
        path_coords = [Coordinate(3, i) for i in range(1, 16)]
        
        direction = self.direction_optimizer.optimize_direction_for_path(
            current_pos, target_pos, path_coords
        )
        
        print(f"✅ Odd aisle (3) direction: {direction.value}")
        
        # Should be FORWARD for odd aisle left-to-right
        self.assertEqual(direction, Direction.FORWARD)
        
        # Test even aisle movement
        current_pos = Coordinate(4, 15)
        target_pos = Coordinate(4, 1)
        path_coords = [Coordinate(4, i) for i in range(15, 0, -1)]
        
        direction = self.direction_optimizer.optimize_direction_for_path(
            current_pos, target_pos, path_coords
        )
        
        print(f"✅ Even aisle (4) direction: {direction.value}")
        
        # Should be REVERSE for even aisle right-to-left
        self.assertEqual(direction, Direction.REVERSE)
    
    def test_complex_direction_scenarios(self):
        """Test complex direction scenarios."""
        print("\n9. Testing Complex Direction Scenarios...")
        
        # Test multiple direction changes
        current_pos = Coordinate(1, 1)
        
        # Change to reverse
        success1 = self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        time.sleep(0.2)
        
        # Change to forward
        success2 = self.direction_optimizer.change_direction(Direction.FORWARD, current_pos)
        time.sleep(0.2)
        
        # Change to reverse again
        success3 = self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        
        print(f"✅ Success 1: {success1}")
        print(f"✅ Success 2: {success2}")
        print(f"✅ Success 3: {success3}")
        
        # All should be successful
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertTrue(success3)
        
        # Check final direction
        final_direction = self.direction_optimizer.get_current_direction()
        print(f"✅ Final direction: {final_direction.value}")
        
        self.assertEqual(final_direction, Direction.REVERSE)
        
        # Check total changes
        changes = self.direction_optimizer.get_direction_changes()
        print(f"✅ Total changes: {len(changes)}")
        
        self.assertEqual(len(changes), 3)
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        print("\n10. Testing Reset Functionality...")
        
        # Make some changes
        current_pos = Coordinate(1, 1)
        self.direction_optimizer.change_direction(Direction.REVERSE, current_pos)
        time.sleep(0.2)
        self.direction_optimizer.change_direction(Direction.FORWARD, current_pos)
        
        # Check changes before reset
        changes_before = self.direction_optimizer.get_direction_changes()
        print(f"✅ Changes before reset: {len(changes_before)}")
        
        self.assertEqual(len(changes_before), 2)
        
        # Reset
        self.direction_optimizer.reset_direction_changes()
        
        # Check changes after reset
        changes_after = self.direction_optimizer.get_direction_changes()
        print(f"✅ Changes after reset: {len(changes_after)}")
        
        self.assertEqual(len(changes_after), 0)
        
        # Direction should remain the same
        current_direction = self.direction_optimizer.get_current_direction()
        print(f"✅ Current direction after reset: {current_direction.value}")
        
        self.assertEqual(current_direction, Direction.FORWARD)


def run_comprehensive_tests():
    """Run all comprehensive tests for DirectionOptimizer."""
    print("🚀 Starting Comprehensive DirectionOptimizer Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectionOptimizer)
    
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
        print("\n🎉 All tests passed! DirectionOptimizer is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 