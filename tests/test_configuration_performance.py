"""
Test suite for configuration management and performance monitoring.

Tests the bidirectional navigation configuration management,
performance monitoring, and integration with the main system.
"""

import pytest
from unittest.mock import Mock, patch
import time

from core.config.bidirectional_config import (
    BidirectionalConfigManager, 
    PathOptimizationConfig,
    PerformanceMonitoringConfig,
    DebuggingConfig,
    get_bidirectional_config
)
from core.performance.path_performance_monitor import PathPerformanceMonitor
from core.engine import SimulationEngine


class TestBidirectionalConfiguration:
    """Test bidirectional navigation configuration management."""
    
    def test_config_manager_initialization(self):
        """Test that configuration manager initializes correctly."""
        config_manager = BidirectionalConfigManager()
        
        # Check that configuration is loaded
        assert config_manager.config is not None
        assert config_manager.config.aisle_traversal_time == 7.0
        assert config_manager.config.direction_change_cooldown == 0.5
        
        # Check that sub-configurations are initialized
        assert config_manager.config.path_optimization is not None
        assert config_manager.config.performance_monitoring is not None
        assert config_manager.config.debugging is not None
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        config_manager = BidirectionalConfigManager()
        
        # Test valid configuration
        assert config_manager.validate_configuration() is True
        
        # Test invalid configuration
        config_manager.config.aisle_traversal_time = -1.0
        assert config_manager.validate_configuration() is False
        
        # Reset to valid configuration
        config_manager.config.aisle_traversal_time = 7.0
        assert config_manager.validate_configuration() is True
    
    def test_configuration_accessors(self):
        """Test configuration accessor methods."""
        config_manager = BidirectionalConfigManager()
        
        # Test basic settings
        assert config_manager.get_aisle_traversal_time() == 7.0
        assert config_manager.get_direction_change_cooldown() == 0.5
        
        # Test path optimization settings
        assert config_manager.is_shortest_path_enabled() is True
        assert config_manager.is_direction_optimization_enabled() is True
        assert config_manager.is_snake_pattern_integrity_enabled() is True
        assert config_manager.get_max_path_calculation_time() == 0.1
        
        # Test performance monitoring settings
        assert config_manager.is_path_calculation_timing_enabled() is True
        assert config_manager.is_direction_change_tracking_enabled() is True
        assert config_manager.is_movement_efficiency_tracking_enabled() is True
        assert config_manager.get_performance_warning_threshold() == 0.05
        
        # Test debugging settings
        assert config_manager.is_path_visualization_enabled() is False
        assert config_manager.is_direction_debug_enabled() is False
        assert config_manager.is_timing_debug_enabled() is False
        assert config_manager.get_log_level() == "info"
    
    def test_configuration_summary(self):
        """Test configuration summary generation."""
        config_manager = BidirectionalConfigManager()
        summary = config_manager.get_configuration_summary()
        
        # Check that summary contains all sections
        assert "aisle_traversal_time" in summary
        assert "direction_change_cooldown" in summary
        assert "path_optimization" in summary
        assert "performance_monitoring" in summary
        assert "debugging" in summary
        
        # Check path optimization section
        path_opt = summary["path_optimization"]
        assert "enable_shortest_path" in path_opt
        assert "enable_direction_optimization" in path_opt
        assert "enable_snake_pattern_integrity" in path_opt
        assert "max_path_calculation_time" in path_opt
        
        # Check performance monitoring section
        perf_mon = summary["performance_monitoring"]
        assert "enable_path_calculation_timing" in perf_mon
        assert "enable_direction_change_tracking" in perf_mon
        assert "enable_movement_efficiency_tracking" in perf_mon
        assert "performance_warning_threshold" in perf_mon
    
    def test_global_config_access(self):
        """Test global configuration access."""
        config_manager = get_bidirectional_config()
        
        # Check that we get the same instance
        config_manager2 = get_bidirectional_config()
        assert config_manager is config_manager2
        
        # Check that configuration is accessible
        assert config_manager.get_aisle_traversal_time() == 7.0


