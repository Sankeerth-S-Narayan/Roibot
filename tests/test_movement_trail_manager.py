"""
Comprehensive tests for MovementTrailManager.

Tests movement trail system, short-distance trail tracking, trail update mechanism,
integration with GridVisualizer, trail cleanup and management, and trail configuration options.
"""

import unittest
import time
from unittest.mock import Mock, patch

from core.layout.movement_trail_manager import (
    MovementTrailManager, 
    TrailType, 
    TrailPoint, 
    TrailConfig
)
from core.layout.coordinate import Coordinate


class TestMovementTrailManager(unittest.TestCase):
    """Test suite for MovementTrailManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        print("\n🧪 Setting up MovementTrailManager tests...")
        
        # Test configuration
        self.test_config = {
            "trail": {
                "max_trail_length": 10,
                "trail_duration": 5.0,
                "fade_rate": 0.2,
                "update_interval": 0.05,
                "show_recent_path": True,
                "show_complete_path": True,
                "show_highlights": True,
                "show_debug": True
            }
        }
        
        # Initialize trail manager
        self.trail_manager = MovementTrailManager(self.test_config)
        
        # Test coordinates
        self.test_positions = [
            Coordinate(1, 1),
            Coordinate(2, 3),
            Coordinate(3, 5),
            Coordinate(4, 7),
            Coordinate(5, 9)
        ]
        
        print("✅ Test setup complete")
    
    def test_initialization(self):
        """Test MovementTrailManager initialization."""
        print("\n1. Testing Initialization...")
        
        # Test default initialization
        default_manager = MovementTrailManager()
        self.assertIsNotNone(default_manager.config)
        self.assertEqual(default_manager.config.max_trail_length, 20)
        
        # Test config loading
        self.assertEqual(self.trail_manager.config.max_trail_length, 10)
        self.assertEqual(self.trail_manager.config.trail_duration, 5.0)
        self.assertEqual(self.trail_manager.config.fade_rate, 0.2)
        
        # Test initial state
        self.assertEqual(len(self.trail_manager.trail_points), 0)
        self.assertIsNone(self.trail_manager.current_position)
        
        print("✅ Initialization tests passed")
    
    def test_add_trail_point(self):
        """Test adding trail points."""
        print("\n2. Testing Add Trail Point...")
        
        # Add trail points
        for i, pos in enumerate(self.test_positions):
            self.trail_manager.add_trail_point(pos, TrailType.RECENT_PATH)
            self.assertEqual(len(self.trail_manager.trail_points), i + 1)
            self.assertEqual(self.trail_manager.current_position, pos)
        
        # Verify trail points
        self.assertEqual(len(self.trail_manager.trail_points), 5)
        self.assertEqual(self.trail_manager.total_points_added, 5)
        
        # Test different trail types
        highlight_pos = Coordinate(10, 10)
        self.trail_manager.add_trail_point(highlight_pos, TrailType.HIGHLIGHT)
        
        highlight_points = self.trail_manager.get_trail_points(TrailType.HIGHLIGHT)
        self.assertEqual(len(highlight_points), 1)
        self.assertEqual(highlight_points[0].position, highlight_pos)
        
        print(f"✅ Added {self.trail_manager.total_points_added} trail points")
        print("✅ Trail point addition tests passed")
    
    def test_trail_length_limiting(self):
        """Test trail length limiting functionality."""
        print("\n3. Testing Trail Length Limiting...")
        
        # Add more points than max_trail_length
        for i in range(15):
            pos = Coordinate(i + 1, i + 1)  # Ensure valid coordinates (1-25)
            self.trail_manager.add_trail_point(pos)
        
        # Verify trail is limited to max_trail_length
        self.assertEqual(len(self.trail_manager.trail_points), 10)  # max_trail_length
        self.assertEqual(self.trail_manager.total_points_added, 15)
        self.assertEqual(self.trail_manager.total_points_removed, 5)
        
        print(f"✅ Trail length limited to {self.trail_manager.config.max_trail_length}")
        print("✅ Trail length limiting tests passed")
    
    def test_trail_update_and_fading(self):
        """Test trail update and fading functionality."""
        print("\n4. Testing Trail Update and Fading...")
        
        # Add trail points
        for pos in self.test_positions:
            self.trail_manager.add_trail_point(pos)
        
        # Test initial intensities
        for point in self.trail_manager.trail_points:
            self.assertEqual(point.intensity, 1.0)
        
        # Update trail after some time
        time.sleep(0.1)  # Small delay
        update_result = self.trail_manager.update_trail()
        
        self.assertEqual(update_result["status"], "updated")
        self.assertGreater(update_result["points_updated"], 0)
        
        # Check that intensities have faded
        for point in self.trail_manager.trail_points:
            self.assertLess(point.intensity, 1.0)
        
        print(f"✅ Trail updated: {update_result['points_updated']} points faded")
        print("✅ Trail update and fading tests passed")
    
    def test_trail_cleanup(self):
        """Test trail cleanup functionality."""
        print("\n5. Testing Trail Cleanup...")
        
        # Add trail points
        for pos in self.test_positions:
            self.trail_manager.add_trail_point(pos)
        
        initial_count = len(self.trail_manager.trail_points)
        
        # Simulate time passing beyond trail duration
        future_time = time.time() + 10.0  # Beyond trail_duration
        
        # Update trail to trigger cleanup
        update_result = self.trail_manager.update_trail(future_time)
        
        # All points should be removed
        self.assertEqual(len(self.trail_manager.trail_points), 0)
        self.assertEqual(update_result["points_removed"], initial_count)
        
        print(f"✅ Trail cleanup: {update_result['points_removed']} old points removed")
        print("✅ Trail cleanup tests passed")
    
    def test_get_recent_path(self):
        """Test getting recent path functionality."""
        print("\n6. Testing Get Recent Path...")
        
        # Add trail points
        for pos in self.test_positions:
            self.trail_manager.add_trail_point(pos)
        
        # Get recent path
        recent_path = self.trail_manager.get_recent_path()
        self.assertEqual(len(recent_path), 5)
        
        # Verify coordinates
        for i, coord in enumerate(recent_path):
            self.assertEqual(coord, self.test_positions[i])
        
        # Test with max_points limit
        limited_path = self.trail_manager.get_recent_path(max_points=3)
        self.assertEqual(len(limited_path), 3)
        self.assertEqual(limited_path[-1], self.test_positions[-1])
        
        print(f"✅ Recent path: {len(recent_path)} coordinates")
        print("✅ Get recent path tests passed")
    
    def test_add_complete_path(self):
        """Test adding complete path functionality."""
        print("\n7. Testing Add Complete Path...")
        
        # Enable complete path display
        self.trail_manager.config.show_complete_path = True
        
        # Add complete path
        path_coords = [Coordinate(1, 1), Coordinate(2, 2), Coordinate(3, 3)]
        self.trail_manager.add_complete_path(path_coords)
        
        # Verify complete path points
        complete_path_points = self.trail_manager.get_trail_points(TrailType.COMPLETE_PATH)
        self.assertEqual(len(complete_path_points), 3)
        
        for i, point in enumerate(complete_path_points):
            self.assertEqual(point.position, path_coords[i])
            self.assertEqual(point.intensity, 0.5)  # Lower intensity for planned path
        
        print(f"✅ Complete path added: {len(complete_path_points)} points")
        print("✅ Add complete path tests passed")
    
    def test_add_highlights_and_debug(self):
        """Test adding highlights and debug points."""
        print("\n8. Testing Add Highlights and Debug...")
        
        # Add highlight
        highlight_pos = Coordinate(5, 5)
        self.trail_manager.add_highlight(highlight_pos, intensity=0.8)
        
        highlight_points = self.trail_manager.get_trail_points(TrailType.HIGHLIGHT)
        self.assertEqual(len(highlight_points), 1)
        self.assertEqual(highlight_points[0].position, highlight_pos)
        self.assertEqual(highlight_points[0].intensity, 0.8)
        
        # Add debug point
        debug_pos = Coordinate(10, 10)
        self.trail_manager.add_debug_point(debug_pos)
        
        debug_points = self.trail_manager.get_trail_points(TrailType.DEBUG)
        self.assertEqual(len(debug_points), 1)
        self.assertEqual(debug_points[0].position, debug_pos)
        self.assertEqual(debug_points[0].intensity, 0.8)
        
        print(f"✅ Highlights: {len(highlight_points)}, Debug: {len(debug_points)}")
        print("✅ Add highlights and debug tests passed")
    
    def test_clear_trail(self):
        """Test trail clearing functionality."""
        print("\n9. Testing Clear Trail...")
        
        # Add different types of trail points
        self.trail_manager.add_trail_point(Coordinate(1, 1), TrailType.RECENT_PATH)
        self.trail_manager.add_trail_point(Coordinate(2, 2), TrailType.HIGHLIGHT)
        self.trail_manager.add_trail_point(Coordinate(3, 3), TrailType.DEBUG)
        
        initial_count = len(self.trail_manager.trail_points)
        
        # Clear specific type
        removed_count = self.trail_manager.clear_trail(TrailType.HIGHLIGHT)
        self.assertEqual(removed_count, 1)
        self.assertEqual(len(self.trail_manager.trail_points), initial_count - 1)
        
        # Clear all
        removed_count = self.trail_manager.clear_trail()
        self.assertEqual(removed_count, initial_count - 1)
        self.assertEqual(len(self.trail_manager.trail_points), 0)
        
        print(f"✅ Trail cleared: {removed_count} points removed")
        print("✅ Clear trail tests passed")
    
    def test_trail_statistics(self):
        """Test trail statistics collection."""
        print("\n10. Testing Trail Statistics...")
        
        # Add various trail points
        self.trail_manager.add_trail_point(Coordinate(1, 1), TrailType.RECENT_PATH)
        self.trail_manager.add_trail_point(Coordinate(2, 2), TrailType.HIGHLIGHT)
        self.trail_manager.add_trail_point(Coordinate(3, 3), TrailType.DEBUG)
        
        # Get statistics
        stats = self.trail_manager.get_trail_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_points"], 3)
        self.assertEqual(stats["total_points_added"], 3)
        self.assertGreaterEqual(stats["trail_age"], 0)  # Allow 0 for very fast tests
        self.assertIsNotNone(stats["current_position"])
        
        # Verify type counts
        type_counts = stats["type_counts"]
        self.assertEqual(type_counts["recent_path"], 1)
        self.assertEqual(type_counts["highlight"], 1)
        self.assertEqual(type_counts["debug"], 1)
        
        print(f"✅ Statistics: {stats['total_points']} points, {stats['total_points_added']} added")
        print("✅ Trail statistics tests passed")
    
    def test_export_for_visualization(self):
        """Test trail export for visualization."""
        print("\n11. Testing Export for Visualization...")
        
        # Add various trail points
        self.trail_manager.add_trail_point(Coordinate(1, 1), TrailType.RECENT_PATH)
        self.trail_manager.add_trail_point(Coordinate(2, 2), TrailType.HIGHLIGHT)
        self.trail_manager.add_trail_point(Coordinate(3, 3), TrailType.DEBUG)
        
        # Export trail data
        trail_data = self.trail_manager.export_trail_for_visualization()
        
        # Verify export structure
        self.assertIn("recent_path", trail_data)
        self.assertIn("complete_path", trail_data)
        self.assertIn("highlights", trail_data)
        self.assertIn("debug_points", trail_data)
        
        # Verify data content
        self.assertEqual(len(trail_data["recent_path"]), 1)
        self.assertEqual(len(trail_data["highlights"]), 1)
        self.assertEqual(len(trail_data["debug_points"]), 1)
        
        # Verify coordinate format
        for point_data in trail_data["recent_path"]:
            self.assertIn("position", point_data)
            self.assertIn("intensity", point_data)
            self.assertIn("age", point_data)
        
        print(f"✅ Export: {len(trail_data['recent_path'])} recent, {len(trail_data['highlights'])} highlights")
        print("✅ Export for visualization tests passed")
    
    def test_configuration_updates(self):
        """Test configuration updates and validation."""
        print("\n12. Testing Configuration Updates...")
        
        # Test updating configuration
        new_config = {
            "trail": {
                "max_trail_length": 5,
                "trail_duration": 3.0,
                "fade_rate": 0.3
            }
        }
        
        self.trail_manager.load_config(new_config)
        
        # Verify configuration updated
        self.assertEqual(self.trail_manager.config.max_trail_length, 5)
        self.assertEqual(self.trail_manager.config.trail_duration, 3.0)
        self.assertEqual(self.trail_manager.config.fade_rate, 0.3)
        
        print("✅ Configuration updated successfully")
        
        # Test with new configuration
        for i in range(10):
            self.trail_manager.add_trail_point(Coordinate(i + 1, i + 1))  # Ensure valid coordinates
        
        # Should be limited to new max_trail_length
        self.assertEqual(len(self.trail_manager.trail_points), 5)
        
        print("✅ Configuration update tests passed")
    
    def test_integration_with_grid_visualizer(self):
        """Test integration with GridVisualizer."""
        print("\n13. Testing GridVisualizer Integration...")
        
        # Add trail points
        for pos in self.test_positions:
            self.trail_manager.add_trail_point(pos)
        
        # Export for visualization
        trail_data = self.trail_manager.export_trail_for_visualization()
        
        # Simulate GridVisualizer integration
        # This would typically be used by GridVisualizer to display trails
        recent_path_coords = [point["position"] for point in trail_data["recent_path"]]
        highlight_coords = [point["position"] for point in trail_data["highlights"]]
        
        self.assertEqual(len(recent_path_coords), 5)
        self.assertEqual(len(highlight_coords), 0)  # No highlights added in this test
        
        print(f"✅ GridVisualizer integration: {len(recent_path_coords)} recent path coordinates")
        print("✅ GridVisualizer integration tests passed")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 