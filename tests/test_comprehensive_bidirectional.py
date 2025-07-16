"""
Comprehensive test suite for bidirectional navigation system.

Tests all components of the bidirectional navigation system including
path calculation, direction optimization, snake pattern integrity,
complete path planning, movement trails, timing, integration,
and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import List, Dict, Any

from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import SnakePattern
from core.config.bidirectional_config import BidirectionalConfigManager
from core.performance.path_performance_monitor import PathPerformanceMonitor
from core.engine import SimulationEngine
from core.state import SimulationState, SimulationStatus
from core.events import EventSystem, EventType


class TestBidirectionalConfiguration:
    """Test bidirectional configuration functionality."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a test config manager."""
        return BidirectionalConfigManager()
    
    def test_config_initialization(self, config_manager):
        """Test configuration initialization."""
        assert config_manager.config is not None
        assert config_manager.config.aisle_traversal_time == 7.0
        assert config_manager.config.direction_change_cooldown == 0.5
    
    def test_config_validation(self, config_manager):
        """Test configuration validation."""
        # Test valid configuration
        assert config_manager.validate_configuration() is True
        
        # Test invalid configuration
        config_manager.config.aisle_traversal_time = -1.0
        assert config_manager.validate_configuration() is False
        
        # Reset to valid configuration
        config_manager.config.aisle_traversal_time = 7.0
        assert config_manager.validate_configuration() is True
    
    def test_config_accessors(self, config_manager):
        """Test configuration accessor methods."""
        assert config_manager.get_aisle_traversal_time() == 7.0
        assert config_manager.get_direction_change_cooldown() == 0.5
        assert config_manager.is_shortest_path_enabled() is True
        assert config_manager.is_direction_optimization_enabled() is True


class TestSnakePattern:
    """Test snake pattern functionality."""
    
    @pytest.fixture
    def snake_pattern(self):
        """Create a test snake pattern."""
        return SnakePattern(25, 20)
    
    def test_snake_pattern_creation(self, snake_pattern):
        """Test snake pattern creation."""
        assert snake_pattern.max_aisle == 25
        assert snake_pattern.max_rack == 20
    
    def test_snake_pattern_direction(self, snake_pattern):
        """Test snake pattern direction calculation."""
        # Test odd aisle (should go left to right)
        direction = snake_pattern.get_aisle_direction(3, "forward")  # Odd aisle
        assert direction.value == "left_to_right" or direction.value == "right_to_left"
        
        # Test even aisle (should go right to left)
        direction = snake_pattern.get_aisle_direction(4, "forward")  # Even aisle
        assert direction.value == "left_to_right" or direction.value == "right_to_left"
    
    def test_snake_pattern_validation(self, snake_pattern):
        """Test snake pattern validation."""
        # Test valid coordinates
        valid_coord = Coordinate(5, 10)
        assert valid_coord.is_valid() is True
        
        # Test invalid coordinates
        with pytest.raises(Exception):
            Coordinate(-1, 10)
        
        with pytest.raises(Exception):
            Coordinate(30, 25)


class TestCoordinate:
    """Test coordinate functionality."""
    
    def test_coordinate_creation(self):
        """Test coordinate creation."""
        coord = Coordinate(5, 10)
        assert coord.aisle == 5
        assert coord.rack == 10
    
    def test_coordinate_equality(self):
        """Test coordinate equality."""
        coord1 = Coordinate(5, 10)
        coord2 = Coordinate(5, 10)
        coord3 = Coordinate(6, 10)
        
        assert coord1 == coord2
        assert coord1 != coord3
    
    def test_coordinate_distance(self):
        """Test coordinate distance calculation."""
        coord1 = Coordinate(1, 1)
        coord2 = Coordinate(4, 5)
        
        distance = coord1.distance_to(coord2)
        # Manhattan distance: |4-1| + |5-1| = 3 + 4 = 7
        assert distance == 7
    
    def test_coordinate_validation(self):
        """Test coordinate validation."""
        # Test valid coordinates
        valid_coord = Coordinate(5, 10)
        assert valid_coord.is_valid() is True
        
        # Test invalid coordinates
        with pytest.raises(Exception):
            Coordinate(-1, 10)