class TestPathPerformanceMonitor:
    """Test path performance monitoring."""
    
    @pytest.fixture
    def monitor(self):
        """Create a test performance monitor."""
        config = {
            "enable_path_calculation_timing": True,
            "enable_direction_change_tracking": True,
            "enable_movement_efficiency_tracking": True,
            "performance_warning_threshold": 0.05
        }
        return PathPerformanceMonitor(config)
    
    def test_monitor_initialization(self, monitor):
        """Test that performance monitor initializes correctly."""
        assert monitor.enable_path_calculation_timing is True
        assert monitor.enable_direction_change_tracking is True
        assert monitor.enable_movement_efficiency_tracking is True
        assert monitor.performance_warning_threshold == 0.05
        
        # Check that metrics storage is initialized
        assert len(monitor.path_calculation_metrics) == 0
        assert len(monitor.direction_change_metrics) == 0
        assert len(monitor.movement_efficiency_metrics) == 0
    
    def test_path_calculation_timing(self, monitor):
        """Test path calculation timing."""
        # Start timing
        start_time = monitor.start_path_calculation_timing()
        assert start_time > 0
        
        # Simulate some work
        time.sleep(0.01)
        
        # End timing
        monitor.end_path_calculation_timing(start_time, 10, 2, "standard")
        
        # Check that metrics were recorded
        assert len(monitor.path_calculation_metrics) == 1
        assert monitor.total_path_calculations == 1
        
        # Check metrics
        metrics = monitor.path_calculation_metrics[0]
        assert metrics.path_length == 10
        assert metrics.direction_changes == 2
        assert metrics.optimization_level == "standard"
        assert metrics.calculation_time > 0
    
    def test_direction_change_tracking(self, monitor):
        """Test direction change tracking."""
        # Record direction changes
        monitor.record_direction_change("north", "east", True)
        monitor.record_direction_change("east", "south", False)  # Cooldown violation
        
        # Check that metrics were recorded
        assert len(monitor.direction_change_metrics) == 2
        assert monitor.total_direction_changes == 2
        
        # Check metrics
        metrics1 = monitor.direction_change_metrics[0]
        assert metrics1.old_direction == "north"
        assert metrics1.new_direction == "east"
        assert metrics1.cooldown_respected is True
        
        metrics2 = monitor.direction_change_metrics[1]
        assert metrics2.old_direction == "east"
        assert metrics2.new_direction == "south"
        assert metrics2.cooldown_respected is False
    
    def test_movement_efficiency_tracking(self, monitor):
        """Test movement efficiency tracking."""
        # Record movement efficiency
        monitor.record_movement_efficiency(5.0, 4.0, 2.0)  # 80% efficient
        monitor.record_movement_efficiency(6.0, 4.0, 2.0)  # 67% efficient (warning)
        
        # Check that metrics were recorded
        assert len(monitor.movement_efficiency_metrics) == 2
        assert monitor.total_movements == 2
        
        # Check metrics
        metrics1 = monitor.movement_efficiency_metrics[0]
        assert metrics1.distance_traveled == 5.0
        assert metrics1.optimal_distance == 4.0
        assert metrics1.efficiency_ratio == 0.8
        assert metrics1.movement_time == 2.0
        
        metrics2 = monitor.movement_efficiency_metrics[1]
        assert abs(metrics2.efficiency_ratio - 0.67) < 0.01  # 4.0 / 6.0 ≈ 0.67
    
    def test_performance_warnings(self, monitor):
        """Test performance warning generation."""
        # Trigger a performance warning
        start_time = monitor.start_path_calculation_timing()
        time.sleep(0.06)  # Exceeds 0.05 threshold
        monitor.end_path_calculation_timing(start_time, 10, 2, "standard")
        
        # Check that warning was generated
        warnings = monitor.get_performance_warnings()
        assert len(warnings) == 1
        assert "Path calculation took" in warnings[0]
        
        # Test warning clearing
        monitor.clear_performance_warnings()
        assert len(monitor.get_performance_warnings()) == 0
    
    def test_performance_statistics(self, monitor):
        """Test performance statistics generation."""
        # Record some metrics
        monitor.record_direction_change("north", "east", True)
        monitor.record_direction_change("east", "south", False)
        monitor.record_movement_efficiency(5.0, 4.0, 2.0)
        
        # Get statistics
        dir_stats = monitor.get_direction_change_statistics()
        move_stats = monitor.get_movement_efficiency_statistics()
        
        # Check direction change statistics
        assert dir_stats["total_changes"] == 2
        assert dir_stats["cooldown_violations"] == 1
        assert dir_stats["cooldown_compliance_rate"] == 0.5
        
        # Check movement efficiency statistics
        assert move_stats["total_movements"] == 1
        assert move_stats["avg_efficiency"] == 0.8
        assert move_stats["avg_distance_traveled"] == 5.0
    
    def test_performance_summary(self, monitor):
        """Test comprehensive performance summary."""
        # Record various metrics
        start_time = monitor.start_path_calculation_timing()
        time.sleep(0.01)
        monitor.end_path_calculation_timing(start_time, 10, 2, "standard")
        
        monitor.record_direction_change("north", "east", True)
        monitor.record_movement_efficiency(5.0, 4.0, 2.0)
        
        # Get summary
        summary = monitor.get_performance_summary()
        
        # Check summary structure
        assert "path_calculation" in summary
        assert "direction_changes" in summary
        assert "movement_efficiency" in summary
        assert "performance_warnings" in summary
        assert "total_metrics" in summary
        
        # Check total metrics
        total_metrics = summary["total_metrics"]
        assert total_metrics["path_calculations"] == 1
        assert total_metrics["direction_changes"] == 1
        assert total_metrics["movements"] == 1
    
    def test_metrics_reset(self, monitor):
        """Test metrics reset functionality."""
        # Record some metrics
        monitor.record_direction_change("north", "east", True)
        monitor.record_movement_efficiency(5.0, 4.0, 2.0)
        
        # Verify metrics were recorded
        assert len(monitor.direction_change_metrics) == 1
        assert len(monitor.movement_efficiency_metrics) == 1
        
        # Reset metrics
        monitor.reset_metrics()
        
        # Verify metrics were cleared
        assert len(monitor.direction_change_metrics) == 0
        assert len(monitor.movement_efficiency_metrics) == 0
        assert monitor.total_direction_changes == 0
        assert monitor.total_movements == 0
    
    def test_configuration_update(self, monitor):
        """Test configuration update."""
        # Update configuration
        new_config = {
            "enable_path_calculation_timing": False,
            "enable_direction_change_tracking": False,
            "enable_movement_efficiency_tracking": False,
            "performance_warning_threshold": 0.1
        }
        monitor.configure(new_config)
        
        # Check that configuration was updated
        assert monitor.enable_path_calculation_timing is False
        assert monitor.enable_direction_change_tracking is False
        assert monitor.enable_movement_efficiency_tracking is False
        assert monitor.performance_warning_threshold == 0.1


