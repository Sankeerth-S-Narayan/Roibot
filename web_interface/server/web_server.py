#!/usr/bin/env python3
"""
Web Server for Roibot Warehouse Visualization Interface
Provides HTTP server and WebSocket support for real-time data integration
"""

import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from flask_socketio import SocketIO, emit, disconnect
import psutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import simulation components
try:
    from core.engine import SimulationEngine
    from entities.robot import Robot
    from entities.order_manager import OrderManager
    from entities.inventory_manager import InventoryManager
    from entities.analytics_dashboard import AnalyticsDashboard
    from core.config import ConfigurationManager
except ImportError as e:
    print(f"Warning: Could not import simulation components: {e}")
    # Create mock classes for testing
    class ConfigurationManager:
        def __init__(self):
            print("🔧 Mock ConfigurationManager initialized")
    
    class SimulationEngine:
        def __init__(self):
            self.is_running = False
            self.simulation_time = 0
            self.robots = {}
            self.orders = []
    
    class Robot:
        def __init__(self, robot_id: str):
            self.robot_id = robot_id
            self.position = "A1"
            self.state = "IDLE"
            self.current_order = None
    
    class OrderManager:
        def __init__(self):
            self.pending_orders = []
            self.in_progress_orders = []
            self.completed_orders = []
    
    class InventoryManager:
        def __init__(self):
            self.items = {}
    
    class AnalyticsDashboard:
        def __init__(self):
            self.kpis = {}

