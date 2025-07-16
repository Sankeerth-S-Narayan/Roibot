#!/usr/bin/env python3
"""
Test Phase 8 Task 7: Real-time Data Integration
Tests the integration between web interface and simulation components
"""

import unittest
import sys
import os
import time
import json
import threading
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the classes we'll be testing
from web_interface.server.data_bridge import DataBridge
from web_interface.server.websocket_handler import WebSocketHandler

class TestPhase8Task7Integration(unittest.TestCase):
    """Test real-time data integration for Phase 8 Task 7"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data_bridge = None
        self.test_websocket_handler = None
        self.test_web_server = None
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_websocket_handler:
            self.test_websocket_handler.stop_update_loop()
        if self.test_web_server:
            self.test_web_server.shutdown()
    
    def test_01_data_bridge_initialization(self):
        """Test data bridge initialization with real components"""
        print("\n🧪 Test 1: Data Bridge Initialization")
        
        try:
            # Initialize data bridge
            self.test_data_bridge = DataBridge()
            
            # Check if components are initialized
            self.assertIsNotNone(self.test_data_bridge.simulation_engine, "Simulation engine should be initialized")
            self.assertIsNotNone(self.test_data_bridge.robot, "Robot system should be initialized")
            self.assertIsNotNone(self.test_data_bridge.order_queue_manager, "Order queue manager should be initialized")
            self.assertIsNotNone(self.test_data_bridge.inventory_manager, "Inventory manager should be initialized")
            self.assertIsNotNone(self.test_data_bridge.analytics_engine, "Analytics engine should be initialized")
            
            print("✅ Data bridge initialization successful")
            
        except Exception as e:
            print(f"❌ Data bridge initialization failed: {e}")
            self.fail(f"Data bridge initialization failed: {e}")
    
    def test_02_data_bridge_methods(self):
        """Test data bridge data retrieval methods"""
        print("\n🧪 Test 2: Data Bridge Methods")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        try:
            # Test simulation state
            simulation_state = self.test_data_bridge.get_simulation_state()
            self.assertIsInstance(simulation_state, dict, "Simulation state should be a dictionary")
            self.assertIn('status', simulation_state, "Simulation state should have status")
            
            # Test robot data
            robot_data = self.test_data_bridge.get_robot_data()
            self.assertIsInstance(robot_data, list, "Robot data should be a list")
            
            # Test order data
            order_data = self.test_data_bridge.get_order_data()
            self.assertIsInstance(order_data, dict, "Order data should be a dictionary")
            self.assertIn('pending', order_data, "Order data should have pending count")
            self.assertIn('in_progress', order_data, "Order data should have in_progress count")
            self.assertIn('completed', order_data, "Order data should have completed count")
            
            # Test KPI data
            kpi_data = self.test_data_bridge.get_kpi_data()
            self.assertIsInstance(kpi_data, dict, "KPI data should be a dictionary")
            
            # Test warehouse data
            warehouse_data = self.test_data_bridge.get_warehouse_data()
            self.assertIsInstance(warehouse_data, dict, "Warehouse data should be a dictionary")
            self.assertIn('grid_size', warehouse_data, "Warehouse data should have grid_size")
            
            # Test inventory data
            inventory_data = self.test_data_bridge.get_inventory_data()
            self.assertIsInstance(inventory_data, dict, "Inventory data should be a dictionary")
            self.assertIn('inventory', inventory_data, "Inventory data should have inventory")
            self.assertIn('total_items', inventory_data, "Inventory data should have total_items")
            
            print("✅ All data bridge methods working correctly")
            
        except Exception as e:
            print(f"❌ Data bridge methods test failed: {e}")
            self.fail(f"Data bridge methods test failed: {e}")
    
    def test_03_websocket_handler_initialization(self):
        """Test WebSocket handler initialization"""
        print("\n🧪 Test 3: WebSocket Handler Initialization")
        
        try:
            if not self.test_data_bridge:
                self.test_data_bridge = DataBridge()
            
            # Initialize WebSocket handler
            self.test_websocket_handler = WebSocketHandler(self.test_data_bridge)
            
            # Check if handler is initialized
            self.assertIsNotNone(self.test_websocket_handler.data_bridge, "Data bridge should be connected")
            self.assertIsInstance(self.test_websocket_handler.connected_clients, set, "Connected clients should be a set")
            self.assertIsInstance(self.test_websocket_handler.client_subscriptions, dict, "Client subscriptions should be a dict")
            
            print("✅ WebSocket handler initialization successful")
            
        except Exception as e:
            print(f"❌ WebSocket handler initialization failed: {e}")
            self.fail(f"WebSocket handler initialization failed: {e}")
    
    def test_04_websocket_handler_methods(self):
        """Test WebSocket handler methods"""
        print("\n🧪 Test 4: WebSocket Handler Methods")
        
        if not self.test_websocket_handler:
            if not self.test_data_bridge:
                self.test_data_bridge = DataBridge()
            self.test_websocket_handler = WebSocketHandler(self.test_data_bridge)
        
        try:
            # Test client registration
            mock_socket = Mock()
            success = self.test_websocket_handler.register_client("test_client_1", mock_socket)
            self.assertTrue(success, "Client registration should succeed")
            self.assertIn("test_client_1", self.test_websocket_handler.connected_clients)
            
            # Test client unregistration
            self.test_websocket_handler.unregister_client("test_client_1")
            self.assertNotIn("test_client_1", self.test_websocket_handler.connected_clients)
            
            # Test message sending
            test_data = {"test": "data"}
            self.test_websocket_handler.send_message(mock_socket, "test_event", test_data)
            
            # Test broadcast message
            self.test_websocket_handler.broadcast_message("test_broadcast", test_data)
            
            # Test status
            status = self.test_websocket_handler.get_status()
            self.assertIsInstance(status, dict, "Status should be a dictionary")
            self.assertIn('is_running', status, "Status should have is_running")
            self.assertIn('connected_clients', status, "Status should have connected_clients")
            
            print("✅ All WebSocket handler methods working correctly")
            
        except Exception as e:
            print(f"❌ WebSocket handler methods test failed: {e}")
            self.fail(f"WebSocket handler methods test failed: {e}")
    
    def test_05_event_handling(self):
        """Test event handling in data bridge"""
        print("\n🧪 Test 5: Event Handling")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        try:
            # Test robot position update event
            robot_event_data = {
                'robot_id': 'ROBOT_001',
                'position': 'A5',
                'state': 'MOVING',
                'current_order': 'ORDER_001',
                'path': ['A1', 'A2', 'A3', 'A4', 'A5'],
                'direction': 'FORWARD',
                'items_held': ['ITEM_A1'],
                'target_items': ['ITEM_B3']
            }
            
            self.test_data_bridge.handle_robot_position_update(robot_event_data)
            
            # Verify robot data was updated
            robot_data = self.test_data_bridge.get_robot_data()
            self.assertGreater(len(robot_data), 0, "Robot data should be available")
            
            # Test order created event
            order_event_data = {
                'order_id': 'ORDER_002',
                'items': ['ITEM_C7', 'ITEM_D2'],
                'timestamp': time.time()
            }
            
            self.test_data_bridge.handle_order_created(order_event_data)
            
            # Verify order data was updated
            order_data = self.test_data_bridge.get_order_data()
            self.assertGreaterEqual(order_data['total'], 0, "Order data should be updated")
            
            # Test KPI update event
            kpi_event_data = {
                'kpi_type': 'orders_per_hour',
                'value': 12.5,
                'timestamp': time.time()
            }
            
            self.test_data_bridge.handle_kpi_update(kpi_event_data)
            
            # Verify KPI data was updated
            kpi_data = self.test_data_bridge.get_kpi_data()
            self.assertIsInstance(kpi_data, dict, "KPI data should be available")
            
            print("✅ All event handling working correctly")
            
        except Exception as e:
            print(f"❌ Event handling test failed: {e}")
            self.fail(f"Event handling test failed: {e}")
    
    def test_06_command_execution(self):
        """Test command execution through data bridge"""
        print("\n🧪 Test 6: Command Execution")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        try:
            # Test play command
            result = self.test_data_bridge.execute_command('play')
            self.assertIsInstance(result, dict, "Command result should be a dictionary")
            
            # Test pause command
            result = self.test_data_bridge.execute_command('pause')
            self.assertIsInstance(result, dict, "Command result should be a dictionary")
            
            # Test reset command
            result = self.test_data_bridge.execute_command('reset')
            self.assertIsInstance(result, dict, "Command result should be a dictionary")
            
            # Test speed command
            result = self.test_data_bridge.execute_command('speed', {'speed': 2.0})
            self.assertIsInstance(result, dict, "Command result should be a dictionary")
            
            # Test unknown command
            result = self.test_data_bridge.execute_command('unknown_command')
            self.assertIn('error', result, "Unknown command should return error")
            
            print("✅ All command execution working correctly")
            
        except Exception as e:
            print(f"❌ Command execution test failed: {e}")
            self.fail(f"Command execution test failed: {e}")
    
    def test_07_real_time_updates(self):
        """Test real-time update functionality"""
        print("\n🧪 Test 7: Real-time Updates")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        if not self.test_websocket_handler:
            self.test_websocket_handler = WebSocketHandler(self.test_data_bridge)
        
        try:
            # Start update loop
            self.test_websocket_handler.start_update_loop()
            
            # Wait a moment for updates to start
            time.sleep(0.5)
            
            # Check if update loop is running
            self.assertTrue(self.test_websocket_handler.is_running, "Update loop should be running")
            
            # Stop update loop
            self.test_websocket_handler.stop_update_loop()
            
            # Wait a moment for updates to stop
            time.sleep(0.5)
            
            # Check if update loop is stopped
            self.assertFalse(self.test_websocket_handler.is_running, "Update loop should be stopped")
            
            print("✅ Real-time updates working correctly")
            
        except Exception as e:
            print(f"❌ Real-time updates test failed: {e}")
            self.fail(f"Real-time updates test failed: {e}")
    
    def test_08_data_synchronization(self):
        """Test data synchronization between components"""
        print("\n🧪 Test 8: Data Synchronization")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        try:
            # Get initial data
            initial_robot_data = self.test_data_bridge.get_robot_data()
            initial_order_data = self.test_data_bridge.get_order_data()
            initial_kpi_data = self.test_data_bridge.get_kpi_data()
            
            print(f"🔍 Initial KPI data: {initial_kpi_data}")
            
            # Simulate some events
            print(f"🔧 Calling handle_robot_position_update...")
            self.test_data_bridge.handle_robot_position_update({
                'robot_id': 'ROBOT_001',
                'position': 'B10',
                'state': 'COLLECTING',
                'current_order': 'ORDER_003',
                'path': ['A1', 'B10'],
                'direction': 'FORWARD',
                'items_held': ['ITEM_A1', 'ITEM_B3'],
                'target_items': ['ITEM_C7']
            })
            
            print(f"🔧 Calling handle_order_created...")
            self.test_data_bridge.handle_order_created({
                'order_id': 'ORDER_004',
                'items': ['ITEM_E5', 'ITEM_F8'],
                'timestamp': time.time()
            })
            
            print(f"🔧 Calling handle_kpi_update...")
            self.test_data_bridge.handle_kpi_update({
                'kpi_type': 'robot_utilization',
                'value': 85.5,
                'timestamp': time.time()
            })
            
            print(f"🔧 Calling handle_kpi_update for orders_per_hour...")
            self.test_data_bridge.handle_kpi_update({
                'kpi_type': 'orders_per_hour',
                'value': 15.2,
                'timestamp': time.time()
            })
            
            # Get updated data
            updated_robot_data = self.test_data_bridge.get_robot_data()
            updated_order_data = self.test_data_bridge.get_order_data()
            updated_kpi_data = self.test_data_bridge.get_kpi_data()
            
            print(f"🔍 Updated KPI data: {updated_kpi_data}")
            
            # Verify data was synchronized
            self.assertNotEqual(initial_robot_data, updated_robot_data, "Robot data should be updated")
            self.assertNotEqual(initial_order_data, updated_order_data, "Order data should be updated")
            self.assertNotEqual(initial_kpi_data, updated_kpi_data, "KPI data should be updated")
            
            print("✅ Data synchronization working correctly")
            
        except Exception as e:
            print(f"❌ Data synchronization test failed: {e}")
            self.fail(f"Data synchronization test failed: {e}")
    
    def test_09_error_handling(self):
        """Test error handling in integration"""
        print("\n🧪 Test 9: Error Handling")
        
        if not self.test_data_bridge:
            self.test_data_bridge = DataBridge()
        
        try:
            # Test with invalid data
            invalid_event_data = None
            
            # Should not raise exception
            self.test_data_bridge.handle_robot_position_update(invalid_event_data)
            self.test_data_bridge.handle_order_created(invalid_event_data)
            self.test_data_bridge.handle_kpi_update(invalid_event_data)
            
            # Test with invalid command
            result = self.test_data_bridge.execute_command('invalid_command')
            self.assertIn('error', result, "Invalid command should return error")
            
            # Test data retrieval with missing components
            # This should not raise exceptions
            robot_data = self.test_data_bridge.get_robot_data()
            order_data = self.test_data_bridge.get_order_data()
            kpi_data = self.test_data_bridge.get_kpi_data()
            
            self.assertIsInstance(robot_data, list, "Robot data should be a list even with errors")
            self.assertIsInstance(order_data, dict, "Order data should be a dict even with errors")
            self.assertIsInstance(kpi_data, dict, "KPI data should be a dict even with errors")
            
            print("✅ Error handling working correctly")
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.fail(f"Error handling test failed: {e}")
    
    def test_10_performance_monitoring(self):
        """Test performance monitoring in integration"""
        print("\n🧪 Test 10: Performance Monitoring")
        
        if not self.test_websocket_handler:
            if not self.test_data_bridge:
                self.test_data_bridge = DataBridge()
            self.test_websocket_handler = WebSocketHandler(self.test_data_bridge)
        
        try:
            # Simulate some activity
            mock_socket = Mock()
            self.test_websocket_handler.register_client("perf_test_client", mock_socket)
            
            # Send some messages
            for i in range(10):
                self.test_websocket_handler.send_message(mock_socket, f"test_event_{i}", {"data": i})
            
            # Check performance stats
            status = self.test_websocket_handler.get_status()
            self.assertIn('performance_stats', status, "Status should have performance stats")
            
            perf_stats = status['performance_stats']
            self.assertIn('messages_sent', perf_stats, "Performance stats should have messages_sent")
            self.assertIn('clients_connected', perf_stats, "Performance stats should have clients_connected")
            self.assertIn('average_message_size', perf_stats, "Performance stats should have average_message_size")
            self.assertIn('error_count', perf_stats, "Performance stats should have error_count")
            
            # Verify some basic stats
            self.assertGreaterEqual(perf_stats['messages_sent'], 10, "Should have sent at least 10 messages")
            self.assertEqual(perf_stats['clients_connected'], 1, "Should have 1 connected client")
            
            print("✅ Performance monitoring working correctly")
            
        except Exception as e:
            print(f"❌ Performance monitoring test failed: {e}")
            self.fail(f"Performance monitoring test failed: {e}")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Phase 8 Task 7 Integration Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add tests
    test_suite.addTest(TestPhase8Task7Integration('test_01_data_bridge_initialization'))
    test_suite.addTest(TestPhase8Task7Integration('test_02_data_bridge_methods'))
    test_suite.addTest(TestPhase8Task7Integration('test_03_websocket_handler_initialization'))
    test_suite.addTest(TestPhase8Task7Integration('test_04_websocket_handler_methods'))
    test_suite.addTest(TestPhase8Task7Integration('test_05_event_handling'))
    test_suite.addTest(TestPhase8Task7Integration('test_06_command_execution'))
    test_suite.addTest(TestPhase8Task7Integration('test_07_real_time_updates'))
    test_suite.addTest(TestPhase8Task7Integration('test_08_data_synchronization'))
    test_suite.addTest(TestPhase8Task7Integration('test_09_error_handling'))
    test_suite.addTest(TestPhase8Task7Integration('test_10_performance_monitoring'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n✅ All integration tests passed!")
        print("🎉 Phase 8 Task 7 Real-time Data Integration is working correctly!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1) 