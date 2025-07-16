#!/usr/bin/env python3
"""
WebSocket Handler for Roibot Warehouse Visualization Interface
Provides real-time data streaming with efficient updates and error handling
"""

import json
import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketHandler:
    """WebSocket handler for real-time data streaming"""
    
    def __init__(self, data_bridge):
        self.data_bridge = data_bridge
        self.connected_clients: Set[str] = set()
        self.client_subscriptions: Dict[str, Set[str]] = {}
        self.is_running = False
        self.update_interval = 0.1  # 100ms (10 FPS)
        self.max_clients = 100
        self.heartbeat_interval = 30  # 30 seconds
        
        # Performance tracking
        self.message_count = 0
        self.last_performance_check = time.time()
        self.performance_stats = {
            'messages_sent': 0,
            'clients_connected': 0,
            'average_message_size': 0,
            'error_count': 0
        }
        
        # Client socket storage
        self.client_sockets = {}
    
    def register_client(self, client_id: str, socket):
        """Register a new client connection"""
        try:
            if len(self.connected_clients) >= self.max_clients:
                logger.warning(f"Maximum clients reached ({self.max_clients})")
                return False
            
            self.connected_clients.add(client_id)
            self.client_subscriptions[client_id] = set()
            self.client_sockets[client_id] = socket
            
            # Update performance stats
            self.performance_stats['clients_connected'] = len(self.connected_clients)
            
            # Send initial data
            self.send_initial_data(client_id, socket)
            
            logger.info(f"✅ Client {client_id} registered. Total clients: {len(self.connected_clients)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering client {client_id}: {e}")
            return False
    
    def unregister_client(self, client_id: str):
        """Unregister a client connection"""
        try:
            self.connected_clients.discard(client_id)
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
            if client_id in self.client_sockets:
                del self.client_sockets[client_id]
            
            # Update performance stats
            self.performance_stats['clients_connected'] = len(self.connected_clients)
            
            logger.info(f"🛑 Client {client_id} unregistered. Total clients: {len(self.connected_clients)}")
            
        except Exception as e:
            logger.error(f"❌ Error unregistering client {client_id}: {e}")
    
    def send_initial_data(self, client_id: str, socket):
        """Send initial data to new client"""
        try:
            # Send simulation state
            simulation_state = self.data_bridge.get_simulation_state()
            self.send_message(socket, 'simulation_state', simulation_state)
            
            # Send robot data
            robot_data = self.data_bridge.get_robot_data()
            self.send_message(socket, 'robot_data', robot_data)
            
            # Send order data
            order_data = self.data_bridge.get_order_data()
            self.send_message(socket, 'order_data', order_data)
            
            # Send KPI data
            kpi_data = self.data_bridge.get_kpi_data()
            self.send_message(socket, 'kpi_data', kpi_data)
            
            # Send warehouse data
            warehouse_data = self.data_bridge.get_warehouse_data()
            self.send_message(socket, 'warehouse_data', warehouse_data)
            
            # Send inventory data
            inventory_data = self.data_bridge.get_inventory_data()
            self.send_message(socket, 'inventory_data', inventory_data)
            
            logger.info(f"✅ Initial data sent to client {client_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending initial data to client {client_id}: {e}")
    
    def send_message(self, socket, event_type: str, data: Dict[str, Any]):
        """Send message to client"""
        try:
            # Convert data to JSON-serializable format
            serializable_data = self._make_json_serializable(data)
            
            message = {
                'type': event_type,
                'data': serializable_data,
                'timestamp': time.time()
            }
            
            message_json = json.dumps(message)
            socket.send(message_json)
            
            # Update performance stats
            self.message_count += 1
            self.performance_stats['messages_sent'] += 1
            self.performance_stats['average_message_size'] = (
                (self.performance_stats['average_message_size'] * (self.message_count - 1) + len(message_json)) / self.message_count
            )
            
        except Exception as e:
            logger.error(f"❌ Error sending message to client: {e}")
            self.performance_stats['error_count'] += 1
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON-serializable format"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Handle custom objects like Coordinate
            return str(obj)
        elif hasattr(obj, 'value'):
            # Handle Enum objects
            return obj.value
        else:
            return obj
    
    def broadcast_message(self, event_type: str, data: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return
        
        message = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        message_json = json.dumps(message)
        disconnected_clients = set()
        
        for client_id in self.connected_clients:
            try:
                # Get socket from client_id (this would need to be implemented based on your WebSocket framework)
                # For now, we'll use a placeholder
                socket = self.get_socket_for_client(client_id)
                if socket:
                    socket.send(message_json)
                else:
                    disconnected_clients.add(client_id)
                    
            except Exception as e:
                logger.error(f"❌ Error broadcasting to client {client_id}: {e}")
                disconnected_clients.add(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.unregister_client(client_id)
    
    def get_socket_for_client(self, client_id: str):
        """Get socket for client ID"""
        return self.client_sockets.get(client_id)
    
    def handle_client_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming message from client"""
        try:
            message_type = message.get('type', '')
            data = message.get('data', {})
            
            if message_type == 'subscribe':
                # Handle subscription to specific data types
                data_types = data.get('data_types', [])
                self.client_subscriptions[client_id].update(data_types)
                logger.info(f"Client {client_id} subscribed to: {data_types}")
                
            elif message_type == 'unsubscribe':
                # Handle unsubscription from specific data types
                data_types = data.get('data_types', [])
                self.client_subscriptions[client_id].difference_update(data_types)
                logger.info(f"Client {client_id} unsubscribed from: {data_types}")
                
            elif message_type == 'command':
                # Handle simulation commands
                command = data.get('command', '')
                params = data.get('params', {})
                
                result = self.data_bridge.execute_command(command, params)
                
                # Send command response back to client
                socket = self.get_socket_for_client(client_id)
                if socket:
                    self.send_message(socket, 'command_response', {
                        'command': command,
                        'result': result,
                        'timestamp': time.time()
                    })
                
                logger.info(f"Client {client_id} executed command: {command}")
                
            elif message_type == 'ping':
                # Handle ping for connection health
                socket = self.get_socket_for_client(client_id)
                if socket:
                    self.send_message(socket, 'pong', {
                        'timestamp': time.time()
                    })
                
            else:
                logger.warning(f"Unknown message type from client {client_id}: {message_type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling message from client {client_id}: {e}")
    
    def start_update_loop(self):
        """Start the update loop for real-time data streaming"""
        self.is_running = True
        
        def update_loop():
            while self.is_running:
                try:
                    # Update performance stats
                    current_time = time.time()
                    if current_time - self.last_performance_check >= 60:  # Every minute
                        self.update_performance_stats()
                        self.last_performance_check = current_time
                    
                    # Broadcast updates to all clients
                    self.broadcast_updates()
                    
                    # Sleep for update interval
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"❌ Error in update loop: {e}")
                    time.sleep(1)  # Wait before retrying
        
        # Start update loop in separate thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        logger.info("✅ WebSocket update loop started")
    
    def stop_update_loop(self):
        """Stop the update loop"""
        self.is_running = False
        logger.info("🛑 WebSocket update loop stopped")
    
    def broadcast_updates(self):
        """Broadcast real-time updates to all clients"""
        try:
            # Get current data from data bridge
            simulation_state = self.data_bridge.get_simulation_state()
            robot_data = self.data_bridge.get_robot_data()
            order_data = self.data_bridge.get_order_data()
            kpi_data = self.data_bridge.get_kpi_data()
            inventory_data = self.data_bridge.get_inventory_data()
            
            # Broadcast to all clients
            self.broadcast_message('simulation_state', simulation_state)
            self.broadcast_message('robot_data', robot_data)
            self.broadcast_message('order_data', order_data)
            self.broadcast_message('kpi_data', kpi_data)
            self.broadcast_message('inventory_data', inventory_data)
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting updates: {e}")
    
    def update_performance_stats(self):
        """Update performance statistics"""
        self.performance_stats['clients_connected'] = len(self.connected_clients)
        
        logger.info(f"📊 WebSocket Performance Stats:")
        logger.info(f"  - Connected clients: {self.performance_stats['clients_connected']}")
        logger.info(f"  - Messages sent: {self.performance_stats['messages_sent']}")
        logger.info(f"  - Average message size: {self.performance_stats['average_message_size']:.1f} bytes")
        logger.info(f"  - Error count: {self.performance_stats['error_count']}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket handler status"""
        return {
            'is_running': self.is_running,
            'connected_clients': len(self.connected_clients),
            'max_clients': self.max_clients,
            'update_interval': self.update_interval,
            'performance_stats': self.performance_stats.copy(),
            'client_subscriptions': {
                client_id: list(subscriptions) 
                for client_id, subscriptions in self.client_subscriptions.items()
            }
        }
    
    def handle_robot_update(self, robot_data: Dict[str, Any]):
        """Handle robot data updates from data bridge"""
        try:
            self.broadcast_message('robot_data', robot_data)
        except Exception as e:
            logger.error(f"❌ Error handling robot update: {e}")
    
    def handle_order_update(self, order_data: Dict[str, Any]):
        """Handle order data updates from data bridge"""
        try:
            self.broadcast_message('order_data', order_data)
        except Exception as e:
            logger.error(f"❌ Error handling order update: {e}")
    
    def handle_kpi_update(self, kpi_data: Dict[str, Any]):
        """Handle KPI data updates from data bridge"""
        try:
            self.broadcast_message('kpi_data', kpi_data)
        except Exception as e:
            logger.error(f"❌ Error handling KPI update: {e}")
    
    def handle_inventory_update(self, inventory_data: Dict[str, Any]):
        """Handle inventory data updates from data bridge"""
        try:
            self.broadcast_message('inventory_data', inventory_data)
        except Exception as e:
            logger.error(f"❌ Error handling inventory update: {e}")
    
    def handle_simulation_state_update(self, simulation_state: Dict[str, Any]):
        """Handle simulation state updates from data bridge"""
        try:
            self.broadcast_message('simulation_state', simulation_state)
        except Exception as e:
            logger.error(f"❌ Error handling simulation state update: {e}")

def main():
    """Test the WebSocket handler"""
    from data_bridge import DataBridge
    
    # Create data bridge
    data_bridge = DataBridge()
    
    # Create WebSocket handler
    ws_handler = WebSocketHandler(data_bridge)
    
    # Start update loop
    ws_handler.start_update_loop()
    
    try:
        # Keep running for testing
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping WebSocket handler...")
        ws_handler.stop_update_loop()

if __name__ == "__main__":
    main() 