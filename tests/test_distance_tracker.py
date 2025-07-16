"""
Tests for distance tracking and KPI integration.

Tests the DistanceTracker class functionality including distance calculations,
event tracking, KPI metrics, and data persistence.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

from core.layout.distance_tracker import DistanceTracker, DistanceEvent, DistanceEventType
from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import Direction


class TestDistanceTracker(unittest.TestCase):
    """Test cases for DistanceTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = DistanceTracker()
        self.coord1 = Coordinate(1, 1)
        self.coord2 = Coordinate(5, 5)
        self.coord3 = Coordinate(10, 10)
        self.coord4 = Coordinate(15, 15)
    
    def test_initialization(self):
        """Test DistanceTracker initialization."""
        self.assertEqual(self.tracker.total_distance, 0.0)
        self.assertEqual(self.tracker.order_distances, {})
        self.assertEqual(self.tracker.robot_distances, {})
        self.assertEqual(len(self.tracker.events), 0)
    
    def test_calculate_distance(self):
        """Test basic distance calculation."""
        distance = self.tracker.calculate_distance(self.coord1, self.coord2)
        expected = abs(1 - 5) + abs(1 - 5)  # 4 + 4 = 8
        self.assertEqual(distance, expected)
    
    def test_calculate_distance_same_coordinate(self):
        """Test distance calculation for same coordinate."""
        distance = self.tracker.calculate_distance(self.coord1, self.coord1)
        self.assertEqual(distance, 0.0)
    
    def test_calculate_optimal_path_distance(self):
        """Test optimal path distance calculation."""
        distance = self.tracker.calculate_optimal_path_distance(
            self.coord1, self.coord2, Direction.FORWARD
        )
        # Should be positive distance
        self.assertGreater(distance, 0)
    
    def test_track_robot_move(self):
        """Test robot movement tracking."""
        robot_id = "robot_001"
        
        # Track a move
        distance = self.tracker.track_robot_move(
            robot_id, self.coord1, self.coord2, Direction.FORWARD
        )
        
        # Verify tracking
        self.assertGreater(self.tracker.total_distance, 0)
        self.assertEqual(self.tracker.get_robot_distance(robot_id), distance)
        self.assertEqual(self.tracker.get_current_position(robot_id), self.coord2)
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.ROBOT_MOVE)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].robot_id, robot_id)
        self.assertEqual(events[0].from_coord, self.coord1)
        self.assertEqual(events[0].to_coord, self.coord2)
    
    def test_track_robot_move_invalid_coordinates(self):
        """Test robot movement with invalid coordinates."""
        # Create a coordinate that's just outside the valid range
        # We need to bypass the Coordinate validation for this test
        class InvalidCoordinate:
            def __init__(self, aisle, rack):
                self.aisle = aisle
                self.rack = rack
            
            def __str__(self):
                return f"({self.aisle}, {self.rack})"
        
        invalid_coord = InvalidCoordinate(30, 30)  # Outside warehouse bounds
        
        with self.assertRaises(ValueError):
            self.tracker.track_robot_move("robot_001", self.coord1, invalid_coord)
    
    def test_track_order_start(self):
        """Test order start tracking."""
        order_id = "order_001"
        robot_id = "robot_001"
        
        self.tracker.track_order_start(order_id, robot_id, self.coord1)
        
        # Verify order distance initialized
        self.assertEqual(self.tracker.get_order_distance(order_id), 0.0)
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.ORDER_START)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].order_id, order_id)
        self.assertEqual(events[0].robot_id, robot_id)
    
    def test_track_pickup_item(self):
        """Test item pickup tracking."""
        order_id = "order_001"
        robot_id = "robot_001"
        
        # Start order
        self.tracker.track_order_start(order_id, robot_id, self.coord1)
        
        # Track pickup
        distance = self.tracker.track_pickup_item(
            order_id, robot_id, self.coord1, self.coord2, Direction.FORWARD
        )
        
        # Verify order distance updated
        self.assertEqual(self.tracker.get_order_distance(order_id), distance)
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.PICKUP_ITEM)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].order_id, order_id)
        self.assertEqual(events[0].robot_id, robot_id)
    
    def test_track_deliver_to_packout(self):
        """Test delivery to packout tracking."""
        order_id = "order_001"
        robot_id = "robot_001"
        
        # Start order
        self.tracker.track_order_start(order_id, robot_id, self.coord1)
        
        # Track delivery to packout
        distance = self.tracker.track_deliver_to_packout(
            order_id, robot_id, self.coord2, Direction.FORWARD
        )
        
        # Verify order distance updated
        self.assertEqual(self.tracker.get_order_distance(order_id), distance)
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.DELIVER_TO_PACKOUT)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].order_id, order_id)
        self.assertEqual(events[0].robot_id, robot_id)
    
    def test_track_return_to_start(self):
        """Test return to start tracking."""
        robot_id = "robot_001"
        start_coord = self.coord1
        
        # Track return to start
        distance = self.tracker.track_return_to_start(
            robot_id, self.coord2, start_coord, Direction.FORWARD
        )
        
        # Verify robot distance updated
        self.assertEqual(self.tracker.get_robot_distance(robot_id), distance)
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.RETURN_TO_START)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].robot_id, robot_id)
    
    def test_track_order_complete(self):
        """Test order completion tracking."""
        order_id = "order_001"
        robot_id = "robot_001"
        
        # Start order and add some distance
        self.tracker.track_order_start(order_id, robot_id, self.coord1)
        self.tracker.track_pickup_item(order_id, robot_id, self.coord1, self.coord2)
        
        # Track order completion
        total_distance = self.tracker.track_order_complete(order_id, robot_id, self.coord2)
        
        # Verify total order distance
        self.assertEqual(total_distance, self.tracker.get_order_distance(order_id))
        
        # Verify event was created
        events = self.tracker.get_events_by_type(DistanceEventType.ORDER_COMPLETE)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].order_id, order_id)
        self.assertEqual(events[0].robot_id, robot_id)
    
    def test_get_kpi_metrics_empty(self):
        """Test KPI metrics with no data."""
        metrics = self.tracker.get_kpi_metrics()
        
        expected = {
            "total_distance": 0.0,
            "average_order_distance": 0.0,
            "total_orders": 0,
            "average_robot_distance": 0.0,
            "total_robots": 0,
            "efficiency_score": 0.0
        }
        
        self.assertEqual(metrics, expected)
    
    def test_get_kpi_metrics_with_data(self):
        """Test KPI metrics with tracking data."""
        # Add some tracking data
        self.tracker.track_order_start("order_001", "robot_001", self.coord1)
        self.tracker.track_pickup_item("order_001", "robot_001", self.coord1, self.coord2)
        self.tracker.track_order_complete("order_001", "robot_001", self.coord2)
        
        metrics = self.tracker.get_kpi_metrics()
        
        # Verify metrics are calculated
        self.assertGreater(metrics["total_distance"], 0)
        self.assertEqual(metrics["total_orders"], 1)
        self.assertEqual(metrics["total_robots"], 1)
        self.assertGreater(metrics["efficiency_score"], 0)
    
    def test_get_events_by_order(self):
        """Test filtering events by order."""
        order_id = "order_001"
        robot_id = "robot_001"
        
        # Create events for this order
        self.tracker.track_order_start(order_id, robot_id, self.coord1)
        self.tracker.track_pickup_item(order_id, robot_id, self.coord1, self.coord2)
        self.tracker.track_order_complete(order_id, robot_id, self.coord2)
        
        # Create events for different order
        self.tracker.track_order_start("order_002", robot_id, self.coord3)
        
        # Get events for order_001
        events = self.tracker.get_events_by_order(order_id)
        
        # Should have 3 events for order_001
        self.assertEqual(len(events), 3)
        for event in events:
            self.assertEqual(event.order_id, order_id)
    
    def test_get_events_by_robot(self):
        """Test filtering events by robot."""
        robot_id = "robot_001"
        
        # Create events for this robot
        self.tracker.track_robot_move(robot_id, self.coord1, self.coord2)
        self.tracker.track_return_to_start(robot_id, self.coord2, self.coord1)
        
        # Create events for different robot
        self.tracker.track_robot_move("robot_002", self.coord3, self.coord4)
        
        # Get events for robot_001
        events = self.tracker.get_events_by_robot(robot_id)
        
        # Should have 3 events for robot_001 (2 robot_moves + 1 return_to_start)
        self.assertEqual(len(events), 3)
        for event in events:
            self.assertEqual(event.robot_id, robot_id)
    
    def test_reset(self):
        """Test reset functionality."""
        # Add some data
        self.tracker.track_robot_move("robot_001", self.coord1, self.coord2)
        self.tracker.track_order_start("order_001", "robot_001", self.coord1)
        
        # Verify data exists
        self.assertGreater(self.tracker.total_distance, 0)
        self.assertGreater(len(self.tracker.events), 0)
        
        # Reset
        self.tracker.reset()
        
        # Verify all data cleared
        self.assertEqual(self.tracker.total_distance, 0.0)
        self.assertEqual(self.tracker.order_distances, {})
        self.assertEqual(self.tracker.robot_distances, {})
        self.assertEqual(len(self.tracker.events), 0)
    
    def test_export_data(self):
        """Test data export functionality."""
        # Add some data
        self.tracker.track_order_start("order_001", "robot_001", self.coord1)
        self.tracker.track_pickup_item("order_001", "robot_001", self.coord1, self.coord2)
        
        # Export data
        data = self.tracker.export_data()
        
        # Verify export structure
        self.assertIn("total_distance", data)
        self.assertIn("order_distances", data)
        self.assertIn("robot_distances", data)
        self.assertIn("events", data)
        self.assertIn("current_positions", data)
        
        # Verify data integrity
        self.assertGreater(data["total_distance"], 0)
        self.assertIn("order_001", data["order_distances"])
        self.assertIn("robot_001", data["robot_distances"])
        self.assertGreater(len(data["events"]), 0)
    
    def test_import_data(self):
        """Test data import functionality."""
        # Create test data
        test_data = {
            "total_distance": 10.0,
            "order_distances": {"order_001": 5.0},
            "robot_distances": {"robot_001": 10.0},
            "events": [
                {
                    "event_type": "robot_move",
                    "from_coord": (1, 1),
                    "to_coord": (5, 5),
                    "distance": 8.0,
                    "timestamp": "2024-01-01T12:00:00",
                    "order_id": None,
                    "robot_id": "robot_001",
                    "metadata": {}
                }
            ],
            "current_positions": {"robot_001": (5, 5)}
        }
        
        # Import data
        self.tracker.import_data(test_data)
        
        # Verify data imported correctly
        self.assertEqual(self.tracker.total_distance, 10.0)
        self.assertEqual(self.tracker.get_order_distance("order_001"), 5.0)
        self.assertEqual(self.tracker.get_robot_distance("robot_001"), 10.0)
        self.assertEqual(len(self.tracker.events), 1)
        self.assertEqual(self.tracker.get_current_position("robot_001"), Coordinate(5, 5))
    
    def test_complete_order_workflow(self):
        """Test complete order workflow with distance tracking."""
        order_id = "order_001"
        robot_id = "robot_001"
        start_coord = self.coord1
        item_coord = self.coord2
        
        # Complete order workflow
        self.tracker.track_order_start(order_id, robot_id, start_coord)
        
        # Move to item location
        pickup_distance = self.tracker.track_pickup_item(
            order_id, robot_id, start_coord, item_coord
        )
        
        # Deliver to packout
        delivery_distance = self.tracker.track_deliver_to_packout(
            order_id, robot_id, item_coord
        )
        
        # Return to start
        return_distance = self.tracker.track_return_to_start(
            robot_id, self.tracker.get_current_position(robot_id), start_coord
        )
        
        # Complete order
        total_order_distance = self.tracker.track_order_complete(
            order_id, robot_id, start_coord
        )
        
        # Verify distances
        expected_order_distance = pickup_distance + delivery_distance
        self.assertEqual(self.tracker.get_order_distance(order_id), expected_order_distance)
        
        # Verify total robot distance includes return
        expected_robot_distance = pickup_distance + delivery_distance + return_distance
        self.assertEqual(self.tracker.get_robot_distance(robot_id), expected_robot_distance)
        
        # Verify KPI metrics
        metrics = self.tracker.get_kpi_metrics()
        self.assertEqual(metrics["total_orders"], 1)
        self.assertEqual(metrics["total_robots"], 1)
        self.assertGreater(metrics["efficiency_score"], 0)


if __name__ == "__main__":
    unittest.main() 