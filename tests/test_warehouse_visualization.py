"""
Test Warehouse Visualization

This test verifies that the warehouse visualization system
properly renders the 25x20 grid, layout, and interactive features.
"""

import os
import sys
import unittest
import tempfile
import subprocess
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestWarehouseVisualization(unittest.TestCase):
    """Test warehouse visualization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.web_interface_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface')
        self.static_dir = os.path.join(self.web_interface_dir, 'static')
        self.js_dir = os.path.join(self.static_dir, 'js')
        
    def test_warehouse_js_exists(self):
        """Test that warehouse.js file exists."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        print(f"\n🔍 DEBUG: Checking warehouse.js")
        print(f"📄 File path: {warehouse_js}")
        print(f"📄 File exists: {os.path.exists(warehouse_js)}")
        
        self.assertTrue(os.path.exists(warehouse_js), "warehouse.js should exist")
        
        if os.path.exists(warehouse_js):
            with open(warehouse_js, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📏 File size: {len(content)} characters")
                self.assertGreater(len(content), 0, "warehouse.js should not be empty")
                
    def test_warehouse_js_structure(self):
        """Test that warehouse.js has proper structure."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required JavaScript elements
            required_elements = [
                'class WarehouseVisualizer',
                'constructor(canvasId)',
                'gridWidth = 25',
                'gridHeight = 20',
                'cellSize = 24',
                'generateSnakePath()',
                'draw()',
                'drawGrid()',
                'drawLayout()',
                'drawInventoryLocations()',
                'drawSnakePath()',
                'drawCoordinates()',
                'getGridCoordinates(',
                'getPixelCoordinates(',
                'isValidPosition(',
                'handleClick(',
                'initEventListeners()'
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"warehouse.js should contain {element}")
                
    def test_warehouse_layout_configuration(self):
        """Test that warehouse layout configuration is properly defined."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for layout configuration
            layout_elements = [
                'aisles: [',
                'racks: [',
                'packoutZone: {',
                'inventoryLocations: [',
                'x: 5, y: 0, width: 1, height: 20',  # Aisle 1
                'x: 15, y: 0, width: 1, height: 20', # Aisle 2
                'x: 0, y: 0, width: 5, height: 20',  # Rack 1
                'x: 6, y: 0, width: 9, height: 20',  # Rack 2
                'x: 16, y: 0, width: 9, height: 20', # Rack 3
                'x: 20, y: 15, width: 5, height: 5'  # Packout zone
            ]
            
            for element in layout_elements:
                self.assertIn(element, content, f"warehouse.js should contain layout configuration: {element}")
                
    def test_inventory_locations(self):
        """Test that inventory locations are properly defined."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for inventory location types (A-R)
            inventory_types = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
            
            for inv_type in inventory_types:
                self.assertIn(f"type: '{inv_type}'", content, f"warehouse.js should contain inventory type {inv_type}")
                
    def test_color_scheme(self):
        """Test that color scheme is properly defined."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for color scheme (light theme)
            colors = [
                'background: \'#FFFFFF\'',
                'gridLines: \'#E0E0E0\'',
                'aisles: \'#F5F5F5\'',
                'racks: \'#D3D3D3\'',
                'packoutZone: \'#E8F5E8\'',
                'inventory: \'#FFE0B2\'',
                'path: \'#2196F3\'',
                'boundary: \'#9E9E9E\''
            ]
            
            for color in colors:
                self.assertIn(color, content, f"warehouse.js should contain color: {color}")
                
    def test_coordinate_system(self):
        """Test that coordinate system is properly implemented."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for coordinate system implementation
            coord_elements = [
                'String.fromCharCode(65 + x)',  # Column labels A-Z
                'drawCoordinates()',
                'getGridCoordinates(',
                'getPixelCoordinates(',
                'updateGridCoordinates('
            ]
            
            for element in coord_elements:
                self.assertIn(element, content, f"warehouse.js should contain coordinate system: {element}")
                
    def test_snake_path_generation(self):
        """Test that snake path generation is implemented."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for snake path implementation
            snake_elements = [
                'generateSnakePath()',
                'snakePath = this.generateSnakePath()',
                'drawSnakePath()',
                'y % 2 === 0',
                'Left to right',
                'Right to left'
            ]
            
            for element in snake_elements:
                self.assertIn(element, content, f"warehouse.js should contain snake path: {element}")
                
    def test_event_handling(self):
        """Test that event handling is properly implemented."""
        warehouse_js = os.path.join(self.js_dir, 'warehouse.js')
        
        with open(warehouse_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for event handling
            event_elements = [
                'handleClick(',
                'initEventListeners()',
                'addEventListener(\'click\'',
                'getBoundingClientRect()',
                'clientX - rect.left',
                'clientY - rect.top'
            ]
            
            for element in event_elements:
                self.assertIn(element, content, f"warehouse.js should contain event handling: {element}")
                
    def test_main_js_integration(self):
        """Test that main.js properly integrates warehouse visualizer."""
        main_js = os.path.join(self.js_dir, 'main.js')
        
        with open(main_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for warehouse visualizer integration
            integration_elements = [
                'new WarehouseVisualizer(\'warehouse-canvas\')',
                'this.warehouse.initEventListeners()',
                'this.warehouse.render(',
                'warehouse_update'
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"main.js should contain warehouse integration: {element}")
                
    def test_html_template_references(self):
        """Test that HTML template properly references warehouse.js."""
        html_file = os.path.join(self.web_interface_dir, 'templates', 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for warehouse.js reference
            self.assertIn('<script src="/static/js/warehouse.js"></script>', content, 
                         "HTML template should reference warehouse.js")
                         
    def test_canvas_configuration(self):
        """Test that canvas is properly configured for warehouse visualization."""
        html_file = os.path.join(self.web_interface_dir, 'templates', 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for canvas configuration
            canvas_elements = [
                'id="warehouse-canvas"',
                'width="1200"',
                'height="800"'
            ]
            
            for element in canvas_elements:
                self.assertIn(element, content, f"HTML template should contain canvas configuration: {element}")


def test_warehouse_visualization():
    """Run the warehouse visualization tests."""
    print("🏭 Testing Warehouse Visualization")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWarehouseVisualization)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ❌ Failures: {len(result.failures)}")
    print(f"  ⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All warehouse visualization tests passed!")
        return True
    else:
        print("\n❌ Some warehouse visualization tests failed.")
        return False


if __name__ == "__main__":
    success = test_warehouse_visualization()
    sys.exit(0 if success else 1) 