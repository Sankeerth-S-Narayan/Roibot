import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class OrderGenerationConfig:
    """Configuration for order generation settings."""
    generation_interval: float = 30.0  # seconds
    min_items_per_order: int = 1
    max_items_per_order: int = 4
    enabled: bool = True
    auto_start: bool = True

@dataclass
class RobotConfig:
    """Configuration for robot settings."""
    robot_id: str = "ROBOT_001"
    max_speed: float = 1.0  # units per second
    acceleration: float = 0.5  # units per second squared
    deceleration: float = 0.5  # units per second squared
    turning_speed: float = 0.3  # radians per second
    battery_capacity: float = 100.0  # percentage
    charging_rate: float = 10.0  # percentage per minute

@dataclass
class WarehouseLayoutConfig:
    """Configuration for warehouse layout parameters."""
    num_aisles: int = 20
    num_racks_per_aisle: int = 20
    aisle_width: float = 3.0  # meters
    rack_depth: float = 2.0  # meters
    rack_height: float = 5.0  # meters
    item_spacing: float = 0.5  # meters
    robot_start_position: Dict[str, int] = None  # Default to None, will be set to center

@dataclass
class AnalyticsConfig:
    """Configuration for analytics and performance thresholds."""
    efficiency_threshold: float = 0.7  # minimum acceptable efficiency
    completion_time_threshold: float = 300.0  # maximum acceptable completion time (seconds)
    distance_threshold: float = 1000.0  # maximum acceptable distance (units)
    direction_changes_threshold: int = 10  # maximum acceptable direction changes
    auto_export_interval: float = 300.0  # seconds
    export_directory: str = "exports"
    dashboard_refresh_interval: float = 1.0  # seconds

@dataclass
class ExportConfig:
    """Configuration for export settings."""
    export_formats: List[str] = None  # Default to ["json", "csv"]
    auto_export_enabled: bool = True
    export_filename_prefix: str = "warehouse_analytics"
    include_timestamps: bool = True
    compression_enabled: bool = False
    max_export_file_size: int = 100  # MB

@dataclass
class SystemConfig:
    """Overall system configuration."""
    log_level: str = "INFO"
    log_file: str = "warehouse_simulation.log"
    max_log_file_size: int = 10  # MB
    backup_logs: bool = True
    debug_mode: bool = False
    performance_monitoring: bool = True

@dataclass
class SimulationConfig:
    """Configuration for simulation settings."""
    path_optimization: Dict[str, Any] = None
    trail_config: Dict[str, Any] = None
    aisle_timing: Dict[str, Any] = None
    bidirectional_navigation: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.path_optimization is None:
            self.path_optimization = {
                "enabled": True,
                "algorithm": "bidirectional",
                "optimization_level": "medium"
            }
        if self.trail_config is None:
            self.trail_config = {
                "enabled": True,
                "max_trail_length": 100,
                "trail_decay_time": 30.0
            }
        if self.aisle_timing is None:
            self.aisle_timing = {
                "aisle_traversal_time": 7.0,
                "direction_change_cooldown": 0.5,
                "horizontal_movement_time": 0.35
            }
        if self.bidirectional_navigation is None:
            self.bidirectional_navigation = {
                "enabled": True,
                "performance_monitoring": {
                    "enabled": True,
                    "metrics_interval": 5.0
                }
            }

