"""
Comprehensive configuration management system for the Roibot warehouse simulation.
Provides robust configuration loading, validation, and extensibility.
"""

import json
import os
from typing import Dict, Any, Optional, List, Union, Type
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigSection(Enum):
    """Configuration section identifiers."""
    SIMULATION = "simulation"
    TIMING = "timing"
    ENGINE = "engine"
    PERFORMANCE = "performance"
    WAREHOUSE = "warehouse"
    ROBOT = "robot"
    ORDERS = "orders"
    ANALYTICS = "analytics"  # For future phases
    VISUALIZATION = "visualization"  # For future phases
    DASHBOARD = "dashboard"  # For future phases


@dataclass
class ConfigValidationRule:
    """Configuration validation rule definition."""
    key: str
    required: bool = True
    data_type: Type = str
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    default: Any = None
    description: str = ""


@dataclass
class SimulationTimingConstants:
    """Simulation timing constants with validation."""
    TARGET_FPS: int = 60
    TICK_INTERVAL: float = 1.0 / 60.0  # 60 FPS
    MAX_DELTA_TIME: float = 0.1  # Maximum time step
    SIMULATION_SPEED: float = 1.0
    FRAME_TIME_WARNING: float = 33.33  # ms
    FRAME_TIME_CRITICAL: float = 100.0  # ms
    
    def __post_init__(self):
        """Validate timing constants."""
        if self.TARGET_FPS <= 0:
            raise ConfigurationError("TARGET_FPS must be positive")
        if self.TICK_INTERVAL <= 0:
            raise ConfigurationError("TICK_INTERVAL must be positive")
        if self.SIMULATION_SPEED <= 0:
            raise ConfigurationError("SIMULATION_SPEED must be positive")
        
        print(f"✅ SimulationTimingConstants validated: {self.TARGET_FPS} FPS")


@dataclass
class WarehouseConstants:
    """Warehouse layout constants with validation."""
    AISLES: int = 25
    RACKS: int = 20
    TOTAL_STORAGE_LOCATIONS: int = field(init=False)
    BASE_AISLE: int = 0
    BASE_RACK: int = 0
    
    def __post_init__(self):
        """Calculate derived values and validate."""
        self.TOTAL_STORAGE_LOCATIONS = self.AISLES * self.RACKS
        
        if self.AISLES <= 0:
            raise ConfigurationError("AISLES must be positive")
        if self.RACKS <= 0:
            raise ConfigurationError("RACKS must be positive")
        if self.BASE_AISLE < 0 or self.BASE_AISLE >= self.AISLES:
            raise ConfigurationError("BASE_AISLE must be within warehouse bounds")
        if self.BASE_RACK < 0 or self.BASE_RACK >= self.RACKS:
            raise ConfigurationError("BASE_RACK must be within warehouse bounds")
        
        print(f"✅ WarehouseConstants validated: {self.AISLES}x{self.RACKS} = {self.TOTAL_STORAGE_LOCATIONS} locations")


@dataclass
class RobotConstants:
    """Robot behavior constants with validation."""
    MOVEMENT_SPEED: float = 2.0  # units per second
    ANIMATION_SMOOTHING: float = 0.1  # interpolation factor
    STATE_CHANGE_DELAY: float = 0.05  # seconds
    
    def __post_init__(self):
        """Validate robot constants."""
        if self.MOVEMENT_SPEED <= 0:
            raise ConfigurationError("MOVEMENT_SPEED must be positive")
        if not (0.0 <= self.ANIMATION_SMOOTHING <= 1.0):
            raise ConfigurationError("ANIMATION_SMOOTHING must be between 0.0 and 1.0")
        if self.STATE_CHANGE_DELAY < 0:
            raise ConfigurationError("STATE_CHANGE_DELAY must be non-negative")
        
        print(f"✅ RobotConstants validated: {self.MOVEMENT_SPEED} units/s speed")


@dataclass
class OrderConstants:
    """Order generation constants with validation."""
    GENERATION_INTERVAL: int = 40  # seconds
    MAX_ITEMS_PER_ORDER: int = 4
    CONTINUOUS_ASSIGNMENT: bool = True
    
    def __post_init__(self):
        """Validate order constants."""
        if self.GENERATION_INTERVAL <= 0:
            raise ConfigurationError("GENERATION_INTERVAL must be positive")
        if self.MAX_ITEMS_PER_ORDER <= 0:
            raise ConfigurationError("MAX_ITEMS_PER_ORDER must be positive")
        
        print(f"✅ OrderConstants validated: {self.GENERATION_INTERVAL}s interval, {self.MAX_ITEMS_PER_ORDER} max items")


