"""
Test Robot Visualization

This test verifies that the robot visualization system
properly handles movement, state visualization, and integration.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestRobotVisualization(unittest.TestCase):
    """Test robot visualization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.web_interface_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface')
        self.static_dir = os.path.join(self.web_interface_dir, 'static')
        self.js_dir = os.path.join(self.static_dir, 'js')
        
    def test_robot_js_exists(self):
        """Test that robot.js file exists."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        print(f"\n🔍 DEBUG: Checking robot.js")
        print(f"📄 File path: {robot_js}")
        print(f"📄 File exists: {os.path.exists(robot_js)}")
        
        self.assertTrue(os.path.exists(robot_js), "robot.js should exist")
        
        if os.path.exists(robot_js):
            with open(robot_js, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📏 File size: {len(content)} characters")
                self.assertGreater(len(content), 0, "robot.js should not be empty")
                
    def test_robot_js_structure(self):
        """Test that robot.js has proper structure."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required JavaScript elements
            required_elements = [
                'class RobotVisualizer',
                'constructor(warehouseVisualizer)',
                'robotSize = 20',
                'robotRadius = this.robotSize / 2',
                'robotColors = {',
                'IDLE: \'#4CAF50\'',
                'MOVING: \'#2196F3\'',
                'COLLECTING: \'#FF9800\'',
                'RETURNING: \'#9C27B0\'',
                'ERROR: \'#F44336\'',
                'setRobotPosition(',
                'moveRobotTo(',
                'setRobotState(',
                'assignOrder(',
                'update(',
                'render(',
                'drawRobot(',
                'drawDirectionIndicator(',
                'drawPath(',
                'getRobotPosition(',
                'updateFromData(',
                'simulateMovement('
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"robot.js should contain {element}")
                
    def test_robot_state_colors(self):
        """Test that robot state colors are properly defined."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for robot state colors
            state_colors = [
                'IDLE: \'#4CAF50\'',      # Green
                'MOVING: \'#2196F3\'',     # Blue
                'COLLECTING: \'#FF9800\'',  # Orange
                'RETURNING: \'#9C27B0\'',   # Purple
                'ERROR: \'#F44336\''        # Red
            ]
            
            for color in state_colors:
                self.assertIn(color, content, f"robot.js should contain state color: {color}")
                
    def test_robot_animation_configuration(self):
        """Test that robot animation configuration is properly defined."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for animation configuration
            animation_elements = [
                'animationSpeed = 0.05',
                'stateTransitionDuration = 200',
                'pathArrowSize = 8',
                'movementProgress = 0',
                'isMoving = false'
            ]
            
            for element in animation_elements:
                self.assertIn(element, content, f"robot.js should contain animation config: {element}")
                
    def test_robot_movement_methods(self):
        """Test that robot movement methods are implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for movement methods
            movement_elements = [
                'setRobotPosition(',
                'moveRobotTo(',
                'updateMovement(',
                'handleOrderState(',
                'isAtPackoutZone(',
                'Math.atan2(dy, dx)',
                'movementProgress +='
            ]
            
            for element in movement_elements:
                self.assertIn(element, content, f"robot.js should contain movement method: {element}")
                
    def test_robot_rendering_methods(self):
        """Test that robot rendering methods are implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for rendering methods
            rendering_elements = [
                'render()',
                'drawRobot(',
                'drawRobotIcon(',
                'drawStateIndicator(',
                'drawDirectionIndicator(',
                'drawPath(',
                'drawPathArrows(',
                'drawArrow(',
                'getPixelCoordinates(',
                'arc(x, y, this.robotRadius'
            ]
            
            for element in rendering_elements:
                self.assertIn(element, content, f"robot.js should contain rendering method: {element}")
                
    def test_robot_state_management(self):
        """Test that robot state management is implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for state management
            state_elements = [
                'state: \'IDLE\'',
                'setRobotState(',
                'assignOrder(',
                'clearOrder(',
                'currentOrder = null',
                'handleOrderState(',
                'getInventoryLocation('
            ]
            
            for element in state_elements:
                self.assertIn(element, content, f"robot.js should contain state management: {element}")
                
    def test_robot_path_visualization(self):
        """Test that robot path visualization is implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for path visualization
            path_elements = [
                'path: []',
                'drawPath(',
                'drawPathArrows(',
                'drawArrow(',
                'setLineDash([5, 5])',
                'arrowSize = this.pathArrowSize',
                'Math.cos(angle)',
                'Math.sin(angle)'
            ]
            
            for element in path_elements:
                self.assertIn(element, content, f"robot.js should contain path visualization: {element}")
                
    def test_robot_direction_indicators(self):
        """Test that robot direction indicators are implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for direction indicators
            direction_elements = [
                'direction: 0',
                'drawDirectionIndicator(',
                'Math.atan2(dy, dx)',
                'Math.cos(angle)',
                'Math.sin(angle)',
                'arrowheadAngle = Math.PI / 6',
                'arrowheadLength = 6'
            ]
            
            for element in direction_elements:
                self.assertIn(element, content, f"robot.js should contain direction indicators: {element}")
                
    def test_robot_integration_methods(self):
        """Test that robot integration methods are implemented."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for integration methods
            integration_elements = [
                'getRobotPosition(',
                'updateFromData(',
                'simulateMovement(',
                'warehouseVisualizer',
                'this.warehouse = warehouseVisualizer',
                'this.ctx = warehouseVisualizer.ctx',
                'this.canvas = warehouseVisualizer.canvas'
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"robot.js should contain integration method: {element}")
                
    def test_main_js_robot_integration(self):
        """Test that main.js properly integrates robot visualizer."""
        main_js = os.path.join(self.js_dir, 'main.js')
        
        with open(main_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for robot visualizer integration
            integration_elements = [
                'new RobotVisualizer(this.warehouse)',
                'this.robot.render(',
                'robot_update',
                'this.robot.update('
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"main.js should contain robot integration: {element}")
                
    def test_html_template_robot_references(self):
        """Test that HTML template properly references robot.js."""
        html_file = os.path.join(self.web_interface_dir, 'templates', 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for robot.js reference
            self.assertIn('<script src="/static/js/robot.js"></script>', content, 
                         "HTML template should reference robot.js")
                         
    def test_robot_icon_and_visualization(self):
        """Test that robot icon and visualization elements are properly defined."""
        robot_js = os.path.join(self.js_dir, 'robot.js')
        
        with open(robot_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for robot icon and visualization
            icon_elements = [
                '🤖',
                'drawRobotIcon(',
                'drawStateIndicator(',
                'arc(x, y, this.robotRadius',
                'strokeStyle = \'#FFFFFF\'',
                'lineWidth = 2'
            ]
            
            for element in icon_elements:
                self.assertIn(element, content, f"robot.js should contain icon/visualization: {element}")


def test_robot_visualization():
    """Run the robot visualization tests."""
    print("🤖 Testing Robot Visualization")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRobotVisualization)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ❌ Failures: {len(result.failures)}")
    print(f"  ⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All robot visualization tests passed!")
        return True
    else:
        print("\n❌ Some robot visualization tests failed.")
        return False


if __name__ == "__main__":
    success = test_robot_visualization()
    sys.exit(0 if success else 1) 