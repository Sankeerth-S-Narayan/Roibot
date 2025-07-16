"""
Comprehensive tests for OrderQueueManager class.

Tests FIFO queue management, order status tracking, queue statistics,
error handling, and integration with order system.

Author: Roibot Development Team
Version: 1.0
"""

import unittest
import time
from unittest.mock import Mock, patch

from entities.order_queue_manager import OrderQueueManager, QueueStatus, QueueStatistics
from entities.robot_orders import Order, OrderStatus


class TestOrderQueueManager(unittest.TestCase):
    """Test cases for OrderQueueManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue_manager = OrderQueueManager(max_queue_size=10)
        
        # Create test orders
        self.order1 = Order("ORD_001", ["ITEM_A1", "ITEM_B2"], [(1, 1), (2, 2)])
        self.order2 = Order("ORD_002", ["ITEM_C3"], [(3, 3)])
        self.order3 = Order("ORD_003", ["ITEM_D4", "ITEM_E5", "ITEM_F6"], [(4, 4), (5, 5), (6, 6)])
    
    def test_initialization(self):
        """Test OrderQueueManager initialization."""
        self.assertEqual(self.queue_manager.max_queue_size, 10)
        self.assertEqual(len(self.queue_manager.queue), 0)
        self.assertEqual(len(self.queue_manager.completed_orders), 0)
        self.assertEqual(len(self.queue_manager.failed_orders), 0)
        self.assertIsInstance(self.queue_manager.statistics, QueueStatistics)
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_removed, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_completed, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_failed, 0)
    
    def test_add_order_success(self):
        """Test successful order addition."""
        result = self.queue_manager.add_order(self.order1)
        
        self.assertTrue(result)
        self.assertEqual(len(self.queue_manager.queue), 1)
        self.assertEqual(self.queue_manager.queue[0], self.order1)
        self.assertEqual(self.order1.status, OrderStatus.ASSIGNED)
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 1)
        self.assertEqual(self.queue_manager.statistics.current_queue_size, 1)
        self.assertEqual(self.queue_manager.statistics.peak_queue_size, 1)
    
    def test_add_order_queue_full(self):
        """Test adding order when queue is full."""
        # Fill the queue with valid positions (1-25, 1-20)
        for i in range(10):
            order = Order(f"ORD_{i:03d}", [f"ITEM_{i}"], [(i + 1, (i % 20) + 1)])
            self.queue_manager.add_order(order)
        
        # Try to add another order
        new_order = Order("ORD_011", ["ITEM_11"], [(11, 11)])
        result = self.queue_manager.add_order(new_order)
        
        self.assertFalse(result)
        self.assertEqual(len(self.queue_manager.queue), 10)
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 10)
    
    def test_add_invalid_order(self):
        """Test adding invalid order."""
        # Create invalid order (missing item_ids)
        invalid_order = Order("ORD_INVALID", [], [])
        invalid_order.item_ids = None
        
        result = self.queue_manager.add_order(invalid_order)
        
        self.assertFalse(result)
        self.assertEqual(len(self.queue_manager.queue), 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 0)
    
    def test_add_duplicate_order(self):
        """Test adding duplicate order."""
        # Add order first time
        self.queue_manager.add_order(self.order1)
        
        # Try to add same order again
        result = self.queue_manager.add_order(self.order1)
        
        self.assertFalse(result)
        self.assertEqual(len(self.queue_manager.queue), 1)
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 1)
    
    def test_remove_order_success(self):
        """Test successful order removal."""
        self.queue_manager.add_order(self.order1)
        self.queue_manager.add_order(self.order2)
        
        result = self.queue_manager.remove_order(self.order1)
        
        self.assertTrue(result)
        self.assertEqual(len(self.queue_manager.queue), 1)
        self.assertEqual(self.queue_manager.queue[0], self.order2)
        self.assertEqual(self.queue_manager.statistics.total_orders_removed, 1)
        self.assertEqual(self.queue_manager.statistics.current_queue_size, 1)
    
    def test_remove_order_not_in_queue(self):
        """Test removing order not in queue."""
        result = self.queue_manager.remove_order(self.order1)
        
        self.assertFalse(result)
        self.assertEqual(self.queue_manager.statistics.total_orders_removed, 0)
    
    def test_get_next_order_fifo(self):
        """Test getting next order in FIFO order."""
        self.queue_manager.add_order(self.order1)
        self.queue_manager.add_order(self.order2)
        self.queue_manager.add_order(self.order3)
        
        next_order = self.queue_manager.get_next_order()
        
        self.assertEqual(next_order, self.order1)
        self.assertEqual(next_order.status, OrderStatus.IN_PROGRESS)
        self.assertEqual(len(self.queue_manager.queue), 3)  # Order not removed, just status changed
    
    def test_get_next_order_empty_queue(self):
        """Test getting next order from empty queue."""
        next_order = self.queue_manager.get_next_order()
        
        self.assertIsNone(next_order)
    
    def test_peek_next_order(self):
        """Test peeking at next order without removing."""
        self.queue_manager.add_order(self.order1)
        self.queue_manager.add_order(self.order2)
        
        peeked_order = self.queue_manager.peek_next_order()
        
        self.assertEqual(peeked_order, self.order1)
        self.assertEqual(len(self.queue_manager.queue), 2)  # Order not removed
        self.assertEqual(self.order1.status, OrderStatus.ASSIGNED)  # Status not changed
    
    def test_peek_next_order_empty_queue(self):
        """Test peeking at next order from empty queue."""
        peeked_order = self.queue_manager.peek_next_order()
        
        self.assertIsNone(peeked_order)
    
    def test_complete_order_success(self):
        """Test successful order completion."""
        self.queue_manager.add_order(self.order1)
        
        result = self.queue_manager.complete_order(self.order1)
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.COMPLETED)
        self.assertEqual(len(self.queue_manager.completed_orders), 1)
        self.assertEqual(self.queue_manager.completed_orders[0], self.order1)
        self.assertEqual(self.queue_manager.statistics.total_orders_completed, 1)
        self.assertEqual(len(self.queue_manager.queue), 0)  # Removed from queue
    
    def test_complete_order_not_in_queue(self):
        """Test completing order not in queue."""
        result = self.queue_manager.complete_order(self.order1)
        
        self.assertTrue(result)  # Should still complete
        self.assertEqual(self.order1.status, OrderStatus.COMPLETED)
        self.assertEqual(len(self.queue_manager.completed_orders), 1)
        self.assertEqual(self.queue_manager.statistics.total_orders_completed, 1)
    
    def test_fail_order_success(self):
        """Test successful order failure."""
        self.queue_manager.add_order(self.order1)
        
        result = self.queue_manager.fail_order(self.order1)
        
        self.assertTrue(result)
        self.assertEqual(self.order1.status, OrderStatus.FAILED)
        self.assertEqual(len(self.queue_manager.failed_orders), 1)
        self.assertEqual(self.queue_manager.failed_orders[0], self.order1)
        self.assertEqual(self.queue_manager.statistics.total_orders_failed, 1)
        self.assertEqual(len(self.queue_manager.queue), 0)  # Removed from queue
    
    def test_fail_order_not_in_queue(self):
        """Test failing order not in queue."""
        result = self.queue_manager.fail_order(self.order1)
        
        self.assertTrue(result)  # Should still fail
        self.assertEqual(self.order1.status, OrderStatus.FAILED)
        self.assertEqual(len(self.queue_manager.failed_orders), 1)
        self.assertEqual(self.queue_manager.statistics.total_orders_failed, 1)
    
    def test_is_empty(self):
        """Test is_empty method."""
        self.assertTrue(self.queue_manager.is_empty())
        
        self.queue_manager.add_order(self.order1)
        self.assertFalse(self.queue_manager.is_empty())
    
    def test_is_full(self):
        """Test is_full method."""
        self.assertFalse(self.queue_manager.is_full())
        
        # Fill the queue with valid positions (1-25, 1-20)
        for i in range(10):
            order = Order(f"ORD_{i:03d}", [f"ITEM_{i}"], [(i + 1, (i % 20) + 1)])
            self.queue_manager.add_order(order)
        
        self.assertTrue(self.queue_manager.is_full())
    
    def test_get_queue_size(self):
        """Test get_queue_size method."""
        self.assertEqual(self.queue_manager.get_queue_size(), 0)
        
        self.queue_manager.add_order(self.order1)
        self.assertEqual(self.queue_manager.get_queue_size(), 1)
        
        self.queue_manager.add_order(self.order2)
        self.assertEqual(self.queue_manager.get_queue_size(), 2)
    
    def test_get_queue_status(self):
        """Test get_queue_status method."""
        # Empty queue
        self.assertEqual(self.queue_manager.get_queue_status(), QueueStatus.EMPTY)
        
        # Queue with orders
        self.queue_manager.add_order(self.order1)
        self.assertEqual(self.queue_manager.get_queue_status(), QueueStatus.HAS_ORDERS)
        
        # Full queue
        for i in range(1, 10):  # Already have 1 order
            order = Order(f"ORD_{i:03d}", [f"ITEM_{i}"], [(i, i)])
            self.queue_manager.add_order(order)
        
        self.assertEqual(self.queue_manager.get_queue_status(), QueueStatus.FULL)
    
    def test_get_queue_orders(self):
        """Test get_queue_orders method."""
        self.assertEqual(len(self.queue_manager.get_queue_orders()), 0)
        
        self.queue_manager.add_order(self.order1)
        self.queue_manager.add_order(self.order2)
        
        orders = self.queue_manager.get_queue_orders()
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0], self.order1)
        self.assertEqual(orders[1], self.order2)
    
    def test_get_completed_orders(self):
        """Test get_completed_orders method."""
        self.assertEqual(len(self.queue_manager.get_completed_orders()), 0)
        
        self.queue_manager.complete_order(self.order1)
        
        completed = self.queue_manager.get_completed_orders()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0], self.order1)
    
    def test_get_failed_orders(self):
        """Test get_failed_orders method."""
        self.assertEqual(len(self.queue_manager.get_failed_orders()), 0)
        
        self.queue_manager.fail_order(self.order1)
        
        failed = self.queue_manager.get_failed_orders()
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0], self.order1)
    
    def test_get_queue_statistics(self):
        """Test get_queue_statistics method."""
        stats = self.queue_manager.get_queue_statistics()
        
        self.assertIn('queue_status', stats)
        self.assertIn('queue_size', stats)
        self.assertIn('max_queue_size', stats)
        self.assertIn('completed_orders', stats)
        self.assertIn('failed_orders', stats)
        self.assertIn('statistics', stats)
        
        self.assertEqual(stats['queue_status'], QueueStatus.EMPTY.value)
        self.assertEqual(stats['queue_size'], 0)
        self.assertEqual(stats['max_queue_size'], 10)
        self.assertEqual(stats['completed_orders'], 0)
        self.assertEqual(stats['failed_orders'], 0)
    
    def test_validate_order_valid(self):
        """Test order validation with valid order."""
        result = self.queue_manager._validate_order(self.order1)
        self.assertTrue(result)
    
    def test_validate_order_invalid_missing_order_id(self):
        """Test order validation with missing order ID."""
        invalid_order = Order("", ["ITEM_A1"], [(1, 1)])
        result = self.queue_manager._validate_order(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_invalid_missing_item_ids(self):
        """Test order validation with missing item IDs."""
        invalid_order = Order("ORD_INVALID", None, [(1, 1)])
        result = self.queue_manager._validate_order(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_invalid_missing_positions(self):
        """Test order validation with missing positions."""
        # Create order with valid positions first, then modify to None
        invalid_order = Order("ORD_INVALID", ["ITEM_A1"], [(1, 1)])
        invalid_order.item_positions = None
        result = self.queue_manager._validate_order(invalid_order)
        self.assertFalse(result)
    
    def test_validate_order_already_in_queue(self):
        """Test order validation with order already in queue."""
        self.queue_manager.add_order(self.order1)
        result = self.queue_manager._validate_order(self.order1)
        self.assertFalse(result)
    
    def test_validate_order_already_completed(self):
        """Test order validation with order already completed."""
        self.queue_manager.complete_order(self.order1)
        result = self.queue_manager._validate_order(self.order1)
        self.assertFalse(result)
    
    def test_validate_order_already_failed(self):
        """Test order validation with order already failed."""
        self.queue_manager.fail_order(self.order1)
        result = self.queue_manager._validate_order(self.order1)
        self.assertFalse(result)
    
    def test_clear_queue(self):
        """Test clearing the queue."""
        self.queue_manager.add_order(self.order1)
        self.queue_manager.add_order(self.order2)
        
        self.queue_manager.clear_queue()
        
        self.assertEqual(len(self.queue_manager.queue), 0)
        self.assertEqual(self.queue_manager.statistics.current_queue_size, 0)
    
    def test_reset_statistics(self):
        """Test resetting statistics."""
        # Add some activity
        self.queue_manager.add_order(self.order1)
        self.queue_manager.complete_order(self.order1)
        
        self.queue_manager.reset_statistics()
        
        self.assertEqual(self.queue_manager.statistics.total_orders_added, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_removed, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_completed, 0)
        self.assertEqual(self.queue_manager.statistics.total_orders_failed, 0)
        self.assertEqual(len(self.queue_manager.wait_times), 0)
    
    def test_get_debug_info(self):
        """Test get_debug_info method."""
        debug_info = self.queue_manager.get_debug_info()
        
        self.assertIn('queue_manager_status', debug_info)
        self.assertIn('queue_orders', debug_info)
        self.assertIn('completed_orders', debug_info)
        self.assertIn('failed_orders', debug_info)
        self.assertIn('queue_timing', debug_info)
        
        self.assertIsInstance(debug_info['queue_orders'], list)
        self.assertIsInstance(debug_info['completed_orders'], list)
        self.assertIsInstance(debug_info['failed_orders'], list)
        self.assertIsInstance(debug_info['queue_timing'], dict)
    
    def test_wait_time_tracking(self):
        """Test wait time tracking."""
        self.queue_manager.add_order(self.order1)
        
        # Simulate some time passing
        time.sleep(0.1)
        
        next_order = self.queue_manager.get_next_order()
        
        self.assertEqual(next_order, self.order1)
        self.assertGreater(len(self.queue_manager.wait_times), 0)
        self.assertGreater(self.queue_manager.statistics.average_wait_time, 0)
        self.assertGreater(self.queue_manager.statistics.max_wait_time, 0)


if __name__ == '__main__':
    unittest.main() 