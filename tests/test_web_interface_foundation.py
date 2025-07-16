"""
Test Web Interface Foundation

This test verifies that the web interface foundation files
are properly created and accessible.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestWebInterfaceFoundation(unittest.TestCase):
    """Test web interface foundation files."""
    
    def setUp(self):
        """Set up test environment."""
        self.web_interface_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface')
        self.static_dir = os.path.join(self.web_interface_dir, 'static')
        self.templates_dir = os.path.join(self.web_interface_dir, 'templates')
        
    def test_js_files_exist(self):
        """Test that JavaScript files exist."""
        # Current state: Only main.js exists, but HTML template expects multiple files
        js_files = [
            'main.js'
            # TODO: These files need to be created in future tasks:
            # 'warehouse.js',
            # 'robot.js', 
            # 'orders.js',
            # 'kpis.js',
            # 'controls.js'
        ]
        
        # Debug: Check what files actually exist
        js_dir = os.path.join(self.static_dir, 'js')
        print(f"\n🔍 DEBUG: Checking JavaScript files in {js_dir}")
        print(f"📁 Directory exists: {os.path.exists(js_dir)}")
        
        if os.path.exists(js_dir):
            actual_files = os.listdir(js_dir)
            print(f"📋 Actual files in js directory: {actual_files}")
        else:
            print("❌ JS directory does not exist!")
            actual_files = []
        
        print(f"🎯 Expected files (current phase): {js_files}")
        print(f"📝 NOTE: HTML template references additional files that will be created in future tasks:")
        print(f"   - warehouse.js (for warehouse grid visualization)")
        print(f"   - robot.js (for robot movement and rendering)")
        print(f"   - orders.js (for order management and display)")
        print(f"   - kpis.js (for real-time KPI updates)")
        print(f"   - controls.js (for simulation controls)")
        
        missing_files = [f for f in js_files if f not in actual_files]
        if missing_files:
            print(f"🔍 Missing files: {missing_files}")
        
        for js_file in js_files:
            file_path = os.path.join(self.static_dir, 'js', js_file)
            exists = os.path.exists(file_path)
            print(f"  📄 {js_file}: {'✅ EXISTS' if exists else '❌ MISSING'} at {file_path}")
            
            if exists:
                # Check file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"    📏 Size: {len(content)} characters")
                        self.assertGreater(len(content), 0, f"{js_file} should not be empty")
                except Exception as e:
                    print(f"    ❌ Error reading file: {e}")
                    raise
            else:
                self.assertTrue(False, f"{js_file} should exist at {file_path}")
                
    def test_css_files_exist(self):
        """Test that CSS files exist."""
        css_files = [
            'main.css',
            'warehouse.css', 
            'components.css'
        ]
        
        # Debug: Check what files actually exist
        css_dir = os.path.join(self.static_dir, 'css')
        print(f"\n🔍 DEBUG: Checking CSS files in {css_dir}")
        print(f"📁 Directory exists: {os.path.exists(css_dir)}")
        
        if os.path.exists(css_dir):
            actual_files = os.listdir(css_dir)
            print(f"📋 Actual files in css directory: {actual_files}")
        else:
            print("❌ CSS directory does not exist!")
            actual_files = []
        
        print(f"🎯 Expected files: {css_files}")
        print(f"🔍 Missing files: {[f for f in css_files if f not in actual_files]}")
        
        for css_file in css_files:
            file_path = os.path.join(self.static_dir, 'css', css_file)
            exists = os.path.exists(file_path)
            print(f"  📄 {css_file}: {'✅ EXISTS' if exists else '❌ MISSING'} at {file_path}")
            
            if exists:
                # Check file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"    📏 Size: {len(content)} characters")
                        self.assertGreater(len(content), 0, f"{css_file} should not be empty")
                except Exception as e:
                    print(f"    ❌ Error reading file: {e}")
                    raise
            else:
                self.assertTrue(False, f"{css_file} should exist at {file_path}")
                
    def test_html_template_exists(self):
        """Test that the main HTML template exists."""
        html_file = os.path.join(self.templates_dir, 'index.html')
        
        print(f"\n🔍 DEBUG: Checking HTML template")
        print(f"📁 Templates directory: {self.templates_dir}")
        print(f"📁 Directory exists: {os.path.exists(self.templates_dir)}")
        print(f"📄 HTML file path: {html_file}")
        print(f"📄 File exists: {os.path.exists(html_file)}")
        
        if os.path.exists(html_file):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"📏 HTML file size: {len(content)} characters")
                    self.assertIn('Roibot - Warehouse Visualization', content)
                    self.assertIn('warehouse-canvas', content)
                    self.assertIn('kpi-sidebar', content)
                    print("✅ HTML content validation passed")
            except Exception as e:
                print(f"❌ Error reading HTML file: {e}")
                raise
        else:
            self.assertTrue(False, f"index.html should exist at {html_file}")
            
    def test_directory_structure(self):
        """Test that the web interface directory structure exists."""
        print(f"\n🔍 DEBUG: Checking directory structure")
        print(f"📁 Web interface dir: {self.web_interface_dir}")
        print(f"📁 Static dir: {self.static_dir}")
        print(f"📁 Templates dir: {self.templates_dir}")
        
        # Check main directories
        web_interface_exists = os.path.exists(self.web_interface_dir)
        static_exists = os.path.exists(self.static_dir)
        templates_exists = os.path.exists(self.templates_dir)
        
        print(f"📁 web_interface exists: {web_interface_exists}")
        print(f"📁 static exists: {static_exists}")
        print(f"📁 templates exists: {templates_exists}")
        
        self.assertTrue(web_interface_exists, "web_interface directory should exist")
        self.assertTrue(static_exists, "static directory should exist")
        self.assertTrue(templates_exists, "templates directory should exist")
        
        # Check CSS directories
        css_dir = os.path.join(self.static_dir, 'css')
        css_exists = os.path.exists(css_dir)
        print(f"📁 css directory exists: {css_exists}")
        self.assertTrue(css_exists, "css directory should exist")
        
        # Check JS directories
        js_dir = os.path.join(self.static_dir, 'js')
        js_exists = os.path.exists(js_dir)
        print(f"📁 js directory exists: {js_exists}")
        self.assertTrue(js_exists, "js directory should exist")
                
    def test_html_structure(self):
        """Test that HTML has proper structure."""
        html_file = os.path.join(self.templates_dir, 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required elements
            required_elements = [
                '<!DOCTYPE html>',
                '<html lang="en">',
                '<head>',
                '<title>Roibot - Warehouse Visualization</title>',
                '<body>',
                '<canvas id="warehouse-canvas"',
                '<aside class="kpi-sidebar">',
                '<footer class="control-panel">',
                '</body>',
                '</html>'
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"HTML should contain {element}")
                
    def test_css_structure(self):
        """Test that CSS has proper structure."""
        main_css = os.path.join(self.static_dir, 'css', 'main.css')
        
        with open(main_css, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required CSS classes
            required_classes = [
                '.app-container',
                '.app-header',
                '.main-content',
                '.kpi-sidebar',
                '.warehouse-section',
                '.control-panel'
            ]
            
            for css_class in required_classes:
                self.assertIn(css_class, content, f"CSS should contain {css_class}")
                
    def test_js_structure(self):
        """Test that JavaScript has proper structure."""
        main_js = os.path.join(self.static_dir, 'js', 'main.js')
        
        with open(main_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required JavaScript elements
            required_elements = [
                'class RoibotApp',
                'constructor()',
                'async init()',
                'DOMContentLoaded',
                'WebSocket'
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"JavaScript should contain {element}")
                
    def test_file_permissions(self):
        """Test that files are readable."""
        files_to_test = [
            os.path.join(self.templates_dir, 'index.html'),
            os.path.join(self.static_dir, 'css', 'main.css'),
            os.path.join(self.static_dir, 'js', 'main.js')
        ]
        
        for file_path in files_to_test:
            self.assertTrue(os.access(file_path, os.R_OK), f"{file_path} should be readable")
            
    def test_directory_permissions(self):
        """Test that directories are accessible."""
        dirs_to_test = [
            self.web_interface_dir,
            self.static_dir,
            self.templates_dir,
            os.path.join(self.static_dir, 'css'),
            os.path.join(self.static_dir, 'js')
        ]
        
        for dir_path in dirs_to_test:
            self.assertTrue(os.access(dir_path, os.R_OK), f"{dir_path} should be readable")
            self.assertTrue(os.access(dir_path, os.X_OK), f"{dir_path} should be executable")


def test_web_interface_foundation():
    """Run the web interface foundation tests."""
    print("🚀 Testing Web Interface Foundation")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebInterfaceFoundation)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ❌ Failures: {len(result.failures)}")
    print(f"  ⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All web interface foundation tests passed!")
        return True
    else:
        print("\n❌ Some web interface foundation tests failed.")
        return False


if __name__ == "__main__":
    success = test_web_interface_foundation()
    sys.exit(0 if success else 1) 