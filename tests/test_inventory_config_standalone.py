#!/usr/bin/env python3
"""
Standalone tests for InventoryConfigManager class

This test file can be run independently without complex dependencies.
"""

import sys
import os
import json
import time
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock classes for testing
@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    
    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class InventoryItem:
    item_id: str
    location: Coordinate
    quantity: float
    category: str
    created_at: float = 0.0
    last_updated: float = 0.0
    
    VALID_CATEGORIES = {
        "electronics", "clothing", "books", "home_goods", "sports",
        "automotive", "toys", "health_beauty", "food_beverages", "office_supplies"
    }

# Performance classes for testing
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

# Mock managers for testing
class MockInventoryManager:
    """Mock InventoryManager for testing"""
    
    def __init__(self):
        self._items = {}
        self._initialized = False
    
    def initialize_inventory(self) -> bool:
        """Initialize with test items"""
        items = []
        for i in range(5):
            item = InventoryItem(
                item_id=f"ITEM_A{i+1}",
                location=Coordinate(i, i),
                quantity=100.0,
                category="electronics",
                created_at=time.time(),
                last_updated=time.time()
            )
            items.append(item)
            self._items[item.item_id] = item
        
        self._initialized = True
        return True
    
    def get_inventory_statistics(self) -> Dict:
        """Get inventory statistics"""
        return {
            "total_items": len(self._items),
            "items_with_stock": sum(1 for item in self._items.values() if item.quantity > 0),
            "items_out_of_stock": sum(1 for item in self._items.values() if item.quantity == 0),
            "initialized": self._initialized
        }

class MockInventorySyncManager:
    """Mock InventorySyncManager for testing"""
    
    def __init__(self):
        self._order_status = {}
    
    def get_sync_statistics(self) -> Dict:
        """Get sync statistics"""
        return {
            "total_orders": 2,
            "completed_orders": 1,
            "cancelled_orders": 0,
            "completion_rate": 0.5
        }

