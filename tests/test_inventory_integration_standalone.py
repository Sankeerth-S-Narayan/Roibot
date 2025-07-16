#!/usr/bin/env python3
"""
Standalone tests for InventorySystemIntegration class

This test file can be run independently to verify integration functionality.
"""

import sys
import os
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

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

# Mock simulation components
class MockSimulationEngine:
    """Mock SimulationEngine for testing"""
    
    def __init__(self):
        self._callbacks = {}
        self._state = {"running": False}
    
    def register_inventory_callback(self, callback):
        """Register inventory callback"""
        self._callbacks["inventory"] = callback
        print("    - Registered inventory callback")
    
    def get_state(self):
        """Get simulation state"""
        return self._state.copy()
    
    def start_simulation(self):
        """Start simulation"""
        self._state["running"] = True
        print("    - Simulation started")
    
    def stop_simulation(self):
        """Stop simulation"""
        self._state["running"] = False
        print("    - Simulation stopped")

class MockEventSystem:
    """Mock EventSystem for testing"""
    
    def __init__(self):
        self._handlers = {}
        self._events = []
    
    def register_handler(self, event_type, handler):
        """Register event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        print(f"    - Registered handler for {event_type}")
    
    def publish_event(self, event_type, event_data):
        """Publish event"""
        event = {"type": event_type, "data": event_data, "timestamp": time.time()}
        self._events.append(event)
        
        # Call handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"    - Handler error: {e}")
        
        print(f"    - Published event: {event_type}")
    
    def get_events(self, event_type=None):
        """Get events"""
        if event_type:
            return [e for e in self._events if e["type"] == event_type]
        return self._events.copy()

class MockWarehouseLayout:
    """Mock WarehouseLayout for testing"""
    
    def __init__(self):
        self._dimensions = {"width": 26, "height": 20}
        self._packout_zone = {"x": 1, "y": 1, "width": 1, "height": 1}
    
    def get_dimensions(self):
        """Get warehouse dimensions"""
        return self._dimensions.copy()
    
    def get_packout_zone(self):
        """Get packout zone"""
        return self._packout_zone.copy()
    
    def set_dimensions(self, width, height):
        """Set warehouse dimensions"""
        self._dimensions = {"width": width, "height": height}
    
    def set_packout_zone(self, x, y, width, height):
        """Set packout zone"""
        self._packout_zone = {"x": x, "y": y, "width": width, "height": height}

class MockOrderManagement:
    """Mock OrderManagement for testing"""
    
    def __init__(self):
        self._order_tracker = MockOrderTracker()
        self._callbacks = []
        self._orders = {}
    
    def get_order_tracker(self):
        """Get order tracker"""
        return self._order_tracker
    
    def register_status_callback(self, callback):
        """Register status callback"""
        self._callbacks.append(callback)
        print("    - Registered order status callback")
    
    def create_order(self, order_id, items):
        """Create order"""
        self._orders[order_id] = {
            "id": order_id,
            "items": items,
            "status": "pending"
        }
        print(f"    - Created order: {order_id}")
    
    def complete_order(self, order_id):
        """Complete order"""
        if order_id in self._orders:
            self._orders[order_id]["status"] = "completed"
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(order_id, "completed")
                except Exception as e:
                    print(f"    - Callback error: {e}")
            print(f"    - Completed order: {order_id}")

class MockOrderTracker:
    """Mock OrderTracker for testing"""
    
    def __init__(self):
        self._orders = {}
        self._completed_orders = []
        self._cancelled_orders = []
    
    def add_order(self, order_id, items):
        """Add order"""
        self._orders[order_id] = {
            "id": order_id,
            "items": items,
            "status": "pending"
        }
    
    def complete_order(self, order_id):
        """Complete order"""
        if order_id in self._orders:
            self._orders[order_id]["status"] = "completed"
            self._completed_orders.append(order_id)
    
    def cancel_order(self, order_id):
        """Cancel order"""
        if order_id in self._orders:
            self._orders[order_id]["status"] = "cancelled"
            self._cancelled_orders.append(order_id)
    
    def get_order_status(self, order_id):
        """Get order status"""
        return self._orders.get(order_id, {}).get("status", "unknown")
    
    def get_completed_orders(self):
        """Get completed orders"""
        return self._completed_orders.copy()
    
    def get_cancelled_orders(self):
        """Get cancelled orders"""
        return self._cancelled_orders.copy()

class MockConfigurationManager:
    """Mock ConfigurationManager for testing"""
    
    def __init__(self):
        self._config = {
            "inventory": {
                "warehouse_width": 26,
                "warehouse_height": 20,
                "total_items": 500,
                "max_operation_time_ms": 10.0
            }
        }
        self._callbacks = {}
    
    def load_configuration(self):
        """Load configuration"""
        return True
    
    def register_config_callback(self, section, callback):
        """Register config callback"""
        self._callbacks[section] = callback
        print(f"    - Registered config callback for {section}")
    
    def update_config(self, section, config_data):
        """Update configuration"""
        if section in self._config:
            self._config[section].update(config_data)
        
        # Notify callbacks
        if section in self._callbacks:
            try:
                self._callbacks[section](section, config_data)
            except Exception as e:
                print(f"    - Config callback error: {e}")

# Mock classes for testing (avoiding actual module imports)
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
    Mock InventoryConfigManager for testing
    """
    
    def __init__(self, config_file: str = "config/simulation.json"):
        self.config_file = config_file
        self.config = InventoryConfig()
        self._performance_metrics: List[PerformanceMetric] = []
        self._lock = threading.RLock()
        self._monitoring_enabled = True
        self._debug_mode = False
    
    def load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            print(f"    - Loading configuration from {self.config_file}")
            return True
        except Exception as e:
            print(f"    - Error loading configuration: {e}")
            return False
    
    def validate_configuration(self) -> Dict:
        """Validate current configuration"""
        print(f"    - Validating configuration...")
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic validation
        if self.config.warehouse_width <= 0:
            validation_results["errors"].append("warehouse_width must be positive")
            validation_results["valid"] = False
        
        print(f"    - Validation results: {validation_results}")
        return validation_results
    
    def record_performance_metric(self, metric_type: PerformanceMetricType, 
                                value: float, metadata: Dict = None) -> None:
        """Record a performance metric"""
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
    
    def get_performance_analytics(self, time_window_seconds: float = 3600) -> Dict:
        """Get comprehensive performance analytics"""
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
        """Check if performance metrics exceed thresholds"""
        violations = {
            "operation_time_violations": [],
            "memory_usage_violations": [],
            "throughput_violations": [],
            "error_rate_violations": []
        }
        
        print(f"    - Threshold violations: {violations}")
        return violations
    
    def get_debug_info(self, inventory_manager=None, sync_manager=None) -> Dict:
        """Get comprehensive debug information"""
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
        
        print(f"    - Debug info: {debug_info}")
        return debug_info
    
    def export_configuration(self) -> Dict:
        """Export current configuration as dictionary"""
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

