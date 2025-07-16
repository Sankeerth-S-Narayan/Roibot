#!/usr/bin/env python3
"""
Integration test for Robot Entity components.
Tests that all robot components work together properly.
"""

import sys
import time
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.robot import Robot, RobotState
from core.layout.coordinate import Coordinate

"""
Tests for Task 6: Robot State Integration & Movement Enhancement

This module tests the integration of bidirectional navigation components
with the robot's movement system in the SimulationEngine.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from core.engine import SimulationEngine, Robot, RobotState
from core.layout.coordinate import Coordinate
from core.layout.bidirectional_path_calculator import BidirectionalPathCalculator
from core.layout.movement_trail_manager import MovementTrailManager
from core.layout.aisle_timing_manager import AisleTimingManager
from core.events import EventType


class TestRobotStateIntegration:
    """Test robot state integration with bidirectional navigation."""
    
    @pytest.fixture
    def engine(self):
        """Create a simulation engine for testing."""
        engine = SimulationEngine()
        # Mock the async components to avoid initialization issues
        engine.state = Mock()
        engine.event_system = Mock()
        engine.timing_manager = Mock()
        engine.performance_benchmark = Mock()
        engine.performance_optimizer = Mock()
        return engine
    
    @pytest.fixture
    def mock_order(self):
        """Create a mock order for testing."""
        return {
            "id": "test_order_1",
            "items": ["item_A", "item_B", "item_C"],
            "priority": "high"
        }
    
    @pytest.fixture
    def mock_item_positions(self):
        """Create mock item positions."""
        return {
            "item_A": Coordinate(2, 3),
            "item_B": Coordinate(5, 7),
            "item_C": Coordinate(8, 1)
        }

    def test_robot_initialization(self, engine):
        """Test robot initialization with enhanced navigation properties."""
        robot = engine.robot
        
        assert robot.position == Coordinate(1, 1)
        assert robot.state == RobotState.IDLE
        assert robot.current_path == []
        assert robot.path_index == 0
        assert robot.target_item is None
        assert robot.collected_items == []
        assert robot.total_distance == 0.0
        assert robot.current_direction is None
        assert robot.path_execution_state == "ready"
        assert robot.trail_points == []
        assert robot.direction_change_cooldown == 0.5

    def test_add_order(self, engine, mock_order):
        """Test adding orders to the simulation."""
        initial_count = len(engine.orders)
        
        engine.add_order(mock_order)
        
        assert len(engine.orders) == initial_count + 1
        assert engine.orders[-1] == mock_order

    def test_start_simulation_no_orders(self, engine):
        """Test starting simulation with no orders."""
        engine.start_simulation()
        
        # Should not start if no orders
        assert not engine.is_running
        assert engine.robot.state == RobotState.IDLE

    @patch.object(BidirectionalPathCalculator, 'calculate_complete_path_for_items')
    def test_start_simulation_with_orders(self, mock_calc_path, engine, mock_order, mock_item_positions):
        """Test starting simulation with orders."""
        # Setup mocks
        engine.add_order(mock_order)
        engine.warehouse_layout.get_item_position = Mock(side_effect=lambda item: mock_item_positions.get(item))
        
        # Mock path calculation
        from core.layout.bidirectional_path_calculator import CompletePath, PathSegment
        from core.layout.aisle_timing_manager import MovementType
        
        # Create mock segments
        mock_segments = [
            PathSegment(
                start=Coordinate(1, 1),
                end=Coordinate(2, 3),
                direction=None,
                duration=1.0,
                aisle_number=2,
                is_horizontal=False
            ),
            PathSegment(
                start=Coordinate(2, 3),
                end=Coordinate(5, 7),
                direction=None,
                duration=2.0,
                aisle_number=5,
                is_horizontal=False
            ),
            PathSegment(
                start=Coordinate(5, 7),
                end=Coordinate(8, 1),
                direction=None,
                duration=3.0,
                aisle_number=8,
                is_horizontal=False
            )
        ]
        
        mock_complete_path = CompletePath(
            segments=mock_segments,
            total_distance=15.5,
            total_duration=10.0,
            direction_changes=3,
            items_to_collect=[Coordinate(2, 3), Coordinate(5, 7), Coordinate(8, 1)],
            optimized_order=[Coordinate(2, 3), Coordinate(5, 7), Coordinate(8, 1)]
        )
        mock_calc_path.return_value = mock_complete_path
        
        engine.start_simulation()
        
        assert engine.is_running
        assert engine.robot.state == RobotState.MOVING
        assert engine.current_order_index == 0
        assert engine.simulation_time == 0.0
        assert engine.robot.path_index == 0
        assert engine.robot.path_execution_state == "executing"
        assert engine.robot.target_item == "item_A"

    def test_determine_movement_type(self, engine):
        """Test movement type determination."""
        # Horizontal movement
        assert engine._determine_movement_type(Coordinate(1, 1), Coordinate(5, 1)) == "horizontal"
        
        # Vertical movement
        assert engine._determine_movement_type(Coordinate(1, 1), Coordinate(1, 5)) == "vertical"
        
        # Diagonal movement
        assert engine._determine_movement_type(Coordinate(1, 1), Coordinate(5, 5)) == "diagonal"

    def test_calculate_direction(self, engine):
        """Test direction calculation."""
        # East
        assert engine._calculate_direction(Coordinate(1, 1), Coordinate(5, 1)) == "east"
        
        # West
        assert engine._calculate_direction(Coordinate(5, 1), Coordinate(1, 1)) == "west"
        
        # South
        assert engine._calculate_direction(Coordinate(1, 1), Coordinate(1, 5)) == "south"
        
        # North
        assert engine._calculate_direction(Coordinate(1, 5), Coordinate(1, 1)) == "north"
        
        # None (same position)
        assert engine._calculate_direction(Coordinate(1, 1), Coordinate(1, 1)) == "none"

    def test_handle_direction_change_with_cooldown(self, engine):
        """Test direction change handling with cooldown."""
        # Reset robot state
        engine.robot.current_direction = None
        engine.simulation_time = 1.0
        engine.robot.last_direction_change = 0.5  # Within cooldown

        # Should not change direction due to cooldown
        engine._handle_direction_change("east")
        assert engine.robot.current_direction is None
        
        # After cooldown period
        engine.simulation_time = 1.5
        engine._handle_direction_change("east")
        assert engine.robot.current_direction == "east"
        assert engine.robot.last_direction_change == 1.5
        assert engine.performance_metrics["direction_changes"] == 1

    def test_handle_direction_change_first_time(self, engine):
        """Test direction change when no previous direction."""
        engine.simulation_time = 1.0
        engine.robot.last_direction_change = None
        
        engine._handle_direction_change("south")
        assert engine.robot.current_direction == "south"
        assert engine.robot.last_direction_change == 1.0
        assert engine.performance_metrics["direction_changes"] == 1

    @patch.object(AisleTimingManager, 'calculate_movement_timing')
    def test_update_robot_movement(self, mock_timing, engine):
        """Test robot movement update."""
        # Setup robot state
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(1, 1), Coordinate(2, 2), Coordinate(3, 3)]
        engine.robot.path_index = 0
        engine.robot.position = Coordinate(1, 1)
        
        # Mock timing
        from core.layout.aisle_timing_manager import MovementTiming
        mock_movement = MovementTiming(
            start_time=1.0,
            end_time=1.5,
            duration=0.5,
            movement_type=None,
            start_position=Coordinate(1, 1),
            end_position=Coordinate(2, 2)
        )
        mock_timing.return_value = mock_movement
        
        # Mock distance calculation
        engine.distance_tracker.calculate_distance = Mock(return_value=1.414)
        
        # Update movement
        engine._update_robot_movement(0.1)
        
        # Check robot state
        assert engine.robot.position == Coordinate(1, 1)
        assert engine.robot.path_index == 1
        assert engine.robot.total_distance == 1.414
        assert engine.performance_metrics["total_distance"] == 1.414

    def test_update_robot_movement_path_completion(self, engine):
        """Test robot movement when path is completed."""
        # Setup robot at end of path
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(1, 1)]
        engine.robot.path_index = 1  # Already at end
        engine.robot.target_item = "test_item"
        
        # Mock item collection
        engine._handle_path_completion = Mock()
        
        engine._update_robot_movement(0.1)
        
        # Should call path completion handler
        engine._handle_path_completion.assert_called_once()

    def test_handle_path_completion_with_item(self, engine):
        """Test path completion when collecting an item."""
        engine.robot.target_item = "test_item"
        engine.robot.collected_items = []
        engine.performance_metrics["items_collected"] = 0
        
        # Mock next item movement
        engine._move_to_next_item = Mock()
        
        engine._handle_path_completion()
        
        # Check item collection
        assert "test_item" in engine.robot.collected_items
        assert engine.robot.state == RobotState.COLLECTING
        assert engine.performance_metrics["items_collected"] == 1
        
        # Should move to next item
        engine._move_to_next_item.assert_called_once()

    def test_handle_path_completion_no_item(self, engine):
        """Test path completion when no item to collect."""
        engine.robot.target_item = None
        
        # Mock order completion
        engine._complete_current_order = Mock()
        
        engine._handle_path_completion()
        
        # Should complete current order
        engine._complete_current_order.assert_called_once()

    def test_move_to_next_item(self, engine):
        """Test moving to the next item in order."""
        # Setup order and robot state
        engine.current_order_index = 0
        engine.orders = [{"items": ["item_A", "item_B", "item_C"]}]
        engine.robot.collected_items = ["item_A"]
        engine.robot.position = Coordinate(1, 1)
        
        # Mock item position and path calculation
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Create a mock CompletePath object
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
        
        engine._move_to_next_item()
        
        # Check robot state
        assert engine.robot.target_item == "item_B"
        assert engine.robot.state == RobotState.MOVING
        # The path should contain the start and end coordinates from the segment
        assert engine.robot.current_path == [Coordinate(1, 1), Coordinate(5, 5)]
        assert engine.robot.path_index == 0

    def test_move_to_next_item_no_remaining(self, engine):
        """Test moving to next item when all items collected."""
        # Setup order with all items collected
        engine.current_order_index = 0
        engine.orders = [{"items": ["item_A", "item_B"]}]
        engine.robot.collected_items = ["item_A", "item_B"]
        
        # Mock order completion
        engine._complete_current_order = Mock()
        
        engine._move_to_next_item()
        
        # Should complete current order
        engine._complete_current_order.assert_called_once()

    def test_complete_current_order(self, engine):
        """Test completing the current order."""
        engine.current_order_index = 0
        engine.orders = [{"id": "test_order_1"}, {"id": "test_order_2"}]  # Two orders
        engine.performance_metrics["orders_completed"] = 0
        
        # Mock next order initialization
        engine._initialize_current_order = Mock()
        
        # Mock path calculation to return empty segments (no more orders)
        from core.layout.bidirectional_path_calculator import CompletePath
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=CompletePath(
            segments=[],
            total_distance=0.0,
            total_duration=0.0,
            direction_changes=0,
            items_to_collect=[],
            optimized_order=[]
        ))
        
        engine._complete_current_order()
        
        # Check metrics
        assert engine.performance_metrics["orders_completed"] == 1
        assert engine.current_order_index == 1
        
        # Should initialize next order
        engine._initialize_current_order.assert_called_once()

    def test_complete_current_order_last_order(self, engine):
        """Test completing the last order."""
        engine.current_order_index = 0
        engine.orders = [{"id": "test_order"}]
        
        # Mock simulation completion
        engine._complete_simulation = Mock()
        
        engine._complete_current_order()
        
        # Should complete simulation
        engine._complete_simulation.assert_called_once()

    def test_complete_simulation(self, engine):
        """Test simulation completion."""
        engine.is_running = True
        engine.robot.state = RobotState.MOVING
        engine.simulation_time = 10.5
        
        engine._complete_simulation()
        
        assert not engine.is_running
        assert engine.robot.state == RobotState.COMPLETED

    def test_get_simulation_state(self, engine):
        """Test getting simulation state."""
        # Setup some state
        engine.robot.position = Coordinate(5, 5)
        engine.orders = [{"id": "test"}]
        engine.current_order_index = 0
        engine.simulation_time = 10.0
        engine.is_running = True
        engine.performance_metrics = {"total_distance": 15.5}
        
        # Mock trail points
        engine.trail_manager.get_trail_points = Mock(return_value=[(Coordinate(1, 1), 1.0)])
        
        state = engine.get_simulation_state()
        
        assert state["robot"] == engine.robot
        assert state["orders"] == engine.orders
        assert state["current_order_index"] == 0
        assert state["simulation_time"] == 10.0
        assert state["is_running"] is True
        assert state["performance_metrics"] == {"total_distance": 15.5}
        assert state["trail_points"] == [(Coordinate(1, 1), 1.0)]

    def test_pause_simulation(self, engine):
        """Test pausing the simulation."""
        engine.is_running = True
        engine.robot.path_execution_state = "executing"
        
        engine.pause_simulation()
        
        assert not engine.is_running
        assert engine.robot.path_execution_state == "paused"

    def test_resume_simulation(self, engine):
        """Test resuming the simulation."""
        engine.is_running = False
        engine.robot.state = RobotState.MOVING
        engine.robot.path_execution_state = "paused"
        
        engine.resume_simulation()
        
        assert engine.is_running
        assert engine.robot.path_execution_state == "executing"

    def test_resume_simulation_completed(self, engine):
        """Test resuming when simulation is completed."""
        engine.is_running = False
        engine.robot.state = RobotState.COMPLETED
        
        engine.resume_simulation()
        
        # Should not resume if completed
        assert not engine.is_running

    def test_stop_simulation(self, engine):
        """Test stopping the simulation."""
        engine.is_running = True
        engine.robot.state = RobotState.MOVING
        engine.robot.path_execution_state = "executing"
        
        engine.stop_simulation()
        
        assert not engine.is_running
        assert engine.robot.state == RobotState.IDLE
        assert engine.robot.path_execution_state == "ready"

    def test_reset_simulation(self, engine):
        """Test resetting the simulation."""
        # Setup some state
        engine.robot.position = Coordinate(5, 5)
        engine.robot.collected_items = ["item_A"]
        engine.current_order_index = 2
        engine.simulation_time = 10.0
        engine.is_running = True
        engine.performance_metrics = {"total_distance": 15.5}
        
        # Mock trail clearing
        engine.trail_manager.clear_trail = Mock()
        
        engine.reset_simulation()
        
        # Check reset state
        assert engine.robot.position == Coordinate(1, 1)
        assert engine.robot.collected_items == []
        assert engine.current_order_index == 0
        assert engine.simulation_time == 0.0
        assert not engine.is_running
        assert engine.performance_metrics["total_distance"] == 0.0
        
        # Should clear trail
        engine.trail_manager.clear_trail.assert_called_once()

    def test_check_order_completion(self, engine):
        """Test checking order completion."""
        engine.current_order_index = 0
        engine.orders = [{"items": ["item_A", "item_B"]}]
        engine.robot.collected_items = ["item_A", "item_B"]
        
        # Mock order completion
        engine._complete_current_order = Mock()
        
        engine._check_order_completion()
        
        # Should complete current order
        engine._complete_current_order.assert_called_once()

    def test_check_order_completion_incomplete(self, engine):
        """Test checking order completion when not all items collected."""
        engine.current_order_index = 0
        engine.orders = [{"items": ["item_A", "item_B"]}]
        engine.robot.collected_items = ["item_A"]  # Missing item_B
        
        # Mock order completion
        engine._complete_current_order = Mock()
        
        engine._check_order_completion()
        
        # Should not complete current order
        engine._complete_current_order.assert_not_called()

    def test_integration_with_trail_manager(self, engine):
        """Test integration with movement trail manager."""
        # Setup robot movement
        engine.robot.position = Coordinate(1, 1)
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(1, 1)]
        engine.robot.path_index = 0
        engine.simulation_time = 1.0
        
        # Mock timing and distance
        engine.aisle_timing.get_movement_time = Mock(return_value=0.5)
        engine.distance_tracker.calculate_distance = Mock(return_value=1.414)
        
        # Mock trail manager
        engine.trail_manager.add_trail_point = Mock()
        
        engine._update_robot_movement(0.1)
        
        # Should add trail point
        engine.trail_manager.add_trail_point.assert_called_once_with(Coordinate(1, 1), 1.0)

    def test_integration_with_event_system(self, engine):
        """Test integration with event system."""
        # Setup robot movement
        engine.robot.position = Coordinate(1, 1)
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(1, 1)]
        engine.robot.path_index = 0
        engine.simulation_time = 1.0
        
        # Mock timing and distance
        engine.aisle_timing.get_movement_time = Mock(return_value=0.5)
        engine.distance_tracker.calculate_distance = Mock(return_value=1.414)
        
        # Mock event system
        engine.event_system.emit = Mock()
        
        engine._update_robot_movement(0.1)
        
        # Should emit movement event
        engine.event_system.emit.assert_called_once()
        call_args = engine.event_system.emit.call_args
        assert call_args[0][0] == EventType.ROBOT_MOVED
        assert "robot" in call_args[0][1]
        assert "old_position" in call_args[0][1]
        assert "new_position" in call_args[0][1]
        assert "distance" in call_args[0][1]
        assert "movement_time" in call_args[0][1]


class TestRobotStateTransitions:
    """Test robot state transitions and edge cases."""
    
    @pytest.fixture
    def engine(self):
        """Create a simulation engine for testing."""
        engine = SimulationEngine()
        engine.state = Mock()
        engine.event_system = Mock()
        engine.timing_manager = Mock()
        engine.performance_benchmark = Mock()
        engine.performance_optimizer = Mock()
        return engine

    def test_robot_state_transitions(self, engine):
        """Test robot state transitions through different phases."""
        # Initial state
        assert engine.robot.state == RobotState.IDLE
        
        # Start simulation
        engine.add_order({"items": ["item_A", "item_B"]})  # Two items
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Mock path calculation
        from core.layout.bidirectional_path_calculator import CompletePath, PathSegment
        mock_segments = [
            PathSegment(
                start=Coordinate(1, 1),
                end=Coordinate(5, 5),
                direction=None,
                duration=1.0,
                aisle_number=5,
                is_horizontal=False
            )
        ]
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=CompletePath(
            segments=mock_segments,
            total_distance=5.0,
            total_duration=1.0,
            direction_changes=0,
            items_to_collect=[Coordinate(5, 5)],
            optimized_order=[Coordinate(5, 5)]
        ))
        
        engine.start_simulation()
        assert engine.robot.state == RobotState.MOVING
        
        # Complete path and collect item
        engine.robot.path_index = 1  # End of path
        engine.robot.target_item = "item_A"
        
        # Mock _move_to_next_item to avoid it being called
        original_move_to_next = engine._move_to_next_item
        engine._move_to_next_item = Mock()
        
        engine._handle_path_completion()
        
        # Check that item was collected and state was COLLECTING
        assert "item_A" in engine.robot.collected_items
        assert engine.robot.state == RobotState.COLLECTING
        
        # Restore original method
        engine._move_to_next_item = original_move_to_next
        
        # Complete simulation
        engine._complete_simulation()
        assert engine.robot.state == RobotState.COMPLETED

    def test_performance_metrics_tracking(self, engine):
        """Test performance metrics tracking during robot movement."""
        # Setup robot movement
        engine.robot.state = RobotState.MOVING
        engine.robot.current_path = [Coordinate(1, 1), Coordinate(2, 2)]
        engine.robot.path_index = 0
        engine.robot.position = Coordinate(1, 1)
        
        # Mock components
        engine.aisle_timing.get_movement_time = Mock(return_value=0.5)
        engine.distance_tracker.calculate_distance = Mock(return_value=1.414)
        engine.trail_manager.add_trail_point = Mock()
        engine.event_system.emit = Mock()
        
        # Initial metrics
        initial_distance = engine.performance_metrics["total_distance"]
        initial_direction_changes = engine.performance_metrics["direction_changes"]
        
        # Update movement
        engine._update_robot_movement(0.1)
        
        # Check metrics updated
        assert engine.performance_metrics["total_distance"] > initial_distance
        assert engine.robot.total_distance > 0

    def test_error_handling_invalid_path(self, engine):
        """Test error handling for invalid paths."""
        # Setup order with invalid item positions
        engine.add_order({"items": ["invalid_item"]})
        engine.warehouse_layout.get_item_position = Mock(return_value=None)
        
        # Should handle gracefully
        engine.start_simulation()
        assert not engine.is_running

    def test_error_handling_path_calculation_failure(self, engine):
        """Test error handling when path calculation fails."""
        # Setup order
        engine.add_order({"items": ["item_A"]})
        engine.warehouse_layout.get_item_position = Mock(return_value=Coordinate(5, 5))
        
        # Mock path calculation to return empty segments (simulating failure)
        from core.layout.bidirectional_path_calculator import CompletePath
        engine.path_calculator.calculate_complete_path_for_items = Mock(return_value=CompletePath(
            segments=[],
            total_distance=0.0,
            total_duration=0.0,
            direction_changes=0,
            items_to_collect=[],
            optimized_order=[]
        ))
        
        # Should handle gracefully
        engine.start_simulation()
        assert not engine.is_running


if __name__ == "__main__":
    pytest.main([__file__]) 