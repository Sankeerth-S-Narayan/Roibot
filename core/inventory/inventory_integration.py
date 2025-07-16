"""
Inventory System Integration

This module integrates the inventory system with existing simulation components:
- SimulationEngine
- EventSystem
- ConfigurationManager
- Warehouse Layout System
- Order Management System
"""

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .inventory_item import InventoryItem, Coordinate
from .item_generator import ItemGenerator
from .inventory_manager import InventoryManager
from .inventory_sync import InventorySyncManager
from .inventory_config import InventoryConfigManager, PerformanceMetricType


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
    Integrates inventory system with existing simulation components.
    
    Features:
    - Integration with SimulationEngine
    - Event system integration
    - Configuration management integration
    - Warehouse layout integration
    - Order management integration
    - Comprehensive error handling
    - Performance monitoring
    """
    
    def __init__(self, config_manager: InventoryConfigManager = None):
        """
        Initialize InventorySystemIntegration.
        
        Args:
            config_manager: InventoryConfigManager instance (optional)
        """
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
        """
        Integrate with SimulationEngine.
        
        Args:
            simulation_engine: SimulationEngine instance
            
        Returns:
            True if integration successful, False otherwise
        """
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
        """
        Integrate with EventSystem.
        
        Args:
            event_system: EventSystem instance
            
        Returns:
            True if integration successful, False otherwise
        """
        try:
            print("Integrating with EventSystem...")
            self.event_system = event_system
            
            # Register event handlers
            if hasattr(event_system, 'register_handler'):
                event_system.register_handler('inventory_update', self._handle_inventory_event)
                event_system.register_handler('order_completed', self._handle_order_completed)
                event_system.register_handler('order_cancelled', self._handle_order_cancelled)
                print("  - Registered event handlers")
            
            # Set up event publishing
            if self.inventory_manager:
                self.inventory_manager.set_event_system(event_system)
                print("  - Connected inventory manager to event system")
            
            if self.sync_manager:
                self.sync_manager.set_event_system(event_system)
                print("  - Connected sync manager to event system")
            
            print("✅ EventSystem integration completed")
            return True
            
        except Exception as e:
            print(f"❌ EventSystem integration failed: {e}")
            return False
    
    def integrate_with_warehouse_layout(self, warehouse_layout) -> bool:
        """
        Integrate with warehouse layout system.
        
        Args:
            warehouse_layout: Warehouse layout system instance
            
        Returns:
            True if integration successful, False otherwise
        """
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
        """
        Integrate with order management system.
        
        Args:
            order_management: Order management system instance
            
        Returns:
            True if integration successful, False otherwise
        """
        try:
            print("Integrating with order management system...")
            self.order_management = order_management
            
            # Connect sync manager to order management
            if self.sync_manager and hasattr(order_management, 'get_order_tracker'):
                order_tracker = order_management.get_order_tracker()
                if order_tracker:
                    self.sync_manager.set_order_tracker(order_tracker)
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
        """
        Integrate with main ConfigurationManager.
        
        Args:
            config_manager: Main ConfigurationManager instance
            
        Returns:
            True if integration successful, False otherwise
        """
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
        """
        Initialize the complete inventory system.
        
        Returns:
            True if initialization successful, False otherwise
        """
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
        """Initialize core inventory components."""
        print("  - Initializing inventory components...")
        
        # Initialize item generator
        self.item_generator = ItemGenerator(
            warehouse_width=self.config_manager.config.warehouse_width,
            warehouse_height=self.config_manager.config.warehouse_height,
            packout_zone_x=self.config_manager.config.packout_zone_x,
            packout_zone_y=self.config_manager.config.packout_zone_y,
            packout_zone_width=self.config_manager.config.packout_zone_width,
            packout_zone_height=self.config_manager.config.packout_zone_height,
            total_items=self.config_manager.config.total_items,
            item_id_prefix=self.config_manager.config.item_id_prefix,
            max_items_per_letter=self.config_manager.config.max_items_per_letter
        )
        print("    - ItemGenerator initialized")
        
        # Generate items
        items = self.item_generator.generate_items()
        print(f"    - Generated {len(items)} items")
        
        # Initialize inventory manager
        self.inventory_manager = InventoryManager()
        self.inventory_manager.initialize_inventory(items)
        print("    - InventoryManager initialized")
        
        # Initialize sync manager
        self.sync_manager = InventorySyncManager(self.inventory_manager)
        print("    - InventorySyncManager initialized")
        
        # Connect components
        if self.event_system:
            self.inventory_manager.set_event_system(self.event_system)
            self.sync_manager.set_event_system(self.event_system)
    
    def _start_integration_thread(self) -> None:
        """Start the integration monitoring thread."""
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
        """Main integration monitoring loop."""
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
        """Check system health and report issues."""
        try:
            # Check inventory manager health
            if self.inventory_manager:
                stats = self.inventory_manager.get_inventory_statistics()
                if not stats.get("initialized", False):
                    print("⚠️  Inventory manager not initialized")
            
            # Check sync manager health
            if self.sync_manager:
                sync_stats = self.sync_manager.get_sync_statistics()
                if sync_stats.get("completion_rate", 1.0) < 0.8:
                    print("⚠️  Low order completion rate detected")
            
            # Check performance thresholds
            violations = self.config_manager.check_performance_thresholds()
            for violation_type, violations_list in violations.items():
                if violations_list:
                    print(f"⚠️  Performance threshold violations: {violation_type}")
                    
        except Exception as e:
            print(f"Health check error: {e}")
    
    def _sync_with_external_systems(self) -> None:
        """Synchronize with external systems."""
        try:
            # Sync with order management
            if self.order_management and self.sync_manager:
                self.sync_manager.sync_with_order_management()
            
            # Sync with warehouse layout
            if self.warehouse_layout and self.inventory_manager:
                # Update item locations if layout changed
                pass
            
        except Exception as e:
            print(f"External sync error: {e}")
    
    def _record_performance_metrics(self) -> None:
        """Record performance metrics."""
        try:
            if self.inventory_manager:
                # Record inventory operation metrics
                self.config_manager.record_performance_metric(
                    PerformanceMetricType.OPERATION_TIME,
                    1.0,  # Placeholder - would be actual measurement
                    {"operation": "inventory_sync"}
                )
            
        except Exception as e:
            print(f"Performance recording error: {e}")
    
    def _on_simulation_update(self, simulation_data: Dict) -> None:
        """Handle simulation update callback."""
        try:
            # Process simulation updates
            if self.inventory_manager:
                # Update inventory based on simulation state
                pass
                
        except Exception as e:
            print(f"Simulation update error: {e}")
    
    def _handle_inventory_event(self, event_data: Dict) -> None:
        """Handle inventory-related events."""
        try:
            event_type = event_data.get("type")
            if event_type == "item_updated":
                # Process item update
                pass
            elif event_type == "stock_changed":
                # Process stock change
                pass
                
        except Exception as e:
            print(f"Inventory event handling error: {e}")
    
    def _handle_order_completed(self, event_data: Dict) -> None:
        """Handle order completion events."""
        try:
            if self.sync_manager:
                order_id = event_data.get("order_id")
                self.sync_manager.handle_order_completion(order_id)
                
        except Exception as e:
            print(f"Order completion handling error: {e}")
    
    def _handle_order_cancelled(self, event_data: Dict) -> None:
        """Handle order cancellation events."""
        try:
            if self.sync_manager:
                order_id = event_data.get("order_id")
                self.sync_manager.handle_order_cancellation(order_id)
                
        except Exception as e:
            print(f"Order cancellation handling error: {e}")
    
    def _on_order_status_change(self, order_id: str, status: str) -> None:
        """Handle order status changes."""
        try:
            if self.sync_manager:
                self.sync_manager.handle_order_status_change(order_id, status)
                
        except Exception as e:
            print(f"Order status change error: {e}")
    
    def _on_config_change(self, config_section: str, config_data: Dict) -> None:
        """Handle configuration changes."""
        try:
            if config_section == "inventory":
                self.config_manager.import_configuration(config_data)
                print("  - Inventory configuration updated")
                
        except Exception as e:
            print(f"Configuration change error: {e}")
    
    def get_integration_status(self) -> Dict:
        """
        Get integration status and health information.
        
        Returns:
            Dictionary with integration status
        """
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
        if self.inventory_manager:
            status["inventory_stats"] = self.inventory_manager.get_inventory_statistics()
        
        if self.sync_manager:
            status["sync_stats"] = self.sync_manager.get_sync_statistics()
        
        if self.config_manager:
            status["performance_analytics"] = self.config_manager.get_performance_analytics()
        
        return status
    
    def shutdown(self) -> None:
        """Shutdown the integration system."""
        print("Shutting down inventory integration...")
        
        # Stop integration thread
        self._stop_integration.set()
        if self._integration_thread and self._integration_thread.is_alive():
            self._integration_thread.join(timeout=5.0)
        
        # Shutdown components
        if self.inventory_manager:
            self.inventory_manager.shutdown()
        
        if self.sync_manager:
            self.sync_manager.shutdown()
        
        self._initialized = False
        print("✅ Inventory integration shutdown completed")
    
    def get_debug_info(self) -> Dict:
        """
        Get comprehensive debug information.
        
        Returns:
            Dictionary with debug information
        """
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
        if self.inventory_manager:
            debug_info["inventory_manager"] = self.inventory_manager.get_debug_info()
        
        if self.sync_manager:
            debug_info["sync_manager"] = self.sync_manager.get_debug_info()
        
        if self.config_manager:
            debug_info["config_manager"] = self.config_manager.get_debug_info(
                self.inventory_manager, self.sync_manager
            )
        
        return debug_info 