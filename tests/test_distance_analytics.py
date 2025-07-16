"""
Test suite for real-time distance analytics and event system integration.

Tests the enhanced distance tracking, order-specific metrics, and event integration.
"""

import pytest
from unittest.mock import Mock, patch
import time

from core.engine import SimulationEngine, RobotState
from core.layout.coordinate import Coordinate
from core.events import EventType


class TestDistanceAnalytics:
    """Test real-time distance tracking and analytics."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        engine = SimulationEngine()
        # Use a real Robot instance instead of Mock
        from core.engine import Robot
        engine.robot = Robot(Coordinate(1, 1))
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(2, 1), Coordinate(3, 1)]
        engine.robot.path_index = 0
        engine.robot.total_distance = 0.0
        
        # Mock distance tracker
        engine.distance_tracker = Mock()
        engine.distance_tracker.calculate_distance.return_value = 1.0
        
        # Mock trail manager
        engine.trail_manager = Mock()
        
        # Mock event system
        engine.event_system = Mock()
        
        # Setup test orders
        engine.orders = [
            {"id": "order_1", "items": ["item_A", "item_B"]},
            {"id": "order_2", "items": ["item_C"]}
        ]
        engine.current_order_index = 0
        engine.simulation_time = 0.0
        
        return engine
    
    def test_distance_tracking_initialization(self, engine):
        """Test that distance tracking is properly initialized."""
        assert "order_distances" in engine.performance_metrics
        assert "current_order_distance" in engine.performance_metrics
        assert engine.performance_metrics["order_distances"] == {}
        assert engine.performance_metrics["current_order_distance"] == 0.0
    
    def test_distance_accumulation_during_movement(self, engine):
        """Test that distance is accumulated during robot movement."""
        # Mock robot movement
        old_position = Coordinate(1, 1)
        new_position = Coordinate(2, 1)
        engine.robot.position = old_position
        
        # Call movement update
        engine._update_robot_movement(0.1)
        
        # Check distance tracking
        assert engine.performance_metrics["total_distance"] == 1.0
        assert engine.performance_metrics["order_distances"]["order_1"] == 1.0
        assert engine.performance_metrics["current_order_distance"] == 1.0
    
    def test_order_specific_distance_tracking(self, engine):
        """Test that distance is tracked separately for each order."""
        # Move robot and accumulate distance for first order
        engine._update_robot_movement(0.1)  # First movement
        engine._update_robot_movement(0.1)  # Second movement
        
        # Check first order distance
        assert engine.performance_metrics["order_distances"]["order_1"] == 2.0
        assert engine.performance_metrics["current_order_distance"] == 2.0
        
        # Complete first order and move to second
        engine.current_order_index = 1
        engine.robot.position = Coordinate(1, 1)
        engine.robot.current_path = [Coordinate(5, 5)]
        engine.robot.path_index = 0
        
        # Move robot for second order
        engine._update_robot_movement(0.1)
        
        # Check second order distance
        assert engine.performance_metrics["order_distances"]["order_2"] == 1.0
        assert engine.performance_metrics["current_order_distance"] == 1.0
        
        # First order distance should remain unchanged
        assert engine.performance_metrics["order_distances"]["order_1"] == 2.0
    
    def test_order_completion_with_distance(self, engine):
        """Test that order completion includes distance information."""
        # Mock warehouse layout to return valid positions
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Mock path calculator to return valid path
        from core.layout.bidirectional_path_calculator import CompletePath, PathSegment, Direction
        mock_segments = [PathSegment(
            start=Coordinate(1, 1),
            end=Coordinate(5, 5),
            direction=Direction.FORWARD,
            duration=7.0,
            aisle_number=1,
            is_horizontal=True
        )]
        mock_complete_path = CompletePath(
            segments=mock_segments,
            total_distance=4.0,
            total_duration=7.0,
            direction_changes=0,
            items_to_collect=[Coordinate(5, 5)],
            optimized_order=[Coordinate(5, 5)]
        )
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=mock_complete_path)
        
        # Accumulate some distance
        engine._update_robot_movement(0.1)
        engine._update_robot_movement(0.1)
        
        # Mock robot state for order completion
        engine.robot.collected_items = ["item_A", "item_B"]
        
        # Complete order
        engine._complete_current_order()
        
        # Check that order completion event was emitted with distance
        engine.event_system.emit.assert_called()
        call_args = engine.event_system.emit.call_args
        assert call_args[0][0] == EventType.ORDER_COMPLETED
        
        event_data = call_args[0][1]
        assert "order_distance" in event_data
        assert event_data["order_distance"] == 2.0
    
    def test_simulation_state_includes_distance(self, engine):
        """Test that simulation state includes distance information."""
        # Accumulate some distance
        engine._update_robot_movement(0.1)
        
        # Get simulation state
        state = engine.get_simulation_state()
        
        # Check distance information is included
        assert "current_order_distance" in state
        assert "order_distances" in state
        assert state["current_order_distance"] == 1.0
        assert state["order_distances"]["order_1"] == 1.0
    
    def test_distance_reset_on_order_completion(self, engine):
        """Test that current order distance resets when order is completed."""
        # Mock warehouse layout to return valid positions
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Mock path calculator to return valid path
        from core.layout.bidirectional_path_calculator import CompletePath, PathSegment, Direction
        mock_segments = [PathSegment(
            start=Coordinate(1, 1),
            end=Coordinate(5, 5),
            direction=Direction.FORWARD,
            duration=7.0,
            aisle_number=1,
            is_horizontal=True
        )]
        mock_complete_path = CompletePath(
            segments=mock_segments,
            total_distance=4.0,
            total_duration=7.0,
            direction_changes=0,
            items_to_collect=[Coordinate(5, 5)],
            optimized_order=[Coordinate(5, 5)]
        )
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=mock_complete_path)
        
        # Accumulate distance for first order
        engine._update_robot_movement(0.1)
        assert engine.performance_metrics["current_order_distance"] == 1.0
        
        # Complete first order
        engine.robot.collected_items = ["item_A", "item_B"]
        engine._complete_current_order()
        
        # Check that current order distance is reset
        assert engine.performance_metrics["current_order_distance"] == 0.0
        
        # Check that order distances are preserved
        assert engine.performance_metrics["order_distances"]["order_1"] == 1.0
    
    def test_distance_tracking_with_no_orders(self, engine):
        """Test distance tracking when no orders are present."""
        engine.orders = []
        engine.current_order_index = 0
        
        # Movement should not cause errors
        engine._update_robot_movement(0.1)
        
        # Distance should still be tracked globally
        assert engine.performance_metrics["total_distance"] == 1.0
        assert engine.performance_metrics["current_order_distance"] == 0.0
    
    def test_distance_tracking_with_invalid_order_index(self, engine):
        """Test distance tracking with invalid order index."""
        engine.current_order_index = 999  # Invalid index
        
        # Movement should not cause errors
        engine._update_robot_movement(0.1)
        
        # Distance should still be tracked globally
        assert engine.performance_metrics["total_distance"] == 1.0
        assert engine.performance_metrics["current_order_distance"] == 0.0
    
    def test_order_distance_with_custom_order_ids(self, engine):
        """Test distance tracking with custom order IDs."""
        engine.orders = [
            {"id": "custom_order_1", "items": ["item_A"]},
            {"id": "custom_order_2", "items": ["item_B"]}
        ]
        
        # Move robot
        engine._update_robot_movement(0.1)
        
        # Check custom order ID is used
        assert "custom_order_1" in engine.performance_metrics["order_distances"]
        assert engine.performance_metrics["order_distances"]["custom_order_1"] == 1.0
    
    def test_order_distance_without_order_id(self, engine):
        """Test distance tracking when order has no ID."""
        engine.orders = [
            {"items": ["item_A"]},  # No ID
            {"items": ["item_B"]}
        ]
        
        # Move robot
        engine._update_robot_movement(0.1)
        
        # Check default order ID is used
        assert "order_0" in engine.performance_metrics["order_distances"]
        assert engine.performance_metrics["order_distances"]["order_0"] == 1.0


class TestEventIntegration:
    """Test event system integration with distance tracking."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        engine = SimulationEngine()
        # Use a real Robot instance instead of Mock
        from core.engine import Robot
        engine.robot = Robot(Coordinate(1, 1))
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(2, 1)]
        engine.robot.path_index = 0
        
        # Mock components
        engine.distance_tracker = Mock()
        engine.distance_tracker.calculate_distance.return_value = 1.0
        engine.trail_manager = Mock()
        engine.event_system = Mock()
        
        # Setup test order
        engine.orders = [{"id": "test_order", "items": ["item_A"]}]
        engine.current_order_index = 0
        engine.simulation_time = 0.0
        
        return engine
    
    def test_movement_event_includes_distance(self, engine):
        """Test that movement events include distance information."""
        old_position = Coordinate(1, 1)
        engine.robot.position = old_position
        
        # Trigger movement
        engine._update_robot_movement(0.1)
        
        # Check movement event was emitted with distance
        engine.event_system.emit.assert_called()
        call_args = engine.event_system.emit.call_args
        assert call_args[0][0] == EventType.ROBOT_MOVED
        
        event_data = call_args[0][1]
        assert "distance" in event_data
        assert event_data["distance"] == 1.0
    
    def test_order_completion_event_includes_distance(self, engine):
        """Test that order completion events include distance information."""
        # Add multiple orders to prevent simulation completion
        engine.orders = [
            {"id": "test_order", "items": ["item_A"]},
            {"id": "test_order_2", "items": ["item_B"]}
        ]
        
        # Mock warehouse layout to return valid positions
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Mock path calculator to return valid path
        from core.layout.bidirectional_path_calculator import CompletePath, PathSegment, Direction
        mock_segments = [PathSegment(
            start=Coordinate(1, 1),
            end=Coordinate(5, 5),
            direction=Direction.FORWARD,
            duration=7.0,
            aisle_number=1,
            is_horizontal=True
        )]
        mock_complete_path = CompletePath(
            segments=mock_segments,
            total_distance=4.0,
            total_duration=7.0,
            direction_changes=0,
            items_to_collect=[Coordinate(5, 5)],
            optimized_order=[Coordinate(5, 5)]
        )
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=mock_complete_path)
        
        # Accumulate distance
        engine._update_robot_movement(0.1)
        
        # Complete order
        engine.robot.collected_items = ["item_A"]
        engine._complete_current_order()
        
        # Check order completion event includes distance
        engine.event_system.emit.assert_called()
        call_args = engine.event_system.emit.call_args
        assert call_args[0][0] == EventType.ORDER_COMPLETED
        
        event_data = call_args[0][1]
        assert "order_distance" in event_data
        assert event_data["order_distance"] == 1.0
    
    def test_event_throttling_performance(self, engine):
        """Test that event emission doesn't impact performance significantly."""
        import time
        
        # Reset robot path to allow multiple movements
        engine.robot.current_path = [Coordinate(2, 1), Coordinate(3, 1), Coordinate(4, 1)]
        engine.robot.path_index = 0
        
        # Measure time for multiple movement updates
        start_time = time.time()
        
        for _ in range(100):
            engine._update_robot_movement(0.1)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        assert execution_time < 1.0
        
        # Check that events were emitted (at least some)
        assert engine.event_system.emit.call_count > 0


