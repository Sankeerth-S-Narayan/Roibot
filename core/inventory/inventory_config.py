"""
Inventory Configuration Management and Performance Monitoring

This module provides configuration management, performance monitoring,
and analytics for the inventory system.
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .inventory_manager import InventoryManager
from .inventory_sync import InventorySyncManager


class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    OPERATION_TIME = "operation_time"
    MEMORY_USAGE = "memory_usage"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class InventoryConfig:
    """Inventory configuration settings"""
    # Warehouse dimensions
    warehouse_width: int = 26
    warehouse_height: int = 20
    packout_zone_x: int = 1
    packout_zone_y: int = 1
    packout_zone_width: int = 1
    packout_zone_height: int = 1
    
    # Item generation settings
    total_items: int = 500
    item_id_prefix: str = "ITEM_"
    max_items_per_letter: int = 20
    
    # Performance settings
    max_operation_time_ms: float = 10.0
    max_memory_usage_mb: float = 100.0
    performance_monitoring_enabled: bool = True
    debug_mode: bool = False
    
    # Event settings
    event_buffer_size: int = 1000
    event_flush_interval_seconds: float = 5.0
    
    # Validation settings
    strict_validation: bool = True
    allow_duplicate_items: bool = False
    allow_invalid_locations: bool = False


class InventoryConfigManager:
    """
    Manages inventory configuration and validation.
    
    Features:
    - Configuration loading and validation
    - Performance monitoring
    - Analytics and metrics
    - Debugging tools
    """
    
    def __init__(self, config_file: str = "config/simulation.json"):
        """
        Initialize InventoryConfigManager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = InventoryConfig()
        self._performance_metrics: List[PerformanceMetric] = []
        self._lock = threading.RLock()
        self._monitoring_enabled = True
        self._debug_mode = False
    
    def load_configuration(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Extract inventory configuration
            inventory_config = data.get("inventory", {})
            
            # Update configuration with loaded values
            for key, value in inventory_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self._monitoring_enabled = self.config.performance_monitoring_enabled
            self._debug_mode = self.config.debug_mode
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            # Load existing configuration
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Update inventory section
            inventory_config = {}
            for field in self.config.__dataclass_fields__:
                inventory_config[field] = getattr(self.config, field)
            
            data["inventory"] = inventory_config
            
            # Save updated configuration
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def validate_configuration(self) -> Dict:
        """
        Validate current configuration.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate warehouse dimensions
        if self.config.warehouse_width <= 0:
            validation_results["errors"].append("warehouse_width must be positive")
            validation_results["valid"] = False
        
        if self.config.warehouse_height <= 0:
            validation_results["errors"].append("warehouse_height must be positive")
            validation_results["valid"] = False
        
        # Validate packout zone
        if (self.config.packout_zone_x < 0 or 
            self.config.packout_zone_y < 0 or
            self.config.packout_zone_width <= 0 or
            self.config.packout_zone_height <= 0):
            validation_results["errors"].append("Invalid packout zone configuration")
            validation_results["valid"] = False
        
        # Check if packout zone is within warehouse bounds
        if (self.config.packout_zone_x + self.config.packout_zone_width > self.config.warehouse_width or
            self.config.packout_zone_y + self.config.packout_zone_height > self.config.warehouse_height):
            validation_results["errors"].append("Packout zone outside warehouse bounds")
            validation_results["valid"] = False
        
        # Validate item generation settings
        if self.config.total_items <= 0:
            validation_results["errors"].append("total_items must be positive")
            validation_results["valid"] = False
        
        if self.config.max_items_per_letter <= 0:
            validation_results["errors"].append("max_items_per_letter must be positive")
            validation_results["valid"] = False
        
        # Check if warehouse can accommodate items
        available_locations = (self.config.warehouse_width * self.config.warehouse_height - 
                             self.config.packout_zone_width * self.config.packout_zone_height)
        
        if self.config.total_items > available_locations:
            validation_results["errors"].append(
                f"Insufficient warehouse space: {self.config.total_items} items need "
                f"{available_locations} locations"
            )
            validation_results["valid"] = False
        
        # Validate performance settings
        if self.config.max_operation_time_ms <= 0:
            validation_results["warnings"].append("max_operation_time_ms should be positive")
        
        if self.config.max_memory_usage_mb <= 0:
            validation_results["warnings"].append("max_memory_usage_mb should be positive")
        
        return validation_results
    
    def record_performance_metric(self, metric_type: PerformanceMetricType, 
                                value: float, metadata: Dict = None) -> None:
        """
        Record a performance metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            metadata: Additional metadata
        """
        if not self._monitoring_enabled:
            return
        
        with self._lock:
            metric = PerformanceMetric(
                metric_type=metric_type,
                value=value,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            
            self._performance_metrics.append(metric)
            
            # Keep only recent metrics (last 1000)
            if len(self._performance_metrics) > 1000:
                self._performance_metrics = self._performance_metrics[-1000:]
    
    def get_performance_metrics(self, metric_type: Optional[PerformanceMetricType] = None,
                              time_window_seconds: Optional[float] = None) -> List[PerformanceMetric]:
        """
        Get performance metrics.
        
        Args:
            metric_type: Filter by metric type (optional)
            time_window_seconds: Filter by time window (optional)
            
        Returns:
            List of performance metrics
        """
        with self._lock:
            metrics = self._performance_metrics.copy()
        
        # Filter by metric type
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # Filter by time window
        if time_window_seconds:
            cutoff_time = time.time() - time_window_seconds
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return metrics
    
    def get_performance_analytics(self, time_window_seconds: float = 3600) -> Dict:
        """
        Get comprehensive performance analytics.
        
        Args:
            time_window_seconds: Time window for analytics (default: 1 hour)
            
        Returns:
            Dictionary with performance analytics
        """
        with self._lock:
            recent_metrics = [m for m in self._performance_metrics 
                            if m.timestamp >= time.time() - time_window_seconds]
        
        analytics = {
            "time_window_seconds": time_window_seconds,
            "total_metrics": len(recent_metrics),
            "metric_types": {},
            "performance_summary": {}
        }
        
        # Group metrics by type
        for metric in recent_metrics:
            metric_type = metric.metric_type.value
            if metric_type not in analytics["metric_types"]:
                analytics["metric_types"][metric_type] = []
            analytics["metric_types"][metric_type].append(metric.value)
        
        # Calculate statistics for each metric type
        for metric_type, values in analytics["metric_types"].items():
            if values:
                analytics["performance_summary"][metric_type] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "average": sum(values) / len(values),
                    "latest": values[-1] if values else 0
                }
        
        return analytics
    
    def check_performance_thresholds(self) -> Dict:
        """
        Check if performance metrics exceed thresholds.
        
        Returns:
            Dictionary with threshold violations
        """
        violations = {
            "operation_time_violations": [],
            "memory_usage_violations": [],
            "throughput_violations": [],
            "error_rate_violations": []
        }
        
        # Get recent metrics
        recent_metrics = self.get_performance_metrics(time_window_seconds=300)  # Last 5 minutes
        
        for metric in recent_metrics:
            if metric.metric_type == PerformanceMetricType.OPERATION_TIME:
                if metric.value > self.config.max_operation_time_ms:
                    violations["operation_time_violations"].append({
                        "value": metric.value,
                        "threshold": self.config.max_operation_time_ms,
                        "timestamp": metric.timestamp
                    })
            
            elif metric.metric_type == PerformanceMetricType.MEMORY_USAGE:
                if metric.value > self.config.max_memory_usage_mb:
                    violations["memory_usage_violations"].append({
                        "value": metric.value,
                        "threshold": self.config.max_memory_usage_mb,
                        "timestamp": metric.timestamp
                    })
        
        return violations
    
    def get_debug_info(self, inventory_manager: InventoryManager = None,
                      sync_manager: InventorySyncManager = None) -> Dict:
        """
        Get comprehensive debug information.
        
        Args:
            inventory_manager: InventoryManager instance (optional)
            sync_manager: InventorySyncManager instance (optional)
            
        Returns:
            Dictionary with debug information
        """
        debug_info = {
            "configuration": {
                "warehouse_dimensions": {
                    "width": self.config.warehouse_width,
                    "height": self.config.warehouse_height
                },
                "packout_zone": {
                    "x": self.config.packout_zone_x,
                    "y": self.config.packout_zone_y,
                    "width": self.config.packout_zone_width,
                    "height": self.config.packout_zone_height
                },
                "item_generation": {
                    "total_items": self.config.total_items,
                    "item_id_prefix": self.config.item_id_prefix,
                    "max_items_per_letter": self.config.max_items_per_letter
                },
                "performance": {
                    "max_operation_time_ms": self.config.max_operation_time_ms,
                    "max_memory_usage_mb": self.config.max_memory_usage_mb,
                    "monitoring_enabled": self.config.performance_monitoring_enabled,
                    "debug_mode": self.config.debug_mode
                }
            },
            "performance_metrics": {
                "total_metrics": len(self._performance_metrics),
                "monitoring_enabled": self._monitoring_enabled,
                "debug_mode": self._debug_mode
            }
        }
        
        # Add inventory manager debug info
        if inventory_manager:
            try:
                stats = inventory_manager.get_inventory_statistics()
                debug_info["inventory_manager"] = {
                    "initialized": stats.get("initialized", False),
                    "total_items": stats.get("total_items", 0),
                    "items_with_stock": stats.get("items_with_stock", 0),
                    "items_out_of_stock": stats.get("items_out_of_stock", 0)
                }
            except Exception as e:
                debug_info["inventory_manager"] = {"error": str(e)}
        
        # Add sync manager debug info
        if sync_manager:
            try:
                sync_stats = sync_manager.get_sync_statistics()
                debug_info["sync_manager"] = {
                    "total_orders": sync_stats.get("total_orders", 0),
                    "completed_orders": sync_stats.get("completed_orders", 0),
                    "cancelled_orders": sync_stats.get("cancelled_orders", 0),
                    "completion_rate": sync_stats.get("completion_rate", 0)
                }
            except Exception as e:
                debug_info["sync_manager"] = {"error": str(e)}
        
        return debug_info
    
    def export_configuration(self) -> Dict:
        """
        Export current configuration as dictionary.
        
        Returns:
            Dictionary with configuration
        """
        return {
            "warehouse_dimensions": {
                "width": self.config.warehouse_width,
                "height": self.config.warehouse_height
            },
            "packout_zone": {
                "x": self.config.packout_zone_x,
                "y": self.config.packout_zone_y,
                "width": self.config.packout_zone_width,
                "height": self.config.packout_zone_height
            },
            "item_generation": {
                "total_items": self.config.total_items,
                "item_id_prefix": self.config.item_id_prefix,
                "max_items_per_letter": self.config.max_items_per_letter
            },
            "performance": {
                "max_operation_time_ms": self.config.max_operation_time_ms,
                "max_memory_usage_mb": self.config.max_memory_usage_mb,
                "performance_monitoring_enabled": self.config.performance_monitoring_enabled,
                "debug_mode": self.config.debug_mode
            },
            "events": {
                "event_buffer_size": self.config.event_buffer_size,
                "event_flush_interval_seconds": self.config.event_flush_interval_seconds
            },
            "validation": {
                "strict_validation": self.config.strict_validation,
                "allow_duplicate_items": self.config.allow_duplicate_items,
                "allow_invalid_locations": self.config.allow_invalid_locations
            }
        }
    
    def import_configuration(self, config_data: Dict) -> bool:
        """
        Import configuration from dictionary.
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            # Update warehouse dimensions
            if "warehouse_dimensions" in config_data:
                warehouse = config_data["warehouse_dimensions"]
                self.config.warehouse_width = warehouse.get("width", self.config.warehouse_width)
                self.config.warehouse_height = warehouse.get("height", self.config.warehouse_height)
            
            # Update packout zone
            if "packout_zone" in config_data:
                packout = config_data["packout_zone"]
                self.config.packout_zone_x = packout.get("x", self.config.packout_zone_x)
                self.config.packout_zone_y = packout.get("y", self.config.packout_zone_y)
                self.config.packout_zone_width = packout.get("width", self.config.packout_zone_width)
                self.config.packout_zone_height = packout.get("height", self.config.packout_zone_height)
            
            # Update item generation
            if "item_generation" in config_data:
                items = config_data["item_generation"]
                self.config.total_items = items.get("total_items", self.config.total_items)
                self.config.item_id_prefix = items.get("item_id_prefix", self.config.item_id_prefix)
                self.config.max_items_per_letter = items.get("max_items_per_letter", self.config.max_items_per_letter)
            
            # Update performance settings
            if "performance" in config_data:
                perf = config_data["performance"]
                self.config.max_operation_time_ms = perf.get("max_operation_time_ms", self.config.max_operation_time_ms)
                self.config.max_memory_usage_mb = perf.get("max_memory_usage_mb", self.config.max_memory_usage_mb)
                self.config.performance_monitoring_enabled = perf.get("performance_monitoring_enabled", self.config.performance_monitoring_enabled)
                self.config.debug_mode = perf.get("debug_mode", self.config.debug_mode)
            
            # Update event settings
            if "events" in config_data:
                events = config_data["events"]
                self.config.event_buffer_size = events.get("event_buffer_size", self.config.event_buffer_size)
                self.config.event_flush_interval_seconds = events.get("event_flush_interval_seconds", self.config.event_flush_interval_seconds)
            
            # Update validation settings
            if "validation" in config_data:
                validation = config_data["validation"]
                self.config.strict_validation = validation.get("strict_validation", self.config.strict_validation)
                self.config.allow_duplicate_items = validation.get("allow_duplicate_items", self.config.allow_duplicate_items)
                self.config.allow_invalid_locations = validation.get("allow_invalid_locations", self.config.allow_invalid_locations)
            
            return True
            
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False 