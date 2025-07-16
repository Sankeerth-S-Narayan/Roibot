"""
Configuration management for bidirectional navigation.

Handles configuration loading, validation, and access for bidirectional
navigation settings including path optimization, performance monitoring,
and debugging options.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..main_config import get_config


@dataclass
class PathOptimizationConfig:
    """Configuration for path optimization settings."""
    enable_shortest_path: bool = True
    enable_direction_optimization: bool = True
    enable_snake_pattern_integrity: bool = True
    max_path_calculation_time: float = 0.1


@dataclass
class PerformanceMonitoringConfig:
    """Configuration for performance monitoring settings."""
    enable_path_calculation_timing: bool = True
    enable_direction_change_tracking: bool = True
    enable_movement_efficiency_tracking: bool = True
    performance_warning_threshold: float = 0.05


@dataclass
class DebuggingConfig:
    """Configuration for debugging settings."""
    enable_path_visualization: bool = False
    enable_direction_debug: bool = False
    enable_timing_debug: bool = False
    log_level: str = "info"


@dataclass
class BidirectionalNavigationConfig:
    """Complete configuration for bidirectional navigation."""
    aisle_traversal_time: float = 7.0
    direction_change_cooldown: float = 0.5
    path_optimization: PathOptimizationConfig = None
    performance_monitoring: PerformanceMonitoringConfig = None
    debugging: DebuggingConfig = None
    
    def __post_init__(self):
        if self.path_optimization is None:
            self.path_optimization = PathOptimizationConfig()
        if self.performance_monitoring is None:
            self.performance_monitoring = PerformanceMonitoringConfig()
        if self.debugging is None:
            self.debugging = DebuggingConfig()


class BidirectionalConfigManager:
    """
    Manages configuration for bidirectional navigation.
    
    Handles loading, validation, and access to bidirectional navigation
    settings including path optimization, performance monitoring, and debugging.
    """
    
    def __init__(self):
        """Initialize the bidirectional configuration manager."""
        self.config = BidirectionalNavigationConfig()
        self.logger = logging.getLogger(__name__)
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from the main config manager."""
        try:
            config_manager = get_config()
            bidirectional_config = config_manager.get_value("simulation", "bidirectional_navigation", {})
            
            # Load basic settings
            self.config.aisle_traversal_time = bidirectional_config.get("aisle_traversal_time", 7.0)
            self.config.direction_change_cooldown = bidirectional_config.get("direction_change_cooldown", 0.5)
            
            # Load path optimization settings
            path_opt_config = bidirectional_config.get("path_optimization", {})
            self.config.path_optimization.enable_shortest_path = path_opt_config.get("enable_shortest_path", True)
            self.config.path_optimization.enable_direction_optimization = path_opt_config.get("enable_direction_optimization", True)
            self.config.path_optimization.enable_snake_pattern_integrity = path_opt_config.get("enable_snake_pattern_integrity", True)
            self.config.path_optimization.max_path_calculation_time = path_opt_config.get("max_path_calculation_time", 0.1)
            
            # Load performance monitoring settings
            perf_config = bidirectional_config.get("performance_monitoring", {})
            self.config.performance_monitoring.enable_path_calculation_timing = perf_config.get("enable_path_calculation_timing", True)
            self.config.performance_monitoring.enable_direction_change_tracking = perf_config.get("enable_direction_change_tracking", True)
            self.config.performance_monitoring.enable_movement_efficiency_tracking = perf_config.get("enable_movement_efficiency_tracking", True)
            self.config.performance_monitoring.performance_warning_threshold = perf_config.get("performance_warning_threshold", 0.05)
            
            # Load debugging settings
            debug_config = bidirectional_config.get("debugging", {})
            self.config.debugging.enable_path_visualization = debug_config.get("enable_path_visualization", False)
            self.config.debugging.enable_direction_debug = debug_config.get("enable_direction_debug", False)
            self.config.debugging.enable_timing_debug = debug_config.get("enable_timing_debug", False)
            self.config.debugging.log_level = debug_config.get("log_level", "info")
            
            self.logger.info("Bidirectional navigation configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load bidirectional navigation configuration: {e}")
            # Use default configuration
            self._set_default_configuration()
    
    def _set_default_configuration(self) -> None:
        """Set default configuration values."""
        self.logger.warning("Using default bidirectional navigation configuration")
        self.config = BidirectionalNavigationConfig()
    
    def validate_configuration(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate basic settings
            if self.config.aisle_traversal_time <= 0:
                self.logger.error("Aisle traversal time must be positive")
                return False
            
            if self.config.direction_change_cooldown < 0:
                self.logger.error("Direction change cooldown must be non-negative")
                return False
            
            # Validate path optimization settings
            if self.config.path_optimization.max_path_calculation_time <= 0:
                self.logger.error("Max path calculation time must be positive")
                return False
            
            # Validate performance monitoring settings
            if self.config.performance_monitoring.performance_warning_threshold <= 0:
                self.logger.error("Performance warning threshold must be positive")
                return False
            
            # Validate debugging settings
            valid_log_levels = ["debug", "info", "warning", "error"]
            if self.config.debugging.log_level not in valid_log_levels:
                self.logger.error(f"Invalid log level: {self.config.debugging.log_level}")
                return False
            
            self.logger.info("Bidirectional navigation configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_aisle_traversal_time(self) -> float:
        """Get the aisle traversal time setting."""
        return self.config.aisle_traversal_time
    
    def get_direction_change_cooldown(self) -> float:
        """Get the direction change cooldown setting."""
        return self.config.direction_change_cooldown
    
    def is_shortest_path_enabled(self) -> bool:
        """Check if shortest path calculation is enabled."""
        return self.config.path_optimization.enable_shortest_path
    
    def is_direction_optimization_enabled(self) -> bool:
        """Check if direction optimization is enabled."""
        return self.config.path_optimization.enable_direction_optimization
    
    def is_snake_pattern_integrity_enabled(self) -> bool:
        """Check if snake pattern integrity is enabled."""
        return self.config.path_optimization.enable_snake_pattern_integrity
    
    def get_max_path_calculation_time(self) -> float:
        """Get the maximum path calculation time."""
        return self.config.path_optimization.max_path_calculation_time
    
    def is_path_calculation_timing_enabled(self) -> bool:
        """Check if path calculation timing is enabled."""
        return self.config.performance_monitoring.enable_path_calculation_timing
    
    def is_direction_change_tracking_enabled(self) -> bool:
        """Check if direction change tracking is enabled."""
        return self.config.performance_monitoring.enable_direction_change_tracking
    
    def is_movement_efficiency_tracking_enabled(self) -> bool:
        """Check if movement efficiency tracking is enabled."""
        return self.config.performance_monitoring.enable_movement_efficiency_tracking
    
    def get_performance_warning_threshold(self) -> float:
        """Get the performance warning threshold."""
        return self.config.performance_monitoring.performance_warning_threshold
    
    def is_path_visualization_enabled(self) -> bool:
        """Check if path visualization is enabled."""
        return self.config.debugging.enable_path_visualization
    
    def is_direction_debug_enabled(self) -> bool:
        """Check if direction debugging is enabled."""
        return self.config.debugging.enable_direction_debug
    
    def is_timing_debug_enabled(self) -> bool:
        """Check if timing debugging is enabled."""
        return self.config.debugging.enable_timing_debug
    
    def get_log_level(self) -> str:
        """Get the logging level."""
        return self.config.debugging.log_level
    
    def reload_configuration(self) -> None:
        """Reload configuration from the main config manager."""
        self._load_configuration()
        if self.validate_configuration():
            self.logger.info("Bidirectional navigation configuration reloaded successfully")
        else:
            self.logger.error("Failed to reload bidirectional navigation configuration")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.
        
        Returns:
            Dictionary containing configuration summary
        """
        return {
            "aisle_traversal_time": self.config.aisle_traversal_time,
            "direction_change_cooldown": self.config.direction_change_cooldown,
            "path_optimization": {
                "enable_shortest_path": self.config.path_optimization.enable_shortest_path,
                "enable_direction_optimization": self.config.path_optimization.enable_direction_optimization,
                "enable_snake_pattern_integrity": self.config.path_optimization.enable_snake_pattern_integrity,
                "max_path_calculation_time": self.config.path_optimization.max_path_calculation_time
            },
            "performance_monitoring": {
                "enable_path_calculation_timing": self.config.performance_monitoring.enable_path_calculation_timing,
                "enable_direction_change_tracking": self.config.performance_monitoring.enable_direction_change_tracking,
                "enable_movement_efficiency_tracking": self.config.performance_monitoring.enable_movement_efficiency_tracking,
                "performance_warning_threshold": self.config.performance_monitoring.performance_warning_threshold
            },
            "debugging": {
                "enable_path_visualization": self.config.debugging.enable_path_visualization,
                "enable_direction_debug": self.config.debugging.enable_direction_debug,
                "enable_timing_debug": self.config.debugging.enable_timing_debug,
                "log_level": self.config.debugging.log_level
            }
        }


# Global instance for easy access
_bidirectional_config_manager: Optional[BidirectionalConfigManager] = None


def get_bidirectional_config() -> BidirectionalConfigManager:
    """
    Get the global bidirectional configuration manager instance.
    
    Returns:
        BidirectionalConfigManager instance
    """
    global _bidirectional_config_manager
    if _bidirectional_config_manager is None:
        _bidirectional_config_manager = BidirectionalConfigManager()
    return _bidirectional_config_manager 