class ConfigurationManager:
    """
    Comprehensive configuration management system.
    Handles loading, validation, and access to all configuration data.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (default: config/simulation.json)
        """
        self.config_path = config_path or "config/simulation.json"
        self.config_data: Dict[str, Any] = {}
        self.is_loaded = False
        
        # Initialize constants
        self.timing = SimulationTimingConstants()
        self.warehouse = WarehouseConstants()
        self.robot = RobotConstants()
        self.orders = OrderConstants()
        
        # Add simulation configuration
        self.simulation = {
            "path_optimization": {
                "enabled": True,
                "algorithm": "bidirectional",
                "optimization_level": "medium"
            },
            "trail_config": {
                "enabled": True,
                "max_trail_length": 100,
                "trail_decay_time": 30.0
            },
            "aisle_timing": {
                "aisle_traversal_time": 7.0,
                "direction_change_cooldown": 0.5,
                "horizontal_movement_time": 0.35
            },
            "bidirectional_navigation": {
                "enabled": True,
                "performance_monitoring": {
                    "enabled": True,
                    "metrics_interval": 5.0
                }
            }
        }
        
        # Define validation rules
        self.validation_rules = self._create_validation_rules()
        
        print("🔧 ConfigurationManager initialized")
    
    def _create_validation_rules(self) -> Dict[str, List[ConfigValidationRule]]:
        """Create comprehensive validation rules for all configuration sections."""
        return {
            ConfigSection.SIMULATION.value: [
                ConfigValidationRule("name", required=True, data_type=str, description="Simulation name"),
                ConfigValidationRule("version", required=True, data_type=str, description="Simulation version"),
                ConfigValidationRule("description", required=False, data_type=str, description="Simulation description")
            ],
            ConfigSection.TIMING.value: [
                ConfigValidationRule("target_fps", required=True, data_type=int, min_value=1, max_value=240, default=60, description="Target frames per second"),
                ConfigValidationRule("tick_interval", required=True, data_type=float, min_value=0.001, max_value=1.0, default=0.016667, description="Tick interval in seconds"),
                ConfigValidationRule("simulation_speed", required=True, data_type=float, min_value=0.1, max_value=10.0, default=1.0, description="Simulation speed multiplier"),
                ConfigValidationRule("max_delta_time", required=True, data_type=float, min_value=0.01, max_value=1.0, default=0.1, description="Maximum delta time per frame")
            ],
            ConfigSection.ENGINE.value: [
                ConfigValidationRule("event_queue_size", required=True, data_type=int, min_value=100, max_value=10000, default=1000, description="Maximum event queue size"),
                ConfigValidationRule("max_concurrent_events", required=True, data_type=int, min_value=10, max_value=1000, default=50, description="Maximum concurrent events"),
                ConfigValidationRule("performance_monitoring", required=True, data_type=bool, default=True, description="Enable performance monitoring"),
                ConfigValidationRule("debug_prints", required=True, data_type=bool, default=True, description="Enable debug print statements")
            ],
            ConfigSection.PERFORMANCE.value: [
                ConfigValidationRule("target_frame_time", required=True, data_type=float, min_value=5.0, max_value=200.0, default=16.67, description="Target frame time in milliseconds"),
                ConfigValidationRule("warning_frame_time", required=True, data_type=float, min_value=10.0, max_value=500.0, default=33.33, description="Warning frame time threshold"),
                ConfigValidationRule("critical_frame_time", required=True, data_type=float, min_value=20.0, max_value=1000.0, default=100.0, description="Critical frame time threshold")
            ],
            ConfigSection.WAREHOUSE.value: [
                ConfigValidationRule("aisles", required=True, data_type=int, min_value=1, max_value=100, default=25, description="Number of warehouse aisles"),
                ConfigValidationRule("racks", required=True, data_type=int, min_value=1, max_value=100, default=20, description="Number of racks per aisle"),
                ConfigValidationRule("base_location", required=True, data_type=dict, description="Robot base location coordinates")
            ],
            ConfigSection.ROBOT.value: [
                ConfigValidationRule("movement_speed", required=True, data_type=float, min_value=0.1, max_value=10.0, default=2.0, description="Robot movement speed"),
                ConfigValidationRule("animation_smoothing", required=True, data_type=float, min_value=0.0, max_value=1.0, default=0.1, description="Animation smoothing factor"),
                ConfigValidationRule("state_change_delay", required=True, data_type=float, min_value=0.0, max_value=1.0, default=0.05, description="State change delay in seconds")
            ],
            ConfigSection.ORDERS.value: [
                ConfigValidationRule("generation_interval", required=True, data_type=int, min_value=1, max_value=300, default=40, description="Order generation interval in seconds"),
                ConfigValidationRule("max_items_per_order", required=True, data_type=int, min_value=1, max_value=20, default=4, description="Maximum items per order"),
                ConfigValidationRule("continuous_assignment", required=True, data_type=bool, default=True, description="Enable continuous order assignment")
            ]
        }
    
    def load_configuration(self) -> None:
        """Load and validate configuration from file."""
        print(f"📁 Loading configuration from: {self.config_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(self.config_path):
                print(f"⚠️  Configuration file not found: {self.config_path}")
                print("🔧 Creating default configuration...")
                self._create_default_configuration()
                return
            
            # Load JSON file
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            
            print("✅ Configuration file loaded successfully")
            
            # Validate configuration
            self._validate_configuration()
            
            # Update constants with loaded values
            self._update_constants()
            
            self.is_loaded = True
            print("🎯 Configuration loaded and validated successfully")
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in configuration file: {e}"
            print(f"❌ {error_msg}")
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Error loading configuration: {e}"
            print(f"❌ {error_msg}")
            raise ConfigurationError(error_msg)
    
    def _validate_configuration(self) -> None:
        """Validate configuration data against rules."""
        print("🔍 Validating configuration...")
        
        validation_errors = []
        
        for section_name, rules in self.validation_rules.items():
            section_data = self.config_data.get(section_name, {})
            
            for rule in rules:
                # Check if required field exists
                if rule.required and rule.key not in section_data:
                    if rule.default is not None:
                        section_data[rule.key] = rule.default
                        print(f"🔧 Applied default value for {section_name}.{rule.key}: {rule.default}")
                    else:
                        validation_errors.append(f"Missing required field: {section_name}.{rule.key}")
                        continue
                
                # Skip validation if field doesn't exist and isn't required
                if rule.key not in section_data:
                    continue
                
                value = section_data[rule.key]
                
                # Type validation
                if not isinstance(value, rule.data_type):
                    validation_errors.append(f"Type mismatch for {section_name}.{rule.key}: expected {rule.data_type.__name__}, got {type(value).__name__}")
                    continue
                
                # Range validation for numeric types
                if isinstance(value, (int, float)):
                    if rule.min_value is not None and value < rule.min_value:
                        validation_errors.append(f"Value too low for {section_name}.{rule.key}: {value} < {rule.min_value}")
                    if rule.max_value is not None and value > rule.max_value:
                        validation_errors.append(f"Value too high for {section_name}.{rule.key}: {value} > {rule.max_value}")
                
                # Allowed values validation
                if rule.allowed_values is not None and value not in rule.allowed_values:
                    validation_errors.append(f"Invalid value for {section_name}.{rule.key}: {value} not in {rule.allowed_values}")
        
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in validation_errors)
            print(f"❌ {error_msg}")
            raise ConfigurationError(error_msg)
        
        print("✅ Configuration validation passed")
    
    def _update_constants(self) -> None:
        """Update constant objects with loaded configuration values."""
        print("🔄 Updating constants with configuration values...")
        
        # Update timing constants
        timing_data = self.config_data.get(ConfigSection.TIMING.value, {})
        self.timing = SimulationTimingConstants(
            TARGET_FPS=timing_data.get("target_fps", 60),
            TICK_INTERVAL=timing_data.get("tick_interval", 1.0/60.0),
            SIMULATION_SPEED=timing_data.get("simulation_speed", 1.0),
            MAX_DELTA_TIME=timing_data.get("max_delta_time", 0.1),
            FRAME_TIME_WARNING=self.config_data.get("performance", {}).get("warning_frame_time", 33.33),
            FRAME_TIME_CRITICAL=self.config_data.get("performance", {}).get("critical_frame_time", 100.0)
        )
        
        # Update warehouse constants
        warehouse_data = self.config_data.get(ConfigSection.WAREHOUSE.value, {})
        self.warehouse = WarehouseConstants(
            AISLES=warehouse_data.get("aisles", 25),
            RACKS=warehouse_data.get("racks", 20),
            BASE_AISLE=warehouse_data.get("base_location", {}).get("aisle", 0),
            BASE_RACK=warehouse_data.get("base_location", {}).get("rack", 0)
        )
        
        # Update robot constants
        robot_data = self.config_data.get(ConfigSection.ROBOT.value, {})
        self.robot = RobotConstants(
            MOVEMENT_SPEED=robot_data.get("movement_speed", 2.0),
            ANIMATION_SMOOTHING=robot_data.get("animation_smoothing", 0.1),
            STATE_CHANGE_DELAY=robot_data.get("state_change_delay", 0.05)
        )
        
        # Update order constants
        orders_data = self.config_data.get(ConfigSection.ORDERS.value, {})
        self.orders = OrderConstants(
            GENERATION_INTERVAL=orders_data.get("generation_interval", 40),
            MAX_ITEMS_PER_ORDER=orders_data.get("max_items_per_order", 4),
            CONTINUOUS_ASSIGNMENT=orders_data.get("continuous_assignment", True)
        )
        
        print("✅ Constants updated successfully")
    
    def _create_default_configuration(self) -> None:
        """Create default configuration file."""
        default_config = {
            "simulation": {
                "name": "Roibot Warehouse Simulation",
                "version": "1.0.0",
                "description": "E-commerce warehouse robot simulation with bidirectional snake path navigation"
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
                "base_location": {
                    "aisle": 0,
                    "rack": 0
                }
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
        
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(self.config_path)
        if config_dir:  # Only create directory if path contains a directory
            os.makedirs(config_dir, exist_ok=True)
        
        # Write default configuration
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config_data = default_config
        self._update_constants()
        self.is_loaded = True
        
        print(f"✅ Default configuration created at: {self.config_path}")
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value by section and key.
        
        Args:
            section: Configuration section name
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if not self.is_loaded:
            print("⚠️  Configuration not loaded, loading now...")
            self.load_configuration()
        
        return self.config_data.get(section, {}).get(key, default)
    
    def set_value(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value by section and key.
        
        Args:
            section: Configuration section name
            key: Configuration key
            value: New value
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        
        self.config_data[section][key] = value
        print(f"🔧 Configuration updated: {section}.{key} = {value}")
    
    def save_configuration(self) -> None:
        """Save current configuration to file."""
        print(f"💾 Saving configuration to: {self.config_path}")
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            print("✅ Configuration saved successfully")
            
        except Exception as e:
            error_msg = f"Error saving configuration: {e}"
            print(f"❌ {error_msg}")
            raise ConfigurationError(error_msg)
    
    def get_all_sections(self) -> List[str]:
        """Get list of all configuration sections."""
        return list(self.config_data.keys())
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self.config_data.get(section, {})
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            "config_path": self.config_path,
            "is_loaded": self.is_loaded,
            "sections": self.get_all_sections(),
            "validation_rules_count": sum(len(rules) for rules in self.validation_rules.values()),
            "timing_constants": {
                "target_fps": self.timing.TARGET_FPS,
                "simulation_speed": self.timing.SIMULATION_SPEED
            },
            "warehouse_constants": {
                "aisles": self.warehouse.AISLES,
                "racks": self.warehouse.RACKS,
                "total_locations": self.warehouse.TOTAL_STORAGE_LOCATIONS
            },
            "robot_constants": {
                "movement_speed": self.robot.MOVEMENT_SPEED
            },
            "order_constants": {
                "generation_interval": self.orders.GENERATION_INTERVAL,
                "max_items_per_order": self.orders.MAX_ITEMS_PER_ORDER
            }
        }
    
    def reload_configuration(self) -> None:
        """Reload configuration from file."""
        print("🔄 Reloading configuration...")
        self.is_loaded = False
        self.config_data = {}
        self.load_configuration()
        print("✅ Configuration reloaded successfully")


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_config() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return config_manager 