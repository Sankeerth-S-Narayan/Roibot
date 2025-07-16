"""
Test suite for configuration management system.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open

from core.main_config import (
    ConfigurationManager, ConfigSection, ConfigValidationRule,
    SimulationTimingConstants, WarehouseConstants, RobotConstants, OrderConstants,
    ConfigurationError, get_config
)


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file."""
        config_data = {
            "simulation": {
                "name": "Test Simulation",
                "version": "1.0.0",
                "description": "Test description"
            },
            "timing": {
                "target_fps": 60,
                "tick_interval": 0.016667,
                "simulation_speed": 1.0,
                "max_delta_time": 0.1
            },
            "engine": {
                "event_queue_size": 1000,
                "max_concurrent_events": 50,
                "performance_monitoring": True,
                "debug_prints": True
            },
            "performance": {
                "target_frame_time": 16.67,
                "warning_frame_time": 33.33,
                "critical_frame_time": 100.0
            },
            "warehouse": {
                "aisles": 25,
                "racks": 20,
                "base_location": {"aisle": 0, "rack": 0}
            },
            "robot": {
                "movement_speed": 2.0,
                "animation_smoothing": 0.1,
                "state_change_delay": 0.05
            },
            "orders": {
                "generation_interval": 40,
                "max_items_per_order": 4,
                "continuous_assignment": True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    def test_config_manager_initialization(self):
        """Test configuration manager initialization."""
        config_manager = ConfigurationManager()
        
        assert config_manager.config_path == "config/simulation.json"
        assert config_manager.config_data == {}
        assert not config_manager.is_loaded
        assert isinstance(config_manager.timing, SimulationTimingConstants)
        assert isinstance(config_manager.warehouse, WarehouseConstants)
        assert isinstance(config_manager.robot, RobotConstants)
        assert isinstance(config_manager.orders, OrderConstants)
        assert len(config_manager.validation_rules) == 7
    
    def test_load_configuration_success(self, temp_config_file):
        """Test successful configuration loading."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        assert config_manager.is_loaded
        assert config_manager.config_data["simulation"]["name"] == "Test Simulation"
        assert config_manager.config_data["timing"]["target_fps"] == 60
    
    def test_load_configuration_file_not_found(self):
        """Test configuration loading with missing file."""
        config_manager = ConfigurationManager("nonexistent.json")
        
        with patch('os.path.exists', return_value=False):
            with patch.object(config_manager, '_create_default_configuration') as mock_create:
                config_manager.load_configuration()
                mock_create.assert_called_once()
    
    def test_load_configuration_invalid_json(self):
        """Test configuration loading with invalid JSON."""
        config_manager = ConfigurationManager("invalid.json")
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='{invalid json')):
                with pytest.raises(ConfigurationError, match="Invalid JSON"):
                    config_manager.load_configuration()
    
    def test_validation_rules_creation(self):
        """Test validation rules creation."""
        config_manager = ConfigurationManager()
        rules = config_manager.validation_rules
        
        # Check that all sections have rules
        assert ConfigSection.SIMULATION.value in rules
        assert ConfigSection.TIMING.value in rules
        assert ConfigSection.ENGINE.value in rules
        assert ConfigSection.PERFORMANCE.value in rules
        assert ConfigSection.WAREHOUSE.value in rules
        assert ConfigSection.ROBOT.value in rules
        assert ConfigSection.ORDERS.value in rules
        
        # Check specific rules
        timing_rules = rules[ConfigSection.TIMING.value]
        fps_rule = next(rule for rule in timing_rules if rule.key == "target_fps")
        assert fps_rule.required
        assert fps_rule.data_type == int
        assert fps_rule.min_value == 1
        assert fps_rule.max_value == 240
    
    def test_validation_success(self, temp_config_file):
        """Test successful configuration validation."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()  # Should not raise
        
        assert config_manager.is_loaded
    
    def test_validation_missing_required_field(self):
        """Test validation with missing required field."""
        config_data = {
            "simulation": {
                "name": "Test Simulation"
                # Missing required "version" field
            },
            "timing": {
                "target_fps": 60,
                "tick_interval": 0.016667,
                "simulation_speed": 1.0,
                "max_delta_time": 0.1
            }
        }
        
        config_manager = ConfigurationManager()
        config_manager.config_data = config_data
        
        with pytest.raises(ConfigurationError, match="Missing required field"):
            config_manager._validate_configuration()
    
    def test_validation_type_mismatch(self):
        """Test validation with type mismatch."""
        config_data = {
            "timing": {
                "target_fps": "60",  # Should be int, not string
                "tick_interval": 0.016667,
                "simulation_speed": 1.0,
                "max_delta_time": 0.1
            }
        }
        
        config_manager = ConfigurationManager()
        config_manager.config_data = config_data
        
        with pytest.raises(ConfigurationError, match="Type mismatch"):
            config_manager._validate_configuration()
    
    def test_validation_value_out_of_range(self):
        """Test validation with value out of range."""
        config_data = {
            "timing": {
                "target_fps": 500,  # Too high
                "tick_interval": 0.016667,
                "simulation_speed": 1.0,
                "max_delta_time": 0.1
            }
        }
        
        config_manager = ConfigurationManager()
        config_manager.config_data = config_data
        
        with pytest.raises(ConfigurationError, match="Value too high"):
            config_manager._validate_configuration()
    
    def test_get_value(self, temp_config_file):
        """Test getting configuration values."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        # Test existing value
        assert config_manager.get_value("simulation", "name") == "Test Simulation"
        assert config_manager.get_value("timing", "target_fps") == 60
        
        # Test non-existent value with default
        assert config_manager.get_value("nonexistent", "key", "default") == "default"
        
        # Test non-existent value without default
        assert config_manager.get_value("nonexistent", "key") is None
    
    def test_set_value(self, temp_config_file):
        """Test setting configuration values."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        # Set existing value
        config_manager.set_value("timing", "target_fps", 120)
        assert config_manager.get_value("timing", "target_fps") == 120
        
        # Set value in new section
        config_manager.set_value("new_section", "new_key", "new_value")
        assert config_manager.get_value("new_section", "new_key") == "new_value"
    
    def test_save_configuration(self, temp_config_file):
        """Test saving configuration."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        # Modify value
        config_manager.set_value("timing", "target_fps", 120)
        
        # Save configuration
        config_manager.save_configuration()
        
        # Load again and verify
        config_manager2 = ConfigurationManager(temp_config_file)
        config_manager2.load_configuration()
        assert config_manager2.get_value("timing", "target_fps") == 120
    
    def test_get_configuration_summary(self, temp_config_file):
        """Test getting configuration summary."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        summary = config_manager.get_configuration_summary()
        
        assert summary["config_path"] == temp_config_file
        assert summary["is_loaded"] is True
        assert "sections" in summary
        assert "timing_constants" in summary
        assert "warehouse_constants" in summary
        assert "robot_constants" in summary
        assert "order_constants" in summary
        
        # Check constants
        assert summary["timing_constants"]["target_fps"] == 60
        assert summary["warehouse_constants"]["aisles"] == 25
        assert summary["robot_constants"]["movement_speed"] == 2.0
        assert summary["order_constants"]["generation_interval"] == 40
    
    def test_reload_configuration(self, temp_config_file):
        """Test reloading configuration."""
        config_manager = ConfigurationManager(temp_config_file)
        config_manager.load_configuration()
        
        # Modify config data in memory
        config_manager.config_data["timing"]["target_fps"] = 999
        
        # Reload should restore original values
        config_manager.reload_configuration()
        assert config_manager.get_value("timing", "target_fps") == 60


class TestConfigurationConstants:
    """Test cases for configuration constants."""
    
    def test_timing_constants_validation(self):
        """Test timing constants validation."""
        # Valid constants
        constants = SimulationTimingConstants()
        assert constants.TARGET_FPS == 60
        assert constants.TICK_INTERVAL == 1.0 / 60.0
        
        # Invalid TARGET_FPS
        with pytest.raises(ConfigurationError, match="TARGET_FPS must be positive"):
            SimulationTimingConstants(TARGET_FPS=0)
        
        # Invalid TICK_INTERVAL
        with pytest.raises(ConfigurationError, match="TICK_INTERVAL must be positive"):
            SimulationTimingConstants(TICK_INTERVAL=0)
    
    def test_warehouse_constants_validation(self):
        """Test warehouse constants validation."""
        # Valid constants
        constants = WarehouseConstants()
        assert constants.AISLES == 25
        assert constants.RACKS == 20
        assert constants.TOTAL_STORAGE_LOCATIONS == 500
        
        # Invalid AISLES
        with pytest.raises(ConfigurationError, match="AISLES must be positive"):
            WarehouseConstants(AISLES=0)
        
        # Invalid base location
        with pytest.raises(ConfigurationError, match="BASE_AISLE must be within warehouse bounds"):
            WarehouseConstants(BASE_AISLE=30)
    
    def test_robot_constants_validation(self):
        """Test robot constants validation."""
        # Valid constants
        constants = RobotConstants()
        assert constants.MOVEMENT_SPEED == 2.0
        assert constants.ANIMATION_SMOOTHING == 0.1
        
        # Invalid MOVEMENT_SPEED
        with pytest.raises(ConfigurationError, match="MOVEMENT_SPEED must be positive"):
            RobotConstants(MOVEMENT_SPEED=0)
        
        # Invalid ANIMATION_SMOOTHING
        with pytest.raises(ConfigurationError, match="ANIMATION_SMOOTHING must be between 0.0 and 1.0"):
            RobotConstants(ANIMATION_SMOOTHING=1.5)
    
    def test_order_constants_validation(self):
        """Test order constants validation."""
        # Valid constants
        constants = OrderConstants()
        assert constants.GENERATION_INTERVAL == 40
        assert constants.MAX_ITEMS_PER_ORDER == 4
        
        # Invalid GENERATION_INTERVAL
        with pytest.raises(ConfigurationError, match="GENERATION_INTERVAL must be positive"):
            OrderConstants(GENERATION_INTERVAL=0)
        
        # Invalid MAX_ITEMS_PER_ORDER
        with pytest.raises(ConfigurationError, match="MAX_ITEMS_PER_ORDER must be positive"):
            OrderConstants(MAX_ITEMS_PER_ORDER=0)


class TestConfigValidationRule:
    """Test cases for ConfigValidationRule."""
    
    def test_validation_rule_creation(self):
        """Test validation rule creation."""
        rule = ConfigValidationRule(
            key="test_key",
            required=True,
            data_type=int,
            min_value=1,
            max_value=100,
            default=50,
            description="Test rule"
        )
        
        assert rule.key == "test_key"
        assert rule.required is True
        assert rule.data_type == int
        assert rule.min_value == 1
        assert rule.max_value == 100
        assert rule.default == 50
        assert rule.description == "Test rule"


class TestGlobalConfigManager:
    """Test cases for global configuration manager."""
    
    def test_get_config_returns_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
        assert isinstance(config1, ConfigurationManager)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 