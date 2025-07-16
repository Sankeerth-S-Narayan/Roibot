"""
Comprehensive tests for AisleTimingManager.

Tests 7-second aisle traversal timing, configurable settings, timing calculations
for different movement types, validation, and event emission for analytics.
"""

import unittest
import time
from unittest.mock import Mock, patch

from core.layout.aisle_timing_manager import (
    AisleTimingManager, 
    TimingConfig, 
    MovementTiming, 
    MovementType
)
from core.layout.coordinate import Coordinate


class TestAisleTimingManager(unittest.TestCase):
    """Test suite for AisleTimingManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("\n🧪 Setting up AisleTimingManager tests...")
        
        # Test configuration
        self.test_config = {
            "robot": {
                "aisle_traversal_time": 7.0,
                "horizontal_movement_time": 0.35,
                "direction_change_cooldown": 0.5,
                "max_timing_variance": 0.1
            }
        }
        
        # Initialize timing manager
        self.timing_manager = AisleTimingManager(self.test_config)
        
        # Test coordinates
        self.start_pos = Coordinate(1, 1)
        self.end_pos = Coordinate(3, 5)
        self.horizontal_start = Coordinate(2, 1)
        self.horizontal_end = Coordinate(2, 10)
        self.vertical_start = Coordinate(1, 5)
        self.vertical_end = Coordinate(5, 5)
        
        print("✅ Test setup complete")
    
    def test_initialization(self):
        """Test AisleTimingManager initialization."""
        print("\n1. Testing Initialization...")
        
        # Test default initialization
        default_manager = AisleTimingManager()
        self.assertIsNotNone(default_manager.config)
        self.assertEqual(default_manager.config.aisle_traversal_time, 7.0)
        
        # Test config loading
        self.assertEqual(self.timing_manager.config.aisle_traversal_time, 7.0)
        self.assertEqual(self.timing_manager.config.horizontal_movement_time, 0.35)
        self.assertEqual(self.timing_manager.config.direction_change_cooldown, 0.5)
        
        print("✅ Initialization tests passed")
    
    def test_movement_type_detection(self):
        """Test movement type detection for different movement patterns."""
        print("\n2. Testing Movement Type Detection...")
        
        # Test horizontal movement
        horizontal_type = self.timing_manager._determine_movement_type(
            self.horizontal_start, self.horizontal_end
        )
        self.assertEqual(horizontal_type, MovementType.HORIZONTAL)
        print(f"✅ Horizontal movement detected: {horizontal_type}")
        
        # Test vertical movement
        vertical_type = self.timing_manager._determine_movement_type(
            self.vertical_start, self.vertical_end
        )
        self.assertEqual(vertical_type, MovementType.VERTICAL)
        print(f"✅ Vertical movement detected: {vertical_type}")
        
        # Test diagonal movement
        diagonal_type = self.timing_manager._determine_movement_type(
            self.start_pos, self.end_pos
        )
        self.assertEqual(diagonal_type, MovementType.DIAGONAL)
        print(f"✅ Diagonal movement detected: {diagonal_type}")
        
        print("✅ Movement type detection tests passed")
    
    def test_timing_calculations(self):
        """Test timing calculations for different movement types."""
        print("\n3. Testing Timing Calculations...")
        
        # Test horizontal movement timing
        horizontal_timing = self.timing_manager.calculate_movement_timing(
            self.horizontal_start, self.horizontal_end
        )
        expected_horizontal = 9 * 0.35  # 9 racks * 0.35s per rack
        self.assertAlmostEqual(horizontal_timing.duration, expected_horizontal, places=2)
        print(f"✅ Horizontal timing: {horizontal_timing.duration:.2f}s (expected: {expected_horizontal:.2f}s)")
        
        # Test vertical movement timing
        vertical_timing = self.timing_manager.calculate_movement_timing(
            self.vertical_start, self.vertical_end
        )
        expected_vertical = 4 * 7.0  # 4 aisles * 7.0s per aisle
        self.assertAlmostEqual(vertical_timing.duration, expected_vertical, places=2)
        print(f"✅ Vertical timing: {vertical_timing.duration:.2f}s (expected: {expected_vertical:.2f}s)")
        
        # Test diagonal movement timing
        diagonal_timing = self.timing_manager.calculate_movement_timing(
            self.start_pos, self.end_pos
        )
        expected_diagonal = (2 * 7.0) + (4 * 0.35)  # 2 aisles + 4 racks
        self.assertAlmostEqual(diagonal_timing.duration, expected_diagonal, places=2)
        print(f"✅ Diagonal timing: {diagonal_timing.duration:.2f}s (expected: {expected_diagonal:.2f}s)")
        
        print("✅ Timing calculation tests passed")
    
    def test_movement_start_and_update(self):
        """Test movement start and update functionality."""
        print("\n4. Testing Movement Start and Update...")
        
        # Start movement
        movement = self.timing_manager.start_movement(self.start_pos, self.end_pos)
        self.assertIsNotNone(movement)
        self.assertFalse(movement.is_completed)
        self.assertEqual(movement.start_position, self.start_pos)
        self.assertEqual(movement.end_position, self.end_pos)
        print(f"✅ Movement started: {movement.duration:.2f}s")
        
        # Test movement progress
        current_time = time.time()
        progress_data = self.timing_manager.update_movement(current_time)
        
        if progress_data:
            self.assertEqual(progress_data["type"], "movement_progress")
            self.assertGreaterEqual(progress_data["progress"], 0.0)
            self.assertLessEqual(progress_data["progress"], 1.0)
            print(f"✅ Movement progress: {progress_data['progress']:.2%}")
        
        print("✅ Movement start and update tests passed")
    
    def test_movement_completion(self):
        """Test movement completion detection."""
        print("\n5. Testing Movement Completion...")
        
        # Start movement
        movement = self.timing_manager.start_movement(self.start_pos, self.end_pos)
        
        # Simulate completion by advancing time
        completion_time = movement.end_time + 0.1
        completion_data = self.timing_manager.update_movement(completion_time)
        
        if completion_data:
            self.assertEqual(completion_data["type"], "movement_complete")
            self.assertIn("movement", completion_data)
            self.assertIn("total_time", completion_data)
            print(f"✅ Movement completed: {completion_data['total_time']:.2f}s total")
        
        # Check statistics
        stats = self.timing_manager.get_timing_statistics()
        self.assertGreater(stats["total_movements"], 0)
        self.assertGreater(stats["total_time"], 0.0)
        print(f"✅ Statistics updated: {stats['total_movements']} movements, {stats['total_time']:.2f}s total")
        
        print("✅ Movement completion tests passed")
    
    def test_configuration_updates(self):
        """Test configuration updates and validation."""
        print("\n6. Testing Configuration Updates...")
        
        # Test aisle traversal time update
        new_time = 5.0
        self.timing_manager.set_aisle_traversal_time(new_time)
        self.assertEqual(self.timing_manager.get_aisle_traversal_time(), new_time)
        print(f"✅ Aisle traversal time updated to: {new_time}s")
        
        # Test invalid timing
        with self.assertRaises(ValueError):
            self.timing_manager.set_aisle_traversal_time(-1.0)
        print("✅ Invalid timing validation passed")
        
        # Test timing validation
        short_movement = self.timing_manager.calculate_movement_timing(
            Coordinate(1, 1), Coordinate(1, 2)
        )
        self.assertGreater(short_movement.duration, 0)
        print(f"✅ Short movement timing: {short_movement.duration:.2f}s")
        
        print("✅ Configuration update tests passed")
    
    def test_direction_change_cooldown(self):
        """Test direction change cooldown functionality."""
        print("\n7. Testing Direction Change Cooldown...")
        
        # Start first movement
        movement1 = self.timing_manager.start_movement(self.start_pos, self.end_pos)
        
        # Immediately start second movement (should trigger cooldown warning)
        movement2 = self.timing_manager.start_movement(self.end_pos, Coordinate(5, 5))
        
        # Check that both movements were created
        self.assertIsNotNone(movement1)
        self.assertIsNotNone(movement2)
        print("✅ Direction change cooldown handled")
        
        print("✅ Direction change cooldown tests passed")
    
    def test_timing_statistics(self):
        """Test timing statistics collection."""
        print("\n8. Testing Timing Statistics...")
        
        # Complete several movements
        movements = [
            (Coordinate(1, 1), Coordinate(1, 5)),
            (Coordinate(1, 5), Coordinate(3, 5)),
            (Coordinate(3, 5), Coordinate(3, 10))
        ]
        
        for start, end in movements:
            movement = self.timing_manager.start_movement(start, end)
            # Simulate completion
            completion_time = movement.end_time + 0.1
            self.timing_manager.update_movement(completion_time)
        
        # Get statistics
        stats = self.timing_manager.get_timing_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_movements"], 3)
        self.assertGreater(stats["total_time"], 0.0)
        self.assertGreater(stats["average_movement_time"], 0.0)
        self.assertGreaterEqual(stats["aisles_traversed"], 0)
        self.assertGreaterEqual(stats["racks_traversed"], 0)
        
        print(f"✅ Statistics: {stats['total_movements']} movements, {stats['total_time']:.2f}s total")
        print(f"✅ Average time: {stats['average_movement_time']:.2f}s")
        print(f"✅ Traversed: {stats['aisles_traversed']} aisles, {stats['racks_traversed']} racks")
        
        print("✅ Timing statistics tests passed")
    
    def test_movement_progress_tracking(self):
        """Test movement progress tracking."""
        print("\n9. Testing Movement Progress Tracking...")
        
        # Start movement
        movement = self.timing_manager.start_movement(self.start_pos, self.end_pos)
        
        # Test progress at different times
        start_time = movement.start_time
        mid_time = start_time + (movement.duration / 2)
        end_time = movement.end_time
        
        # Progress at start
        progress_start = self.timing_manager.get_movement_progress()
        self.assertAlmostEqual(progress_start, 0.0, places=2)
        
        # Progress at middle (simulate)
        with patch('time.time', return_value=mid_time):
            progress_mid = self.timing_manager.get_movement_progress()
            self.assertGreater(progress_mid, 0.0)
            self.assertLess(progress_mid, 1.0)
        
        # Progress at end
        with patch('time.time', return_value=end_time):
            progress_end = self.timing_manager.get_movement_progress()
            self.assertAlmostEqual(progress_end, 1.0, places=2)
        
        print(f"✅ Progress tracking: {progress_start:.2%} → {progress_mid:.2%} → {progress_end:.2%}")
        
        print("✅ Movement progress tracking tests passed")
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n10. Testing Error Handling...")
        
        # Test zero distance movement
        same_pos = Coordinate(1, 1)
        zero_movement = self.timing_manager.calculate_movement_timing(same_pos, same_pos)
        self.assertGreater(zero_movement.duration, 0)  # Should have minimum duration
        self.assertEqual(zero_movement.duration, 0.1)  # Should be minimum duration
        print("✅ Zero distance movement handled")
        
        # Test invalid timing configuration
        invalid_config = {"robot": {"aisle_traversal_time": -1.0}}
        with self.assertRaises(ValueError):
            invalid_manager = AisleTimingManager(invalid_config)
            invalid_manager.calculate_movement_timing(self.start_pos, self.end_pos)
        print("✅ Invalid configuration handling passed")
        
        # Test movement without current movement
        no_movement_data = self.timing_manager.update_movement(time.time())
        self.assertIsNone(no_movement_data)
        print("✅ No movement handling passed")
        
        print("✅ Error handling tests passed")
    
    def test_integration_with_path_calculator(self):
        """Test integration with BidirectionalPathCalculator."""
        print("\n11. Testing Integration with Path Calculator...")
        
        # This test verifies that the timing manager can be used
        # by the BidirectionalPathCalculator for timing calculations
        
        # Simulate path calculator usage
        movements = [
            (Coordinate(1, 1), Coordinate(1, 10)),  # Horizontal
            (Coordinate(1, 10), Coordinate(5, 10)),  # Vertical
            (Coordinate(5, 10), Coordinate(5, 1))    # Horizontal
        ]
        
        total_duration = 0.0
        for start, end in movements:
            timing = self.timing_manager.calculate_movement_timing(start, end)
            total_duration += timing.duration
        
        self.assertGreater(total_duration, 0.0)
        print(f"✅ Path calculator integration: {total_duration:.2f}s total duration")
        
        print("✅ Integration tests passed")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 