# InventoryConfigManager implementation for testing
class InventoryConfigManager:
    """
    Manages inventory configuration and validation.
    """
    
    def __init__(self, config_file: str = "config/simulation.json"):
        """
        Initialize InventoryConfigManager.
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
        """
        try:
            print(f"    - Loading configuration from {self.config_file}")
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Extract inventory configuration
            inventory_config = data.get("inventory", {})
            print(f"    - Found inventory config: {inventory_config}")
            
            # Update configuration with loaded values
            for key, value in inventory_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    print(f"    - Set {key} = {value}")
            
            self._monitoring_enabled = self.config.performance_monitoring_enabled
            self._debug_mode = self.config.debug_mode
            
            print(f"    - Configuration loaded successfully")
            return True
            
        except Exception as e:
            print(f"    - Error loading configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """
        Save current configuration to file.
        """
        try:
            print(f"    - Saving configuration to {self.config_file}")
            
            # Load existing configuration
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Update inventory section
            inventory_config = {}
            for field in self.config.__dataclass_fields__:
                inventory_config[field] = getattr(self.config, field)
            
            data["inventory"] = inventory_config
            print(f"    - Updated inventory config: {inventory_config}")
            
            # Save updated configuration
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"    - Configuration saved successfully")
            return True
            
        except Exception as e:
            print(f"    - Error saving configuration: {e}")
            return False
    
    def validate_configuration(self) -> Dict:
        """
        Validate current configuration.
        """
        print(f"    - Validating configuration...")
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
        
        print(f"    - Validation results: {validation_results}")
        return validation_results
    
    def record_performance_metric(self, metric_type: PerformanceMetricType, 
                                value: float, metadata: Dict = None) -> None:
        """
        Record a performance metric.
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
            print(f"    - Recorded {metric_type.value} metric: {value}")
            
            # Keep only recent metrics (last 1000)
            if len(self._performance_metrics) > 1000:
                self._performance_metrics = self._performance_metrics[-1000:]
    
    def get_performance_metrics(self, metric_type: Optional[PerformanceMetricType] = None,
                              time_window_seconds: Optional[float] = None) -> List[PerformanceMetric]:
        """
        Get performance metrics.
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
        
        print(f"    - Retrieved {len(metrics)} metrics")
        return metrics
    
    def get_performance_analytics(self, time_window_seconds: float = 3600) -> Dict:
        """
        Get comprehensive performance analytics.
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
        
        print(f"    - Analytics: {analytics}")
        return analytics
    
    def check_performance_thresholds(self) -> Dict:
        """
        Check if performance metrics exceed thresholds.
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
        
        print(f"    - Threshold violations: {violations}")
        return violations
    
    def get_debug_info(self, inventory_manager: MockInventoryManager = None,
                      sync_manager: MockInventorySyncManager = None) -> Dict:
        """
        Get comprehensive debug information.
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
        
        print(f"    - Debug info: {debug_info}")
        return debug_info
    
    def export_configuration(self) -> Dict:
        """
        Export current configuration as dictionary.
        """
        config = {
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
        
        print(f"    - Exported configuration: {config}")
        return config
    
    def import_configuration(self, config_data: Dict) -> bool:
        """
        Import configuration from dictionary.
        """
        try:
            print(f"    - Importing configuration: {config_data}")
            
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
            
            print(f"    - Configuration imported successfully")
            return True
            
        except Exception as e:
            print(f"    - Error importing configuration: {e}")
            return False


class TestInventoryConfigManager:
    """Test suite for InventoryConfigManager class"""
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        print("Testing configuration validation...")
        
        config_manager = InventoryConfigManager()
        
        # Test valid configuration
        validation = config_manager.validate_configuration()
        assert validation["valid"] == True, "Default configuration should be valid"
        assert len(validation["errors"]) == 0, "Should have no errors"
        
        # Test invalid warehouse dimensions
        config_manager.config.warehouse_width = -1
        validation = config_manager.validate_configuration()
        assert validation["valid"] == False, "Invalid warehouse width should fail"
        assert len(validation["errors"]) > 0, "Should have errors"
        
        # Reset to valid configuration
        config_manager.config.warehouse_width = 26
        
        print("✅ Configuration validation tests passed")
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        print("Testing performance monitoring...")
        
        config_manager = InventoryConfigManager()
        
        # Record performance metrics
        config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 5.0)
        config_manager.record_performance_metric(PerformanceMetricType.MEMORY_USAGE, 50.0)
        config_manager.record_performance_metric(PerformanceMetricType.THROUGHPUT, 100.0)
        
        # Get metrics
        metrics = config_manager.get_performance_metrics()
        assert len(metrics) == 3, f"Expected 3 metrics, got {len(metrics)}"
        
        # Test filtering by metric type
        operation_metrics = config_manager.get_performance_metrics(PerformanceMetricType.OPERATION_TIME)
        assert len(operation_metrics) == 1, "Should have 1 operation time metric"
        assert operation_metrics[0].value == 5.0, "Wrong metric value"
        
        print("✅ Performance monitoring tests passed")
    
    def test_performance_analytics(self):
        """Test performance analytics"""
        print("Testing performance analytics...")
        
        config_manager = InventoryConfigManager()
        
        # Record multiple metrics
        for i in range(5):
            config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, i + 1.0)
            config_manager.record_performance_metric(PerformanceMetricType.MEMORY_USAGE, 50.0 + i)
        
        # Get analytics
        analytics = config_manager.get_performance_analytics()
        
        assert analytics["total_metrics"] == 10, f"Expected 10 metrics, got {analytics['total_metrics']}"
        assert "operation_time" in analytics["performance_summary"], "Should have operation_time summary"
        assert "memory_usage" in analytics["performance_summary"], "Should have memory_usage summary"
        
        # Check operation time statistics
        op_stats = analytics["performance_summary"]["operation_time"]
        assert op_stats["count"] == 5, "Should have 5 operation time metrics"
        assert op_stats["min"] == 1.0, "Wrong min value"
        assert op_stats["max"] == 5.0, "Wrong max value"
        assert op_stats["average"] == 3.0, "Wrong average value"
        
        print("✅ Performance analytics tests passed")
    
    def test_performance_thresholds(self):
        """Test performance threshold checking"""
        print("Testing performance thresholds...")
        
        config_manager = InventoryConfigManager()
        
        # Set low thresholds for testing
        config_manager.config.max_operation_time_ms = 5.0
        config_manager.config.max_memory_usage_mb = 60.0
        
        # Record metrics within and above thresholds
        config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 3.0)  # Within threshold
        config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 7.0)  # Above threshold
        config_manager.record_performance_metric(PerformanceMetricType.MEMORY_USAGE, 50.0)   # Within threshold
        config_manager.record_performance_metric(PerformanceMetricType.MEMORY_USAGE, 70.0)   # Above threshold
        
        # Check violations
        violations = config_manager.check_performance_thresholds()
        
        assert len(violations["operation_time_violations"]) == 1, "Should have 1 operation time violation"
        assert len(violations["memory_usage_violations"]) == 1, "Should have 1 memory usage violation"
        
        # Check violation details
        op_violation = violations["operation_time_violations"][0]
        assert op_violation["value"] == 7.0, "Wrong violation value"
        assert op_violation["threshold"] == 5.0, "Wrong threshold"
        
        print("✅ Performance threshold tests passed")
    
    def test_debug_info(self):
        """Test debug information generation"""
        print("Testing debug info generation...")
        
        config_manager = InventoryConfigManager()
        inventory_manager = MockInventoryManager()
        sync_manager = MockInventorySyncManager()
        
        # Initialize managers
        inventory_manager.initialize_inventory()
        
        # Get debug info
        debug_info = config_manager.get_debug_info(inventory_manager, sync_manager)
        
        # Check configuration section
        assert "configuration" in debug_info, "Should have configuration section"
        assert "warehouse_dimensions" in debug_info["configuration"], "Should have warehouse dimensions"
        assert "performance" in debug_info["configuration"], "Should have performance settings"
        
        # Check inventory manager section
        assert "inventory_manager" in debug_info, "Should have inventory manager section"
        assert debug_info["inventory_manager"]["initialized"] == True, "Should be initialized"
        assert debug_info["inventory_manager"]["total_items"] == 5, "Should have 5 items"
        
        # Check sync manager section
        assert "sync_manager" in debug_info, "Should have sync manager section"
        assert debug_info["sync_manager"]["total_orders"] == 2, "Should have 2 orders"
        
        print("✅ Debug info tests passed")
    
    def test_configuration_export_import(self):
        """Test configuration export and import"""
        print("Testing configuration export/import...")
        
        config_manager = InventoryConfigManager()
        
        # Export configuration
        exported_config = config_manager.export_configuration()
        
        # Verify export structure
        assert "warehouse_dimensions" in exported_config, "Should have warehouse dimensions"
        assert "item_generation" in exported_config, "Should have item generation"
        assert "performance" in exported_config, "Should have performance settings"
        
        # Modify configuration
        config_manager.config.warehouse_width = 30
        config_manager.config.total_items = 600
        config_manager.config.max_operation_time_ms = 15.0
        
        # Import configuration back
        success = config_manager.import_configuration(exported_config)
        assert success == True, "Import should succeed"
        
        # Verify configuration was restored
        assert config_manager.config.warehouse_width == 26, "Should restore warehouse width"
        assert config_manager.config.total_items == 500, "Should restore total items"
        assert config_manager.config.max_operation_time_ms == 10.0, "Should restore operation time"
        
        print("✅ Configuration export/import tests passed")
    
    def test_configuration_file_operations(self):
        """Test configuration file operations"""
        print("Testing configuration file operations...")
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "inventory": {
                    "warehouse_width": 30,
                    "warehouse_height": 25,
                    "total_items": 600,
                    "max_operation_time_ms": 15.0,
                    "debug_mode": True
                }
            }
            json.dump(config_data, f)
            temp_config_file = f.name
        
        try:
            # Create config manager with temp file
            config_manager = InventoryConfigManager(temp_config_file)
            
            # Load configuration
            success = config_manager.load_configuration()
            assert success == True, "Configuration loading should succeed"
            
            # Verify loaded values
            assert config_manager.config.warehouse_width == 30, "Should load warehouse width"
            assert config_manager.config.warehouse_height == 25, "Should load warehouse height"
            assert config_manager.config.total_items == 600, "Should load total items"
            assert config_manager.config.max_operation_time_ms == 15.0, "Should load operation time"
            assert config_manager.config.debug_mode == True, "Should load debug mode"
            
            # Test save configuration
            config_manager.config.warehouse_width = 35
            success = config_manager.save_configuration()
            assert success == True, "Configuration saving should succeed"
            
            # Reload and verify
            config_manager.load_configuration()
            assert config_manager.config.warehouse_width == 35, "Should save warehouse width"
            
        finally:
            # Clean up temp file
            os.unlink(temp_config_file)
        
        print("✅ Configuration file operation tests passed")
    
    def test_monitoring_control(self):
        """Test monitoring enable/disable"""
        print("Testing monitoring control...")
        
        config_manager = InventoryConfigManager()
        
        # Disable monitoring
        config_manager._monitoring_enabled = False
        
        # Record metrics (should be ignored)
        config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 5.0)
        
        # Check that no metrics were recorded
        metrics = config_manager.get_performance_metrics()
        assert len(metrics) == 0, "Should not record metrics when monitoring disabled"
        
        # Re-enable monitoring
        config_manager._monitoring_enabled = True
        
        # Record metrics (should be recorded)
        config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 5.0)
        
        # Check that metrics were recorded
        metrics = config_manager.get_performance_metrics()
        assert len(metrics) == 1, "Should record metrics when monitoring enabled"
        
        print("✅ Monitoring control tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running InventoryConfigManager tests...\n")
        
        try:
            self.test_configuration_validation()
            self.test_performance_monitoring()
            self.test_performance_analytics()
            self.test_performance_thresholds()
            self.test_debug_info()
            self.test_configuration_export_import()
            self.test_configuration_file_operations()
            self.test_monitoring_control()
            
            print("\n🎉 All InventoryConfigManager tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    # Run tests
    test_suite = TestInventoryConfigManager()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 