class ConfigurationManager:
    """
    Manages system-wide configuration for the warehouse simulation.
    
    Handles JSON-based configuration files with comprehensive validation,
    default values, and integration with all system components.
    """
    
    def __init__(self, config_file_path: str = "config/warehouse_config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file_path: Path to the JSON configuration file
        """
        self.config_file_path = Path(config_file_path)
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration sections
        self.order_generation = OrderGenerationConfig()
        self.robot = RobotConfig()
        self.warehouse_layout = WarehouseLayoutConfig()
        self.analytics = AnalyticsConfig()
        self.export = ExportConfig()
        self.system = SystemConfig()
        self.simulation = SimulationConfig()
        
        # Set default values for nested objects
        if self.warehouse_layout.robot_start_position is None:
            self.warehouse_layout.robot_start_position = {
                "aisle": self.warehouse_layout.num_aisles // 2,
                "rack": self.warehouse_layout.num_racks_per_aisle // 2
            }
        
        if self.export.export_formats is None:
            self.export.export_formats = ["json", "csv"]
        
        # Load configuration
        self.load_configuration()
        
        # Setup logging
        self._setup_logging()
        
        print(f"📋 ConfigurationManager initialized with config: {self.config_file_path}")
    
    def load_configuration(self) -> bool:
        """
        Load configuration from JSON file.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if self.config_file_path.exists():
                with open(self.config_file_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration sections
                self._update_config_section('order_generation', config_data.get('order_generation', {}))
                self._update_config_section('robot', config_data.get('robot', {}))
                self._update_config_section('warehouse_layout', config_data.get('warehouse_layout', {}))
                self._update_config_section('analytics', config_data.get('analytics', {}))
                self._update_config_section('export', config_data.get('export', {}))
                self._update_config_section('system', config_data.get('system', {}))
                self._update_config_section('simulation', config_data.get('simulation', {}))
                
                # Validate configuration
                self._validate_configuration()
                
                print(f"✅ Configuration loaded from {self.config_file_path}")
                return True
            else:
                # Create default configuration file
                self.save_configuration()
                print(f"📝 Created default configuration at {self.config_file_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """
        Save current configuration to JSON file.
        
        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            config_data = {
                'order_generation': asdict(self.order_generation),
                'robot': asdict(self.robot),
                'warehouse_layout': asdict(self.warehouse_layout),
                'analytics': asdict(self.analytics),
                'export': asdict(self.export),
                'system': asdict(self.system),
                'simulation': asdict(self.simulation)
            }
            
            with open(self.config_file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"💾 Configuration saved to {self.config_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def _update_config_section(self, section_name: str, section_data: Dict[str, Any]):
        """
        Update a configuration section with new data.
        
        Args:
            section_name: Name of the configuration section
            section_data: New configuration data
        """
        try:
            section = getattr(self, section_name)
            
            for key, value in section_data.items():
                if hasattr(section, key):
                    setattr(section, key, value)
                    
        except Exception as e:
            print(f"❌ Error updating {section_name} configuration: {e}")
    
    def _validate_configuration(self):
        """
        Validate the current configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        errors = []
        
        # Validate order generation
        if self.order_generation.generation_interval <= 0:
            errors.append("Order generation interval must be positive")
        if self.order_generation.min_items_per_order < 1:
            errors.append("Minimum items per order must be at least 1")
        if self.order_generation.max_items_per_order < self.order_generation.min_items_per_order:
            errors.append("Maximum items per order must be greater than or equal to minimum")
        if self.order_generation.max_items_per_order > 10:
            errors.append("Maximum items per order cannot exceed 10")
        
        # Validate robot settings
        if self.robot.max_speed <= 0:
            errors.append("Robot max speed must be positive")
        if self.robot.acceleration <= 0:
            errors.append("Robot acceleration must be positive")
        if self.robot.battery_capacity <= 0 or self.robot.battery_capacity > 100:
            errors.append("Robot battery capacity must be between 0 and 100")
        
        # Validate warehouse layout
        if self.warehouse_layout.num_aisles <= 0:
            errors.append("Number of aisles must be positive")
        if self.warehouse_layout.num_racks_per_aisle <= 0:
            errors.append("Number of racks per aisle must be positive")
        if self.warehouse_layout.aisle_width <= 0:
            errors.append("Aisle width must be positive")
        
        # Validate analytics thresholds
        if self.analytics.efficiency_threshold < 0 or self.analytics.efficiency_threshold > 1:
            errors.append("Efficiency threshold must be between 0 and 1")
        if self.analytics.completion_time_threshold <= 0:
            errors.append("Completion time threshold must be positive")
        if self.analytics.distance_threshold <= 0:
            errors.append("Distance threshold must be positive")
        if self.analytics.direction_changes_threshold < 0:
            errors.append("Direction changes threshold must be non-negative")
        if self.analytics.auto_export_interval <= 0:
            errors.append("Auto export interval must be positive")
        
        # Validate export settings
        if self.export.max_export_file_size <= 0:
            errors.append("Max export file size must be positive")
        if not self.export.export_formats:
            errors.append("Export formats cannot be empty")
        
        # Validate system settings
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.system.log_level not in valid_log_levels:
            errors.append(f"Log level must be one of: {valid_log_levels}")
        if self.system.max_log_file_size <= 0:
            errors.append("Max log file size must be positive")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"• {error}" for error in errors)
            raise ValueError(error_msg)
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        try:
            log_level = getattr(logging, self.system.log_level.upper())
            
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.system.log_file),
                    logging.StreamHandler()
                ]
            )
            
        except Exception as e:
            print(f"❌ Error setting up logging: {e}")
    
    def get_order_generation_config(self) -> OrderGenerationConfig:
        """Get order generation configuration."""
        return self.order_generation
    
    def get_robot_config(self) -> RobotConfig:
        """Get robot configuration."""
        return self.robot
    
    def get_warehouse_layout_config(self) -> WarehouseLayoutConfig:
        """Get warehouse layout configuration."""
        return self.warehouse_layout
    
    def get_analytics_config(self) -> AnalyticsConfig:
        """Get analytics configuration."""
        return self.analytics
    
    def get_export_config(self) -> ExportConfig:
        """Get export configuration."""
        return self.export
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration."""
        return self.system
    
    def get_simulation_config(self) -> SimulationConfig:
        """Get simulation configuration."""
        return self.simulation
    
    def update_configuration(self, section: str, key: str, value: Any) -> bool:
        """
        Update a specific configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key
            value: New value
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if hasattr(self, section):
                section_obj = getattr(self, section)
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
                    self._validate_configuration()
                    return True
                else:
                    print(f"❌ Configuration key '{key}' not found in section '{section}'")
                    return False
            else:
                print(f"❌ Configuration section '{section}' not found")
                return False
                
        except Exception as e:
            print(f"❌ Error updating configuration: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all configuration to default values."""
        try:
            self.order_generation = OrderGenerationConfig()
            self.robot = RobotConfig()
            self.warehouse_layout = WarehouseLayoutConfig()
            self.analytics = AnalyticsConfig()
            self.export = ExportConfig()
            self.system = SystemConfig()
            
            # Set default values for nested objects
            if self.warehouse_layout.robot_start_position is None:
                self.warehouse_layout.robot_start_position = {
                    "aisle": self.warehouse_layout.num_aisles // 2,
                    "rack": self.warehouse_layout.num_racks_per_aisle // 2
                }
            
            if self.export.export_formats is None:
                self.export.export_formats = ["json", "csv"]
            
            self._validate_configuration()
            print("🔄 Configuration reset to defaults")
            
        except Exception as e:
            print(f"❌ Error resetting configuration: {e}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        try:
            return {
                'config_file_path': str(self.config_file_path),
                'order_generation': {
                    'generation_interval': self.order_generation.generation_interval,
                    'item_range': f"{self.order_generation.min_items_per_order}-{self.order_generation.max_items_per_order}",
                    'enabled': self.order_generation.enabled
                },
                'robot': {
                    'robot_id': self.robot.robot_id,
                    'max_speed': self.robot.max_speed,
                    'battery_capacity': self.robot.battery_capacity
                },
                'warehouse_layout': {
                    'dimensions': f"{self.warehouse_layout.num_aisles}x{self.warehouse_layout.num_racks_per_aisle}",
                    'aisle_width': self.warehouse_layout.aisle_width,
                    'start_position': self.warehouse_layout.robot_start_position
                },
                'analytics': {
                    'efficiency_threshold': self.analytics.efficiency_threshold,
                    'auto_export_interval': self.analytics.auto_export_interval,
                    'export_directory': self.analytics.export_directory
                },
                'export': {
                    'formats': self.export.export_formats,
                    'auto_export_enabled': self.export.auto_export_enabled,
                    'compression_enabled': self.export.compression_enabled
                },
                'system': {
                    'log_level': self.system.log_level,
                    'debug_mode': self.system.debug_mode,
                    'performance_monitoring': self.system.performance_monitoring
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting configuration summary: {e}")
            return {}
    
    def validate_config_file(self, config_file_path: str) -> bool:
        """
        Validate a configuration file without loading it.
        
        Args:
            config_file_path: Path to the configuration file
            
        Returns:
            True if configuration file is valid, False otherwise
        """
        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)
            
            # Create temporary configuration manager to validate
            temp_config = ConfigurationManager(config_file_path)
            temp_config._validate_configuration()
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration file validation failed: {e}")
            return False 