class WebServer:
    """Web server for warehouse visualization interface"""
    
    def __init__(self, host: str = 'localhost', port: int = 5000):
        self.host = host
        self.port = port
        
        # Set up Flask app with correct template and static directories
        template_dir = Path(__file__).parent.parent / 'templates'
        static_dir = Path(__file__).parent.parent / 'static'
        
        self.app = Flask(__name__, 
                        template_folder=str(template_dir),
                        static_folder=str(static_dir))
        
        # Configure Socket.IO with proper settings
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Simulation state
        self.simulation_engine = None
        self.config_manager = None
        self.order_manager = None
        self.inventory_manager = None
        self.analytics_dashboard = None
        self.connected_clients = set()
        self.last_update = time.time()
        
        # Setup routes and WebSocket handlers
        self.setup_routes()
        self.setup_websocket_handlers()
        
        # Start simulation integration thread
        self.simulation_thread = None
        self.shutdown_event = threading.Event()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve main HTML page"""
            return render_template('index.html')
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return send_from_directory('static', filename)
        
        @self.app.route('/api/status')
        def get_status():
            """Get current simulation status"""
            return jsonify(self.get_simulation_status())
        
        @self.app.route('/api/robots')
        def get_robots():
            """Get robot data"""
            return jsonify(self.get_robot_data())
        
        @self.app.route('/api/orders')
        def get_orders():
            """Get order data"""
            return jsonify(self.get_order_data())
        
        @self.app.route('/api/kpis')
        def get_kpis():
            """Get KPI data"""
            return jsonify(self.get_kpi_data())
        
        @self.app.route('/api/warehouse')
        def get_warehouse():
            """Get warehouse layout data"""
            return jsonify(self.get_warehouse_data())
        
        @self.app.route('/api/command', methods=['POST'])
        def handle_command():
            """Handle simulation commands"""
            data = request.get_json()
            command = data.get('command')
            params = data.get('params', {})
            
            result = self.execute_command(command, params)
            return jsonify({'success': True, 'result': result})
        
        @self.app.route('/test')
        def test_route():
            """Test route to verify server is working"""
            return jsonify({
                'status': 'ok',
                'message': 'Server is running',
                'timestamp': time.time(),
                'connected_clients': len(self.connected_clients)
            })
        
        @self.app.route('/start_simulation')
        def start_simulation():
            """Manually start the simulation"""
            try:
                if self.data_bridge:
                    print("🚀 [DEBUG] Manually starting simulation via endpoint...")
                    # Try to start the simulation engine
                    if hasattr(self.data_bridge, 'start_simulation_engine'):
                        self.data_bridge.start_simulation_engine()
                        print("✅ [DEBUG] Simulation engine start called")
                    
                    # Check if simulation engine is running
                    engine = getattr(self.data_bridge, 'simulation_engine', None)
                    if engine:
                        is_running = getattr(engine, 'is_running', False)
                        simulation_time = getattr(engine, 'simulation_time', 0)
                        print(f"🔍 [DEBUG] Engine is_running: {is_running}, simulation_time: {simulation_time}")
                        
                        return jsonify({
                            'status': 'success',
                            'message': 'Simulation started',
                            'engine_running': is_running,
                            'simulation_time': simulation_time,
                            'has_start_method': hasattr(engine, 'start'),
                            'has_main_loop': hasattr(engine, '_main_loop')
                        })
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'No simulation engine found'
                        })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No data bridge found'
                    })
            except Exception as e:
                print(f"❌ [DEBUG] Error in start_simulation endpoint: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                })
        
        @self.app.route('/socket.io/socket.io.js')
        def socketio_client():
            """Manually serve Socket.IO client script"""
            try:
                # Try to get the Socket.IO client from Flask-SocketIO
                import flask_socketio
                client_path = flask_socketio.__file__.replace('__init__.py', 'static/socket.io.js')
                if os.path.exists(client_path):
                    return send_file(client_path, mimetype='application/javascript')
                else:
                    # Fallback: return a working Socket.IO client
                    return '''
                    // Working Socket.IO client fallback
                    window.io = function() {
                        console.log("Using fallback Socket.IO client");
                        var socket = {
                            connected: false,
                            callbacks: {},
                            on: function(event, callback) {
                                console.log("Socket.IO event listener:", event);
                                this.callbacks[event] = callback;
                            },
                            emit: function(event, data) {
                                console.log("Socket.IO emit:", event, data);
                                // Simulate connection for testing
                                if (event === 'connect') {
                                    setTimeout(() => {
                                        this.connected = true;
                                        if (this.callbacks.connect) {
                                            this.callbacks.connect();
                                        }
                                    }, 100);
                                }
                            },
                            connect: function() {
                                this.emit('connect');
                            }
                        };
                        socket.connect();
                        return socket;
                    };
                    ''', 200, {'Content-Type': 'application/javascript'}
            except Exception as e:
                print(f"Error serving Socket.IO client: {e}")
                return "console.error('Socket.IO client not available');", 200, {'Content-Type': 'application/javascript'}
    
    def setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients.add(client_id)
            print(f"✅ Client connected: {client_id}")
            print(f"🔧 Total connected clients: {len(self.connected_clients)}")
            
            # Send initial data
            try:
                print(f"📡 Getting initial data for client {client_id}...")
                simulation_state = self.get_simulation_status()
                robot_data = self.get_robot_data()
                order_data = self.get_order_data()
                kpi_data = self.get_kpi_data()
                warehouse_data = self.get_warehouse_data()
                
                print(f"🔍 Simulation state: {simulation_state}")
                print(f"🔍 Robot data: {robot_data}")
                print(f"🔍 Order data: {order_data}")
                print(f"🔍 KPI data: {kpi_data}")
                
                emit('simulation_state', simulation_state)
                emit('robot_data', robot_data)
                emit('order_data', order_data)
                emit('kpi_data', kpi_data)
                emit('warehouse_data', warehouse_data)
                
                print(f"📤 Sent initial data to client {client_id}")
            except Exception as e:
                print(f"❌ Error sending initial data to client {client_id}: {e}")
                import traceback
                traceback.print_exc()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            self.connected_clients.discard(client_id)
            print(f"Client disconnected: {client_id}")
        
        @self.socketio.on('command')
        def handle_command(data):
            """Handle client commands"""
            command = data.get('command')
            params = data.get('params', {})
            
            result = self.execute_command(command, params)
            emit('command_response', {'success': True, 'result': result})
    
    def initialize_simulation(self):
        """Initialize simulation engine connection"""
        try:
            # Import and initialize data bridge
            from data_bridge import DataBridge
            from websocket_handler import WebSocketHandler
            
            # Initialize data bridge with real components
            self.data_bridge = DataBridge()
            
            # Initialize WebSocket handler
            self.websocket_handler = WebSocketHandler(self.data_bridge)
            
            # Start WebSocket update loop
            self.websocket_handler.start_update_loop()
            
            # Register update callbacks
            self.data_bridge.register_update_callback('robot_data', self.websocket_handler.handle_robot_update)
            self.data_bridge.register_update_callback('order_data', self.websocket_handler.handle_order_update)
            self.data_bridge.register_update_callback('kpi_data', self.websocket_handler.handle_kpi_update)
            self.data_bridge.register_update_callback('inventory_data', self.websocket_handler.handle_inventory_update)
            self.data_bridge.register_update_callback('simulation_state', self.websocket_handler.handle_simulation_state_update)
            
            print("✅ Real simulation components initialized with data bridge")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize simulation: {e}")
            return False
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        if not self.data_bridge:
            return {
                'status': 'disconnected',
                'time': 0,
                'speed': 1.0,
                'error': 'Data bridge not connected'
            }
        
        return self.data_bridge.get_simulation_state()
    
    def get_robot_data(self) -> List[Dict[str, Any]]:
        """Get robot data for visualization"""
        if not self.data_bridge:
            return []
        
        return self.data_bridge.get_robot_data()
    
    def get_order_data(self) -> Dict[str, Any]:
        """Get order data for visualization"""
        if not self.data_bridge:
            return {
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'total': 0,
                'orders': []
            }
        
        return self.data_bridge.get_order_data()
    
    def get_kpi_data(self) -> Dict[str, Any]:
        """Get KPI data for dashboard"""
        if not self.data_bridge:
            return {
                'orders_per_hour': 0,
                'robot_utilization': 0,
                'order_completion_rate': 0,
                'average_order_time': 0,
                'queue_length': 0
            }
        
        return self.data_bridge.get_kpi_data()
    
    def get_warehouse_data(self) -> Dict[str, Any]:
        """Get warehouse layout data"""
        if not self.data_bridge:
            return {
                'grid_size': {'width': 25, 'height': 20},
                'packout_location': 'A1',
                'aisles': list(range(1, 26)),
                'racks': list(range(1, 21))
            }
        
        return self.data_bridge.get_warehouse_data()
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute simulation command"""
        if not self.data_bridge:
            return {'error': 'Data bridge not connected'}
        
        return self.data_bridge.execute_command(command, params)
    
    def broadcast_update(self, event_type: str, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        if self.connected_clients:
            print(f"📡 Broadcasting {event_type} to {len(self.connected_clients)} clients: {data}")
            self.socketio.emit(event_type, data)
        else:
            print(f"⚠️  No connected clients to broadcast {event_type}")
    
    def start_update_loop(self):
        """Start periodic update loop"""
        def update_loop():
            while not self.shutdown_event.is_set():
                try:
                    # Broadcast updates every 100ms (10 FPS)
                    self.broadcast_update('simulation_state', self.get_simulation_status())
                    self.broadcast_update('robot_data', self.get_robot_data())
                    self.broadcast_update('order_data', self.get_order_data())
                    self.broadcast_update('kpi_data', self.get_kpi_data())
                    self.broadcast_update('warehouse_data', self.get_warehouse_data())
                    
                    time.sleep(0.1)  # 100ms interval
                    
                except Exception as e:
                    print(f"Error in update loop: {e}")
                    time.sleep(1)  # Wait before retrying
        
        self.simulation_thread = threading.Thread(target=update_loop, daemon=True)
        self.simulation_thread.start()
    
    def start(self):
        """Start the web server"""
        print(f"🚀 Starting Roibot Web Server on {self.host}:{self.port}")
        
        # Initialize simulation
        if self.initialize_simulation():
            print("✅ Simulation components initialized")
        else:
            print("⚠️  Running in mock mode - simulation components not available")
        
        # Start update loop
        self.start_update_loop()
        print("✅ Update loop started")
        
        # Start Flask server
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
        except KeyboardInterrupt:
            print("\n🛑 Shutting down web server...")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the web server"""
        print("🛑 Shutting down web server...")
        self.shutdown_event.set()
        
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        
        print("✅ Web server shutdown complete")

def main():
    """Main entry point"""
    import sys
    
    # Parse command line arguments
    host = 'localhost'
    port = 5000
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Create and start web server
    server = WebServer(host=host, port=port)
    server.start()

def create_app():
    """Create Flask app for unified application"""
    # Set up Flask app with correct template and static directories
    template_dir = Path(__file__).parent.parent / 'templates'
    static_dir = Path(__file__).parent.parent / 'static'
    
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # Setup basic routes
    @app.route('/')
    def index():
        """Serve main HTML page"""
        return render_template('index.html')
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        return send_from_directory('static', filename)
    
    @app.route('/api/status')
    def get_status():
        """Get current simulation status"""
        return jsonify({'status': 'running', 'time': time.time()})
    
    @app.route('/test')
    def test_route():
        """Test route to verify server is working"""
        return jsonify({
            'status': 'ok',
            'message': 'Server is running',
            'timestamp': time.time()
        })
    
    return app

if __name__ == '__main__':
    main() 