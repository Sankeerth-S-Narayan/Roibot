"""
Tests for layout integration with existing systems.

Tests the LayoutIntegrationManager class functionality including integration
with SimulationEngine, EventSystem, and ConfigurationManager.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from core.layout.integration import LayoutIntegrationManager, LayoutEvent
from core.layout.coordinate import Coordinate
from core.layout.warehouse_layout import GridState


class TestLayoutIntegrationManager(unittest.TestCase):
    """Test cases for LayoutIntegrationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = LayoutIntegrationManager()
        self.coord1 = Coordinate(1, 1)
        self.coord2 = Coordinate(5, 5)
        self.coord3 = Coordinate(10, 10)
    
    def test_initialization(self):
        """Test LayoutIntegrationManager initialization."""
        self.assertIsNotNone(self.integration.warehouse_layout)
        self.assertIsNotNone(self.integration.snake_pattern)
        self.assertIsNotNone(self.integration.packout_manager)
        self.assertIsNotNone(self.integration.distance_tracker)
        self.assertIsNotNone(self.integration.grid_visualizer)
        self.assertFalse(self.integration._initialized)
    
    def test_initialize_integration_success(self):
        """Test successful integration initialization."""
        # Mock external systems
        mock_sim_engine = Mock()
        mock_event_system = Mock()
        mock_config_manager = Mock()
        
        # Mock configuration
        mock_config_manager.get_section.return_value = {
            'grid_dimensions': (25, 20),
            'packout_location': {'aisle': 1, 'rack': 1},
            'visualization_settings': {
                'show_coordinates': True,
                'show_legend': True,
                'compact_mode': False
            }
        }
        
        # Initialize integration
        result = self.integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        
        self.assertTrue(result)
        self.assertTrue(self.integration._initialized)
        self.assertEqual(self.integration._simulation_engine, mock_sim_engine)
        self.assertEqual(self.integration._event_system, mock_event_system)
        self.assertEqual(self.integration._config_manager, mock_config_manager)
    
    def test_initialize_integration_with_warnings(self):
        """Test integration initialization with configuration warnings."""
        # Mock external systems that will cause warnings but not failures
        mock_sim_engine = Mock()
        mock_event_system = Mock()
        mock_config_manager = Mock()
        mock_config_manager.get_section.return_value = None  # Will cause warning but not failure
        
        # Initialize integration
        result = self.integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        
        # Should succeed even with warnings
        self.assertTrue(result)
        self.assertTrue(self.integration._initialized)
    
    def test_handle_robot_move(self):
        """Test robot move event handling."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Create event data
        event_data = {
            'robot_id': 'robot_001',
            'from_coordinate': self.coord1,
            'to_coordinate': self.coord2,
            'direction': 'forward'
        }
        
        # Handle robot move
        self.integration._handle_robot_move(event_data)
        
        # Verify robot position was updated
        self.assertEqual(
            self.integration.grid_visualizer.robot_positions['robot_001'],
            self.coord2
        )
        
        # Verify distance was tracked
        self.assertGreater(
            self.integration.distance_tracker.get_robot_distance('robot_001'),
            0
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_handle_order_start(self):
        """Test order start event handling."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Create event data
        event_data = {
            'order_id': 'order_001',
            'robot_id': 'robot_001',
            'start_coordinate': self.coord1
        }
        
        # Handle order start
        self.integration._handle_order_start(event_data)
        
        # Verify order distance was initialized
        self.assertEqual(
            self.integration.distance_tracker.get_order_distance('order_001'),
            0.0
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_handle_order_complete(self):
        """Test order completion event handling."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Start an order first
        self.integration.distance_tracker.track_order_start('order_001', 'robot_001', self.coord1)
        self.integration.distance_tracker.track_pickup_item('order_001', 'robot_001', self.coord1, self.coord2)
        
        # Create event data
        event_data = {
            'order_id': 'order_001',
            'robot_id': 'robot_001',
            'final_coordinate': self.coord2
        }
        
        # Handle order complete
        self.integration._handle_order_complete(event_data)
        
        # Verify order distance was tracked
        self.assertGreater(
            self.integration.distance_tracker.get_order_distance('order_001'),
            0
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_handle_item_pickup(self):
        """Test item pickup event handling."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Start an order first
        self.integration.distance_tracker.track_order_start('order_001', 'robot_001', self.coord1)
        
        # Create event data
        event_data = {
            'order_id': 'order_001',
            'robot_id': 'robot_001',
            'from_coordinate': self.coord1,
            'to_coordinate': self.coord2
        }
        
        # Handle item pickup
        self.integration._handle_item_pickup(event_data)
        
        # Verify pickup distance was tracked
        self.assertGreater(
            self.integration.distance_tracker.get_order_distance('order_001'),
            0
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_handle_item_delivery(self):
        """Test item delivery event handling."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Start an order first
        self.integration.distance_tracker.track_order_start('order_001', 'robot_001', self.coord1)
        
        # Create event data
        event_data = {
            'order_id': 'order_001',
            'robot_id': 'robot_001',
            'from_coordinate': self.coord2
        }
        
        # Handle item delivery
        self.integration._handle_item_delivery(event_data)
        
        # Verify delivery distance was tracked
        self.assertGreater(
            self.integration.distance_tracker.get_order_distance('order_001'),
            0
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_update_simulation_step(self):
        """Test simulation step update."""
        # Initialize integration
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Create step data
        step_data = {
            'robot_positions': {
                'robot_001': self.coord2,
                'robot_002': self.coord3
            },
            'grid_updates': [
                {
                    'coordinate': self.coord2,
                    'state': 'occupied'
                }
            ]
        }
        
        # Update simulation step
        self.integration.update_simulation_step(step_data)
        
        # Verify robot positions were updated
        self.assertEqual(
            self.integration.grid_visualizer.robot_positions['robot_001'],
            self.coord2
        )
        self.assertEqual(
            self.integration.grid_visualizer.robot_positions['robot_002'],
            self.coord3
        )
        
        # Verify event was emitted
        mock_event_system.emit.assert_called()
    
    def test_get_layout_state(self):
        """Test layout state export."""
        # Initialize integration
        self.integration._initialized = True
        
        # Get layout state
        state = self.integration.get_layout_state()
        
        # Verify state structure
        self.assertIn('warehouse_layout', state)
        self.assertIn('distance_tracker', state)
        self.assertIn('grid_visualizer', state)
        self.assertIn('packout_manager', state)
        
        # Verify data integrity
        self.assertIsInstance(state['warehouse_layout'], dict)
        self.assertIsInstance(state['distance_tracker'], dict)
        self.assertIsInstance(state['grid_visualizer'], dict)
        self.assertIsInstance(state['packout_manager'], dict)
    
    def test_load_layout_state(self):
        """Test layout state import."""
        # Initialize integration
        self.integration._initialized = True
        
        # Create test state
        test_state = {
            'warehouse_layout': {
                'dimensions': {'max_aisle': 25, 'max_rack': 20},
                'grid_state': {},
                'occupied_positions': [],
                'statistics': {'total_positions': 500, 'occupied_positions': 0, 'empty_positions': 500}
            },
            'distance_tracker': {
                'total_distance': 10.0,
                'order_distances': {'order_001': 5.0},
                'robot_distances': {'robot_001': 10.0},
                'events': [],
                'current_positions': {}
            },
            'grid_visualizer': {
                'robot_positions': {},
                'highlighted_cells': [],
                'path_cells': [],
                'start_cells': [],
                'target_cells': [],
                'warehouse_stats': {'total_positions': 500, 'occupied_positions': 0, 'empty_positions': 500}
            },
            'packout_manager': {
                'packout_location': {'aisle': 1, 'rack': 1},
                'restricted_zones': []
            }
        }
        
        # Load layout state
        result = self.integration.load_layout_state(test_state)
        
        self.assertTrue(result)
    
    def test_save_configuration(self):
        """Test configuration saving."""
        # Initialize integration with mock config manager
        mock_config_manager = Mock()
        self.integration._config_manager = mock_config_manager
        self.integration._initialized = True
        
        # Save configuration
        result = self.integration.save_configuration()
        
        self.assertTrue(result)
        mock_config_manager.set_section.assert_called()
    
    def test_save_configuration_no_manager(self):
        """Test configuration saving without config manager."""
        # Initialize integration without config manager
        self.integration._config_manager = None
        self.integration._initialized = True
        
        # Save configuration
        result = self.integration.save_configuration()
        
        self.assertFalse(result)
    
    def test_validate_grid_integrity(self):
        """Test grid integrity validation."""
        # Initialize integration
        self.integration._initialized = True
        
        # Validate grid integrity
        results = self.integration.validate_grid_integrity()
        
        # Verify results structure
        self.assertIn('valid', results)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        self.assertIn('statistics', results)
        
        # Should be valid by default
        self.assertTrue(results['valid'])
        self.assertIsInstance(results['errors'], list)
        self.assertIsInstance(results['warnings'], list)
        self.assertIsInstance(results['statistics'], dict)
    
    def test_get_integration_status(self):
        """Test integration status retrieval."""
        # Initialize integration
        self.integration._initialized = True
        
        # Get integration status
        status = self.integration.get_integration_status()
        
        # Verify status structure
        self.assertIn('initialized', status)
        self.assertIn('simulation_engine_connected', status)
        self.assertIn('event_system_connected', status)
        self.assertIn('config_manager_connected', status)
        self.assertIn('warehouse_layout_ready', status)
        self.assertIn('distance_tracker_ready', status)
        self.assertIn('grid_visualizer_ready', status)
        self.assertIn('packout_manager_ready', status)
        self.assertIn('validation_results', status)
        
        # Verify status values
        self.assertTrue(status['initialized'])
        self.assertTrue(status['warehouse_layout_ready'])
        self.assertTrue(status['distance_tracker_ready'])
        self.assertTrue(status['grid_visualizer_ready'])
        self.assertTrue(status['packout_manager_ready'])
    
    def test_create_extension_points(self):
        """Test extension points creation."""
        # Initialize integration
        self.integration._initialized = True
        
        # Create extension points
        extension_points = self.integration.create_extension_points()
        
        # Verify extension points structure
        self.assertIn('warehouse_layout', extension_points)
        self.assertIn('snake_pattern', extension_points)
        self.assertIn('packout_manager', extension_points)
        self.assertIn('distance_tracker', extension_points)
        self.assertIn('grid_visualizer', extension_points)
        self.assertIn('integration_manager', extension_points)
        self.assertIn('event_handlers', extension_points)
        
        # Verify components are accessible
        self.assertIsNotNone(extension_points['warehouse_layout'])
        self.assertIsNotNone(extension_points['snake_pattern'])
        self.assertIsNotNone(extension_points['packout_manager'])
        self.assertIsNotNone(extension_points['distance_tracker'])
        self.assertIsNotNone(extension_points['grid_visualizer'])
        self.assertIsNotNone(extension_points['integration_manager'])
        self.assertIsInstance(extension_points['event_handlers'], dict)
    
    def test_emit_layout_event(self):
        """Test layout event emission."""
        # Initialize integration with mock event system
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        self.integration._initialized = True
        
        # Create event data
        event_data = {
            'robot_id': 'robot_001',
            'position': self.coord2,
            'distance': 10.0
        }
        
        # Emit layout event
        self.integration._emit_layout_event("robot_position_updated", event_data)
        
        # Verify event was emitted
        mock_event_system.emit.assert_called_with("robot_position_updated", unittest.mock.ANY)
    
    def test_emit_layout_event_no_system(self):
        """Test layout event emission without event system."""
        # Initialize integration without event system
        self.integration._event_system = None
        self.integration._initialized = True
        
        # Create event data
        event_data = {
            'robot_id': 'robot_001',
            'position': self.coord2
        }
        
        # Should not raise exception
        self.integration._emit_layout_event("test_event", event_data)
    
    def test_load_configuration(self):
        """Test configuration loading."""
        # Initialize integration with mock config manager
        mock_config_manager = Mock()
        mock_config_manager.get_section.return_value = {
            'grid_dimensions': (25, 20),
            'packout_location': {'aisle': 1, 'rack': 1},
            'visualization_settings': {
                'show_coordinates': False,
                'show_legend': False,
                'compact_mode': True
            }
        }
        self.integration._config_manager = mock_config_manager
        
        # Load configuration
        self.integration._load_configuration()
        
        # Verify configuration was applied
        self.assertFalse(self.integration.grid_visualizer.show_coordinates)
        self.assertFalse(self.integration.grid_visualizer.show_legend)
        self.assertTrue(self.integration.grid_visualizer.compact_mode)
    
    def test_register_event_handlers(self):
        """Test event handler registration."""
        # Initialize integration with mock event system
        mock_event_system = Mock()
        self.integration._event_system = mock_event_system
        
        # Register event handlers
        self.integration._register_event_handlers()
        
        # Verify handlers were registered
        self.assertEqual(mock_event_system.register_handler.call_count, 5)
        
        # Verify specific handlers
        calls = mock_event_system.register_handler.call_args_list
        event_types = [call[0][0] for call in calls]
        self.assertIn("robot_move", event_types)
        self.assertIn("order_start", event_types)
        self.assertIn("order_complete", event_types)
        self.assertIn("item_pickup", event_types)
        self.assertIn("item_delivery", event_types)


class TestLayoutEvent(unittest.TestCase):
    """Test cases for LayoutEvent dataclass."""
    
    def test_layout_event_creation(self):
        """Test LayoutEvent creation."""
        event = LayoutEvent(
            event_type="test_event",
            timestamp=datetime.now(),
            coordinate=Coordinate(1, 1),
            robot_id="robot_001",
            order_id="order_001",
            metadata={"key": "value"}
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertIsInstance(event.timestamp, datetime)
        self.assertEqual(event.coordinate, Coordinate(1, 1))
        self.assertEqual(event.robot_id, "robot_001")
        self.assertEqual(event.order_id, "order_001")
        self.assertEqual(event.metadata, {"key": "value"})
    
    def test_layout_event_defaults(self):
        """Test LayoutEvent default values."""
        event = LayoutEvent(
            event_type="test_event",
            timestamp=datetime.now()
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertIsInstance(event.timestamp, datetime)
        self.assertIsNone(event.coordinate)
        self.assertIsNone(event.robot_id)
        self.assertIsNone(event.order_id)
        self.assertIsInstance(event.metadata, dict)


if __name__ == "__main__":
    unittest.main() 