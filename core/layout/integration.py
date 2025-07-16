"""
Integration module for warehouse layout system.

This module provides integration between the warehouse layout system
and existing SimulationEngine, EventSystem, and ConfigurationManager.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from .warehouse_layout import WarehouseLayoutManager, GridState
from .coordinate import Coordinate
from .snake_pattern import SnakePattern, Direction
from .packout_zone import PackoutZoneManager
from .distance_tracker import DistanceTracker, DistanceEventType
from .grid_visualizer import GridVisualizer


@dataclass
class LayoutEvent:
    """Represents a layout-related event."""
    event_type: str
    timestamp: datetime
    coordinate: Optional[Coordinate] = None
    robot_id: Optional[str] = None
    order_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LayoutIntegrationManager:
    """
    Manages integration between warehouse layout and existing systems.
    
    Provides seamless integration with SimulationEngine, EventSystem,
    and ConfigurationManager for comprehensive warehouse management.
    """
    
    def __init__(self):
        """Initialize layout integration manager."""
        self.warehouse_layout = WarehouseLayoutManager()
        self.snake_pattern = SnakePattern()
        self.packout_manager = PackoutZoneManager(self.warehouse_layout)
        self.distance_tracker = DistanceTracker()
        self.grid_visualizer = GridVisualizer(self.warehouse_layout)
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Configuration
        self.config_section = "warehouse_layout"
        self.logger = logging.getLogger(__name__)
        
        # Integration state
        self._simulation_engine = None
        self._event_system = None
        self._config_manager = None
        self._initialized = False
    
    def initialize_integration(self, simulation_engine=None, event_system=None, 
                             config_manager=None) -> bool:
        """
        Initialize integration with existing systems.
        
        Args:
            simulation_engine: SimulationEngine instance
            event_system: EventSystem instance
            config_manager: ConfigurationManager instance
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._simulation_engine = simulation_engine
            self._event_system = event_system
            self._config_manager = config_manager
            
            # Load configuration
            self._load_configuration()
            
            # Register event handlers
            self._register_event_handlers()
            
            # Initialize grid state
            self._initialize_grid_state()
            
            self._initialized = True
            self.logger.info("Layout integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize layout integration: {e}")
            return False
    
    def _load_configuration(self) -> None:
        """Load configuration from ConfigurationManager."""
        if self._config_manager is None:
            return
        
        try:
            config = self._config_manager.get_section(self.config_section)
            if config:
                # Apply configuration settings
                if 'grid_dimensions' in config:
                    dimensions = config['grid_dimensions']
                    self.logger.info(f"Grid dimensions: {dimensions}")
                
                if 'packout_location' in config:
                    packout = config['packout_location']
                    self.logger.info(f"Packout location: {packout}")
                
                if 'visualization_settings' in config:
                    viz_settings = config['visualization_settings']
                    self.grid_visualizer.set_visualization_options(
                        show_coordinates=viz_settings.get('show_coordinates', True),
                        show_legend=viz_settings.get('show_legend', True),
                        compact_mode=viz_settings.get('compact_mode', False)
                    )
                    
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}")
    
    def _register_event_handlers(self) -> None:
        """Register event handlers with EventSystem."""
        if self._event_system is None:
            return
        
        try:
            # Register layout events
            self._event_system.register_handler("robot_move", self._handle_robot_move)
            self._event_system.register_handler("order_start", self._handle_order_start)
            self._event_system.register_handler("order_complete", self._handle_order_complete)
            self._event_system.register_handler("item_pickup", self._handle_item_pickup)
            self._event_system.register_handler("item_delivery", self._handle_item_delivery)
            
            self.logger.info("Event handlers registered successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to register event handlers: {e}")
    
    def _initialize_grid_state(self) -> None:
        """Initialize grid state from configuration."""
        if self._config_manager is None:
            return
        
        try:
            # Load saved grid state if available
            grid_state = self._config_manager.get_value(f"{self.config_section}.grid_state")
            if grid_state:
                self.warehouse_layout.load_grid_snapshot(grid_state)
                self.logger.info("Grid state loaded from configuration")
            
        except Exception as e:
            self.logger.warning(f"Failed to load grid state: {e}")
    
    def _handle_robot_move(self, event_data: Dict[str, Any]) -> None:
        """Handle robot move events."""
        try:
            robot_id = event_data.get('robot_id')
            from_coord = event_data.get('from_coordinate')
            to_coord = event_data.get('to_coordinate')
            direction = event_data.get('direction', 'forward')
            
            if robot_id and from_coord and to_coord:
                # Update robot position in visualizer
                self.grid_visualizer.set_robot_position(robot_id, to_coord)
                
                # Track distance
                self.distance_tracker.track_robot_move(
                    robot_id, from_coord, to_coord, 
                    Direction.FORWARD if direction == 'forward' else Direction.REVERSE
                )
                
                # Emit layout event
                self._emit_layout_event("robot_position_updated", {
                    'robot_id': robot_id,
                    'position': to_coord,
                    'distance': self.distance_tracker.get_robot_distance(robot_id)
                })
                
        except Exception as e:
            self.logger.error(f"Error handling robot move: {e}")
    
    def _handle_order_start(self, event_data: Dict[str, Any]) -> None:
        """Handle order start events."""
        try:
            order_id = event_data.get('order_id')
            robot_id = event_data.get('robot_id')
            start_coord = event_data.get('start_coordinate')
            
            if order_id and robot_id and start_coord:
                # Track order start
                self.distance_tracker.track_order_start(order_id, robot_id, start_coord)
                
                # Emit layout event
                self._emit_layout_event("order_started", {
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'start_coordinate': start_coord
                })
                
        except Exception as e:
            self.logger.error(f"Error handling order start: {e}")
    
    def _handle_order_complete(self, event_data: Dict[str, Any]) -> None:
        """Handle order completion events."""
        try:
            order_id = event_data.get('order_id')
            robot_id = event_data.get('robot_id')
            final_coord = event_data.get('final_coordinate')
            
            if order_id and robot_id and final_coord:
                # Track order completion
                total_distance = self.distance_tracker.track_order_complete(
                    order_id, robot_id, final_coord
                )
                
                # Emit layout event
                self._emit_layout_event("order_completed", {
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'final_coordinate': final_coord,
                    'total_distance': total_distance
                })
                
        except Exception as e:
            self.logger.error(f"Error handling order complete: {e}")
    
    def _handle_item_pickup(self, event_data: Dict[str, Any]) -> None:
        """Handle item pickup events."""
        try:
            order_id = event_data.get('order_id')
            robot_id = event_data.get('robot_id')
            from_coord = event_data.get('from_coordinate')
            to_coord = event_data.get('to_coordinate')
            
            if order_id and robot_id and from_coord and to_coord:
                # Track pickup
                distance = self.distance_tracker.track_pickup_item(
                    order_id, robot_id, from_coord, to_coord
                )
                
                # Emit layout event
                self._emit_layout_event("item_pickup", {
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'pickup_coordinate': to_coord,
                    'distance': distance
                })
                
        except Exception as e:
            self.logger.error(f"Error handling item pickup: {e}")
    
    def _handle_item_delivery(self, event_data: Dict[str, Any]) -> None:
        """Handle item delivery events."""
        try:
            order_id = event_data.get('order_id')
            robot_id = event_data.get('robot_id')
            from_coord = event_data.get('from_coordinate')
            
            if order_id and robot_id and from_coord:
                # Track delivery to packout
                distance = self.distance_tracker.track_deliver_to_packout(
                    order_id, robot_id, from_coord
                )
                
                # Emit layout event
                self._emit_layout_event("item_delivery", {
                    'order_id': order_id,
                    'robot_id': robot_id,
                    'delivery_coordinate': self.packout_manager.packout_location,
                    'distance': distance
                })
                
        except Exception as e:
            self.logger.error(f"Error handling item delivery: {e}")
    
    def _emit_layout_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit layout event to EventSystem."""
        if self._event_system is None:
            return
        
        try:
            event = LayoutEvent(
                event_type=event_type,
                timestamp=datetime.now(),
                coordinate=data.get('coordinate'),
                robot_id=data.get('robot_id'),
                order_id=data.get('order_id'),
                metadata=data
            )
            
            self._event_system.emit(event_type, event)
            
        except Exception as e:
            self.logger.error(f"Error emitting layout event: {e}")
    
    def update_simulation_step(self, step_data: Dict[str, Any]) -> None:
        """
        Update layout system for simulation step.
        
        Args:
            step_data: Simulation step data
        """
        try:
            # Update robot positions
            robot_positions = step_data.get('robot_positions', {})
            for robot_id, position in robot_positions.items():
                self.grid_visualizer.set_robot_position(robot_id, position)
            
            # Update grid state if needed
            grid_updates = step_data.get('grid_updates', [])
            for update in grid_updates:
                coord = update.get('coordinate')
                state = update.get('state')
                if coord and state:
                    grid_state = GridState(state)
                    self.warehouse_layout.set_grid_state(coord, grid_state)
            
            # Emit step event
            self._emit_layout_event("simulation_step", step_data)
            
        except Exception as e:
            self.logger.error(f"Error updating simulation step: {e}")
    
    def get_layout_state(self) -> Dict[str, Any]:
        """
        Get current layout state for persistence.
        
        Returns:
            Dictionary containing layout state
        """
        return {
            'warehouse_layout': self.warehouse_layout.get_grid_snapshot(),
            'distance_tracker': self.distance_tracker.export_data(),
            'grid_visualizer': self.grid_visualizer.export_grid_state(),
            'packout_manager': {
                'packout_location': self.packout_manager.packout_location.to_dict(),
                'restricted_zones': [
                    coord.to_dict() for coord in self.packout_manager.restricted_zones
                ]
            }
        }
    
    def load_layout_state(self, state: Dict[str, Any]) -> bool:
        """
        Load layout state from persistence.
        
        Args:
            state: Layout state dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load warehouse layout
            if 'warehouse_layout' in state:
                self.warehouse_layout.load_grid_snapshot(state['warehouse_layout'])
            
            # Load distance tracker
            if 'distance_tracker' in state:
                self.distance_tracker.import_data(state['distance_tracker'])
            
            # Load grid visualizer
            if 'grid_visualizer' in state:
                self.grid_visualizer.import_grid_state(state['grid_visualizer'])
            
            # Load packout manager
            if 'packout_manager' in state:
                packout_data = state['packout_manager']
                # Note: PackoutZoneManager doesn't have import method, so we skip this
            
            self.logger.info("Layout state loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading layout state: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """
        Save current configuration to ConfigurationManager.
        
        Returns:
            True if successful, False otherwise
        """
        if self._config_manager is None:
            return False
        
        try:
            config = {
                'grid_dimensions': self.warehouse_layout.get_grid_dimensions(),
                'packout_location': self.packout_manager.packout_location.to_dict(),
                'visualization_settings': {
                    'show_coordinates': self.grid_visualizer.show_coordinates,
                    'show_legend': self.grid_visualizer.show_legend,
                    'compact_mode': self.grid_visualizer.compact_mode
                },
                'grid_state': self.warehouse_layout.get_grid_snapshot()
            }
            
            self._config_manager.set_section(self.config_section, config)
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def validate_grid_integrity(self) -> Dict[str, Any]:
        """
        Validate grid integrity and return results.
        
        Returns:
            Dictionary containing validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            # Check grid dimensions
            dimensions = self.warehouse_layout.get_grid_dimensions()
            if dimensions != (25, 20):
                results['errors'].append(f"Invalid grid dimensions: {dimensions}")
                results['valid'] = False
            
            # Check packout location
            packout = self.packout_manager.packout_location
            if packout != Coordinate(1, 1):
                results['errors'].append(f"Invalid packout location: {packout}")
                results['valid'] = False
            
            # Check grid statistics
            stats = self.warehouse_layout.get_grid_statistics()
            results['statistics'] = stats
            
            # Check for occupied packout location
            if self.warehouse_layout.is_position_occupied(packout):
                results['warnings'].append("Packout location is marked as occupied")
            
            # Check distance tracker integrity
            if self.distance_tracker.total_distance < 0:
                results['errors'].append("Negative total distance detected")
                results['valid'] = False
            
        except Exception as e:
            results['errors'].append(f"Validation error: {e}")
            results['valid'] = False
        
        return results
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get integration status and health information.
        
        Returns:
            Dictionary containing integration status
        """
        return {
            'initialized': self._initialized,
            'simulation_engine_connected': self._simulation_engine is not None,
            'event_system_connected': self._event_system is not None,
            'config_manager_connected': self._config_manager is not None,
            'warehouse_layout_ready': self.warehouse_layout is not None,
            'distance_tracker_ready': self.distance_tracker is not None,
            'grid_visualizer_ready': self.grid_visualizer is not None,
            'packout_manager_ready': self.packout_manager is not None,
            'validation_results': self.validate_grid_integrity()
        }
    
    def create_extension_points(self) -> Dict[str, Any]:
        """
        Create extension points for future phases.
        
        Returns:
            Dictionary containing extension points
        """
        return {
            'warehouse_layout': self.warehouse_layout,
            'snake_pattern': self.snake_pattern,
            'packout_manager': self.packout_manager,
            'distance_tracker': self.distance_tracker,
            'grid_visualizer': self.grid_visualizer,
            'integration_manager': self,
            'event_handlers': {
                'robot_move': self._handle_robot_move,
                'order_start': self._handle_order_start,
                'order_complete': self._handle_order_complete,
                'item_pickup': self._handle_item_pickup,
                'item_delivery': self._handle_item_delivery
            }
        } 