"""
Order Queue Management System for Phase 5: Order Management System

This module provides the OrderQueueManager class that handles FIFO order queue
management with priority based on creation time. Orders are queued in FIFO order
and assigned to robots based on creation timestamp priority.

Key Features:
- FIFO queue implementation with creation time priority
- Order status tracking (PENDING, IN_PROGRESS, COMPLETED)
- Queue management methods (add, remove, get_next, peek)
- Queue validation and error handling
- Queue statistics and monitoring
- Integration with order generation system

Author: Roibot Development Team
Version: 1.0
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

from .robot_orders import Order, OrderStatus


class QueueStatus(Enum):
    """Enumeration for queue status."""
    EMPTY = "empty"
    HAS_ORDERS = "has_orders"
    FULL = "full"


@dataclass
class QueueStatistics:
    """Statistics for the order queue."""
    total_orders_added: int = 0
    total_orders_removed: int = 0
    total_orders_completed: int = 0
    total_orders_failed: int = 0
    average_wait_time: float = 0.0
    max_wait_time: float = 0.0
    current_queue_size: int = 0
    peak_queue_size: int = 0


class OrderQueueManager:
    """
    Handles FIFO order queue management with priority based on creation time.
    
    Orders are queued in FIFO order and assigned to robots based on
    creation timestamp priority. Provides comprehensive queue management
    and statistics tracking.
    """
    
    def __init__(self, max_queue_size: int = 100):
        """
        Initialize the order queue manager.
        
        Args:
            max_queue_size: Maximum number of orders in queue
        """
        self.max_queue_size = max_queue_size
        self.queue: List[Order] = []
        self.completed_orders: List[Order] = []
        self.failed_orders: List[Order] = []
        
        # Statistics tracking
        self.statistics = QueueStatistics()
        self.queue_start_time = time.time()
        
        # Performance tracking
        self.wait_times: List[float] = []
        
        print(f"📋 OrderQueueManager initialized with max queue size: {max_queue_size}")
    
    def add_order(self, order: Order) -> bool:
        """
        Add an order to the queue.
        
        Args:
            order: Order object to add
            
        Returns:
            True if order added successfully, False otherwise
        """
        try:
            # Check if queue is full
            if len(self.queue) >= self.max_queue_size:
                print(f"⚠️  Queue is full ({len(self.queue)}/{self.max_queue_size})")
                return False
            
            # Validate order
            if not self._validate_order(order):
                print(f"❌ Invalid order: {order.order_id}")
                return False
            
            # Keep order status as PENDING (don't change it)
            # order.status = OrderStatus.PENDING
            
            # Add order to queue (FIFO order)
            self.queue.append(order)
            
            # Update statistics
            self.statistics.total_orders_added += 1
            self.statistics.current_queue_size = len(self.queue)
            self.statistics.peak_queue_size = max(self.statistics.peak_queue_size, len(self.queue))
            
            print(f"📦 Added order {order.order_id} to queue (size: {len(self.queue)})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding order to queue: {e}")
            return False
    
    def remove_order(self, order: Order) -> bool:
        """
        Remove an order from the queue.
        
        Args:
            order: Order object to remove
            
        Returns:
            True if order removed successfully, False otherwise
        """
        try:
            if order in self.queue:
                self.queue.remove(order)
                self.statistics.total_orders_removed += 1
                self.statistics.current_queue_size = len(self.queue)
                
                print(f"🗑️  Removed order {order.order_id} from queue (size: {len(self.queue)})")
                return True
            else:
                print(f"⚠️  Order {order.order_id} not found in queue")
                return False
                
        except Exception as e:
            print(f"❌ Error removing order from queue: {e}")
            return False
    
    def get_next_order(self) -> Optional[Order]:
        """
        Get the next order from the queue (FIFO order).
        
        Returns:
            Next order in queue or None if queue is empty
        """
        if self.is_empty():
            return None
        
        # Get the oldest order (FIFO)
        next_order = self.queue[0]
        
        # Don't change order status here - let the assigner handle it
        # next_order.status = OrderStatus.IN_PROGRESS
        
        # Calculate wait time
        wait_time = time.time() - self.queue_start_time
        self.wait_times.append(wait_time)
        
        # Update statistics
        self.statistics.average_wait_time = sum(self.wait_times) / len(self.wait_times)
        self.statistics.max_wait_time = max(self.statistics.max_wait_time, wait_time)
        
        print(f"🎯 Next order: {next_order.order_id} (wait time: {wait_time:.2f}s)")
        return next_order
    
    def peek_next_order(self) -> Optional[Order]:
        """
        Peek at the next order without removing it.
        
        Returns:
            Next order in queue or None if queue is empty
        """
        if self.is_empty():
            return None
        
        return self.queue[0]
    
    def complete_order(self, order: Order) -> bool:
        """
        Mark an order as completed and move to completed list.
        
        Args:
            order: Order object to complete
            
        Returns:
            True if order completed successfully, False otherwise
        """
        try:
            # Remove from queue if present
            if order in self.queue:
                self.remove_order(order)
            
            # Update order status
            order.status = OrderStatus.COMPLETED
            
            # Add to completed orders
            self.completed_orders.append(order)
            
            # Update statistics
            self.statistics.total_orders_completed += 1
            
            print(f"✅ Completed order {order.order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error completing order: {e}")
            return False
    
    def fail_order(self, order: Order) -> bool:
        """
        Mark an order as failed and move to failed list.
        
        Args:
            order: Order object to fail
            
        Returns:
            True if order failed successfully, False otherwise
        """
        try:
            # Remove from queue if present
            if order in self.queue:
                self.remove_order(order)
            
            # Update order status
            order.status = OrderStatus.FAILED
            
            # Add to failed orders
            self.failed_orders.append(order)
            
            # Update statistics
            self.statistics.total_orders_failed += 1
            
            print(f"❌ Failed order {order.order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error failing order: {e}")
            return False
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty, False otherwise
        """
        return len(self.queue) == 0
    
    def is_full(self) -> bool:
        """
        Check if the queue is full.
        
        Returns:
            True if queue is full, False otherwise
        """
        return len(self.queue) >= self.max_queue_size
    
    def get_queue_size(self) -> int:
        """
        Get the current queue size.
        
        Returns:
            Number of orders in queue
        """
        return len(self.queue)
    
    def get_queue_status(self) -> QueueStatus:
        """
        Get the current queue status.
        
        Returns:
            QueueStatus enum value
        """
        if self.is_empty():
            return QueueStatus.EMPTY
        elif self.is_full():
            return QueueStatus.FULL
        else:
            return QueueStatus.HAS_ORDERS
    
    def get_queue_orders(self) -> List[Order]:
        """
        Get all orders in the queue.
        
        Returns:
            List of orders in queue
        """
        return self.queue.copy()
    
    def get_completed_orders(self) -> List[Order]:
        """
        Get all completed orders.
        
        Returns:
            List of completed orders
        """
        return self.completed_orders.copy()
    
    def get_failed_orders(self) -> List[Order]:
        """
        Get all failed orders.
        
        Returns:
            List of failed orders
        """
        return self.failed_orders.copy()
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            'queue_status': self.get_queue_status().value,
            'queue_size': self.get_queue_size(),
            'max_queue_size': self.max_queue_size,
            'completed_orders': len(self.completed_orders),
            'failed_orders': len(self.failed_orders),
            'statistics': {
                'total_orders_added': self.statistics.total_orders_added,
                'total_orders_removed': self.statistics.total_orders_removed,
                'total_orders_completed': self.statistics.total_orders_completed,
                'total_orders_failed': self.statistics.total_orders_failed,
                'average_wait_time': self.statistics.average_wait_time,
                'max_wait_time': self.statistics.max_wait_time,
                'current_queue_size': self.statistics.current_queue_size,
                'peak_queue_size': self.statistics.peak_queue_size
            }
        }
    
    def _validate_order(self, order: Order) -> bool:
        """
        Validate an order before adding to queue.
        
        Args:
            order: Order object to validate
            
        Returns:
            True if order is valid, False otherwise
        """
        try:
            # Check if order has required attributes
            if not hasattr(order, 'order_id') or not order.order_id:
                return False
            
            if not hasattr(order, 'item_ids') or not order.item_ids:
                return False
            
            if not hasattr(order, 'item_positions') or not order.item_positions:
                return False
            
            # Check if order is already in queue
            if order in self.queue:
                return False
            
            # Check if order is already completed or failed
            if order in self.completed_orders or order in self.failed_orders:
                return False
            
            return True
            
        except Exception:
            return False
    
    def clear_queue(self):
        """Clear all orders from the queue."""
        cleared_count = len(self.queue)
        self.queue.clear()
        self.statistics.current_queue_size = 0
        
        print(f"🧹 Cleared {cleared_count} orders from queue")
    
    def reset_statistics(self):
        """Reset queue statistics."""
        self.statistics = QueueStatistics()
        self.wait_times.clear()
        self.queue_start_time = time.time()
        
        print("📊 Queue statistics reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information for the queue manager.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'queue_manager_status': self.get_queue_statistics(),
            'queue_orders': [order.order_id for order in self.queue],
            'completed_orders': [order.order_id for order in self.completed_orders],
            'failed_orders': [order.order_id for order in self.failed_orders],
            'queue_timing': {
                'queue_start_time': self.queue_start_time,
                'current_time': time.time(),
                'queue_duration': time.time() - self.queue_start_time
            }
        } 