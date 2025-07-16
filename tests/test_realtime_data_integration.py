#!/usr/bin/env python3
"""
Test Real-time Data Integration
Tests WebSocket handling, data bridge, and server components for real-time data integration
"""

import os
import sys
import unittest
import json
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRealtimeDataIntegration(unittest.TestCase):
    """Test real-time data integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.web_interface_dir = project_root / "web_interface"
        self.server_dir = self.web_interface_dir / "server"
        
        # Test files
        self.web_server_py = self.server_dir / "web_server.py"
        self.websocket_handler_py = self.server_dir / "websocket_handler.py"
        self.data_bridge_py = self.server_dir / "data_bridge.py"
        
        print(f"\n🔧 Testing Real-time Data Integration")
        print(f"📁 Web interface directory: {self.web_interface_dir}")
        print(f"📁 Server directory: {self.server_dir}")

    def test_01_web_server_exists(self):
        """Test that web_server.py file exists"""
        print(f"\n✅ Testing web_server.py file existence")
        self.assertTrue(self.web_server_py.exists(), f"web_server.py not found at {self.web_server_py}")
        print(f"✅ web_server.py found at {self.web_server_py}")

    def test_02_web_server_content(self):
        """Test web_server.py file content"""
        print(f"\n✅ Testing web_server.py file content")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class
        self.assertIn('class WebServer', content, "WebServer class not found")
        print("✅ WebServer class found")
        
        # Check for required methods
        required_methods = [
            'setup_routes',
            'setup_websocket_handlers',
            'initialize_simulation',
            'get_simulation_status',
            'get_robot_data',
            'get_order_data',
            'get_kpi_data',
            'execute_command',
            'start'
        ]
        
        for method in required_methods:
            self.assertIn(method, content, f"{method} method not found")
            print(f"✅ {method} method found")
        
        # Check for Flask integration
        self.assertIn('Flask', content, "Flask integration not found")
        print("✅ Flask integration found")
        
        # Check for SocketIO integration
        self.assertIn('SocketIO', content, "SocketIO integration not found")
        print("✅ SocketIO integration found")

    def test_03_websocket_handler_exists(self):
        """Test that websocket_handler.py file exists"""
        print(f"\n✅ Testing websocket_handler.py file existence")
        self.assertTrue(self.websocket_handler_py.exists(), f"websocket_handler.py not found at {self.websocket_handler_py}")
        print(f"✅ websocket_handler.py found at {self.websocket_handler_py}")

    def test_04_websocket_handler_content(self):
        """Test websocket_handler.py file content"""
        print(f"\n✅ Testing websocket_handler.py file content")
        
        with open(self.websocket_handler_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class
        self.assertIn('class WebSocketHandler', content, "WebSocketHandler class not found")
        print("✅ WebSocketHandler class found")
        
        # Check for required methods
        required_methods = [
            'register_handler',
            'register_update_callback',
            'add_client',
            'remove_client',
            'handle_message',
            'send_message',
            'broadcast_message',
            'start_update_loop'
        ]
        
        for method in required_methods:
            self.assertIn(method, content, f"{method} method not found")
            print(f"✅ {method} method found")
        
        # Check for message handlers
        self.assertIn('handle_ping', content, "Ping handler not found")
        print("✅ Ping handler found")
        
        self.assertIn('handle_command', content, "Command handler not found")
        print("✅ Command handler found")

    def test_05_data_bridge_exists(self):
        """Test that data_bridge.py file exists"""
        print(f"\n✅ Testing data_bridge.py file existence")
        self.assertTrue(self.data_bridge_py.exists(), f"data_bridge.py not found at {self.data_bridge_py}")
        print(f"✅ data_bridge.py found at {self.data_bridge_py}")

    def test_06_data_bridge_content(self):
        """Test data_bridge.py file content"""
        print(f"\n✅ Testing data_bridge.py file content")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class
        self.assertIn('class DataBridge', content, "DataBridge class not found")
        print("✅ DataBridge class found")
        
        # Check for required methods
        required_methods = [
            'initialize_components',
            'register_update_callback',
            'get_simulation_state',
            'get_robot_data',
            'get_order_data',
            'get_kpi_data',
            'execute_command',
            'start_update_loop'
        ]
        
        for method in required_methods:
            self.assertIn(method, content, f"{method} method not found")
            print(f"✅ {method} method found")
        
        # Check for mock components
        self.assertIn('create_mock_components', content, "Mock components not found")
        print("✅ Mock components found")

    def test_07_server_integration(self):
        """Test server integration functionality"""
        print(f"\n✅ Testing server integration functionality")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for simulation engine integration
        self.assertIn('SimulationEngine', content, "Simulation engine integration not found")
        print("✅ Simulation engine integration found")
        
        # Check for configuration management
        self.assertIn('ConfigurationManager', content, "Configuration management not found")
        print("✅ Configuration management found")
        
        # Check for component integration
        components = ['OrderManager', 'InventoryManager', 'AnalyticsDashboard']
        for component in components:
            self.assertIn(component, content, f"{component} integration not found")
            print(f"✅ {component} integration found")
        
        # Check for WebSocket integration
        self.assertIn('SocketIO', content, "WebSocket integration not found")
        print("✅ WebSocket integration found")

    def test_08_websocket_message_handling(self):
        """Test WebSocket message handling"""
        print(f"\n✅ Testing WebSocket message handling")
        
        with open(self.websocket_handler_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for message type routing
        self.assertIn('message_type', content, "Message type routing not found")
        print("✅ Message type routing found")
        
        # Check for JSON handling
        self.assertIn('json.loads', content, "JSON handling not found")
        print("✅ JSON handling found")
        
        # Check for error handling
        self.assertIn('except Exception', content, "Error handling not found")
        print("✅ Error handling found")

    def test_09_data_bridge_integration(self):
        """Test data bridge integration"""
        print(f"\n✅ Testing data bridge integration")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for simulation component imports
        self.assertIn('SimulationEngine', content, "SimulationEngine import not found")
        print("✅ SimulationEngine import found")
        
        self.assertIn('OrderManager', content, "OrderManager import not found")
        print("✅ OrderManager import found")
        
        self.assertIn('InventoryManager', content, "InventoryManager import not found")
        print("✅ InventoryManager import found")
        
        self.assertIn('AnalyticsDashboard', content, "AnalyticsDashboard import not found")
        print("✅ AnalyticsDashboard import found")

    def test_10_command_execution(self):
        """Test command execution functionality"""
        print(f"\n✅ Testing command execution functionality")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for command handling
        self.assertIn('execute_command', content, "Command execution not found")
        print("✅ Command execution found")
        
        # Check for specific commands
        commands = ['play', 'pause', 'reset', 'step', 'speed']
        for command in commands:
            self.assertIn(f"'{command}'", content, f"{command} command not found")
            print(f"✅ {command} command found")

    def test_11_real_time_updates(self):
        """Test real-time update functionality"""
        print(f"\n✅ Testing real-time update functionality")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for update loop
        self.assertIn('start_update_loop', content, "Update loop not found")
        print("✅ Update loop found")
        
        # Check for threading
        self.assertIn('threading', content, "Threading not found")
        print("✅ Threading found")
        
        # Check for periodic updates
        self.assertIn('update_interval', content, "Update interval not found")
        print("✅ Update interval found")

    def test_12_error_handling(self):
        """Test error handling functionality"""
        print(f"\n✅ Testing error handling functionality")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for try-catch blocks
        self.assertIn('try:', content, "Try-catch blocks not found")
        print("✅ Try-catch blocks found")
        
        # Check for error responses
        self.assertIn('error', content, "Error responses not found")
        print("✅ Error responses found")
        
        # Check for print statements for logging
        self.assertIn('print(', content, "Print statements for logging not found")
        print("✅ Print statements for logging found")

    def test_13_data_caching(self):
        """Test data caching functionality"""
        print(f"\n✅ Testing data caching functionality")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for cache variables
        self.assertIn('last_robot_data', content, "Robot data cache not found")
        print("✅ Robot data cache found")
        
        self.assertIn('last_order_data', content, "Order data cache not found")
        print("✅ Order data cache found")
        
        self.assertIn('last_kpi_data', content, "KPI data cache not found")
        print("✅ KPI data cache found")

    def test_14_api_endpoints(self):
        """Test API endpoints"""
        print(f"\n✅ Testing API endpoints")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for API routes
        endpoints = ['/api/status', '/api/robots', '/api/orders', '/api/kpis', '/api/warehouse', '/api/command']
        for endpoint in endpoints:
            self.assertIn(endpoint, content, f"{endpoint} endpoint not found")
            print(f"✅ {endpoint} endpoint found")

    def test_15_websocket_events(self):
        """Test WebSocket events"""
        print(f"\n✅ Testing WebSocket events")
        
        with open(self.websocket_handler_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for WebSocket events
        events = ['connect', 'disconnect', 'message']
        for event in events:
            self.assertIn(event, content, f"{event} event not found")
            print(f"✅ {event} event found")

    def test_16_data_export(self):
        """Test data export functionality"""
        print(f"\n✅ Testing data export functionality")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for export method
        self.assertIn('export_data', content, "Data export not found")
        print("✅ Data export found")
        
        # Check for JSON export
        self.assertIn('json.dumps', content, "JSON export not found")
        print("✅ JSON export found")

    def test_17_status_monitoring(self):
        """Test status monitoring functionality"""
        print(f"\n✅ Testing status monitoring functionality")
        
        with open(self.data_bridge_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for status methods
        self.assertIn('get_status', content, "Status monitoring not found")
        print("✅ Status monitoring found")
        
        # Check for component status
        self.assertIn('connected', content, "Component status not found")
        print("✅ Component status found")

    def test_18_file_structure(self):
        """Test file structure and organization"""
        print(f"\n✅ Testing file structure and organization")
        
        # Check that all required files exist
        required_files = [
            self.web_server_py,
            self.websocket_handler_py,
            self.data_bridge_py
        ]
        
        for file_path in required_files:
            self.assertTrue(file_path.exists(), f"Required file not found: {file_path}")
            print(f"✅ {file_path.name} exists")
        
        # Check file sizes are reasonable
        for file_path in required_files:
            size = file_path.stat().st_size
            self.assertGreater(size, 100, f"File too small: {file_path.name} ({size} bytes)")
            self.assertLess(size, 50000, f"File too large: {file_path.name} ({size} bytes)")
            print(f"✅ {file_path.name} size: {size} bytes")

    def test_19_code_quality(self):
        """Test code quality and structure"""
        print(f"\n✅ Testing code quality and structure")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper comments
        self.assertIn('"""', content, "Documentation comments not found")
        print("✅ Documentation comments found")
        
        # Check for proper imports
        self.assertIn('import', content, "Import statements not found")
        print("✅ Import statements found")
        
        # Check for proper class structure
        self.assertIn('class WebServer', content, "Class structure not found")
        print("✅ Class structure found")

    def test_20_integration_points(self):
        """Test integration points with existing systems"""
        print(f"\n✅ Testing integration points")
        
        with open(self.web_server_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for simulation engine integration
        self.assertIn('SimulationEngine', content, "Simulation engine integration not found")
        print("✅ Simulation engine integration found")
        
        # Check for configuration management
        self.assertIn('ConfigurationManager', content, "Configuration management not found")
        print("✅ Configuration management found")
        
        # Check for component integration
        components = ['OrderManager', 'InventoryManager', 'AnalyticsDashboard']
        for component in components:
            self.assertIn(component, content, f"{component} integration not found")
            print(f"✅ {component} integration found")

if __name__ == '__main__':
    print("🧪 Running Real-time Data Integration Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRealtimeDataIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1) 