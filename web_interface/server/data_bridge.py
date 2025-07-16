#!/usr/bin/env python3
"""
Data Bridge for Roibot Warehouse Visualization Interface
Connects web interface with existing simulation engine components
"""

import json
import time
import threading
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataBridge:
    """Bridge between web interface and simulation engine"""
    
    def __init__(self):
        self.simulation_engine = None
        self.order_manager = None
        self.inventory_manager = None
        self.analytics_engine = None
        self.config_manager = None
        self.robot_system = None
        
        # Data caches
        self.last_robot_data = {}
        self.last_order_data = {}
        self.last_kpi_data = {}
        self.last_simulation_state = {}
        self.last_inventory_data = {}
        self.last_warehouse_data = {} # Added for caching warehouse data
        
        # Update callbacks
        self.update_callbacks = {}
        self.is_running = False
        self.update_interval = 0.1  # 100ms (10 FPS)
        
        # Event system integration
        self.event_system = None
        self.event_subscriptions = {}
        
        # SocketIO integration
        self.socketio = None
        
        # Initialize components
        self.initialize_components()
        
        # Start the simulation engine after initialization
        self.start_simulation_engine()
    
    def start_simulation_engine(self):
        """Start the simulation engine to generate data"""
        try:
            if self.simulation_engine:
                print("🚀 [DEBUG] Starting simulation engine...")
                # Start the simulation engine
                if hasattr(self.simulation_engine, 'start'):
                    print("🚀 [DEBUG] Simulation engine has start method, calling it...")
                    # Run in a separate thread to avoid blocking
                    import threading
                    def start_and_run_engine():
                        try:
                            print("🚀 [DEBUG] Starting engine in background thread...")
                            # First start the engine
                            asyncio.run(self.simulation_engine.start())
                            print("✅ [DEBUG] Engine start completed")
                            
                            # Then run the main loop
                            print("🔄 [DEBUG] Starting main simulation loop...")
                            asyncio.run(self.simulation_engine.run())
                            print("✅ [DEBUG] Main simulation loop completed")
                        except Exception as e:
                            print(f"❌ [DEBUG] Error in simulation engine: {e}")
                    
                    engine_thread = threading.Thread(target=start_and_run_engine, daemon=True)
                    engine_thread.start()
                    print("✅ [DEBUG] Simulation engine started in background thread")
                else:
                    print("🚀 [DEBUG] Simulation engine has no start method, setting is_running=True")
                    self.simulation_engine.is_running = True
                    print("✅ [DEBUG] Simulation engine marked as running")
            else:
                print("❌ [DEBUG] No simulation engine to start")
        except Exception as e:
            print(f"❌ [DEBUG] Error in start_simulation_engine: {e}")
            logger.error(f"Error starting simulation engine: {e}")
    
    def initialize_components(self):
        """Initialize simulation components with real integration"""
        try:
            print("🔧 Starting component initialization...")
            
            # Import simulation components
            print("📦 Importing simulation components...")
            from core.engine import SimulationEngine
            from core.events import EventSystem, EventType
            from core.main_config import get_config
            from entities.order_generator import OrderGenerator
            from entities.order_queue_manager import OrderQueueManager
            from entities.robot_order_assigner import RobotOrderAssigner
            from entities.order_status_tracker import OrderStatusTracker
            from entities.order_analytics import OrderAnalytics
            from entities.robot import Robot
            from entities.robot_movement import RobotMovement
            from entities.robot_navigation import RobotNavigation
            from entities.robot_collection import RobotCollection
            from entities.robot_orders import RobotOrders
            from entities.robot_events import RobotEvents
            from core.inventory.inventory_manager import InventoryManager
            from core.inventory.inventory_sync import InventorySyncManager
            from core.analytics.analytics_engine import AnalyticsEngine
            from core.analytics.order_analytics import OrderAnalytics as CoreOrderAnalytics
            from core.analytics.robot_analytics import RobotAnalytics
            from core.analytics.system_performance import SystemPerformanceMonitor
            print("✅ All imports successful")
            
            # Initialize configuration
            print("⚙️  Initializing configuration...")
            self.config_manager = get_config()
            print("✅ Configuration initialized")
            
            # Initialize event system
            print("🔌 Initializing event system...")
            self.event_system = EventSystem()
            print("✅ Event system initialized")
            
            # Initialize simulation engine
            print("🚀 Initializing simulation engine...")
            self.simulation_engine = SimulationEngine()
            
            # Connect event system to simulation engine
            if hasattr(self.simulation_engine, 'event_system'):
                # Replace the engine's event system with our data bridge event system
                # so all events go through the same system
                self.simulation_engine.event_system = self.event_system
                print("✅ Event system connected to simulation engine")
            else:
                print("⚠️  Simulation engine does not have event_system attribute")
            
            print("✅ Simulation engine initialized")
            
            # Initialize warehouse layout first (needed by other components)
            print("🏗️  Initializing warehouse layout...")
            from core.layout.warehouse_layout import WarehouseLayoutManager
            self.warehouse_layout = WarehouseLayoutManager()
            print("✅ Warehouse layout initialized")
            
            # Initialize order management system
            print("📋 Initializing order management system...")
            self.order_generator = OrderGenerator(self.warehouse_layout)
            print("✅ Order generator initialized")
            self.order_queue_manager = OrderQueueManager()
            print("✅ Order queue manager initialized")
            self.robot_order_assigner = RobotOrderAssigner()
            print("✅ Robot order assigner initialized")
            self.order_status_tracker = OrderStatusTracker(self.robot_order_assigner, self.order_queue_manager)
            print("✅ Order status tracker initialized")
            self.order_analytics = OrderAnalytics(self.order_status_tracker, self.robot_order_assigner, self.order_queue_manager)
            print("✅ Order analytics initialized")
            
            # Initialize robot system with proper configuration
            print("🤖 Initializing robot system...")
            robot_config = {
                'movement': {
                    'movement_speed': 2.0  # seconds per aisle
                },
                'collection': {
                    'collection_time': 5.0  # seconds per item
                }
            }
            print(f"🔧 Initializing robot with config: {robot_config}")
            self.robot = Robot(robot_config)
            print("✅ Robot initialized")
            # Robot components are already initialized as part of the Robot class
            # We don't need to create separate instances
            print("✅ Robot components initialized (movement, navigation, collection, orders, events)")
            
            # Initialize inventory system
            print("📦 Initializing inventory system...")
            self.inventory_manager = InventoryManager()
            print("✅ Inventory manager initialized")
            self.inventory_sync = InventorySyncManager(self.inventory_manager)
            print("✅ Inventory sync initialized")
            
            # Initialize analytics system
            print("📊 Initializing analytics system...")
            self.analytics_engine = AnalyticsEngine()
            self.analytics_engine.set_event_system(self.event_system)
            print("✅ Analytics engine initialized")
            self.core_order_analytics = CoreOrderAnalytics(self.analytics_engine)
            print("✅ Core order analytics initialized")
            self.robot_analytics = RobotAnalytics(self.analytics_engine)
            print("✅ Robot analytics initialized")
            self.system_performance = SystemPerformanceMonitor(self.analytics_engine)
            print("✅ System performance monitor initialized")
            
            # Set up event subscriptions
            print("🔗 Setting up event subscriptions...")
            self.setup_event_subscriptions()
            print("✅ Event subscriptions set up")
            
            print("🎉 All simulation components initialized successfully!")
            logger.info("✅ Real simulation components initialized successfully")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            logger.warning(f"⚠️  Could not import simulation components: {e}")
            logger.info("Running in mock mode with simulated data")
            self.create_mock_components()
        except Exception as e:
            print(f"❌ Unexpected error during initialization: {e}")
            logger.error(f"❌ Error initializing components: {e}")
            self.create_mock_components()
    
    def setup_event_subscriptions(self):
        """Set up event subscriptions for real-time updates"""
        try:
            # Subscribe to robot events
            self.event_system.subscribe("robot_position_update", self.handle_robot_position_update)
            self.event_system.subscribe("robot_state_change", self.handle_robot_state_change)
            self.event_system.subscribe("robot_movement_progress", self.handle_robot_movement_progress)
            
            # Subscribe to order events
            self.event_system.subscribe("order_created", self.handle_order_created)
            self.event_system.subscribe("order_assigned", self.handle_order_assigned)
            self.event_system.subscribe("order_completed", self.handle_order_completed)
            self.event_system.subscribe("order_status_change", self.handle_order_status_change)
            
            # Subscribe to inventory events
            self.event_system.subscribe("inventory_update", self.handle_inventory_update)
            self.event_system.subscribe("item_collected", self.handle_item_collected)
            
            # Subscribe to analytics events
            self.event_system.subscribe("kpi_update", self.handle_kpi_update)
            self.event_system.subscribe("performance_metric", self.handle_performance_metric)
            
            # Subscribe to simulation events
            self.event_system.subscribe("simulation_start", self.handle_simulation_start)
            self.event_system.subscribe("simulation_pause", self.handle_simulation_pause)
            self.event_system.subscribe("simulation_resume", self.handle_simulation_resume)
            self.event_system.subscribe("simulation_stop", self.handle_simulation_stop)
            
            logger.info("✅ Event subscriptions set up successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to set up event subscriptions: {e}")
    
    def handle_robot_position_update(self, event_data):
        """Handle robot position update events"""
        try:
            # Handle None event_data
            if event_data is None:
                event_data = {}
            
            robot_id = event_data.get('robot_id', 'ROBOT_001')
            new_position = event_data.get('position', 'A1')
            new_state = event_data.get('state', 'IDLE')
            
            # Convert position to string format if it's a Coordinate object
            if hasattr(new_position, 'aisle') and hasattr(new_position, 'rack'):
                # Convert Coordinate or SmoothCoordinate object to string format (A1, B2, etc.)
                # Backend uses 1-based coordinates, frontend expects 0-based
                column = chr(65 + (int(new_position.aisle) - 1))  # Convert 1-based to 0-based for column
                row = int(new_position.rack)  # Keep 1-based for row display
                position_str = f"{column}{row}"
            else:
                # Handle other position formats
                position_str = str(new_position) if new_position else 'A1'
            
            # Update the actual robot if it exists
            if hasattr(self, 'robot') and self.robot:
                if hasattr(self.robot, 'position'):
                    self.robot.position = new_position  # Keep original format for backend
                if hasattr(self.robot, 'state'):
                    self.robot.state = new_state
                if hasattr(self.robot, 'current_direction'):
                    self.robot.current_direction = event_data.get('direction', 'FORWARD')
                if hasattr(self.robot, 'collected_items'):
                    self.robot.collected_items = event_data.get('items_held', [])
                if hasattr(self.robot, 'target_item'):
                    self.robot.target_item = event_data.get('target_items', [])
                if hasattr(self.robot, 'current_path'):
                    self.robot.current_path = event_data.get('path', [])
            
            robot_data = {
                'id': robot_id,
                'position': position_str,  # Send string format to frontend
                'state': new_state,
                'current_order': event_data.get('current_order', None),
                'path': event_data.get('path', []),
                'direction': event_data.get('direction', 'FORWARD'),
                'items_held': event_data.get('items_held', []),
                'target_items': event_data.get('target_items', [])
            }
            
            self.last_robot_data[robot_id] = robot_data
            
            # Trigger update callback
            if 'robot_data' in self.update_callbacks:
                self.update_callbacks['robot_data'](robot_data)
                
        except Exception as e:
            logger.error(f"❌ Error handling robot position update: {e}")
    
    def handle_robot_state_change(self, event_data):
        """Handle robot state change events"""
        try:
            robot_id = event_data.get('robot_id', 'ROBOT_001')
            new_state = event_data.get('new_state', 'IDLE')
            old_state = event_data.get('old_state', 'IDLE')
            
            if robot_id in self.last_robot_data:
                self.last_robot_data[robot_id]['state'] = new_state
                
                # Trigger update callback
                if 'robot_data' in self.update_callbacks:
                    self.update_callbacks['robot_data'](self.last_robot_data[robot_id])
                    
        except Exception as e:
            logger.error(f"❌ Error handling robot state change: {e}")
    
    def handle_robot_movement_progress(self, event_data):
        """Handle robot movement progress events"""
        try:
            robot_id = event_data.get('robot_id', 'ROBOT_001')
            progress = event_data.get('progress', 0.0)
            current_position = event_data.get('current_position', 'A1')
            target_position = event_data.get('target_position', 'A1')
            
            if robot_id in self.last_robot_data:
                self.last_robot_data[robot_id]['movement_progress'] = progress
                self.last_robot_data[robot_id]['current_position'] = current_position
                self.last_robot_data[robot_id]['target_position'] = target_position
                
                # Trigger update callback
                if 'robot_data' in self.update_callbacks:
                    self.update_callbacks['robot_data'](self.last_robot_data[robot_id])
                    
        except Exception as e:
            logger.error(f"❌ Error handling robot movement progress: {e}")
    
    def handle_order_created(self, event_data):
        """Handle order creation events"""
        try:
            # Handle None event_data
            if event_data is None:
                event_data = {}
            
            order_data = {
                'id': event_data.get('order_id', ''),
                'items': event_data.get('items', []),
                'status': 'PENDING',
                'timestamp': event_data.get('timestamp', time.time()),
                'assigned_robot': None
            }
            
            # Update order data cache
            if 'orders' not in self.last_order_data:
                self.last_order_data['orders'] = []
            self.last_order_data['orders'].append(order_data)
            
            # Trigger update callback
            if 'order_data' in self.update_callbacks:
                self.update_callbacks['order_data'](self.get_order_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling order created: {e}")
    
    def handle_order_assigned(self, event_data):
        """Handle order assignment events"""
        try:
            order_id = event_data.get('order_id', '')
            robot_id = event_data.get('robot_id', 'ROBOT_001')
            
            # Update order status
            if 'orders' in self.last_order_data:
                for order in self.last_order_data['orders']:
                    if order['id'] == order_id:
                        order['status'] = 'IN_PROGRESS'
                        order['assigned_robot'] = robot_id
                        break
            
            # Trigger update callback
            if 'order_data' in self.update_callbacks:
                self.update_callbacks['order_data'](self.get_order_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling order assigned: {e}")
    
    def handle_order_completed(self, event_data):
        """Handle order completion events"""
        try:
            order_id = event_data.get('order_id', '')
            completion_time = event_data.get('completion_time', time.time())
            total_distance = event_data.get('total_distance', 0.0)
            efficiency_score = event_data.get('efficiency_score', 0.0)
            
            # Move order to completed list
            if 'orders' in self.last_order_data:
                for i, order in enumerate(self.last_order_data['orders']):
                    if order['id'] == order_id:
                        completed_order = order.copy()
                        completed_order['status'] = 'COMPLETED'
                        completed_order['completion_time'] = completion_time
                        completed_order['total_distance'] = total_distance
                        completed_order['efficiency_score'] = efficiency_score
                        completed_order['completed_timestamp'] = event_data.get('timestamp', time.time())

                        # Remove from active orders
                        self.last_order_data['orders'].pop(i)
                        
                        # Add to completed orders
                        if 'completed_orders' not in self.last_order_data:
                            self.last_order_data['completed_orders'] = []
                        self.last_order_data['completed_orders'].append(completed_order)
                        break
            
            # Trigger update callback
            if 'order_data' in self.update_callbacks:
                self.update_callbacks['order_data'](self.get_order_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling order completed: {e}")
    
    def handle_order_status_change(self, event_data):
        """Handle order status change events"""
        try:
            order_id = event_data.get('order_id', '')
            new_status = event_data.get('new_status', 'PENDING')
            
            # Update order status
            if 'orders' in self.last_order_data:
                for order in self.last_order_data['orders']:
                    if order['id'] == order_id:
                        order['status'] = new_status
                        break
            
            # Trigger update callback
            if 'order_data' in self.update_callbacks:
                self.update_callbacks['order_data'](self.get_order_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling order status change: {e}")
    
    def handle_inventory_update(self, event_data):
        """Handle inventory update events"""
        try:
            item_id = event_data.get('item_id', '')
            location = event_data.get('location', 'A1')
            quantity = event_data.get('quantity', 0)
            
            # Update inventory cache
            if 'inventory' not in self.last_inventory_data:
                self.last_inventory_data['inventory'] = {}
            
            self.last_inventory_data['inventory'][item_id] = {
                'item_id': item_id,
                'location': location,
                'quantity': quantity
            }
            
            # Trigger update callback
            if 'inventory_data' in self.update_callbacks:
                self.update_callbacks['inventory_data'](self.get_inventory_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling inventory update: {e}")
    
    def handle_item_collected(self, event_data):
        """Handle item collection events"""
        try:
            item_id = event_data.get('item_id', '')
            robot_id = event_data.get('robot_id', 'ROBOT_001')
            order_id = event_data.get('order_id', '')
            
            # Update robot data
            if robot_id in self.last_robot_data:
                if 'items_held' not in self.last_robot_data[robot_id]:
                    self.last_robot_data[robot_id]['items_held'] = []
                self.last_robot_data[robot_id]['items_held'].append(item_id)
            
            # Trigger update callbacks
            if 'robot_data' in self.update_callbacks:
                self.update_callbacks['robot_data'](self.last_robot_data.get(robot_id, {}))
            if 'inventory_data' in self.update_callbacks:
                self.update_callbacks['inventory_data'](self.get_inventory_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling item collected: {e}")
    
    def handle_kpi_update(self, event_data):
        """Handle KPI update events"""
        try:
            # Handle None event_data
            if event_data is None:
                event_data = {}
            
            kpi_type = event_data.get('kpi_type', '')
            value = event_data.get('value', 0.0)
            timestamp = event_data.get('timestamp', time.time())
            
            print(f"�� KPI Update - Type: {kpi_type}, Value: {value}, Timestamp: {timestamp}")
            print(f"🔧 Current last_kpi_data keys: {list(self.last_kpi_data.keys()) if hasattr(self, 'last_kpi_data') else 'No last_kpi_data'}")
            
            # Initialize last_kpi_data if it doesn't exist
            if not hasattr(self, 'last_kpi_data'):
                self.last_kpi_data = {}
            
            # Update KPI cache
            if kpi_type not in self.last_kpi_data:
                self.last_kpi_data[kpi_type] = []
            
            self.last_kpi_data[kpi_type].append({
                'value': value,
                'timestamp': timestamp
            })
            
            print(f"🔧 Updated last_kpi_data[{kpi_type}]: {self.last_kpi_data[kpi_type]}")
            
            # Keep only last 100 values for each KPI
            if len(self.last_kpi_data[kpi_type]) > 100:
                self.last_kpi_data[kpi_type] = self.last_kpi_data[kpi_type][-100:]
            
            # Trigger update callback
            if 'kpi_data' in self.update_callbacks:
                self.update_callbacks['kpi_data'](self.get_kpi_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling KPI update: {e}")
            print(f"❌ Exception in handle_kpi_update: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_performance_metric(self, event_data):
        """Handle performance metric events"""
        try:
            metric_type = event_data.get('metric_type', '')
            value = event_data.get('value', 0.0)
            timestamp = event_data.get('timestamp', time.time())
            
            # Update performance cache
            if 'performance' not in self.last_kpi_data:
                self.last_kpi_data['performance'] = {}
            
            if metric_type not in self.last_kpi_data['performance']:
                self.last_kpi_data['performance'][metric_type] = []
            
            self.last_kpi_data['performance'][metric_type].append({
                'value': value,
                'timestamp': timestamp
            })
            
            # Keep only last 50 values for each metric
            if len(self.last_kpi_data['performance'][metric_type]) > 50:
                self.last_kpi_data['performance'][metric_type] = self.last_kpi_data['performance'][metric_type][-50:]
            
            # Trigger update callback
            if 'kpi_data' in self.update_callbacks:
                self.update_callbacks['kpi_data'](self.get_kpi_data())
                
        except Exception as e:
            logger.error(f"❌ Error handling performance metric: {e}")
    
    def handle_simulation_start(self, event_data):
        """Handle simulation start events"""
        try:
            self.last_simulation_state['status'] = 'running'
            self.last_simulation_state['start_time'] = event_data.get('timestamp', time.time())
            
            # Trigger update callback
            if 'simulation_state' in self.update_callbacks:
                self.update_callbacks['simulation_state'](self.get_simulation_state())
                
        except Exception as e:
            logger.error(f"❌ Error handling simulation start: {e}")
    
    def handle_simulation_pause(self, event_data):
        """Handle simulation pause events"""
        try:
            self.last_simulation_state['status'] = 'paused'
            self.last_simulation_state['pause_time'] = event_data.get('timestamp', time.time())
            
            # Trigger update callback
            if 'simulation_state' in self.update_callbacks:
                self.update_callbacks['simulation_state'](self.get_simulation_state())
                
        except Exception as e:
            logger.error(f"❌ Error handling simulation pause: {e}")
    
    def handle_simulation_resume(self, event_data):
        """Handle simulation resume events"""
        try:
            self.last_simulation_state['status'] = 'running'
            self.last_simulation_state['resume_time'] = event_data.get('timestamp', time.time())
            
            # Trigger update callback
            if 'simulation_state' in self.update_callbacks:
                self.update_callbacks['simulation_state'](self.get_simulation_state())
                
        except Exception as e:
            logger.error(f"❌ Error handling simulation resume: {e}")
    
    def handle_simulation_stop(self, event_data):
        """Handle simulation stop events"""
        try:
            self.last_simulation_state['status'] = 'stopped'
            self.last_simulation_state['stop_time'] = event_data.get('timestamp', time.time())
            
            # Trigger update callback
            if 'simulation_state' in self.update_callbacks:
                self.update_callbacks['simulation_state'](self.get_simulation_state())
                
        except Exception as e:
            logger.error(f"❌ Error handling simulation stop: {e}")
    
    def create_mock_components(self):
        """Create mock components for testing"""
        class MockSimulationEngine:
            def __init__(self):
                self.is_running = True
                self.simulation_time = 0
                self.simulation_speed = 1.0
                self.robots = {
                    'robot_1': MockRobot('robot_1', 'A1', 'IDLE'),
                    'robot_2': MockRobot('robot_2', 'B5', 'MOVING')
                }
        
        class MockRobot:
            def __init__(self, robot_id, position, state):
                self.robot_id = robot_id
                self.position = position
                self.state = state
                self.current_order = None
                self.current_path = []
                self.current_direction = 'FORWARD'
                self.collected_items = []
                self.target_item = []
                self.movement_progress = 0.0
                self.total_distance = 0.0
        
        class MockOrderManager:
            def __init__(self):
                self.pending_orders = [
                    {'id': 'order_1', 'items': ['item_A1', 'item_B3'], 'status': 'PENDING'},
                    {'id': 'order_2', 'items': ['item_C7', 'item_D2'], 'status': 'PENDING'}
                ]
                self.in_progress_orders = [
                    {'id': 'order_3', 'items': ['item_E5'], 'status': 'IN_PROGRESS'}
                ]
                self.completed_orders = [
                    {'id': 'order_4', 'items': ['item_F8'], 'status': 'COMPLETED'}
                ]
        
        class MockAnalyticsDashboard:
            def __init__(self):
                self.orders_per_hour = 12.5
                self.completion_rate = 95.2
                self.average_completion_time = 180.5
                self.utilization_rate = 78.3
                self.efficiency_score = 85.0
                self.health_score = 100.0
                self.memory_usage = 45.2
                self.cpu_usage = 32.1
                # Add missing attributes that might be accessed
                self.robot_efficiency = 85.0
                self.order_completion_rate = 95.2
                self.average_order_time = 180.5
        
        self.simulation_engine = MockSimulationEngine()
        self.order_queue_manager = MockOrderManager()
        self.inventory_manager = MockOrderManager()  # Using same mock for inventory
        self.analytics_engine = MockAnalyticsDashboard()
        self.robot = MockRobot('ROBOT_001', 'A1', 'IDLE')  # Add robot attribute
        
        # Add missing analytics components for mock mode
        self.core_order_analytics = MockAnalyticsDashboard()
        self.robot_analytics = MockAnalyticsDashboard()
        self.system_performance = MockAnalyticsDashboard()
        
        logger.info("✅ Mock components created for testing")
    
    def register_socketio(self, socketio):
        """Register SocketIO instance for real-time updates"""
        self.socketio = socketio
        logger.info("SocketIO registered with data bridge")
    
    def send_simulation_data(self, engine):
        """Send simulation data to web interface via SocketIO"""
        try:
            if not hasattr(self, 'socketio') or self.socketio is None:
                return
            
            # Get current simulation data
            robot_data = {
                'id': 'robot-1',
                'position': {
                    'aisle': engine.robot.position.aisle,
                    'rack': engine.robot.position.rack
                },
                'state': engine.robot.state.value,
                'collected_items': engine.robot.collected_items,
                'total_distance': engine.robot.total_distance
            }
            
            order_data = {
                'orders': engine.orders,
                'current_order_index': engine.current_order_index,
                'total_orders': engine.state.total_orders if hasattr(engine.state, 'total_orders') else len(engine.orders)
            }
            
            kpi_data = {
                'simulation_time': engine.simulation_time,
                'orders_completed': engine.performance_metrics.get('orders_completed', 0),
                'items_collected': engine.performance_metrics.get('items_collected', 0),
                'total_distance': engine.performance_metrics.get('total_distance', 0.0),
                'current_fps': engine.state.current_fps if hasattr(engine.state, 'current_fps') else 60
            }
            
            # Send data via SocketIO
            self.socketio.emit('robot_update', robot_data)
            self.socketio.emit('order_update', order_data)
            self.socketio.emit('kpi_update', kpi_data)
            
        except Exception as e:
            logger.error(f"Error sending simulation data: {e}")
    
    def register_update_callback(self, data_type: str, callback: Callable):
        """Register an update callback"""
        self.update_callbacks[data_type] = callback
        logger.info(f"Registered update callback for: {data_type}")
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        if not self.simulation_engine:
            return {
                'status': 'disconnected',
                'time': 0,
                'speed': 1.0,
                'error': 'Simulation engine not connected'
            }
        
        try:
            is_running = getattr(self.simulation_engine, 'is_running', False)
            simulation_time = getattr(self.simulation_engine, 'simulation_time', 0)
            simulation_speed = getattr(self.simulation_engine, 'simulation_speed', 1.0)
            
            # Calculate total orders with multiple fallback methods
            total_orders = 0
            if self.analytics_engine and hasattr(self.analytics_engine, 'get_total_orders_created'):
                try:
                    total_orders = self.analytics_engine.get_total_orders_created()
                    print(f"🔍 [DEBUG] Analytics engine total orders: {total_orders}")
                except Exception as e:
                    print(f"❌ [DEBUG] Error getting total orders from analytics: {e}")
            
            # Fallback to direct order count from simulation engine
            if total_orders == 0 and self.simulation_engine:
                orders = getattr(self.simulation_engine, 'orders', [])
                total_orders = len(orders)
                print(f"🔍 [DEBUG] Fallback - Direct order count from engine: {total_orders}")
            
            print(f"🔍 [DEBUG] Final total_orders value: {total_orders}")

            # Add debug info
            debug_info = {
                'engine_type': type(self.simulation_engine).__name__,
                'has_start_method': hasattr(self.simulation_engine, 'start'),
                'has_update_method': hasattr(self.simulation_engine, 'update'),
                'has_main_loop': hasattr(self.simulation_engine, '_main_loop'),
                'robot_count': len(getattr(self.simulation_engine, 'robots', {})),
                'order_count': len(getattr(self.simulation_engine, 'orders', []))
            }
            
            state = {
                'status': 'running' if is_running else 'paused',
                'time': simulation_time,
                'speed': simulation_speed,
                'total_orders': total_orders,
                'error': None,
                'debug': debug_info
            }
            
            # Update cache
            self.last_simulation_state = state
            return state
            
        except Exception as e:
            return {
                'status': 'error',
                'time': 0,
                'speed': 1.0,
                'error': str(e)
            }
    
    def get_robot_data(self) -> List[Dict[str, Any]]:
        """Get robot data"""
        if not self.simulation_engine:
            print("🔍 [DEBUG] No simulation engine, returning empty robot data")
            return []
        
        try:
            print("🔍 [DEBUG] Getting robot data from single robot")
            robot = getattr(self.simulation_engine, 'robot', None)
            if not robot:
                print("❌ [DEBUG] No robot found in simulation engine")
                return []
            
            # Get robot position - handle both SmoothCoordinate and tuple formats
            if hasattr(robot, 'position') and robot.position:
                if hasattr(robot.position, 'aisle') and hasattr(robot.position, 'rack'):
                    # SmoothCoordinate format
                    aisle = int(robot.position.aisle)
                    rack = int(robot.position.rack)
                elif isinstance(robot.position, (tuple, list)) and len(robot.position) >= 2:
                    # Tuple format
                    aisle = int(robot.position[0])
                    rack = int(robot.position[1])
                else:
                    aisle, rack = 1, 1
                    
                # Convert to grid position (A1, B2, etc.)
                column = chr(ord('A') + aisle - 1)  # A=1, B=2, etc.
                grid_position = f"{column}{rack}"
            else:
                aisle, rack = 1, 1
                grid_position = "A1"
            
            print(f"🔍 [DEBUG] Robot found: position=({aisle:.2f}, {rack:.2f}), state={robot.state}")
            
            # Get robot state as string
            state_str = str(robot.state).replace('RobotState.', '') if hasattr(robot, 'state') else 'IDLE'
            
            # Get robot order information
            current_order = getattr(robot, 'current_order', None)
            target_items = getattr(robot, 'target_items', [])
            collected_items = getattr(robot, 'collected_items', [])
            
            # Calculate items held (same as collected_items)
            items_held = collected_items.copy() if collected_items else []
            
            robot_data = {
                'id': 'ROBOT_001',
                'position': grid_position,
                'state': state_str,
                'current_order': current_order,
                'path': [],  # Path not needed for frontend display
                'direction': getattr(robot, 'direction', 'forward'),
                'items_held': items_held,
                'target_items': target_items,
                'movement_progress': getattr(robot, 'movement_progress', 0.0),
                'total_distance': getattr(robot, 'total_distance', 0.0),
                'battery_level': 100,  # Assume full battery
                'efficiency': 85  # Sample efficiency
            }
            
            print(f"🔍 [DEBUG] Robot data: {robot_data}")
            
            # Update cache
            self.last_robot_data = [robot_data]
            
            print(f"🔍 [DEBUG] Returning 1 robots")
            return [robot_data]
            
        except Exception as e:
            print(f"❌ [DEBUG] Error getting robot data: {e}")
            logger.error(f"Error getting robot data: {e}")
            return []
    
    def _convert_robot_state_to_string(self, state) -> str:
        """Convert robot state to string"""
        if hasattr(state, 'name'):
            # Handle RobotState enum
            return state.name
        elif isinstance(state, str):
            # Already a string
            return state
        elif isinstance(state, int):
            # Handle numeric state
            state_map = {
                1: 'IDLE',
                2: 'MOVING',
                3: 'PICKING',
                4: 'COLLECTING',
                5: 'RETURNING',
                6: 'ERROR'
            }
            return state_map.get(state, 'IDLE')
        else:
            return 'IDLE'
    
    def get_order_data(self) -> Dict[str, Any]:
        """Get order data"""
        if not self.simulation_engine:
            print("🔍 [DEBUG] No simulation engine, returning empty order data")
            return {
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'total': 0,
                'orders': [],
                'completed_orders': []
            }
        
        try:
            # Get orders from simulation engine
            orders = getattr(self.simulation_engine, 'orders', [])
            print(f"🔍 [DEBUG] Found {len(orders)} orders in simulation engine")
            
            # Convert orders to frontend format
            def order_to_dict(order):
                # Determine order status based on robot's current order
                order_id = order.get('id', 'unknown')
                robot = getattr(self.simulation_engine, 'robot', None)
                current_order_index = getattr(self.simulation_engine, 'current_order_index', 0)
                
                # Get the order index from the order ID or use position in list
                try:
                    order_index = orders.index(order)
                except ValueError:
                    order_index = -1
                
                # Determine status based on processing state
                if robot and hasattr(robot, 'current_order') and robot.current_order == order_id:
                    status = 'in_progress'
                elif order_index < current_order_index:
                    status = 'completed'
                else:
                    status = 'pending'
                
                return {
                    'id': order_id,
                    'items': order.get('items', []),
                    'status': status,
                    'timestamp': order.get('timestamp', 0),
                    'completed_timestamp': order.get('completed_timestamp') or order.get('completed_time'),
                    'location': order.get('location', 'A1'),
                    'priority': order.get('priority', 1)
                }
            
            # Convert orders to frontend format first
            formatted_orders = [order_to_dict(o) for o in orders]
            
            # Count orders by status from formatted orders
            pending_orders = [o for o in formatted_orders if o['status'] == 'pending']
            in_progress_orders = [o for o in formatted_orders if o['status'] == 'in_progress']
            completed_orders = [o for o in formatted_orders if o['status'] == 'completed']
            
            pending = len(pending_orders)
            in_progress = len(in_progress_orders)
            completed = len(completed_orders)
            
            order_data = {
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed,
                'total': len(orders),
                'orders': formatted_orders,
                'completed_orders': completed_orders
            }
            
            print(f"🔍 [DEBUG] Order data: pending={pending}, in_progress={in_progress}, completed={completed}, total={len(orders)}")
            print(f"🔍 [DEBUG] Order statuses: {[o['status'] for o in formatted_orders]}")
            print(f"📦 [DEBUG] Order data being sent to frontend: {order_data}")
            
            # Update cache
            self.last_order_data = order_data
            return order_data
            
        except Exception as e:
            print(f"❌ [DEBUG] Error getting order data: {e}")
            logger.error(f"Error getting order data: {e}")
            return {
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'total': 0,
                'orders': [],
                'completed_orders': []
            }
    
    def get_kpi_data(self) -> Dict[str, Any]:
        """Get KPI data for dashboard"""
        try:
            print(f"🔍 get_kpi_data called")
            
            # Start with default values
            kpis = {
                'orders_per_hour': 0.0,
                'robot_utilization': 0.0,
                'order_completion_rate': 0.0,
                'average_order_time': 0.0,
                'queue_length': 0,
                'system_health': 100.0,
                'memory_usage': 0.0,
                'cpu_usage': 0.0,
                'robot_efficiency': 0.0
            }
            
            # Calculate KPIs from simulation engine data
            if self.simulation_engine:
                try:
                    # Get orders data
                    orders = getattr(self.simulation_engine, 'orders', [])
                    robot = getattr(self.simulation_engine, 'robot', None)
                    simulation_time = getattr(self.simulation_engine, 'simulation_time', 0)
                    
                    print(f"🔍 [DEBUG] KPI Calculation - Total orders: {len(orders)}")
                    
                    # Calculate completed orders, total orders, and order status counts
                    completed_orders = [o for o in orders if o.get('status') == 'completed']
                    pending_orders = [o for o in orders if o.get('status') == 'pending']
                    in_progress_orders = [o for o in orders if o.get('status') == 'in_progress']
                    
                    total_orders = len(orders)
                    completed_count = len(completed_orders)
                    pending_count = len(pending_orders)
                    in_progress_count = len(in_progress_orders)
                    
                    print(f"🔍 [DEBUG] KPI Calculation - Completed: {completed_count}, Pending: {pending_count}, In Progress: {in_progress_count}")
                    
                    # Update KPIs with actual calculated values
                    kpis['total_orders'] = total_orders
                    kpis['completed_orders'] = completed_count
                    kpis['pending_orders'] = pending_count
                    kpis['in_progress_orders'] = in_progress_count
                    
                    # Calculate order completion rate
                    if total_orders > 0:
                        kpis['order_completion_rate'] = (completed_count / total_orders) * 100.0
                    else:
                        kpis['order_completion_rate'] = 0.0
                    
                    # Calculate average order time from completed orders
                    if completed_orders:
                        total_time_seconds = 0
                        valid_orders = 0
                        
                        for order in completed_orders:
                            created_time = order.get('created_time', 0)
                            completed_time = order.get('completed_time', 0)
                            
                            if created_time and completed_time and completed_time > created_time:
                                total_time_seconds += (completed_time - created_time)
                                valid_orders += 1
                        
                        if valid_orders > 0:
                            avg_seconds = total_time_seconds / valid_orders
                            kpis['average_order_time'] = avg_seconds
                            print(f"🔍 [DEBUG] Average order time: {avg_seconds:.1f} seconds")
                        else:
                            kpis['average_order_time'] = 0.0
                    else:
                        kpis['average_order_time'] = 0.0
                    
                    # Calculate queue length (pending + in_progress)
                    kpis['queue_length'] = pending_count + in_progress_count
                    
                    # Calculate orders per hour
                    if simulation_time > 0:
                        # Convert simulation time to hours and calculate rate
                        hours = simulation_time / 3600.0
                        if hours > 0:
                            kpis['orders_per_hour'] = completed_count / hours
                        else:
                            kpis['orders_per_hour'] = 0.0
                    else:
                        kpis['orders_per_hour'] = 0.0
                    
                    # Calculate robot utilization
                    if robot:
                        # Robot is utilized if it's not idle
                        robot_state = getattr(robot, 'state', 'IDLE')
                        if hasattr(robot_state, 'value'):
                            state_str = robot_state.value
                        else:
                            state_str = str(robot_state)
                        
                        if state_str.lower() != 'idle':
                            kpis['robot_utilization'] = 85.0  # Active robot utilization
                        else:
                            kpis['robot_utilization'] = 10.0  # Idle robot utilization
                    
                    # Calculate robot efficiency based on items collected
                    if robot:
                        collected_items = getattr(robot, 'collected_items', [])
                        target_items = getattr(robot, 'target_items', [])
                        
                        if target_items:
                            # Efficiency based on collection progress
                            progress = len(collected_items) / len(target_items)
                            kpis['robot_efficiency'] = min(progress * 100, 100.0)
                        else:
                            # Base efficiency when no active order
                            kpis['robot_efficiency'] = 20.0 if collected_items else 0.0
                    
                    print(f"🔍 [DEBUG] Final calculated KPIs: {kpis}")
                    
                except Exception as e:
                    print(f"❌ [DEBUG] Error calculating KPIs from simulation engine: {e}")
                    import traceback
                    traceback.print_exc()
            
            # System metrics (mock values for now)
            kpis['system_health'] = 100.0
            kpis['memory_usage'] = 45.2
            kpis['cpu_usage'] = 32.1
            
            return kpis
            
        except Exception as e:
            logger.error(f"❌ Error getting KPI data: {e}")
            print(f"❌ Exception in get_kpi_data: {e}")
            import traceback
            traceback.print_exc()
            
            # Return basic mock data on error
            return {
                'orders_per_hour': 0.0,
                'robot_utilization': 0.0,
                'order_completion_rate': 0.0,
                'average_order_time': 0.0,
                'queue_length': 0,
                'system_health': 100.0,
                'memory_usage': 0.0,
                'cpu_usage': 0.0,
                'robot_efficiency': 0.0,
                'total_orders': 0,
                'completed_orders': 0,
                'pending_orders': 0,
                'in_progress_orders': 0
            }
    
    def get_warehouse_data(self) -> Dict[str, Any]:
        """Get warehouse layout data"""
        if not self.simulation_engine:
            return {
                'grid_size': {'width': 25, 'height': 20},
                'packout_location': {'aisle': 1, 'rack': 1},
                'aisles': list(range(1, 26)),
                'racks': list(range(1, 21))
            }
        
        try:
            # Get warehouse data from simulation engine
            warehouse_data = {
                'grid_size': {'width': 25, 'height': 20},
                'packout_location': {'aisle': 1, 'rack': 1},  # Convert Coordinate to dict
                'aisles': list(range(1, 26)),
                'racks': list(range(1, 21))
            }
            
            # Update cache
            self.last_warehouse_data = warehouse_data
            return warehouse_data
            
        except Exception as e:
            logger.error(f"Error getting warehouse data: {e}")
            return {
                'grid_size': {'width': 25, 'height': 20},
                'packout_location': {'aisle': 1, 'rack': 1},
                'aisles': list(range(1, 26)),
                'racks': list(range(1, 21))
            }
    
    def get_inventory_data(self) -> Dict[str, Any]:
        """Get inventory data for visualization"""
        try:
            if not self.inventory_manager:
                return {'inventory': {}, 'total_items': 0}
            
            # Get inventory data from real inventory system
            inventory_items = getattr(self.inventory_manager, 'items', {})
            
            # Convert inventory items to dictionary format
            inventory_dict = {}
            for item_id, item in inventory_items.items():
                if hasattr(item, 'to_dict'):
                    inventory_dict[item_id] = item.to_dict()
                elif isinstance(item, dict):
                    inventory_dict[item_id] = item
                else:
                    inventory_dict[item_id] = {
                        'item_id': getattr(item, 'item_id', item_id),
                        'location': getattr(item, 'location', 'A1'),
                        'quantity': getattr(item, 'quantity', 0),
                        'category': getattr(item, 'category', 'unknown')
                    }
            
            return {
                'inventory': inventory_dict,
                'total_items': len(inventory_dict)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting inventory data: {e}")
            return {'inventory': {}, 'total_items': 0}
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute simulation command"""
        if not self.simulation_engine:
            return {'error': 'Simulation engine not connected'}
        
        try:
            if command == 'play':
                # Handle play command based on current simulation state
                print("🎮 Executing play command...")
                
                # Check current simulation state
                is_running = getattr(self.simulation_engine, 'is_running', False)
                is_paused = False
                if hasattr(self.simulation_engine, 'state') and hasattr(self.simulation_engine.state, 'is_paused'):
                    is_paused = self.simulation_engine.state.is_paused()
                
                print(f"🔍 [DEBUG] Current state - is_running: {is_running}, is_paused: {is_paused}")
                
                if is_paused:
                    # Resume from pause
                    print("▶️ Resuming simulation from pause...")
                    if hasattr(self.simulation_engine, 'resume'):
                        # Run async method in a thread
                        import threading
                        def resume_engine():
                            try:
                                asyncio.run(self.simulation_engine.resume())
                                print("✅ [DEBUG] Engine resume completed")
                            except Exception as e:
                                print(f"❌ Error resuming engine: {e}")
                        
                        resume_thread = threading.Thread(target=resume_engine, daemon=True)
                        resume_thread.start()
                        print("✅ Simulation engine resume called")
                    else:
                        self.simulation_engine.is_running = True
                        print("✅ Simulation engine marked as running")
                elif is_running:
                    # Already running, do nothing
                    print("⚠️ Simulation is already running")
                else:
                    # Start fresh simulation
                    print("🚀 Starting fresh simulation...")
                    if hasattr(self.simulation_engine, 'start'):
                        # Run in a separate thread to avoid blocking
                        import threading
                        def start_and_run_engine():
                            try:
                                # First start the engine
                                asyncio.run(self.simulation_engine.start())
                                print("✅ [DEBUG] Engine start completed")
                                
                                # Then run the main loop
                                asyncio.run(self.simulation_engine.run())
                                print("✅ [DEBUG] Main simulation loop completed")
                            except Exception as e:
                                print(f"❌ [DEBUG] Error in simulation engine: {e}")
                        
                        engine_thread = threading.Thread(target=start_and_run_engine, daemon=True)
                        engine_thread.start()
                        print("✅ Simulation engine started in background thread")
                    else:
                        self.simulation_engine.is_running = True
                        print("✅ Simulation engine marked as running")
                
                logger.info("Simulation play command processed")
                return {'status': 'running'}
            
            elif command == 'pause':
                # Pause simulation engine
                print("⏸️ Executing pause command...")
                if hasattr(self.simulation_engine, 'pause'):
                    # Run async method in a thread
                    import threading
                    def pause_engine():
                        try:
                            asyncio.run(self.simulation_engine.pause())
                            print("✅ [DEBUG] Engine pause completed")
                        except Exception as e:
                            print(f"❌ Error pausing engine: {e}")
                    
                    pause_thread = threading.Thread(target=pause_engine, daemon=True)
                    pause_thread.start()
                    print("✅ Simulation engine pause called")
                else:
                    self.simulation_engine.is_running = False
                    print("✅ Simulation engine marked as paused")
                logger.info("Simulation paused")
                return {'status': 'paused'}
            
            elif command == 'resume':
                # Resume simulation engine
                print("▶️ Executing resume command...")
                if hasattr(self.simulation_engine, 'resume'):
                    # Run async method in a thread
                    import threading
                    def resume_engine():
                        try:
                            asyncio.run(self.simulation_engine.resume())
                            print("✅ [DEBUG] Engine resume completed")
                        except Exception as e:
                            print(f"❌ Error resuming engine: {e}")
                    
                    resume_thread = threading.Thread(target=resume_engine, daemon=True)
                    resume_thread.start()
                    print("✅ Simulation engine resume called")
                else:
                    self.simulation_engine.is_running = True
                    print("✅ Simulation engine marked as running")
                logger.info("Simulation resumed")
                return {'status': 'running'}
            
            elif command == 'reset':
                # Reset simulation engine
                print("🔄 Executing reset command...")
                
                # Stop the simulation first if it's running
                if hasattr(self.simulation_engine, 'stop'):
                    try:
                        # Run async method in a thread
                        import threading
                        def stop_engine():
                            try:
                                asyncio.run(self.simulation_engine.stop())
                                print("✅ [DEBUG] Engine stop completed")
                            except Exception as e:
                                print(f"❌ Error stopping engine: {e}")
                        
                        stop_thread = threading.Thread(target=stop_engine, daemon=True)
                        stop_thread.start()
                        print("✅ Simulation engine stop called")
                    except Exception as e:
                        print(f"❌ Error during engine stop: {e}")
                
                # Reset the simulation
                if hasattr(self.simulation_engine, 'reset_simulation'):
                    self.simulation_engine.reset_simulation()
                    print("✅ Called engine reset_simulation method")
                else:
                    # Manual reset if no method available
                    self.simulation_engine.simulation_time = 0
                    self.simulation_engine.is_running = False
                    if hasattr(self.simulation_engine, 'state'):
                        if hasattr(self.simulation_engine.state, 'reset'):
                            self.simulation_engine.state.reset()
                        elif hasattr(self.simulation_engine.state, 'frame_count'):
                            self.simulation_engine.state.frame_count = 0
                    print("✅ Manual simulation reset completed")
                
                logger.info("Simulation reset")
                return {'status': 'reset'}
            
            elif command == 'step':
                # Execute simulation step
                if hasattr(self.simulation_engine, 'step'):
                    self.simulation_engine.step()
                elif hasattr(self.simulation_engine, '_main_loop'):
                    # Trigger a single update
                    asyncio.create_task(self.simulation_engine._main_loop())
                logger.info("Simulation step executed")
                return {'status': 'stepped'}
            
            elif command == 'speed':
                # Change simulation speed
                speed = params.get('speed', 1.0)
                if hasattr(self.simulation_engine, 'set_simulation_speed'):
                    self.simulation_engine.set_simulation_speed(speed)
                else:
                    self.simulation_engine.simulation_speed = speed
                logger.info(f"Simulation speed changed to {speed}x")
                return {'speed': speed}
            
            elif command == 'stop':
                # Stop simulation engine
                if hasattr(self.simulation_engine, 'stop'):
                    asyncio.create_task(self.simulation_engine.stop())
                else:
                    self.simulation_engine.is_running = False
                logger.info("Simulation stopped")
                return {'status': 'stopped'}
            
            else:
                logger.warning(f"Unknown command: {command}")
                return {'error': f'Unknown command: {command}'}
                
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {'error': str(e)}
    
    def start_update_loop(self):
        """Start periodic update loop"""
        self.is_running = True
        
        def update_loop():
            while self.is_running:
                try:
                    # Check if simulation engine is running and start it if needed
                    if self.simulation_engine and not getattr(self.simulation_engine, 'is_running', False):
                        print("🔄 Simulation engine not running, attempting to start...")
                        self.start_simulation_engine()
                    
                    # Trigger update callbacks
                    for data_type, callback in self.update_callbacks.items():
                        if callback:
                            try:
                                data = callback()
                                logger.debug(f"Updated {data_type}: {len(str(data))} bytes")
                            except Exception as e:
                                logger.error(f"Error in {data_type} update: {e}")
                    
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    time.sleep(1)  # Wait before retrying
        
        # Start update loop in separate thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        logger.info("✅ Update loop started")
    
    def stop_update_loop(self):
        """Stop the update loop"""
        self.is_running = False
        logger.info("🛑 Update loop stopped")
    
    def get_cached_data(self, data_type: str) -> Dict[str, Any]:
        """Get cached data by type"""
        if data_type == 'simulation_state':
            return self.last_simulation_state
        elif data_type == 'robot_data':
            return list(self.last_robot_data.values())
        elif data_type == 'order_data':
            return self.last_order_data
        elif data_type == 'kpi_data':
            return self.last_kpi_data
        elif data_type == 'warehouse_data': # Added warehouse data to cached types
            return self.last_warehouse_data
        else:
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get data bridge status"""
        return {
            'is_running': self.is_running,
            'update_interval': self.update_interval,
            'simulation_engine_connected': self.simulation_engine is not None,
            'robot_system_connected': self.robot is not None,
            'order_manager_connected': self.order_queue_manager is not None,
            'inventory_manager_connected': self.inventory_manager is not None,
            'analytics_engine_connected': self.analytics_engine is not None,
            'event_system_connected': self.event_system is not None,
            'registered_callbacks': list(self.update_callbacks.keys()),
            'cached_data_types': ['simulation_state', 'robot_data', 'order_data', 'kpi_data', 'inventory_data', 'warehouse_data'],
            'event_subscriptions': len(self.event_subscriptions) if hasattr(self, 'event_subscriptions') else 0
        }
    
    def export_data(self, data_type: str = 'all') -> Dict[str, Any]:
        """Export data for external use"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'bridge_status': self.get_status()
        }
        
        if data_type == 'all' or data_type == 'simulation_state':
            export_data['simulation_state'] = self.get_simulation_state()
        
        if data_type == 'all' or data_type == 'robot_data':
            export_data['robot_data'] = self.get_robot_data()
        
        if data_type == 'all' or data_type == 'order_data':
            export_data['order_data'] = self.get_order_data()
        
        if data_type == 'all' or data_type == 'kpi_data':
            export_data['kpi_data'] = self.get_kpi_data()
        
        if data_type == 'all' or data_type == 'warehouse_data':
            export_data['warehouse_data'] = self.get_warehouse_data()
        
        return export_data

def main():
    """Main entry point for testing"""
    import sys
    
    # Create data bridge
    bridge = DataBridge()
    
    # Register update callbacks
    bridge.register_update_callback('simulation_state', bridge.get_simulation_state)
    bridge.register_update_callback('robot_data', bridge.get_robot_data)
    bridge.register_update_callback('order_data', bridge.get_order_data)
    bridge.register_update_callback('kpi_data', bridge.get_kpi_data)
    bridge.register_update_callback('warehouse_data', bridge.get_warehouse_data) # Register warehouse data callback
    
    # Start update loop
    bridge.start_update_loop()
    
    try:
        # Run for 10 seconds to test
        print("🧪 Testing Data Bridge for 10 seconds...")
        time.sleep(10)
        
        # Export final data
        export_data = bridge.export_data()
        print(f"📊 Exported data: {json.dumps(export_data, indent=2)}")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping data bridge...")
    finally:
        bridge.stop_update_loop()
        print("✅ Data bridge stopped")

if __name__ == '__main__':
    main() 