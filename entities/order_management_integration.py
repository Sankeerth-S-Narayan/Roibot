import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .order_generator import OrderGenerator
from .order_queue_manager import OrderQueueManager
from .robot_order_assigner import RobotOrderAssigner
from .order_status_tracker import OrderStatusTracker
from .order_analytics import OrderAnalytics
from .analytics_dashboard import AnalyticsDashboard
from .configuration_manager import ConfigurationManager
from .robot_orders import Order, OrderStatus

# Import existing simulation components
from core.engine import SimulationEngine, RobotState
from core.events import EventSystem, EventType
from core.state import SimulationState
from core.layout.coordinate import Coordinate

class IntegrationEventType(Enum):
    """Order management specific event types."""
    ORDER_CREATED = "order_created"
    ORDER_ASSIGNED = "order_assigned"
    ORDER_STARTED = "order_started"
    ORDER_COMPLETED = "order_completed"
    ORDER_FAILED = "order_failed"
    ROBOT_STATE_CHANGED = "robot_state_changed"
    ANALYTICS_UPDATED = "analytics_updated"
    CONFIGURATION_CHANGED = "configuration_changed"

@dataclass
class IntegrationMetrics:
    """Metrics for integration performance."""
    total_orders_processed: int = 0
    successful_integrations: int = 0
    failed_integrations: int = 0
    average_integration_time: float = 0.0
    last_integration_time: float = 0.0
    event_queue_size: int = 0
    robot_state_transitions: int = 0

