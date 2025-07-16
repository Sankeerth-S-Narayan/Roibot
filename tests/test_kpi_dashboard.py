"""
Test KPI Dashboard

This test verifies that the KPI dashboard system
properly handles real-time KPI calculations and updates.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestKPIDashboard(unittest.TestCase):
    """Test KPI dashboard functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.web_interface_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface')
        self.static_dir = os.path.join(self.web_interface_dir, 'static')
        self.js_dir = os.path.join(self.static_dir, 'js')
        
    def test_kpis_js_exists(self):
        """Test that kpis.js file exists."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        print(f"\n🔍 DEBUG: Checking kpis.js")
        print(f"📄 File path: {kpis_js}")
        print(f"📄 File exists: {os.path.exists(kpis_js)}")
        
        self.assertTrue(os.path.exists(kpis_js), "kpis.js should exist")
        
        if os.path.exists(kpis_js):
            with open(kpis_js, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📏 File size: {len(content)} characters")
                self.assertGreater(len(content), 0, "kpis.js should not be empty")
                
    def test_kpis_js_structure(self):
        """Test that kpis.js has proper structure."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required JavaScript elements
            required_elements = [
                'class KPIDashboard',
                'constructor(warehouseVisualizer, robotVisualizer, orderVisualizer)',
                'kpis = {',
                'ordersPerHour: 0',
                'robotUtilization: 0',
                'completionRate: 0',
                'averageOrderTime: 0',
                'queueLength: 0',
                'updateIntervals = {',
                'thresholds = {',
                'historicalData = {',
                'updateOrdersPerHour(',
                'updateRobotUtilization(',
                'updateCompletionRate(',
                'updateAverageOrderTime(',
                'updateQueueLength(',
                'updateSimulationTime(',
                'updateKPIDisplay(',
                'checkThreshold(',
                'getKPIData(',
                'updateFromData(',
                'updateKPIsFromAnalytics(',
                'updateDashboard(',
                'render(',
                'exportKPIData(',
                'reset('
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"kpis.js should contain {element}")
                
    def test_kpi_configuration(self):
        """Test that KPI configuration is properly defined."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for KPI configuration
            kpi_elements = [
                'ordersPerHour: 0',
                'robotUtilization: 0',
                'completionRate: 0',
                'averageOrderTime: 0',
                'queueLength: 0',
                'totalOrders: 0',
                'completedOrders: 0',
                'simulationTime: 0'
            ]
            
            for element in kpi_elements:
                self.assertIn(element, content, f"kpis.js should contain KPI configuration: {element}")
                
    def test_update_intervals(self):
        """Test that update intervals are properly defined."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for update intervals
            interval_elements = [
                'ordersPerHour: 5000',
                'robotUtilization: 2000',
                'completionRate: 3000',
                'averageOrderTime: 4000',
                'queueLength: 1000',
                'simulationTime: 1000'
            ]
            
            for element in interval_elements:
                self.assertIn(element, content, f"kpis.js should contain update interval: {element}")
                
    def test_threshold_configuration(self):
        """Test that threshold configuration is properly defined."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for threshold configuration
            threshold_elements = [
                'ordersPerHour: { low: 10, high: 50 }',
                'robotUtilization: { low: 30, high: 80 }',
                'completionRate: { low: 70, high: 95 }',
                'queueLength: { low: 5, high: 20 }'
            ]
            
            for element in threshold_elements:
                self.assertIn(element, content, f"kpis.js should contain threshold configuration: {element}")
                
    def test_kpi_update_methods(self):
        """Test that KPI update methods are implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for KPI update methods
            update_elements = [
                'updateOrdersPerHour(',
                'updateRobotUtilization(',
                'updateCompletionRate(',
                'updateAverageOrderTime(',
                'updateQueueLength(',
                'updateSimulationTime(',
                'startKPIUpdates(',
                'setInterval('
            ]
            
            for element in update_elements:
                self.assertIn(element, content, f"kpis.js should contain update method: {element}")
                
    def test_kpi_display_methods(self):
        """Test that KPI display methods are implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for display methods
            display_elements = [
                'updateKPIDisplay(',
                'updateDashboard(',
                'getElementById(',
                'textContent = value',
                'classList.add(\'kpi-updated\')',
                'classList.remove(\'kpi-updated\')',
                'classList.add(\'kpi-low\')',
                'classList.add(\'kpi-high\')',
                'classList.add(\'kpi-normal\')'
            ]
            
            for element in display_elements:
                self.assertIn(element, content, f"kpis.js should contain display method: {element}")
                
    def test_threshold_monitoring(self):
        """Test that threshold monitoring is implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for threshold monitoring
            threshold_elements = [
                'checkThreshold(',
                'threshold.low',
                'threshold.high',
                'value <= threshold.low',
                'value >= threshold.high',
                'kpi-low',
                'kpi-high',
                'kpi-normal'
            ]
            
            for element in threshold_elements:
                self.assertIn(element, content, f"kpis.js should contain threshold monitoring: {element}")
                
    def test_historical_data_management(self):
        """Test that historical data management is implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for historical data management
            historical_elements = [
                'historicalData = {',
                'ordersPerHour: []',
                'robotUtilization: []',
                'completionRate: []',
                'averageOrderTime: []',
                'push(',
                'shift(',
                'length > 10'
            ]
            
            for element in historical_elements:
                self.assertIn(element, content, f"kpis.js should contain historical data management: {element}")
                
    def test_analytics_integration(self):
        """Test that analytics integration is implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for analytics integration
            analytics_elements = [
                'updateKPIsFromAnalytics(',
                'analyticsData.ordersPerHour',
                'analyticsData.robotUtilization',
                'analyticsData.completionRate',
                'analyticsData.averageOrderTime',
                'analyticsData.queueLength',
                'kpi_update',
                'simulation_state'
            ]
            
            for element in analytics_elements:
                self.assertIn(element, content, f"kpis.js should contain analytics integration: {element}")
                
    def test_main_js_kpi_integration(self):
        """Test that main.js properly integrates KPI dashboard."""
        main_js = os.path.join(self.js_dir, 'main.js')
        
        with open(main_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for KPI dashboard integration
            integration_elements = [
                'new KPIDashboard(this.warehouse, this.robot, this.orders)',
                'this.kpis.render(',
                'kpi_update',
                'this.kpis.update('
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"main.js should contain KPI integration: {element}")
                
    def test_html_template_kpi_references(self):
        """Test that HTML template properly references kpis.js."""
        html_file = os.path.join(self.web_interface_dir, 'templates', 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for kpis.js reference
            self.assertIn('<script src="/static/js/kpis.js"></script>', content, 
                         "HTML template should reference kpis.js")
                         
    def test_kpi_data_export(self):
        """Test that KPI data export functionality is implemented."""
        kpis_js = os.path.join(self.js_dir, 'kpis.js')
        
        with open(kpis_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for data export
            export_elements = [
                'exportKPIData(',
                'timestamp: Date.now()',
                'kpis: this.kpis',
                'historicalData: this.historicalData',
                'thresholds: this.thresholds',
                'getKPIData(',
                'reset('
            ]
            
            for element in export_elements:
                self.assertIn(element, content, f"kpis.js should contain data export: {element}")


def test_kpi_dashboard():
    """Run the KPI dashboard tests."""
    print("📊 Testing KPI Dashboard")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKPIDashboard)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ❌ Failures: {len(result.failures)}")
    print(f"  ⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All KPI dashboard tests passed!")
        return True
    else:
        print("\n❌ Some KPI dashboard tests failed.")
        return False


if __name__ == "__main__":
    success = test_kpi_dashboard()
    sys.exit(0 if success else 1) 