class TestDebuggingAndAnalytics:
    """Test debugging and analytics functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        engine = SimulationEngine()
        # Use a real Robot instance instead of Mock
        from core.engine import Robot
        engine.robot = Robot(Coordinate(1, 1))
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(2, 1)]
        engine.robot.path_index = 0
        
        # Mock components
        engine.distance_tracker = Mock()
        engine.distance_tracker.calculate_distance.return_value = 1.0
        engine.trail_manager = Mock()
        
        # Mock event system with proper statistics
        engine.event_system = Mock()
        engine.event_system.get_statistics.return_value = {
            "queue_sizes": {"total": 0},
            "success_rate": 1.0
        }
        engine.event_system.processed_events = 10
        engine.event_system.event_count = 15
        engine.event_system.failed_events = 0
        
        # Setup test order
        engine.orders = [{"id": "debug_order", "items": ["item_A"]}]
        engine.current_order_index = 0
        engine.simulation_time = 0.0
        
        # Mock state
        engine.state = Mock()
        engine.state.frame_count = 100
        engine.state.simulation_time = 10.0
        engine.state.current_fps = 60.0
        engine.state.simulation_speed = 1.0
        engine.state.get_active_components.return_value = ["engine", "robot"]
        
        return engine
    
    def test_debug_stats_include_distance(self, engine):
        """Test that debug stats include distance information."""
        # Accumulate some distance
        engine._update_robot_movement(0.1)
        
        # Mock print function to capture output
        with patch('builtins.print') as mock_print:
            # Call the sync version of debug stats
            engine._print_debug_stats_sync()
            
            # Check that distance information is printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            distance_line = None
            for call in print_calls:
                if "Distance:" in call:
                    distance_line = call
                    break
            
            assert distance_line is not None
            assert "debug_order" in distance_line
            assert "1.00" in distance_line  # Current order distance
    
    def test_analytics_accuracy(self, engine):
        """Test that analytics provide accurate distance measurements."""
        # Reset robot path to allow multiple movements
        engine.robot.current_path = [Coordinate(2, 1), Coordinate(3, 1), Coordinate(4, 1), Coordinate(5, 1)]
        engine.robot.path_index = 0
        
        # Perform multiple movements
        movements = [1.0, 2.0, 1.5, 0.5]
        total_expected = sum(movements)
        
        for distance in movements:
            engine.distance_tracker.calculate_distance.return_value = distance
            engine._update_robot_movement(0.1)
        
        # Check accuracy
        assert engine.performance_metrics["total_distance"] == total_expected
        assert engine.performance_metrics["order_distances"]["debug_order"] == total_expected
        assert engine.performance_metrics["current_order_distance"] == total_expected
    
    def test_real_time_analytics_performance(self, engine):
        """Test that real-time analytics don't impact performance."""
        import time
        
        # Reset robot path to allow multiple movements
        engine.robot.current_path = [Coordinate(2, 1)] * 1000  # 1000 movement points
        engine.robot.path_index = 0
        
        # Measure performance with analytics
        start_time = time.time()
        
        for _ in range(1000):
            engine._update_robot_movement(0.01)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        assert execution_time < 0.1  # 100ms for 1000 operations
        
        # Verify analytics are still accurate
        assert engine.performance_metrics["total_distance"] == 1000.0
        assert engine.performance_metrics["order_distances"]["debug_order"] == 1000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 