class OrderManagementIntegration:
    """
    Integrates order management system with existing simulation components.
    
    Provides seamless integration between order management components and
    the existing simulation engine, event system, robot state machine,
    and performance monitoring systems.
    """
    
    def __init__(self, simulation_engine: SimulationEngine, 
                 event_system: EventSystem,
                 config_manager: ConfigurationManager):
        """
        Initialize the order management integration.
        
        Args:
            simulation_engine: Main simulation engine
            event_system: Event system for communication
            config_manager: Configuration manager
        """
        self.simulation_engine = simulation_engine
        self.event_system = event_system
        self.config_manager = config_manager
        
        # Initialize order management components
        # Get warehouse layout from simulation engine
        warehouse_layout = self.simulation_engine.warehouse_layout if hasattr(self.simulation_engine, 'warehouse_layout') else None
        
        if warehouse_layout is None:
            # Create a default warehouse layout if not available
            from core.layout.warehouse_layout import WarehouseLayoutManager
            warehouse_layout = WarehouseLayoutManager()
        
        self.order_generator = OrderGenerator(warehouse_layout)
        self.queue_manager = OrderQueueManager()
        self.robot_assigner = RobotOrderAssigner()
        self.status_tracker = OrderStatusTracker(self.robot_assigner, self.queue_manager)
        self.analytics = OrderAnalytics(self.status_tracker, self.robot_assigner, self.queue_manager)
        self.dashboard = AnalyticsDashboard(self.analytics)
        
        # Integration state
        self.is_integrated = False
        self.integration_metrics = IntegrationMetrics()
        self.last_update_time = time.time()
        
        # Event handlers
        self.event_handlers = {
            IntegrationEventType.ORDER_CREATED: self._handle_order_created,
            IntegrationEventType.ORDER_ASSIGNED: self._handle_order_assigned,
            IntegrationEventType.ORDER_STARTED: self._handle_order_started,
            IntegrationEventType.ORDER_COMPLETED: self._handle_order_completed,
            IntegrationEventType.ROBOT_STATE_CHANGED: self._handle_robot_state_changed,
            IntegrationEventType.ANALYTICS_UPDATED: self._handle_analytics_updated
        }
        
        print(f"🔗 OrderManagementIntegration initialized")
    
    async def integrate_with_simulation(self) -> bool:
        """
        Integrate order management with simulation engine.
        
        Returns:
            True if integration successful, False otherwise
        """
        try:
            print("🔗 Starting order management integration...")
            
            # Configure components with simulation settings
            await self._configure_components()
            
            # Set up event handlers
            await self._setup_event_handlers()
            
            # Initialize integration with robot state machine
            await self._integrate_robot_state_machine()
            
            # Connect analytics with performance monitoring
            await self._integrate_analytics()
            
            # Set up real-time monitoring
            await self._setup_real_time_monitoring()
            
            self.is_integrated = True
            self.integration_metrics.successful_integrations += 1
            
            print("✅ Order management integration completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Order management integration failed: {e}")
            self.integration_metrics.failed_integrations += 1
            return False
    
    async def _configure_components(self):
        """Configure order management components with simulation settings."""
        try:
            # Get configuration
            order_config = self.config_manager.get_order_generation_config()
            robot_config = self.config_manager.get_robot_config()
            analytics_config = self.config_manager.get_analytics_config()
            
            # Configure order generator
            self.order_generator.set_generation_interval(order_config.generation_interval)
            self.order_generator.set_item_limits(order_config.min_items_per_order, order_config.max_items_per_order)
            self.order_generator.set_auto_start(order_config.auto_start)
            
            # Configure robot assigner
            self.robot_assigner.set_robot_id(robot_config.robot_id)
            
            # Configure analytics
            self.analytics.auto_export_interval = analytics_config.auto_export_interval
            self.analytics.export_directory = analytics_config.export_directory
            
            print("⚙️ Components configured with simulation settings")
            
        except Exception as e:
            print(f"❌ Error configuring components: {e}")
            raise
    
    async def _setup_event_handlers(self):
        """Set up event handlers for order management events."""
        try:
            # Register event handlers with simulation event system
            for event_type, handler in self.event_handlers.items():
                await self.event_system.register_handler(event_type.value, handler)
            
            # Set up order generator event emission
            self.order_generator.set_event_emitter(self._emit_order_event)
            
            # Set up robot assigner event emission
            self.robot_assigner.set_event_emitter(self._emit_robot_event)
            
            # Set up status tracker event emission
            self.status_tracker.set_event_emitter(self._emit_status_event)
            
            print("📡 Event handlers configured")
            
        except Exception as e:
            print(f"❌ Error setting up event handlers: {e}")
            raise
    
    async def _integrate_robot_state_machine(self):
        """Integrate with existing robot state machine."""
        try:
            # Get robot from simulation engine
            robot = self.simulation_engine.robot
            
            # Set up robot state change monitoring
            original_state = robot.state
            
            # Monitor robot state changes
            async def monitor_robot_state():
                while self.is_integrated:
                    if robot.state != original_state:
                        await self._handle_robot_state_change(original_state, robot.state)
                        original_state = robot.state
                    await asyncio.sleep(0.1)
            
            # Start monitoring task
            asyncio.create_task(monitor_robot_state())
            
            print("🤖 Robot state machine integration configured")
            
        except Exception as e:
            print(f"❌ Error integrating robot state machine: {e}")
            raise
    
    async def _integrate_analytics(self):
        """Integrate analytics with existing performance monitoring."""
        try:
            # Connect analytics with simulation performance metrics
            simulation_metrics = self.simulation_engine.performance_metrics
            
            # Set up analytics update callback
            def update_analytics_callback():
                # Update analytics with simulation metrics
                self.analytics.update_system_metrics_from_simulation(simulation_metrics)
            
            # Register callback with simulation engine
            self.simulation_engine.register_analytics_callback(update_analytics_callback)
            
            print("📊 Analytics integration configured")
            
        except Exception as e:
            print(f"❌ Error integrating analytics: {e}")
            raise
    
    async def _setup_real_time_monitoring(self):
        """Set up real-time monitoring integration."""
        try:
            # Set up dashboard refresh
            async def refresh_dashboard():
                while self.is_integrated:
                    if self.dashboard.auto_refresh():
                        dashboard_data = self.dashboard.display_dashboard()
                        # Send to simulation debug system
                        await self.event_system.emit(EventType.DEBUG_INFO, {
                            'dashboard_data': dashboard_data,
                            'timestamp': time.time()
                        })
                    await asyncio.sleep(1.0)
            
            # Start dashboard refresh task
            asyncio.create_task(refresh_dashboard())
            
            print("📺 Real-time monitoring configured")
            
        except Exception as e:
            print(f"❌ Error setting up real-time monitoring: {e}")
            raise
    
    async def _emit_order_event(self, event_type: str, data: Dict[str, Any]):
        """Emit order-related events to simulation event system."""
        try:
            # Map order event types to actual EventType enum members
            event_mapping = {
                'order_created': EventType.ORDER_CREATED,
                'order_assigned': EventType.ORDER_ASSIGNED,
                'order_completed': EventType.ORDER_COMPLETED,
                'order_started': EventType.ORDER_ASSIGNED,  # Use ORDER_ASSIGNED for started orders
                'order_failed': EventType.SYSTEM_ERROR,  # Use SYSTEM_ERROR for failed orders
                'order_updated': EventType.ORDER_ASSIGNED  # Use ORDER_ASSIGNED for updates
            }
            
            actual_event_type = event_mapping.get(event_type, EventType.ORDER_CREATED)
            
            await self.event_system.emit(actual_event_type, {
                'order_event_type': event_type,
                'order_data': data,
                'timestamp': time.time()
            })
            
            # Update integration metrics
            self.integration_metrics.total_orders_processed += 1
            self.integration_metrics.last_integration_time = time.time()
            
        except Exception as e:
            print(f"❌ Error emitting order event: {e}")
    
    async def _emit_robot_event(self, event_type: str, data: Dict[str, Any]):
        """Emit robot-related events to simulation event system."""
        try:
            # Map robot event types to actual EventType enum members
            event_mapping = {
                'robot_move': EventType.ROBOT_MOVED,
                'robot_state_changed': EventType.ROBOT_STATE_CHANGED,
                'robot_started': EventType.ROBOT_STATE_CHANGED,
                'robot_stopped': EventType.ROBOT_STATE_CHANGED,
                'robot_error': EventType.SYSTEM_ERROR
            }
            
            actual_event_type = event_mapping.get(event_type, EventType.ROBOT_MOVED)
            
            await self.event_system.emit(actual_event_type, {
                'robot_event_type': event_type,
                'robot_data': data,
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"❌ Error emitting robot event: {e}")
    
    async def _emit_status_event(self, event_type: str, data: Dict[str, Any]):
        """Emit status-related events to simulation event system."""
        try:
            # Map status event types to actual EventType enum members
            event_mapping = {
                'status_updated': EventType.ORDER_ASSIGNED,  # Use ORDER_ASSIGNED for status updates
                'status_completed': EventType.ORDER_COMPLETED,
                'status_failed': EventType.SYSTEM_ERROR,
                'status_warning': EventType.SYSTEM_WARNING
            }
            
            actual_event_type = event_mapping.get(event_type, EventType.ORDER_ASSIGNED)
            
            await self.event_system.emit(actual_event_type, {
                'status_event_type': event_type,
                'status_data': data,
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"❌ Error emitting status event: {e}")
    
    async def _handle_order_created(self, data: Dict[str, Any]):
        """Handle order created event."""
        try:
            order = data.get('order')
            if order:
                # Add to queue
                self.queue_manager.add_order(order)
                
                # Update analytics
                self.analytics.update_order_metrics(order)
                
                print(f"📋 Order {order.order_id} created and queued")
                
        except Exception as e:
            print(f"❌ Error handling order created: {e}")
    
    async def _handle_order_assigned(self, data: Dict[str, Any]):
        """Handle order assigned event."""
        try:
            order_id = data.get('order_id')
            robot_id = data.get('robot_id')
            
            if order_id and robot_id:
                # Update robot state
                robot = self.simulation_engine.robot
                robot.state = RobotState.MOVING
                
                # Update status tracker
                self.status_tracker.update_order_status(order_id, OrderStatus.IN_PROGRESS)
                
                print(f"🤖 Order {order_id} assigned to {robot_id}")
                
        except Exception as e:
            print(f"❌ Error handling order assigned: {e}")
    
    async def _handle_order_started(self, data: Dict[str, Any]):
        """Handle order started event."""
        try:
            order_id = data.get('order_id')
            
            if order_id:
                # Update robot state
                robot = self.simulation_engine.robot
                robot.state = RobotState.COLLECTING
                
                print(f"🚀 Order {order_id} started")
                
        except Exception as e:
            print(f"❌ Error handling order started: {e}")
    
    async def _handle_order_completed(self, data: Dict[str, Any]):
        """Handle order completed event."""
        try:
            order_id = data.get('order_id')
            
            if order_id:
                # Update robot state
                robot = self.simulation_engine.robot
                robot.state = RobotState.IDLE
                
                # Update analytics
                order = self.queue_manager.get_order_by_id(order_id)
                if order:
                    self.analytics.update_order_metrics(order)
                
                # Remove from queue
                self.queue_manager.remove_order(order_id)
                
                print(f"✅ Order {order_id} completed")
                
        except Exception as e:
            print(f"❌ Error handling order completed: {e}")
    
    async def _handle_robot_state_changed(self, data: Dict[str, Any]):
        """Handle robot state change event."""
        try:
            old_state = data.get('old_state')
            new_state = data.get('new_state')
            
            if old_state and new_state:
                self.integration_metrics.robot_state_transitions += 1
                
                # Update analytics
                robot_data = {
                    'status': new_state.value,
                    'current_position': self.simulation_engine.robot.position.__dict__,
                    'target_location': self.simulation_engine.robot.position.__dict__,
                    'movement_direction': 'FORWARD',
                    'items_held': [],
                    'target_items': [],
                    'snake_path_segment': 'AISLE_1_LEFT_TO_RIGHT',
                    'orders_completed': 0,
                    'total_distance_traveled': self.simulation_engine.robot.total_distance
                }
                
                self.analytics.update_robot_metrics('ROBOT_001', robot_data)
                
                print(f"🤖 Robot state changed: {old_state.value} → {new_state.value}")
                
        except Exception as e:
            print(f"❌ Error handling robot state change: {e}")
    
    async def _handle_analytics_updated(self, data: Dict[str, Any]):
        """Handle analytics update event."""
        try:
            # Update dashboard
            dashboard_data = self.dashboard.display_dashboard()
            
            # Emit to simulation debug system using SYSTEM_WARNING for debug info
            await self.event_system.emit(EventType.SYSTEM_WARNING, {
                'analytics_data': dashboard_data,
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"❌ Error handling analytics update: {e}")
    
    async def _handle_robot_state_change(self, old_state: RobotState, new_state: RobotState):
        """Handle robot state change from simulation."""
        try:
            await self._handle_robot_state_changed({
                'old_state': old_state,
                'new_state': new_state
            })
            
        except Exception as e:
            print(f"❌ Error handling robot state change: {e}")
    
    async def update_integration(self, delta_time: float):
        """Update integration components."""
        try:
            if not self.is_integrated:
                return
            
            # Update order generator
            self.order_generator.update(delta_time)
            
            # Update queue manager
            self.queue_manager.update()
            
            # Update robot assigner
            self.robot_assigner.update()
            
            # Update status tracker
            self.status_tracker.update()
            
            # Update analytics
            self.analytics._update_system_metrics()
            
            # Update integration metrics
            self.integration_metrics.last_integration_time = time.time()
            
        except Exception as e:
            print(f"❌ Error updating integration: {e}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and metrics."""
        try:
            return {
                'is_integrated': self.is_integrated,
                'integration_metrics': {
                    'total_orders_processed': self.integration_metrics.total_orders_processed,
                    'successful_integrations': self.integration_metrics.successful_integrations,
                    'failed_integrations': self.integration_metrics.failed_integrations,
                    'average_integration_time': self.integration_metrics.average_integration_time,
                    'last_integration_time': self.integration_metrics.last_integration_time,
                    'event_queue_size': self.integration_metrics.event_queue_size,
                    'robot_state_transitions': self.integration_metrics.robot_state_transitions
                },
                'component_status': {
                    'order_generator': self.order_generator.is_generating,
                    'queue_manager': self.queue_manager.get_queue_size(),
                    'robot_assigner': hasattr(self.robot_assigner, 'is_active') and self.robot_assigner.is_active,
                    'status_tracker': hasattr(self.status_tracker, 'is_tracking') and self.status_tracker.is_tracking,
                    'analytics': self.analytics.get_analytics_summary()
                },
                'last_update': self.last_update_time
            }
            
        except Exception as e:
            print(f"❌ Error getting integration status: {e}")
            return {'error': str(e)}
    
    async def shutdown_integration(self):
        """Shutdown integration components."""
        try:
            print("🔄 Shutting down order management integration...")
            
            # Stop order generator
            self.order_generator.stop()
            
            # Clear queue
            self.queue_manager.clear_queue()
            
            # Stop tracking
            self.status_tracker.stop_tracking()
            
            # Reset analytics
            self.analytics.reset_analytics()
            
            self.is_integrated = False
            
            print("✅ Order management integration shutdown complete")
            
        except Exception as e:
            print(f"❌ Error shutting down integration: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for integration monitoring."""
        try:
            return {
                'integration_status': self.get_integration_status(),
                'dashboard': self.dashboard.get_dashboard_summary(),
                'analytics': self.analytics.get_real_time_metrics()
            }
            
        except Exception as e:
            print(f"❌ Error getting dashboard data: {e}")
            return {'error': str(e)} 