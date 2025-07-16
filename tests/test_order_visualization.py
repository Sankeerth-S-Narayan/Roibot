"""
Test Order Visualization

This test verifies that the order visualization system
properly handles order status, queue management, and integration.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestOrderVisualization(unittest.TestCase):
    """Test order visualization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.web_interface_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_interface')
        self.static_dir = os.path.join(self.web_interface_dir, 'static')
        self.js_dir = os.path.join(self.static_dir, 'js')
        
    def test_orders_js_exists(self):
        """Test that orders.js file exists."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        print(f"\n🔍 DEBUG: Checking orders.js")
        print(f"📄 File path: {orders_js}")
        print(f"📄 File exists: {os.path.exists(orders_js)}")
        
        self.assertTrue(os.path.exists(orders_js), "orders.js should exist")
        
        if os.path.exists(orders_js):
            with open(orders_js, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📏 File size: {len(content)} characters")
                self.assertGreater(len(content), 0, "orders.js should not be empty")
                
    def test_orders_js_structure(self):
        """Test that orders.js has proper structure."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required JavaScript elements
            required_elements = [
                'class OrderVisualizer',
                'constructor(warehouseVisualizer)',
                'orderSize = 16',
                'orderRadius = this.orderSize / 2',
                'orderColors = {',
                'PENDING: \'#FF5722\'',
                'IN_PROGRESS: \'#FFC107\'',
                'COMPLETED: \'#4CAF50\'',
                'CANCELLED: \'#9E9E9E\'',
                'orderStatusIcons = {',
                'PENDING: \'⏳\'',
                'IN_PROGRESS: \'🔄\'',
                'COMPLETED: \'✅\'',
                'CANCELLED: \'❌\'',
                'createOrder(',
                'assignOrderToRobot(',
                'updateOrderProgress(',
                'completeOrder(',
                'cancelOrder(',
                'moveOrderTo(',
                'update(',
                'render(',
                'renderOrder(',
                'drawOrder(',
                'updateOrderQueueDisplay(',
                'getOrderStatistics(',
                'updateFromData(',
                'simulateOrders(',
                'clearOrders('
            ]
            
            for element in required_elements:
                self.assertIn(element, content, f"orders.js should contain {element}")
                
    def test_order_status_colors(self):
        """Test that order status colors are properly defined."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for order status colors
            status_colors = [
                'PENDING: \'#FF5722\'',    # Red
                'IN_PROGRESS: \'#FFC107\'', # Yellow
                'COMPLETED: \'#4CAF50\'',   # Green
                'CANCELLED: \'#9E9E9E\''    # Gray
            ]
            
            for color in status_colors:
                self.assertIn(color, content, f"orders.js should contain status color: {color}")
                
    def test_order_status_icons(self):
        """Test that order status icons are properly defined."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for order status icons
            status_icons = [
                'PENDING: \'⏳\'',
                'IN_PROGRESS: \'🔄\'',
                'COMPLETED: \'✅\'',
                'CANCELLED: \'❌\''
            ]
            
            for icon in status_icons:
                self.assertIn(icon, content, f"orders.js should contain status icon: {icon}")
                
    def test_order_management_methods(self):
        """Test that order management methods are implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for order management methods
            management_elements = [
                'createOrder(',
                'assignOrderToRobot(',
                'updateOrderProgress(',
                'completeOrder(',
                'cancelOrder(',
                'moveOrderTo(',
                'clearOrders(',
                'orders = []',
                'orderQueue = []',
                'completedOrders = []'
            ]
            
            for element in management_elements:
                self.assertIn(element, content, f"orders.js should contain management method: {element}")
                
    def test_order_rendering_methods(self):
        """Test that order rendering methods are implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for rendering methods
            rendering_elements = [
                'render()',
                'renderOrder(',
                'drawOrder(',
                'drawOrderLabel(',
                'drawProgressIndicator(',
                'getPixelCoordinates(',
                'arc(x, y, this.orderRadius',
                'fillText(icon, x, y)',
                'fillText(order.id, x, labelY)'
            ]
            
            for element in rendering_elements:
                self.assertIn(element, content, f"orders.js should contain rendering method: {element}")
                
    def test_order_animation_methods(self):
        """Test that order animation methods are implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for animation methods
            animation_elements = [
                'updateOrderMovement(',
                'movementProgress +=',
                'isMoving = false',
                'movementProgress = 0',
                'orderFadeDuration = 150',
                'orderUpdateInterval = 1000',
                'startOrderUpdates('
            ]
            
            for element in animation_elements:
                self.assertIn(element, content, f"orders.js should contain animation method: {element}")
                
    def test_order_queue_display(self):
        """Test that order queue display is implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for queue display
            queue_elements = [
                'updateOrderQueueDisplay(',
                'getElementById(\'order-queue\')',
                'queueElement.innerHTML',
                'queue-item',
                'order-id',
                'order-status',
                'slice(0, 5)',
                '+${this.orderQueue.length - 5} more'
            ]
            
            for element in queue_elements:
                self.assertIn(element, content, f"orders.js should contain queue display: {element}")
                
    def test_order_statistics(self):
        """Test that order statistics are implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for statistics
            stats_elements = [
                'getOrderStatistics(',
                'total = this.orders.length',
                'pending = this.orderQueue.length',
                'inProgress = this.orders.filter(',
                'completed = this.completedOrders.length',
                'cancelled = this.orders.filter(',
                'completionRate: total > 0 ? (completed / total) * 100 : 0'
            ]
            
            for element in stats_elements:
                self.assertIn(element, content, f"orders.js should contain statistics: {element}")
                
    def test_order_data_integration(self):
        """Test that order data integration is implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for data integration
            integration_elements = [
                'updateFromData(',
                'order_created',
                'order_assigned',
                'order_progress',
                'order_completed',
                'order_cancelled',
                'order_moved',
                'switch (data.type)'
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"orders.js should contain data integration: {element}")
                
    def test_main_js_order_integration(self):
        """Test that main.js properly integrates order visualizer."""
        main_js = os.path.join(self.js_dir, 'main.js')
        
        with open(main_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for order visualizer integration
            integration_elements = [
                'new OrderVisualizer(this.warehouse)',
                'this.orders.render(',
                'order_update',
                'this.orders.update('
            ]
            
            for element in integration_elements:
                self.assertIn(element, content, f"main.js should contain order integration: {element}")
                
    def test_html_template_order_references(self):
        """Test that HTML template properly references orders.js."""
        html_file = os.path.join(self.web_interface_dir, 'templates', 'index.html')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for orders.js reference
            self.assertIn('<script src="/static/js/orders.js"></script>', content, 
                         "HTML template should reference orders.js")
                         
    def test_order_progress_tracking(self):
        """Test that order progress tracking is implemented."""
        orders_js = os.path.join(self.js_dir, 'orders.js')
        
        with open(orders_js, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for progress tracking
            progress_elements = [
                'progress: 0',
                'updateOrderProgress(',
                'order.progress = Math.min(100, Math.max(0, progress))',
                'if (order.progress >= 100)',
                'drawProgressIndicator(',
                'fillRect(x - indicatorWidth / 2, indicatorY, (indicatorWidth * progress) / 100',
                'fillText(`${progress}%`, x, indicatorY + indicatorHeight + 8)'
            ]
            
            for element in progress_elements:
                self.assertIn(element, content, f"orders.js should contain progress tracking: {element}")


def test_order_visualization():
    """Run the order visualization tests."""
    print("📦 Testing Order Visualization")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrderVisualization)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  ✅ Tests run: {result.testsRun}")
    print(f"  ❌ Failures: {len(result.failures)}")
    print(f"  ⚠️  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 All order visualization tests passed!")
        return True
    else:
        print("\n❌ Some order visualization tests failed.")
        return False


if __name__ == "__main__":
    success = test_order_visualization()
    sys.exit(0 if success else 1) 