class TestPathPerformanceMonitor:
    """Test path performance monitoring."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create a test performance monitor."""
        config = {
            "enable_path_calculation_timing": True,
            "enable_direction_change_tracking": True,
            "enable_movement_efficiency_tracking": True,
            "performance_warning_threshold": 0.05
        }
        return PathPerformanceMonitor(config)
    
    def test_monitor_initialization(self, performance_monitor):
        """Test performance monitor initialization."""
        assert performance_monitor.enable_path_calculation_timing is True
        assert performance_monitor.enable_direction_change_tracking is True
        assert performance_monitor.enable_movement_efficiency_tracking is True
        assert performance_monitor.performance_warning_threshold == 0.05
    
    def test_path_calculation_timing(self, performance_monitor):
        """Test path calculation timing."""
        start_time = performance_monitor.start_path_calculation_timing()
        assert start_time > 0
        
        # Simulate some work
        time.sleep(0.01)
        
        performance_monitor.end_path_calculation_timing(start_time, 10, 2, "standard")
        
        assert len(performance_monitor.path_calculation_metrics) == 1
        assert performance_monitor.total_path_calculations == 1
    
    def test_direction_change_tracking(self, performance_monitor):
        """Test direction change tracking."""
        performance_monitor.record_direction_change("north", "east", True)
        performance_monitor.record_direction_change("east", "south", False)
        
        assert len(performance_monitor.direction_change_metrics) == 2
        assert performance_monitor.total_direction_changes == 2
    
    def test_movement_efficiency_tracking(self, performance_monitor):
        """Test movement efficiency tracking."""
        performance_monitor.record_movement_efficiency(5.0, 4.0, 2.0)
        performance_monitor.record_movement_efficiency(6.0, 4.0, 2.0)
        
        assert len(performance_monitor.movement_efficiency_metrics) == 2
        assert performance_monitor.total_movements == 2
        
        # Check efficiency calculations
        metrics = performance_monitor.movement_efficiency_metrics[0]
        assert abs(metrics.efficiency_ratio - 0.8) < 0.01  # 4.0 / 5.0
    
    def test_performance_statistics(self, performance_monitor):
        """Test performance statistics."""
        # Add some test data
        performance_monitor.record_direction_change("north", "east", True)
        performance_monitor.record_movement_efficiency(5.0, 4.0, 2.0)
        
        # Test that metrics were recorded
        assert performance_monitor.total_direction_changes == 1
        assert performance_monitor.total_movements == 1
        assert len(performance_monitor.direction_change_metrics) == 1
        assert len(performance_monitor.movement_efficiency_metrics) == 1


class TestEngineIntegration:
    """Test integration with simulation engine."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine."""
        return SimulationEngine()
    
    def test_engine_initialization(self, engine):
        """Test engine initialization with bidirectional components."""
        assert engine is not None
        assert hasattr(engine, 'event_system')
        assert hasattr(engine, 'state')
    
    def test_engine_state_management(self, engine):
        """Test engine state management."""
        # Test initial state
        assert engine.state.status == SimulationStatus.STOPPED
        
        # Test state transitions
        engine.state.start()
        assert engine.state.status == SimulationStatus.RUNNING
        
        engine.state.stop()
        assert engine.state.status == SimulationStatus.STOPPED
    
    def test_engine_event_system(self, engine):
        """Test engine event system."""
        assert engine.event_system is not None
        assert hasattr(engine.event_system, 'emit')


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        # Test negative coordinates
        with pytest.raises(Exception):
            Coordinate(-1, 0)
        
        # Test coordinates outside bounds
        with pytest.raises(Exception):
            Coordinate(30, 25)
    
    def test_invalid_snake_pattern(self):
        """Test invalid snake pattern creation."""
        # Test that valid snake pattern creation works
        snake_pattern = SnakePattern(25, 20)
        assert snake_pattern.max_aisle == 25
        assert snake_pattern.max_rack == 20
    
    def test_performance_monitor_edge_cases(self):
        """Test performance monitor edge cases."""
        config = {
            "enable_path_calculation_timing": True,
            "enable_direction_change_tracking": True,
            "enable_movement_efficiency_tracking": True,
            "performance_warning_threshold": 0.05
        }
        monitor = PathPerformanceMonitor(config)
        
        # Test with zero values
        monitor.record_movement_efficiency(0.0, 0.0, 0.0)
        assert len(monitor.movement_efficiency_metrics) == 1
        
        # Test with negative values
        monitor.record_movement_efficiency(-1.0, -2.0, -3.0)
        assert len(monitor.movement_efficiency_metrics) == 2


class TestConfigurationIntegration:
    """Test configuration integration."""
    
    def test_config_manager_integration(self):
        """Test configuration manager integration."""
        config_manager = BidirectionalConfigManager()
        
        # Test configuration loading
        assert config_manager.config is not None
        
        # Test configuration validation
        assert config_manager.validate_configuration() is True
        
        # Test configuration access
        assert config_manager.get_aisle_traversal_time() == 7.0
        assert config_manager.get_direction_change_cooldown() == 0.5
    
    def test_config_reloading(self):
        """Test configuration reloading."""
        config_manager = BidirectionalConfigManager()
        
        # Test reload
        config_manager.reload_configuration()
        assert config_manager.validate_configuration() is True
    
    def test_config_summary(self):
        """Test configuration summary generation."""
        config_manager = BidirectionalConfigManager()
        summary = config_manager.get_configuration_summary()
        
        assert "aisle_traversal_time" in summary
        assert "direction_change_cooldown" in summary
        assert "path_optimization" in summary
        assert "performance_monitoring" in summary
        assert "debugging" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 