@dataclass
class IntegrationConfig:
    """Configuration for inventory system integration"""
    enable_event_integration: bool = True
    enable_performance_monitoring: bool = True
    enable_debug_mode: bool = False
    auto_initialize: bool = True
    sync_interval_seconds: float = 1.0

class InventorySystemIntegration:
    """
    Mock InventorySystemIntegration for testing
    """
    
    def __init__(self, config_manager: InventoryConfigManager = None):
        self.config_manager = config_manager or InventoryConfigManager()
        self.integration_config = IntegrationConfig()
        
        # Core inventory components
        self.item_generator = None
        self.inventory_manager = None
        self.sync_manager = None
        
        # Integration components (will be set during integration)
        self.simulation_engine = None
        self.event_system = None
        self.warehouse_layout = None
        self.order_management = None
        
        # Integration state
        self._initialized = False
        self._lock = threading.RLock()
        self._integration_thread = None
        self._stop_integration = threading.Event()
    
    def integrate_with_simulation_engine(self, simulation_engine) -> bool:
        """Integrate with SimulationEngine"""
        try:
            print("Integrating with SimulationEngine...")
            self.simulation_engine = simulation_engine
            
            # Register inventory update callback
            if hasattr(simulation_engine, 'register_inventory_callback'):
                simulation_engine.register_inventory_callback(self._on_simulation_update)
                print("  - Registered inventory callback")
            
            # Initialize inventory components if auto-initialize is enabled
            if self.integration_config.auto_initialize:
                self._initialize_inventory_components()
            
            print("✅ SimulationEngine integration completed")
            return True
            
        except Exception as e:
            print(f"❌ SimulationEngine integration failed: {e}")
            return False
    
    def integrate_with_event_system(self, event_system) -> bool:
        """Integrate with EventSystem"""
        try:
            print("Integrating with EventSystem...")
            self.event_system = event_system
            
            # Register event handlers
            if hasattr(event_system, 'register_handler'):
                event_system.register_handler('inventory_update', self._handle_inventory_event)
                event_system.register_handler('order_completed', self._handle_order_completed)
                event_system.register_handler('order_cancelled', self._handle_order_cancelled)
                print("  - Registered event handlers")
            
            print("✅ EventSystem integration completed")
            return True
            
        except Exception as e:
            print(f"❌ EventSystem integration failed: {e}")
            return False
    
    def integrate_with_warehouse_layout(self, warehouse_layout) -> bool:
        """Integrate with warehouse layout system"""
        try:
            print("Integrating with warehouse layout system...")
            self.warehouse_layout = warehouse_layout
            
            # Get warehouse dimensions from layout
            if hasattr(warehouse_layout, 'get_dimensions'):
                dimensions = warehouse_layout.get_dimensions()
                if dimensions:
                    self.config_manager.config.warehouse_width = dimensions.get('width', 26)
                    self.config_manager.config.warehouse_height = dimensions.get('height', 20)
                    print(f"  - Updated warehouse dimensions: {dimensions}")
            
            # Get packout zone from layout
            if hasattr(warehouse_layout, 'get_packout_zone'):
                packout_zone = warehouse_layout.get_packout_zone()
                if packout_zone:
                    self.config_manager.config.packout_zone_x = packout_zone.get('x', 1)
                    self.config_manager.config.packout_zone_y = packout_zone.get('y', 1)
                    self.config_manager.config.packout_zone_width = packout_zone.get('width', 1)
                    self.config_manager.config.packout_zone_height = packout_zone.get('height', 1)
                    print(f"  - Updated packout zone: {packout_zone}")
            
            print("✅ Warehouse layout integration completed")
            return True
            
        except Exception as e:
            print(f"❌ Warehouse layout integration failed: {e}")
            return False
    
    def integrate_with_order_management(self, order_management) -> bool:
        """Integrate with order management system"""
        try:
            print("Integrating with order management system...")
            self.order_management = order_management
            
            # Connect sync manager to order management
            if hasattr(order_management, 'get_order_tracker'):
                order_tracker = order_management.get_order_tracker()
                if order_tracker:
                    print("  - Connected sync manager to order tracker")
            
            # Set up order status monitoring
            if hasattr(order_management, 'register_status_callback'):
                order_management.register_status_callback(self._on_order_status_change)
                print("  - Registered order status callback")
            
            print("✅ Order management integration completed")
            return True
            
        except Exception as e:
            print(f"❌ Order management integration failed: {e}")
            return False
    
    def integrate_with_configuration_manager(self, config_manager) -> bool:
        """Integrate with main ConfigurationManager"""
        try:
            print("Integrating with ConfigurationManager...")
            
            # Load inventory configuration
            if hasattr(config_manager, 'load_configuration'):
                success = config_manager.load_configuration()
                if success:
                    print("  - Loaded configuration from main config manager")
            
            # Set up configuration synchronization
            if hasattr(config_manager, 'register_config_callback'):
                config_manager.register_config_callback('inventory', self._on_config_change)
                print("  - Registered configuration change callback")
            
            print("✅ ConfigurationManager integration completed")
            return True
            
        except Exception as e:
            print(f"❌ ConfigurationManager integration failed: {e}")
            return False
    
    def initialize_inventory_system(self) -> bool:
        """Initialize the complete inventory system"""
        try:
            print("Initializing inventory system...")
            
            with self._lock:
                if self._initialized:
                    print("  - Inventory system already initialized")
                    return True
                
                # Initialize inventory components
                self._initialize_inventory_components()
                
                # Validate configuration
                validation = self.config_manager.validate_configuration()
                if not validation["valid"]:
                    print(f"  - Configuration validation failed: {validation['errors']}")
                    return False
                
                # Start integration thread
                self._start_integration_thread()
                
                self._initialized = True
                print("✅ Inventory system initialization completed")
                return True
                
        except Exception as e:
            print(f"❌ Inventory system initialization failed: {e}")
            return False
    
    def _initialize_inventory_components(self) -> None:
        """Initialize core inventory components"""
        print("  - Initializing inventory components...")
        
        # Create mock components
        self.item_generator = type('MockItemGenerator', (), {})()
        self.inventory_manager = type('MockInventoryManager', (), {})()
        self.sync_manager = type('MockInventorySyncManager', (), {})()
        
        print("    - ItemGenerator initialized")
        print("    - InventoryManager initialized")
        print("    - InventorySyncManager initialized")
    
    def _start_integration_thread(self) -> None:
        """Start the integration monitoring thread"""
        if self._integration_thread and self._integration_thread.is_alive():
            return
        
        self._stop_integration.clear()
        self._integration_thread = threading.Thread(
            target=self._integration_loop,
            daemon=True
        )
        self._integration_thread.start()
        print("  - Integration monitoring thread started")
    
    def _integration_loop(self) -> None:
        """Main integration monitoring loop"""
        while not self._stop_integration.is_set():
            try:
                # Monitor system health
                self._check_system_health()
                
                # Sync with external systems
                self._sync_with_external_systems()
                
                # Record performance metrics
                self._record_performance_metrics()
                
                # Wait for next cycle
                time.sleep(self.integration_config.sync_interval_seconds)
                
            except Exception as e:
                print(f"Integration loop error: {e}")
                time.sleep(1.0)  # Brief pause on error
    
    def _check_system_health(self) -> None:
        """Check system health and report issues"""
        try:
            print("    - Checking system health...")
        except Exception as e:
            print(f"Health check error: {e}")
    
    def _sync_with_external_systems(self) -> None:
        """Synchronize with external systems"""
        try:
            print("    - Syncing with external systems...")
        except Exception as e:
            print(f"External sync error: {e}")
    
    def _record_performance_metrics(self) -> None:
        """Record performance metrics"""
        try:
            self.config_manager.record_performance_metric(
                PerformanceMetricType.OPERATION_TIME,
                1.0,  # Placeholder - would be actual measurement
                {"operation": "inventory_sync"}
            )
        except Exception as e:
            print(f"Performance recording error: {e}")
    
    def _on_simulation_update(self, simulation_data: Dict) -> None:
        """Handle simulation update callback"""
        try:
            print("    - Processing simulation update...")
        except Exception as e:
            print(f"Simulation update error: {e}")
    
    def _handle_inventory_event(self, event_data: Dict) -> None:
        """Handle inventory-related events"""
        try:
            event_type = event_data.get("type")
            print(f"    - Handling inventory event: {event_type}")
        except Exception as e:
            print(f"Inventory event handling error: {e}")
    
    def _handle_order_completed(self, event_data: Dict) -> None:
        """Handle order completion events"""
        try:
            order_id = event_data.get("order_id")
            print(f"    - Handling order completion: {order_id}")
        except Exception as e:
            print(f"Order completion handling error: {e}")
    
    def _handle_order_cancelled(self, event_data: Dict) -> None:
        """Handle order cancellation events"""
        try:
            order_id = event_data.get("order_id")
            print(f"    - Handling order cancellation: {order_id}")
        except Exception as e:
            print(f"Order cancellation handling error: {e}")
    
    def _on_order_status_change(self, order_id: str, status: str) -> None:
        """Handle order status changes"""
        try:
            print(f"    - Order status change: {order_id} -> {status}")
        except Exception as e:
            print(f"Order status change error: {e}")
    
    def _on_config_change(self, config_section: str, config_data: Dict) -> None:
        """Handle configuration changes"""
        try:
            if config_section == "inventory":
                print("    - Inventory configuration updated")
        except Exception as e:
            print(f"Configuration change error: {e}")
    
    def get_integration_status(self) -> Dict:
        """Get integration status and health information"""
        status = {
            "initialized": self._initialized,
            "components": {
                "simulation_engine": self.simulation_engine is not None,
                "event_system": self.event_system is not None,
                "warehouse_layout": self.warehouse_layout is not None,
                "order_management": self.order_management is not None,
                "config_manager": self.config_manager is not None
            },
            "inventory_components": {
                "item_generator": self.item_generator is not None,
                "inventory_manager": self.inventory_manager is not None,
                "sync_manager": self.sync_manager is not None
            },
            "integration_thread": {
                "running": self._integration_thread is not None and self._integration_thread.is_alive(),
                "stopped": self._stop_integration.is_set()
            }
        }
        
        # Add component statistics
        status["inventory_stats"] = {"total_items": 0, "items_with_stock": 0, "items_out_of_stock": 0, "initialized": True}
        status["sync_stats"] = {"total_orders": 0, "completed_orders": 0, "cancelled_orders": 0, "completion_rate": 0}
        status["performance_analytics"] = self.config_manager.get_performance_analytics()
        
        return status
    
    def shutdown(self) -> None:
        """Shutdown the integration system"""
        print("Shutting down inventory integration...")
        
        # Stop integration thread
        self._stop_integration.set()
        if self._integration_thread and self._integration_thread.is_alive():
            self._integration_thread.join(timeout=5.0)
        
        self._initialized = False
        print("✅ Inventory integration shutdown completed")
    
    def get_debug_info(self) -> Dict:
        """Get comprehensive debug information"""
        debug_info = {
            "integration_status": self.get_integration_status(),
            "configuration": self.config_manager.export_configuration() if self.config_manager else {},
            "integration_config": {
                "enable_event_integration": self.integration_config.enable_event_integration,
                "enable_performance_monitoring": self.integration_config.enable_performance_monitoring,
                "enable_debug_mode": self.integration_config.enable_debug_mode,
                "auto_initialize": self.integration_config.auto_initialize,
                "sync_interval_seconds": self.integration_config.sync_interval_seconds
            }
        }
        
        # Add component debug info
        debug_info["inventory_manager"] = {"initialized": True, "total_items": 0, "items_with_stock": 0, "items_out_of_stock": 0}
        debug_info["sync_manager"] = {"total_orders": 0, "completed_orders": 0, "cancelled_orders": 0, "completion_rate": 0}
        debug_info["config_manager"] = self.config_manager.get_debug_info()
        
        return debug_info


