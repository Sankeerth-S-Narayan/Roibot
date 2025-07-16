#!/usr/bin/env python3
"""
Test Interactive Controls & User Interface
Tests the simulation controls, status indicators, and user interface elements
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestInteractiveControls(unittest.TestCase):
    """Test interactive controls functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.web_interface_dir = project_root / "web_interface"
        self.static_dir = self.web_interface_dir / "static"
        self.js_dir = self.static_dir / "js"
        self.css_dir = self.static_dir / "css"
        
        # Test files
        self.controls_js = self.js_dir / "controls.js"
        self.components_css = self.css_dir / "components.css"
        self.main_js = self.js_dir / "main.js"
        
        print(f"\n🔧 Testing Interactive Controls")
        print(f"📁 Web interface directory: {self.web_interface_dir}")
        print(f"📁 Static directory: {self.static_dir}")
        print(f"📁 JS directory: {self.js_dir}")
        print(f"📁 CSS directory: {self.css_dir}")

    def test_01_controls_js_exists(self):
        """Test that controls.js file exists"""
        print(f"\n✅ Testing controls.js file existence")
        self.assertTrue(self.controls_js.exists(), f"controls.js not found at {self.controls_js}")
        print(f"✅ controls.js found at {self.controls_js}")

    def test_02_controls_js_content(self):
        """Test controls.js file content"""
        print(f"\n✅ Testing controls.js file content")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class
        self.assertIn('class SimulationControls', content, "SimulationControls class not found")
        print("✅ SimulationControls class found")
        
        # Check for required methods
        required_methods = [
            'initializeControls()',
            'setupEventListeners()',
            'toggleSimulation()',
            'resetSimulation()',
            'stepSimulation()',
            'updateSimulationStatus()',
            'updateRobotStatus(robotData)',
            'updateOrderQueueStatus(queueData)',
            'updateErrorStatus(error = null)'
        ]
        
        for method in required_methods:
            self.assertIn(method, content, f"{method} method not found")
            print(f"✅ {method} method found")
        
        # Check for event dispatching
        self.assertIn('CustomEvent', content, "CustomEvent usage not found")
        print("✅ CustomEvent usage found")
        
        # Check for DOM manipulation
        self.assertIn('document.createElement', content, "DOM creation not found")
        print("✅ DOM creation found")

    def test_03_components_css_exists(self):
        """Test that components.css file exists"""
        print(f"\n✅ Testing components.css file existence")
        self.assertTrue(self.components_css.exists(), f"components.css not found at {self.components_css}")
        print(f"✅ components.css found at {self.components_css}")

    def test_04_components_css_content(self):
        """Test components.css file content"""
        print(f"\n✅ Testing components.css file content")
        
        with open(self.components_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for control panel styles
        self.assertIn('.control-panel', content, "Control panel styles not found")
        print("✅ Control panel styles found")
        
        # Check for button styles
        self.assertIn('.control-btn', content, "Control button styles not found")
        print("✅ Control button styles found")
        
        # Check for status styles
        self.assertIn('.status-indicators', content, "Status indicator styles not found")
        print("✅ Status indicator styles found")
        
        # Check for robot status styles
        self.assertIn('.robot-status-panel', content, "Robot status panel styles not found")
        print("✅ Robot status panel styles found")
        
        # Check for order queue styles
        self.assertIn('.order-queue-status', content, "Order queue status styles not found")
        print("✅ Order queue status styles found")
        
        # Check for error status styles
        self.assertIn('.error-status', content, "Error status styles not found")
        print("✅ Error status styles found")

    def test_05_main_js_integration(self):
        """Test main.js integration with controls"""
        print(f"\n✅ Testing main.js integration")
        
        with open(self.main_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for SimulationControls usage
        self.assertIn('SimulationControls', content, "SimulationControls usage not found")
        print("✅ SimulationControls usage found")
        
        # Check for control event listeners
        self.assertIn('setupControlEventListeners', content, "Control event listeners not found")
        print("✅ Control event listeners found")
        
        # Check for event handling
        self.assertIn('simulationToggle', content, "Simulation toggle event not found")
        print("✅ Simulation toggle event found")
        
        self.assertIn('simulationReset', content, "Simulation reset event not found")
        print("✅ Simulation reset event found")
        
        self.assertIn('simulationStep', content, "Simulation step event not found")
        print("✅ Simulation step event found")

    def test_06_control_functionality(self):
        """Test control functionality structure"""
        print(f"\n✅ Testing control functionality structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for pause/resume functionality
        self.assertIn('pause-resume-btn', content, "Pause/resume button not found")
        print("✅ Pause/resume button found")
        
        # Check for reset functionality
        self.assertIn('reset-btn', content, "Reset button not found")
        print("✅ Reset button found")
        
        # Check for step functionality
        self.assertIn('step-btn', content, "Step button not found")
        print("✅ Step button found")
        
        # Check for speed control
        self.assertIn('speed-slider', content, "Speed slider not found")
        print("✅ Speed slider found")

    def test_07_status_indicators(self):
        """Test status indicators structure"""
        print(f"\n✅ Testing status indicators structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for simulation status
        self.assertIn('simulation-status', content, "Simulation status not found")
        print("✅ Simulation status found")
        
        # Check for simulation speed
        self.assertIn('simulation-speed', content, "Simulation speed not found")
        print("✅ Simulation speed found")
        
        # Check for simulation runtime
        self.assertIn('simulation-runtime', content, "Simulation runtime not found")
        print("✅ Simulation runtime found")

    def test_08_robot_status_panel(self):
        """Test robot status panel structure"""
        print(f"\n✅ Testing robot status panel structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for robot status panel
        self.assertIn('robot-status-panel', content, "Robot status panel not found")
        print("✅ Robot status panel found")
        
        # Check for robot status items
        self.assertIn('robot-status-item', content, "Robot status item not found")
        print("✅ Robot status item found")

    def test_09_order_queue_status(self):
        """Test order queue status structure"""
        print(f"\n✅ Testing order queue status structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for order queue status
        self.assertIn('order-queue-status', content, "Order queue status not found")
        print("✅ Order queue status found")
        
        # Check for queue items
        self.assertIn('pending-orders', content, "Pending orders not found")
        print("✅ Pending orders found")
        
        self.assertIn('in-progress-orders', content, "In progress orders not found")
        print("✅ In progress orders found")
        
        self.assertIn('completed-orders', content, "Completed orders not found")
        print("✅ Completed orders found")
        
        self.assertIn('total-orders', content, "Total orders not found")
        print("✅ Total orders found")

    def test_10_error_status(self):
        """Test error status structure"""
        print(f"\n✅ Testing error status structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error status
        self.assertIn('error-status', content, "Error status not found")
        print("✅ Error status found")
        
        # Check for error message
        self.assertIn('error-message', content, "Error message not found")
        print("✅ Error message found")

    def test_11_event_dispatching(self):
        """Test event dispatching functionality"""
        print(f"\n✅ Testing event dispatching functionality")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for simulation toggle event
        self.assertIn('simulationToggle', content, "Simulation toggle event not found")
        print("✅ Simulation toggle event found")
        
        # Check for simulation reset event
        self.assertIn('simulationReset', content, "Simulation reset event not found")
        print("✅ Simulation reset event found")
        
        # Check for simulation step event
        self.assertIn('simulationStep', content, "Simulation step event not found")
        print("✅ Simulation step event found")
        
        # Check for speed change event
        self.assertIn('simulationSpeedChange', content, "Speed change event not found")
        print("✅ Speed change event found")

    def test_12_state_management(self):
        """Test state management functionality"""
        print(f"\n✅ Testing state management functionality")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for state getter
        self.assertIn('getSimulationState', content, "Get simulation state not found")
        print("✅ Get simulation state found")
        
        # Check for state setter
        self.assertIn('setSimulationState', content, "Set simulation state not found")
        print("✅ Set simulation state found")

    def test_13_css_responsive_design(self):
        """Test responsive design in CSS"""
        print(f"\n✅ Testing responsive design in CSS")
        
        with open(self.components_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for responsive media queries
        self.assertIn('@media', content, "Media queries not found")
        print("✅ Media queries found")
        
        # Check for mobile responsiveness
        self.assertIn('max-width: 768px', content, "Mobile responsiveness not found")
        print("✅ Mobile responsiveness found")

    def test_14_accessibility_features(self):
        """Test accessibility features"""
        print(f"\n✅ Testing accessibility features")
        
        with open(self.components_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for focus states
        self.assertIn(':focus', content, "Focus states not found")
        print("✅ Focus states found")
        
        # Check for keyboard navigation
        self.assertIn('outline', content, "Outline styles not found")
        print("✅ Outline styles found")

    def test_15_animation_features(self):
        """Test animation features"""
        print(f"\n✅ Testing animation features")
        
        with open(self.components_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for transitions
        self.assertIn('transition', content, "Transitions not found")
        print("✅ Transitions found")
        
        # Check for hover effects
        self.assertIn(':hover', content, "Hover effects not found")
        print("✅ Hover effects found")

    def test_16_file_structure(self):
        """Test file structure and organization"""
        print(f"\n✅ Testing file structure and organization")
        
        # Check that all required files exist
        required_files = [
            self.controls_js,
            self.components_css,
            self.main_js
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

    def test_17_code_quality(self):
        """Test code quality and structure"""
        print(f"\n✅ Testing code quality and structure")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper comments
        self.assertIn('/**', content, "Documentation comments not found")
        print("✅ Documentation comments found")
        
        # Check for proper class structure
        self.assertIn('constructor()', content, "Constructor not found")
        print("✅ Constructor found")
        
        # Check for proper method organization
        self.assertIn('initializeControls()', content, "Initialization method not found")
        print("✅ Initialization method found")

    def test_18_integration_points(self):
        """Test integration points with other components"""
        print(f"\n✅ Testing integration points")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for warehouse container integration
        self.assertIn('warehouse-container', content, "Warehouse container integration not found")
        print("✅ Warehouse container integration found")
        
        # Check for DOM manipulation
        self.assertIn('appendChild', content, "DOM manipulation not found")
        print("✅ DOM manipulation found")
        
        # Check for event handling
        self.assertIn('addEventListener', content, "Event handling not found")
        print("✅ Event handling found")

    def test_19_error_handling(self):
        """Test error handling functionality"""
        print(f"\n✅ Testing error handling functionality")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error status updates
        self.assertIn('updateErrorStatus', content, "Error status updates not found")
        print("✅ Error status updates found")
        
        # Check for error display
        self.assertIn('error-status', content, "Error display not found")
        print("✅ Error display found")

    def test_20_performance_features(self):
        """Test performance features"""
        print(f"\n✅ Testing performance features")
        
        with open(self.controls_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for efficient DOM queries
        self.assertIn('getElementById', content, "Efficient DOM queries not found")
        print("✅ Efficient DOM queries found")
        
        # Check for event delegation
        self.assertIn('addEventListener', content, "Event delegation not found")
        print("✅ Event delegation found")

if __name__ == '__main__':
    print("🧪 Running Interactive Controls Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInteractiveControls)
    
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