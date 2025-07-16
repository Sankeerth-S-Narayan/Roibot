import unittest
import time
from unittest.mock import Mock, patch
from entities.order_status_tracker import OrderStatusTracker, OrderStatusEvent, OrderCompletionMetrics
from entities.robot_order_assigner import RobotOrderAssigner
from entities.order_queue_manager import OrderQueueManager
from entities.robot_orders import Order, OrderStatus
from entities.robot_state import RobotState

class TestOrderStatusTracker(unittest.TestCase):
    """Test cases for OrderStatusTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.robot_assigner = Mock(spec=RobotOrderAssigner)
        self.queue_manager = Mock(spec=OrderQueueManager)
        
        # Create status tracker
        self.tracker = OrderStatusTracker(self.robot_assigner, self.queue_manager)
        
        # Create test orders
        self.order1 = Order("ORD_001", ["ITEM_A1", "ITEM_B2"], [(1, 1), (2, 2)])
        self.order2 = Order("ORD_002", ["ITEM_C3"], [(3, 3)])
        self.order3 = Order("ORD_003", ["ITEM_D4", "ITEM_E5", "ITEM_F6"], [(4, 4), (5, 5), (6, 6)])
    
    def test_initialization(self):
        """Test OrderStatusTracker initialization."""
        self.assertEqual(len(self.tracker.active_orders), 0)
        self.assertEqual(len(self.tracker.completed_orders), 0)
        self.assertEqual(len(self.tracker.failed_orders), 0)
        self.assertEqual(self.tracker.total_orders_tracked, 0)
        self.assertEqual(self.tracker.total_completions, 0)
        self.assertEqual(self.tracker.total_failures, 0)
        self.assertEqual(self.tracker.order_timeout_seconds, 300.0)
        self.assertEqual(self.tracker.efficiency_threshold, 0.8)
    
    def test_track_order_success(self):
        """Test successful order tracking."""
        result = self.tracker.track_order(self.order1)
        
        self.assertTrue(result)
        self.assertIn(self.order1.order_id, self.tracker.active_orders)
        self.assertEqual(self.tracker.active_orders[self.order1.order_id], self.order1)
        self.assertEqual(self.tracker.total_orders_tracked, 1)
        self.assertIn(self.order1.order_id, self.tracker.completion_metrics)
    
    def test_track_order_already_tracked(self):
        """Test tracking order that's already being tracked."""
        self.tracker.track_order(self.order1)
        
        result = self.tracker.track_order(self.order1)
        
        self.assertFalse(result)
        self.assertEqual(self.tracker.total_orders_tracked, 1)
    
    def test_update_order_status_success(self):
        """Test successful order status update."""
        self.tracker.track_order(self.order1)
        
        result = self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.IN_PROGRESS)
        self.assertEqual(self.order1.assigned_robot_id, "ROBOT_001")
        self.assertIsNotNone(self.order1.timestamp_assigned)
    
    def test_update_order_status_not_found(self):
        """Test updating status for order not being tracked."""
        result = self.tracker.update_order_status(
            "NONEXISTENT_ORDER", 
            OrderStatus.IN_PROGRESS
        )
        
        self.assertFalse(result)
    
    def test_mark_item_collected_success(self):
        """Test successful item collection marking."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        result = self.tracker.mark_item_collected(
            self.order1.order_id, 
            "ITEM_A1", 
            "ROBOT_001", 
            time.time()
        )
        
        self.assertTrue(result)
        self.assertIn("ITEM_A1", self.order1.items_collected)
        self.assertEqual(len(self.order1.items_collected), 1)
        
        metrics = self.tracker.get_completion_metrics(self.order1.order_id)
        self.assertEqual(metrics.items_collected, 1)
    
    def test_mark_item_collected_order_not_found(self):
        """Test marking item collected for order not being tracked."""
        result = self.tracker.mark_item_collected(
            "NONEXISTENT_ORDER", 
            "ITEM_A1", 
            "ROBOT_001", 
            time.time()
        )
        
        self.assertFalse(result)
    
    def test_mark_item_collected_already_collected(self):
        """Test marking item that's already collected."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Mark item as collected
        self.tracker.mark_item_collected(
            self.order1.order_id, 
            "ITEM_A1", 
            "ROBOT_001", 
            time.time()
        )
        
        # Try to mark same item again
        result = self.tracker.mark_item_collected(
            self.order1.order_id, 
            "ITEM_A1", 
            "ROBOT_001", 
            time.time()
        )
        
        self.assertFalse(result)
    
    def test_order_completion_automatic(self):
        """Test automatic order completion when all items collected."""
        self.tracker.track_order(self.order2)  # Single item order
        self.tracker.update_order_status(
            self.order2.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Mark the single item as collected
        self.tracker.mark_item_collected(
            self.order2.order_id, 
            "ITEM_C3", 
            "ROBOT_001", 
            time.time()
        )
        
        # Order should be automatically completed
        self.assertEqual(self.order2.status, OrderStatus.COMPLETED)
        self.assertIn(self.order2.order_id, self.tracker.completed_orders)
        self.assertNotIn(self.order2.order_id, self.tracker.active_orders)
        self.assertEqual(self.tracker.total_completions, 1)
    
    def test_order_completion_manual(self):
        """Test manual order completion."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Mark one item as collected
        self.tracker.mark_item_collected(
            self.order1.order_id, 
            "ITEM_A1", 
            "ROBOT_001", 
            time.time()
        )
        
        # Manually complete order
        result = self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.COMPLETED)
        self.assertIn(self.order1.order_id, self.tracker.completed_orders)
        self.assertEqual(self.tracker.total_completions, 1)
    
    def test_order_failure(self):
        """Test order failure handling."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Mark order as failed
        result = self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.FAILED
        )
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.FAILED)
        self.assertIn(self.order1.order_id, self.tracker.failed_orders)
        self.assertNotIn(self.order1.order_id, self.tracker.active_orders)
        self.assertEqual(self.tracker.total_failures, 1)
    
    def test_completion_metrics_calculation(self):
        """Test completion metrics calculation."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Simulate some time passing
        time.sleep(0.1)
        
        # Complete order
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        metrics = self.tracker.get_completion_metrics(self.order1.order_id)
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.completion_time, 0)
        self.assertGreater(metrics.total_distance, 0)
        self.assertGreaterEqual(metrics.efficiency_score, 0)
        self.assertLessEqual(metrics.efficiency_score, 1)
    
    def test_efficiency_score_calculation(self):
        """Test efficiency score calculation."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Complete order quickly (should have high efficiency)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        metrics = self.tracker.get_completion_metrics(self.order1.order_id)
        self.assertGreater(metrics.efficiency_score, 0)
    
    def test_get_order_status(self):
        """Test getting order status."""
        self.tracker.track_order(self.order1)
        
        # Test active order
        status = self.tracker.get_order_status(self.order1.order_id)
        self.assertEqual(status, OrderStatus.PENDING)
        
        # Test completed order
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        status = self.tracker.get_order_status(self.order1.order_id)
        self.assertEqual(status, OrderStatus.COMPLETED)
        
        # Test non-existent order
        status = self.tracker.get_order_status("NONEXISTENT")
        self.assertIsNone(status)
    
    def test_get_tracking_statistics(self):
        """Test getting tracking statistics."""
        # Add some activity
        self.tracker.track_order(self.order1)
        self.tracker.track_order(self.order2)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        self.tracker.update_order_status(
            self.order2.order_id, 
            OrderStatus.FAILED
        )
        
        stats = self.tracker.get_tracking_statistics()
        
        self.assertEqual(stats['total_orders_tracked'], 2)
        self.assertEqual(stats['active_orders'], 0)
        self.assertEqual(stats['completed_orders'], 1)
        self.assertEqual(stats['failed_orders'], 1)
        self.assertEqual(stats['total_completions'], 1)
        self.assertEqual(stats['total_failures'], 1)
        self.assertIn('completion_rate', stats)
        self.assertIn('failure_rate', stats)
    
    def test_get_active_orders(self):
        """Test getting active orders."""
        self.tracker.track_order(self.order1)
        self.tracker.track_order(self.order2)
        
        active_orders = self.tracker.get_active_orders()
        self.assertEqual(len(active_orders), 2)
        self.assertIn(self.order1, active_orders)
        self.assertIn(self.order2, active_orders)
    
    def test_get_completed_orders(self):
        """Test getting completed orders."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        completed_orders = self.tracker.get_completed_orders()
        self.assertEqual(len(completed_orders), 1)
        self.assertIn(self.order1, completed_orders)
    
    def test_get_failed_orders(self):
        """Test getting failed orders."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.FAILED
        )
        
        failed_orders = self.tracker.get_failed_orders()
        self.assertEqual(len(failed_orders), 1)
        self.assertIn(self.order1, failed_orders)
    
    def test_clear_completed_orders(self):
        """Test clearing completed orders."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        self.assertEqual(len(self.tracker.completed_orders), 1)
        
        self.tracker.clear_completed_orders()
        
        self.assertEqual(len(self.tracker.completed_orders), 0)
    
    def test_clear_failed_orders(self):
        """Test clearing failed orders."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.FAILED
        )
        
        self.assertEqual(len(self.tracker.failed_orders), 1)
        
        self.tracker.clear_failed_orders()
        
        self.assertEqual(len(self.tracker.failed_orders), 0)
    
    def test_reset_statistics(self):
        """Test resetting statistics."""
        # Add some activity
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        self.assertGreater(self.tracker.total_orders_tracked, 0)
        self.assertGreater(self.tracker.total_completions, 0)
        
        self.tracker.reset_statistics()
        
        self.assertEqual(self.tracker.total_orders_tracked, 0)
        self.assertEqual(self.tracker.total_completions, 0)
        self.assertEqual(self.tracker.total_failures, 0)
        self.assertEqual(len(self.tracker.completion_metrics), 0)
    
    def test_status_callback(self):
        """Test status callback functionality."""
        callback_called = False
        callback_data = None
        
        def status_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        self.tracker.add_status_callback(status_callback)
        
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS
        )
        
        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_data)
        self.assertIn('event_type', callback_data)
        self.assertIn('order_id', callback_data)
    
    def test_completion_callback(self):
        """Test completion callback functionality."""
        callback_called = False
        callback_data = None
        
        def completion_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        self.tracker.add_completion_callback(completion_callback)
        
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_data)
        self.assertIn('event_type', callback_data)
        self.assertIn('order_id', callback_data)
    
    def test_get_debug_info(self):
        """Test getting debug information."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS
        )
        
        debug_info = self.tracker.get_debug_info()
        
        self.assertIn('tracking_statistics', debug_info)
        self.assertIn('active_orders', debug_info)
        self.assertIn('completion_metrics', debug_info)
        self.assertIn('callbacks', debug_info)
        
        self.assertIsInstance(debug_info['tracking_statistics'], dict)
        self.assertIsInstance(debug_info['active_orders'], dict)
        self.assertIsInstance(debug_info['completion_metrics'], dict)
        self.assertIsInstance(debug_info['callbacks'], dict)
    
    def test_order_removal_from_queue(self):
        """Test that orders are removed from queue upon completion."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.COMPLETED
        )
        
        # Verify queue manager was called to remove order
        self.queue_manager.remove_order.assert_called_with(self.order1)
    
    def test_order_removal_from_queue_on_failure(self):
        """Test that orders are removed from queue upon failure."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.FAILED
        )
        
        # Verify queue manager was called to remove order
        self.queue_manager.remove_order.assert_called_with(self.order1)
    
    def test_multiple_item_collection(self):
        """Test collection of multiple items in an order."""
        self.tracker.track_order(self.order3)  # 3 items
        self.tracker.update_order_status(
            self.order3.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Collect first item
        self.tracker.mark_item_collected(
            self.order3.order_id, 
            "ITEM_D4", 
            "ROBOT_001", 
            time.time()
        )
        
        # Collect second item
        self.tracker.mark_item_collected(
            self.order3.order_id, 
            "ITEM_E5", 
            "ROBOT_001", 
            time.time()
        )
        
        # Collect third item (should complete order)
        self.tracker.mark_item_collected(
            self.order3.order_id, 
            "ITEM_F6", 
            "ROBOT_001", 
            time.time()
        )
        
        # Order should be completed
        self.assertEqual(self.order3.status, OrderStatus.COMPLETED)
        self.assertEqual(len(self.order3.items_collected), 3)
        self.assertEqual(self.tracker.total_completions, 1)
    
    def test_error_handling_invalid_order_id(self):
        """Test error handling for invalid order ID."""
        result = self.tracker.update_order_status(
            "INVALID_ORDER", 
            OrderStatus.IN_PROGRESS
        )
        
        self.assertFalse(result)
    
    def test_error_handling_invalid_item_id(self):
        """Test error handling for invalid item ID."""
        self.tracker.track_order(self.order1)
        self.tracker.update_order_status(
            self.order1.order_id, 
            OrderStatus.IN_PROGRESS, 
            robot_id="ROBOT_001"
        )
        
        # Try to mark non-existent item as collected
        result = self.tracker.mark_item_collected(
            self.order1.order_id, 
            "NONEXISTENT_ITEM", 
            "ROBOT_001", 
            time.time()
        )
        
        self.assertFalse(result)
    
    def test_average_metrics_calculation(self):
        """Test average metrics calculation."""
        # Complete multiple orders
        for i, order in enumerate([self.order1, self.order2, self.order3]):
            self.tracker.track_order(order)
            self.tracker.update_order_status(
                order.order_id,
                OrderStatus.IN_PROGRESS,
                robot_id="ROBOT_001"
            )
            # Add small delay to simulate time passing
            time.sleep(0.01)
            self.tracker.update_order_status(
                order.order_id,
                OrderStatus.COMPLETED
            )

        stats = self.tracker.get_tracking_statistics()

        self.assertEqual(stats['total_completions'], 3)
        self.assertGreater(stats['average_completion_time'], 0)
        self.assertGreater(stats['average_efficiency_score'], 0)
        self.assertLessEqual(stats['average_efficiency_score'], 1)


if __name__ == '__main__':
    unittest.main() 