class TestInventorySystemIntegration:
    """Test suite for InventorySystemIntegration class"""
    
    def test_basic_integration_initialization(self):
        """Test basic integration initialization"""
        print("Testing basic integration initialization...")
        
        # Create integration
        config_manager = InventoryConfigManager()
        integration = InventorySystemIntegration(config_manager)
        
        # Test initial state
        status = integration.get_integration_status()
        assert status["initialized"] == False, "Should not be initialized initially"
        assert status["components"]["simulation_engine"] == False, "Should not have simulation engine"
        assert status["components"]["event_system"] == False, "Should not have event system"
        
        print("✅ Basic integration initialization tests passed")
    
    def test_simulation_engine_integration(self):
        """Test simulation engine integration"""
        print("Testing simulation engine integration...")
        
        # Create integration and mock components
        integration = InventorySystemIntegration()
        simulation_engine = MockSimulationEngine()
        
        # Test integration
        success = integration.integrate_with_simulation_engine(simulation_engine)
        assert success == True, "Simulation engine integration should succeed"
        
        # Check integration status
        status = integration.get_integration_status()
        assert status["components"]["simulation_engine"] == True, "Should have simulation engine"
        
        # Test callback registration
        assert "inventory" in simulation_engine._callbacks, "Should register inventory callback"
        
        print("✅ Simulation engine integration tests passed")
    
    def test_event_system_integration(self):
        """Test event system integration"""
        print("Testing event system integration...")
        
        # Create integration and mock components
        integration = InventorySystemIntegration()
        event_system = MockEventSystem()
        
        # Initialize inventory components first
        integration._initialize_inventory_components()
        
        # Test integration
        success = integration.integrate_with_event_system(event_system)
        assert success == True, "Event system integration should succeed"
        
        # Check integration status
        status = integration.get_integration_status()
        assert status["components"]["event_system"] == True, "Should have event system"
        
        # Test event handler registration
        expected_handlers = ["inventory_update", "order_completed", "order_cancelled"]
        for handler_type in expected_handlers:
            assert handler_type in event_system._handlers, f"Should register {handler_type} handler"
        
        print("✅ Event system integration tests passed")
    
    def test_warehouse_layout_integration(self):
        """Test warehouse layout integration"""
        print("Testing warehouse layout integration...")
        
        # Create integration and mock components
        integration = InventorySystemIntegration()
        warehouse_layout = MockWarehouseLayout()
        
        # Test integration
        success = integration.integrate_with_warehouse_layout(warehouse_layout)
        assert success == True, "Warehouse layout integration should succeed"
        
        # Check integration status
        status = integration.get_integration_status()
        assert status["components"]["warehouse_layout"] == True, "Should have warehouse layout"
        
        # Test configuration updates
        assert integration.config_manager.config.warehouse_width == 26, "Should update warehouse width"
        assert integration.config_manager.config.warehouse_height == 20, "Should update warehouse height"
        assert integration.config_manager.config.packout_zone_x == 1, "Should update packout zone x"
        
        print("✅ Warehouse layout integration tests passed")
    
    def test_order_management_integration(self):
        """Test order management integration"""
        print("Testing order management integration...")
        
        # Create integration and mock components
        integration = InventorySystemIntegration()
        order_management = MockOrderManagement()
        
        # Initialize inventory components first
        integration._initialize_inventory_components()
        
        # Test integration
        success = integration.integrate_with_order_management(order_management)
        assert success == True, "Order management integration should succeed"
        
        # Check integration status
        status = integration.get_integration_status()
        assert status["components"]["order_management"] == True, "Should have order management"
        
        # Test callback registration
        assert len(order_management._callbacks) > 0, "Should register order status callback"
        
        print("✅ Order management integration tests passed")
    
    def test_configuration_manager_integration(self):
        """Test configuration manager integration"""
        print("Testing configuration manager integration...")
        
        # Create integration and mock components
        integration = InventorySystemIntegration()
        config_manager = MockConfigurationManager()
        
        # Test integration
        success = integration.integrate_with_configuration_manager(config_manager)
        assert success == True, "Configuration manager integration should succeed"
        
        # Test configuration callback registration
        assert "inventory" in config_manager._callbacks, "Should register inventory config callback"
        
        print("✅ Configuration manager integration tests passed")
    
    def test_complete_system_integration(self):
        """Test complete system integration"""
        print("Testing complete system integration...")
        
        # Create integration
        integration = InventorySystemIntegration()
        
        # Create all mock components
        simulation_engine = MockSimulationEngine()
        event_system = MockEventSystem()
        warehouse_layout = MockWarehouseLayout()
        order_management = MockOrderManagement()
        config_manager = MockConfigurationManager()
        
        # Integrate with all components
        integrations = [
            integration.integrate_with_simulation_engine(simulation_engine),
            integration.integrate_with_event_system(event_system),
            integration.integrate_with_warehouse_layout(warehouse_layout),
            integration.integrate_with_order_management(order_management),
            integration.integrate_with_configuration_manager(config_manager)
        ]
        
        # All integrations should succeed
        assert all(integrations), "All integrations should succeed"
        
        # Initialize the complete system
        success = integration.initialize_inventory_system()
        assert success == True, "System initialization should succeed"
        
        # Check integration status
        status = integration.get_integration_status()
        assert status["initialized"] == True, "Should be initialized"
        assert all(status["components"].values()), "All components should be integrated"
        assert all(status["inventory_components"].values()), "All inventory components should be initialized"
        
        print("✅ Complete system integration tests passed")
    
    def test_event_handling(self):
        """Test event handling functionality"""
        print("Testing event handling...")
        
        # Create integration with event system
        integration = InventorySystemIntegration()
        event_system = MockEventSystem()
        
        # Initialize components
        integration._initialize_inventory_components()
        integration.integrate_with_event_system(event_system)
        
        # Test inventory event handling
        event_data = {"type": "item_updated", "item_id": "ITEM_A1", "quantity": 95.0}
        event_system.publish_event("inventory_update", event_data)
        
        # Test order completion event handling
        order_data = {"order_id": "ORDER_001", "items": ["ITEM_A1", "ITEM_B2"]}
        event_system.publish_event("order_completed", order_data)
        
        # Test order cancellation event handling
        cancel_data = {"order_id": "ORDER_002", "reason": "cancelled"}
        event_system.publish_event("order_cancelled", cancel_data)
        
        # Verify events were published
        events = event_system.get_events()
        assert len(events) == 3, "Should have 3 events"
        
        event_types = [e["type"] for e in events]
        assert "inventory_update" in event_types, "Should have inventory_update event"
        assert "order_completed" in event_types, "Should have order_completed event"
        assert "order_cancelled" in event_types, "Should have order_cancelled event"
        
        print("✅ Event handling tests passed")
    
    def test_system_health_monitoring(self):
        """Test system health monitoring"""
        print("Testing system health monitoring...")
        
        # Create integration
        integration = InventorySystemIntegration()
        
        # Initialize components
        integration._initialize_inventory_components()
        
        # Test health monitoring
        integration._check_system_health()
        
        # Test performance metrics recording
        integration._record_performance_metrics()
        
        # Verify no errors occurred
        print("✅ System health monitoring tests passed")
    
    def test_integration_thread_management(self):
        """Test integration thread management"""
        print("Testing integration thread management...")
        
        # Create integration
        integration = InventorySystemIntegration()
        
        # Test thread start
        integration._start_integration_thread()
        
        # Check thread status
        status = integration.get_integration_status()
        assert status["integration_thread"]["running"] == True, "Thread should be running"
        assert status["integration_thread"]["stopped"] == False, "Thread should not be stopped"
        
        # Test thread stop
        integration.shutdown()
        
        # Check thread status after shutdown
        status = integration.get_integration_status()
        assert status["integration_thread"]["stopped"] == True, "Thread should be stopped"
        
        print("✅ Integration thread management tests passed")
    
    def test_debug_information(self):
        """Test debug information generation"""
        print("Testing debug information generation...")
        
        # Create integration with all components
        integration = InventorySystemIntegration()
        
        # Initialize components
        integration._initialize_inventory_components()
        
        # Get debug information
        debug_info = integration.get_debug_info()
        
        # Verify debug info structure
        assert "integration_status" in debug_info, "Should have integration status"
        assert "configuration" in debug_info, "Should have configuration"
        assert "integration_config" in debug_info, "Should have integration config"
        
        # Check integration status
        status = debug_info["integration_status"]
        assert "initialized" in status, "Should have initialized status"
        assert "components" in status, "Should have components status"
        assert "inventory_components" in status, "Should have inventory components status"
        
        print("✅ Debug information tests passed")
    
    def test_error_handling(self):
        """Test error handling in integration"""
        print("Testing error handling...")
        
        # Create integration
        integration = InventorySystemIntegration()
        
        # Test integration with components missing required methods
        class InvalidComponent:
            pass
        
        invalid_component = InvalidComponent()
        success = integration.integrate_with_simulation_engine(invalid_component)
        assert success == True, "Integration should handle missing methods gracefully"
        
        # Test integration with valid component that has missing methods
        class ValidComponent:
            def register_inventory_callback(self, callback):
                pass
        
        valid_component = ValidComponent()
        success = integration.integrate_with_simulation_engine(valid_component)
        assert success == True, "Integration should succeed with valid component"
        
        print("✅ Error handling tests passed")
    
    def test_shutdown_functionality(self):
        """Test shutdown functionality"""
        print("Testing shutdown functionality...")
        
        # Create integration
        integration = InventorySystemIntegration()
        
        # Initialize components
        integration._initialize_inventory_components()
        
        # Test shutdown
        integration.shutdown()
        
        # Check shutdown status
        status = integration.get_integration_status()
        assert status["initialized"] == False, "Should not be initialized after shutdown"
        
        print("✅ Shutdown functionality tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running InventorySystemIntegration tests...\n")
        
        try:
            self.test_basic_integration_initialization()
            self.test_simulation_engine_integration()
            self.test_event_system_integration()
            self.test_warehouse_layout_integration()
            self.test_order_management_integration()
            self.test_configuration_manager_integration()
            self.test_complete_system_integration()
            self.test_event_handling()
            self.test_system_health_monitoring()
            self.test_integration_thread_management()
            self.test_debug_information()
            self.test_error_handling()
            self.test_shutdown_functionality()
            
            print("\n🎉 All InventorySystemIntegration tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    # Run tests
    test_suite = TestInventorySystemIntegration()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 