class TestEngineIntegration:
    """Test integration with the simulation engine."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        engine = SimulationEngine()
        return engine
    
    def test_engine_configuration_integration(self, engine):
        """Test that engine integrates configuration management."""
        # Check that bidirectional config is available
        assert hasattr(engine, 'bidirectional_config')
        assert hasattr(engine, 'path_performance_monitor')
        
        # Check that configuration is accessible
        assert engine.bidirectional_config.get_aisle_traversal_time() == 7.0
        assert engine.bidirectional_config.get_direction_change_cooldown() == 0.5
    
    def test_performance_monitoring_integration(self, engine):
        """Test that engine integrates performance monitoring."""
        # Check that performance monitor is available
        assert engine.path_performance_monitor is not None
        
        # Check that performance monitoring is enabled
        assert engine.path_performance_monitor.enable_path_calculation_timing is True
        assert engine.path_performance_monitor.enable_direction_change_tracking is True
        assert engine.path_performance_monitor.enable_movement_efficiency_tracking is True
    
    def test_configuration_validation_integration(self, engine):
        """Test that engine validates configuration."""
        # Check that configuration is valid
        assert engine.bidirectional_config.validate_configuration() is True
        
        # Get configuration summary
        summary = engine.bidirectional_config.get_configuration_summary()
        assert "aisle_traversal_time" in summary
        assert "path_optimization" in summary
        assert "performance_monitoring" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 