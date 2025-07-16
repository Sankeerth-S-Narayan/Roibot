import unittest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from entities.order_management_integration import (
    OrderManagementIntegration, 
    IntegrationEventType, 
    IntegrationMetrics
)
from entities.configuration_manager import ConfigurationManager
from entities.robot_orders import Order, OrderStatus
from core.engine import SimulationEngine, RobotState
from core.events import EventSystem, EventType
from core.state import SimulationState

class TestOrderManagementIntegration(unittest.TestCase):
    """Test cases for OrderManagementIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.simulation_engine = Mock(spec=SimulationEngine)
        self.event_system = Mock(spec=EventSystem)
        self.config_manager = Mock(spec=ConfigurationManager)
        
        # Set up mock warehouse layout
        self.mock_warehouse_layout = Mock()
        self.simulation_engine.warehouse_layout = self.mock_warehouse_layout
        
        # Set up mock robot
        self.mock_robot = Mock()
        self.mock_robot.state = RobotState.IDLE
        self.mock_robot.position = Mock()
        self.mock_robot.position.__dict__ = {'x': 1, 'y': 1}
        self.mock_robot.total_distance = 0.0
        
        self.simulation_engine.robot = self.mock_robot
        
        # Set up mock performance metrics
        self.simulation_engine.performance_metrics = {
            'total_distance': 100.0,
            'items_collected': 5,
            'orders_completed': 2,
            'direction_changes': 3,
            'path_optimizations': 1
        }
        
        # Set up mock configuration returns
        self.config_manager.get_order_generation_config.return_value = Mock(
            generation_interval=30.0,
            min_items_per_order=1,
            max_items_per_order=4,
            auto_start=True
        )
        
        self.config_manager.get_robot_config.return_value = Mock(
            robot_id="ROBOT_001"
        )
        
        self.config_manager.get_analytics_config.return_value = Mock(
            auto_export_interval=300.0,
            export_directory="exports"
        )
        
        # Create integration instance
        self.integration = OrderManagementIntegration(
            self.simulation_engine,
            self.event_system,
            self.config_manager
        )
    
    def test_initialization(self):
        """Test OrderManagementIntegration initialization."""
        self.assertFalse(self.integration.is_integrated)
        self.assertIsInstance(self.integration.integration_metrics, IntegrationMetrics)
        self.assertIsNotNone(self.integration.order_generator)
        self.assertIsNotNone(self.integration.queue_manager)
        self.assertIsNotNone(self.integration.robot_assigner)
        self.assertIsNotNone(self.integration.status_tracker)
        self.assertIsNotNone(self.integration.analytics)
        self.assertIsNotNone(self.integration.dashboard)
        self.assertEqual(len(self.integration.event_handlers), 6)
    
    @patch('asyncio.create_task')
    async def test_integrate_with_simulation_success(self, mock_create_task):
        """Test successful integration with simulation."""
        # Mock async methods
        self.event_system.register_handler = AsyncMock()
        self.event_system.emit = AsyncMock()
        
        # Mock component methods
        self.integration.order_generator.set_event_emitter = Mock()
        self.integration.robot_assigner.set_event_emitter = Mock()
        self.integration.status_tracker.set_event_emitter = Mock()
        self.simulation_engine.register_analytics_callback = Mock()
        
        # Test integration
        result = await self.integration.integrate_with_simulation()
        
        self.assertTrue(result)
        self.assertTrue(self.integration.is_integrated)
        self.assertEqual(self.integration.integration_metrics.successful_integrations, 1)
        self.assertEqual(self.integration.integration_metrics.failed_integrations, 0)
    
    @patch('asyncio.create_task')
    async def test_integrate_with_simulation_failure(self, mock_create_task):
        """Test integration failure handling."""
        # Mock failure
        self.event_system.register_handler.side_effect = Exception("Integration failed")
        
        # Test integration
        result = await self.integration.integrate_with_simulation()
        
        self.assertFalse(result)
        self.assertFalse(self.integration.is_integrated)
        self.assertEqual(self.integration.integration_metrics.successful_integrations, 0)
        self.assertEqual(self.integration.integration_metrics.failed_integrations, 1)
    
    def test_configure_components(self):
        """Test component configuration."""
        # Mock component methods
        self.integration.order_generator.set_generation_interval = Mock()
        self.integration.order_generator.set_item_limits = Mock()
        self.integration.order_generator.set_auto_start = Mock()
        self.integration.robot_assigner.set_robot_id = Mock()
        
        # Call the async method synchronously for testing
        import asyncio
        asyncio.run(self.integration._configure_components())
        
        # Verify configuration calls
        self.integration.order_generator.set_generation_interval.assert_called_with(30.0)
        self.integration.order_generator.set_item_limits.assert_called_with(1, 4)
        self.integration.order_generator.set_auto_start.assert_called_with(True)
        self.integration.robot_assigner.set_robot_id.assert_called_with("ROBOT_001")
    
    def test_setup_event_handlers(self):
        """Test event handler setup."""
        # Mock async methods
        self.event_system.register_handler = AsyncMock()
        
        # Mock component methods
        self.integration.order_generator.set_event_emitter = Mock()
        self.integration.robot_assigner.set_event_emitter = Mock()
        self.integration.status_tracker.set_event_emitter = Mock()
        
        # Call the async method synchronously for testing
        import asyncio
        asyncio.run(self.integration._setup_event_handlers())
        
        # Verify event handler registration
        self.assertEqual(self.event_system.register_handler.call_count, 6)
        
        # Verify event emitter setup
        self.integration.order_generator.set_event_emitter.assert_called_once()
        self.integration.robot_assigner.set_event_emitter.assert_called_once()
        self.integration.status_tracker.set_event_emitter.assert_called_once()
    
    @patch('asyncio.create_task')
    def test_integrate_robot_state_machine(self, mock_create_task):
        """Test robot state machine integration."""
        import asyncio
        asyncio.run(self.integration._integrate_robot_state_machine())
        
        # Verify monitoring task creation
        mock_create_task.assert_called_once()
    
    def test_integrate_analytics(self):
        """Test analytics integration."""
        # Mock simulation engine method
        self.simulation_engine.register_analytics_callback = Mock()
        
        import asyncio
        asyncio.run(self.integration._integrate_analytics())
        
        # Verify analytics callback registration
        self.simulation_engine.register_analytics_callback.assert_called_once()
    
    @patch('asyncio.create_task')
    def test_setup_real_time_monitoring(self, mock_create_task):
        """Test real-time monitoring setup."""
        # Mock async methods
        self.event_system.emit = AsyncMock()
        
        import asyncio
        asyncio.run(self.integration._setup_real_time_monitoring())
        
        # Verify monitoring task creation
        mock_create_task.assert_called_once()
    
    def test_emit_order_event(self):
        """Test order event emission."""
        # Mock async method
        self.event_system.emit = AsyncMock()
        
        test_data = {'order_id': 'ORD_001', 'items': ['ITEM_A1']}
        import asyncio
        asyncio.run(self.integration._emit_order_event('order_created', test_data))
        
        # Verify event emission
        self.event_system.emit.assert_called_once_with(EventType.ORDER_CREATED, {
            'order_event_type': 'order_created',
            'order_data': test_data,
            'timestamp': unittest.mock.ANY
        })
        
        # Verify metrics update
        self.assertEqual(self.integration.integration_metrics.total_orders_processed, 1)
    
    def test_emit_robot_event(self):
        """Test robot event emission."""
        # Mock async method
        self.event_system.emit = AsyncMock()
        
        test_data = {'robot_id': 'ROBOT_001', 'position': {'x': 1, 'y': 1}}
        import asyncio
        asyncio.run(self.integration._emit_robot_event('robot_move', test_data))
        
        # Verify event emission
        self.event_system.emit.assert_called_once_with(EventType.ROBOT_MOVED, {
            'robot_event_type': 'robot_move',
            'robot_data': test_data,
            'timestamp': unittest.mock.ANY
        })
    
    def test_emit_status_event(self):
        """Test status event emission."""
        # Mock async method
        self.event_system.emit = AsyncMock()
        
        test_data = {'order_id': 'ORD_001', 'status': 'IN_PROGRESS'}
        import asyncio
        asyncio.run(self.integration._emit_status_event('status_updated', test_data))
        
        # Verify event emission
        self.event_system.emit.assert_called_once_with(EventType.ORDER_ASSIGNED, {
            'status_event_type': 'status_updated',
            'status_data': test_data,
            'timestamp': unittest.mock.ANY
        })
    
    def test_handle_order_created(self):
        """Test order created event handling."""
        # Mock component methods
        self.integration.queue_manager.add_order = Mock()
        self.integration.analytics.update_order_metrics = Mock()
        
        test_order = Order("ORD_001", ["ITEM_A1"], [(1, 1)])
        test_data = {'order': test_order}
        
        import asyncio
        asyncio.run(self.integration._handle_order_created(test_data))
        
        # Verify order processing
        self.integration.queue_manager.add_order.assert_called_with(test_order)
        self.integration.analytics.update_order_metrics.assert_called_with(test_order)
    
    def test_handle_order_assigned(self):
        """Test order assigned event handling."""
        # Mock component methods
        self.integration.status_tracker.update_order_status = Mock()
        
        test_data = {'order_id': 'ORD_001', 'robot_id': 'ROBOT_001'}
        
        import asyncio
        asyncio.run(self.integration._handle_order_assigned(test_data))
        
        # Verify robot state update
        self.assertEqual(self.mock_robot.state, RobotState.MOVING)
        
        # Verify status update
        self.integration.status_tracker.update_order_status.assert_called_with(
            'ORD_001', OrderStatus.IN_PROGRESS
        )
    
    def test_handle_order_started(self):
        """Test order started event handling."""
        test_data = {'order_id': 'ORD_001'}
        
        import asyncio
        asyncio.run(self.integration._handle_order_started(test_data))
        
        # Verify robot state update
        self.assertEqual(self.mock_robot.state, RobotState.COLLECTING)
    
    def test_handle_order_completed(self):
        """Test order completed event handling."""
        # Mock component methods
        self.integration.queue_manager.get_order_by_id = Mock(return_value=Order("ORD_001", ["ITEM_A1"], [(1, 1)]))
        self.integration.analytics.update_order_metrics = Mock()
        self.integration.queue_manager.remove_order = Mock()
        
        test_data = {'order_id': 'ORD_001'}
        
        import asyncio
        asyncio.run(self.integration._handle_order_completed(test_data))
        
        # Verify robot state update
        self.assertEqual(self.mock_robot.state, RobotState.IDLE)
        
        # Verify order processing
        self.integration.analytics.update_order_metrics.assert_called_once()
        self.integration.queue_manager.remove_order.assert_called_with('ORD_001')
    
    def test_handle_robot_state_changed(self):
        """Test robot state changed event handling."""
        # Mock component methods
        self.integration.analytics.update_robot_metrics = Mock()
        
        test_data = {
            'old_state': RobotState.IDLE,
            'new_state': RobotState.MOVING
        }
        
        import asyncio
        asyncio.run(self.integration._handle_robot_state_changed(test_data))
        
        # Verify metrics update
        self.integration.analytics.update_robot_metrics.assert_called_once()
        self.assertEqual(self.integration.integration_metrics.robot_state_transitions, 1)
    
    def test_handle_analytics_updated(self):
        """Test analytics updated event handling."""
        # Mock component methods
        self.integration.dashboard.display_dashboard = Mock(return_value={'test': 'data'})
        self.event_system.emit = AsyncMock()
        
        test_data = {'analytics_data': {'test': 'data'}}
        
        import asyncio
        asyncio.run(self.integration._handle_analytics_updated(test_data))
        
        # Verify dashboard update
        self.integration.dashboard.display_dashboard.assert_called_once()
        self.event_system.emit.assert_called_once()
    
    def test_handle_robot_state_change(self):
        """Test robot state change handling."""
        # Mock component methods
        self.integration.analytics.update_robot_metrics = Mock()
        
        import asyncio
        asyncio.run(self.integration._handle_robot_state_change(RobotState.IDLE, RobotState.MOVING))
        
        # Verify metrics update
        self.integration.analytics.update_robot_metrics.assert_called_once()
        self.assertEqual(self.integration.integration_metrics.robot_state_transitions, 1)
    
    def test_update_integration(self):
        """Test integration update."""
        # Mock component methods
        self.integration.order_generator.update = Mock()
        self.integration.queue_manager.update = Mock()
        self.integration.robot_assigner.update = Mock()
        self.integration.status_tracker.update = Mock()
        self.integration.analytics._update_system_metrics = Mock()
        
        # Set integration as active
        self.integration.is_integrated = True
        
        # Test update
        asyncio.run(self.integration.update_integration(0.1))
        
        # Verify component updates
        self.integration.order_generator.update.assert_called_with(0.1)
        self.integration.queue_manager.update.assert_called_once()
        self.integration.robot_assigner.update.assert_called_once()
        self.integration.status_tracker.update.assert_called_once()
        self.integration.analytics._update_system_metrics.assert_called_once()
    
    def test_get_integration_status(self):
        """Test integration status retrieval."""
        status = self.integration.get_integration_status()
        
        self.assertIn('is_integrated', status)
        self.assertIn('integration_metrics', status)
        self.assertIn('component_status', status)
        self.assertIn('last_update', status)
        
        # Check metrics structure
        metrics = status['integration_metrics']
        self.assertIn('total_orders_processed', metrics)
        self.assertIn('successful_integrations', metrics)
        self.assertIn('failed_integrations', metrics)
        self.assertIn('average_integration_time', metrics)
        self.assertIn('last_integration_time', metrics)
        self.assertIn('event_queue_size', metrics)
        self.assertIn('robot_state_transitions', metrics)
        
        # Check component status structure
        component_status = status['component_status']
        self.assertIn('order_generator', component_status)
        self.assertIn('queue_manager', component_status)
        self.assertIn('robot_assigner', component_status)
        self.assertIn('status_tracker', component_status)
        self.assertIn('analytics', component_status)
    
    def test_shutdown_integration(self):
        """Test integration shutdown."""
        # Mock component methods
        self.integration.order_generator.stop = Mock()
        self.integration.queue_manager.clear_queue = Mock()
        self.integration.status_tracker.stop_tracking = Mock()
        self.integration.analytics.reset_analytics = Mock()
        
        # Set integration as active
        self.integration.is_integrated = True
        
        import asyncio
        asyncio.run(self.integration.shutdown_integration())
        
        # Verify shutdown calls
        self.integration.order_generator.stop.assert_called_once()
        self.integration.queue_manager.clear_queue.assert_called_once()
        self.integration.status_tracker.stop_tracking.assert_called_once()
        self.integration.analytics.reset_analytics.assert_called_once()
        
        # Verify integration state
        self.assertFalse(self.integration.is_integrated)
    
    def test_get_dashboard_data(self):
        """Test dashboard data retrieval."""
        # Mock methods
        self.integration.get_integration_status = Mock(return_value={'status': 'active'})
        self.integration.dashboard.get_dashboard_summary = Mock(return_value={'dashboard': 'data'})
        self.integration.analytics.get_real_time_metrics = Mock(return_value={'metrics': 'data'})
        
        dashboard_data = self.integration.get_dashboard_data()
        
        self.assertIn('integration_status', dashboard_data)
        self.assertIn('dashboard', dashboard_data)
        self.assertIn('analytics', dashboard_data)
        
        # Verify method calls
        self.integration.get_integration_status.assert_called_once()
        self.integration.dashboard.get_dashboard_summary.assert_called_once()
        self.integration.analytics.get_real_time_metrics.assert_called_once()


if __name__ == '__main__':
    unittest.main() 