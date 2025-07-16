"""
Inventory Synchronization with Order Management

This module provides inventory synchronization with order management systems,
including order completion tracking, inventory validation, and status consistency.
"""

import time
import threading
from typing import List, Dict, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

from .inventory_manager import InventoryManager, InventoryEventType, InventoryEvent
from .inventory_item import InventoryItem
from core.layout.coordinate import Coordinate


class SyncEventType(Enum):
    """Types of synchronization events"""
    ORDER_STARTED = "order_started"
    ITEM_COLLECTED = "item_collected"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    INVENTORY_VALIDATION = "inventory_validation"
    SYNC_ERROR = "sync_error"


@dataclass
class SyncEvent:
    """Synchronization event data"""
    event_type: SyncEventType
    order_id: str
    item_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


@dataclass
class OrderInventoryStatus:
    """Order inventory status tracking"""
    order_id: str
    required_items: List[str]
    collected_items: List[str] = field(default_factory=list)
    missing_items: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, cancelled
    start_time: float = field(default_factory=time.time)
    completion_time: Optional[float] = None
    robot_id: Optional[str] = None


class InventorySyncManager:
    """
    Manages inventory synchronization with order management systems.
    
    Features:
    - Order inventory tracking
    - Real-time inventory validation
    - Order completion synchronization
    - Status consistency checks
    - Error handling and recovery
    """
    
    def __init__(self, inventory_manager: InventoryManager):
        """
        Initialize InventorySyncManager with inventory manager.
        
        Args:
            inventory_manager: InventoryManager instance for inventory operations
        """
        self.inventory_manager = inventory_manager
        self._order_status: Dict[str, OrderInventoryStatus] = {}
        self._sync_listeners: List[Callable[[SyncEvent], None]] = []
        self._lock = threading.RLock()
        self._sync_metrics = {
            "total_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "total_items_collected": 0,
            "sync_errors": 0,
            "last_sync_time": 0.0
        }
    
    def start_order_tracking(self, order_id: str, required_items: List[str], 
                           robot_id: Optional[str] = None) -> bool:
        """
        Start tracking inventory for an order.
        
        Args:
            order_id: Unique order identifier
            required_items: List of item IDs required for the order
            robot_id: Robot assigned to the order (optional)
            
        Returns:
            True if tracking started successfully, False otherwise
        """
        try:
            with self._lock:
                if order_id in self._order_status:
                    return False  # Order already being tracked
                
                # Validate that all required items exist in inventory
                missing_items = []
                for item_id in required_items:
                    if not self.inventory_manager.get_item(item_id):
                        missing_items.append(item_id)
                
                if missing_items:
                    self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                        "error": "Missing items in inventory",
                        "missing_items": missing_items
                    })
                    return False
                
                # Create order status tracking
                order_status = OrderInventoryStatus(
                    order_id=order_id,
                    required_items=required_items.copy(),
                    missing_items=missing_items,
                    robot_id=robot_id
                )
                
                self._order_status[order_id] = order_status
                self._sync_metrics["total_orders"] += 1
                self._sync_metrics["last_sync_time"] = time.time()
                
                # Emit order started event
                self._emit_sync_event(SyncEventType.ORDER_STARTED, order_id, metadata={
                    "required_items": required_items,
                    "robot_id": robot_id
                })
                
                return True
                
        except Exception as e:
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def record_item_collection(self, order_id: str, item_id: str) -> bool:
        """
        Record that an item has been collected for an order.
        
        Args:
            order_id: Order identifier
            item_id: Item that was collected
            
        Returns:
            True if collection recorded successfully, False otherwise
        """
        try:
            with self._lock:
                if order_id not in self._order_status:
                    return False
                
                order_status = self._order_status[order_id]
                
                # Check if item is required for this order
                if item_id not in order_status.required_items:
                    return False
                
                # Check if item was already collected
                if item_id in order_status.collected_items:
                    return False
                
                # Record item collection
                order_status.collected_items.append(item_id)
                order_status.missing_items = [
                    item for item in order_status.required_items 
                    if item not in order_status.collected_items
                ]
                
                # Update status
                if order_status.status == "pending":
                    order_status.status = "in_progress"
                
                self._sync_metrics["total_items_collected"] += 1
                self._sync_metrics["last_sync_time"] = time.time()
                
                # Emit item collected event
                self._emit_sync_event(SyncEventType.ITEM_COLLECTED, order_id, item_id, {
                    "collected_items": order_status.collected_items,
                    "missing_items": order_status.missing_items,
                    "progress": len(order_status.collected_items) / len(order_status.required_items)
                })
                
                # Check if order is complete
                if len(order_status.collected_items) == len(order_status.required_items):
                    return self._complete_order(order_id)
                
                return True
                
        except Exception as e:
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, item_id, {
                "error": str(e)
            })
            return False
    
    def cancel_order(self, order_id: str, reason: str = "cancelled") -> bool:
        """
        Cancel an order and update inventory status.
        
        Args:
            order_id: Order identifier
            reason: Reason for cancellation
            
        Returns:
            True if order cancelled successfully, False otherwise
        """
        try:
            with self._lock:
                if order_id not in self._order_status:
                    return False
                
                order_status = self._order_status[order_id]
                order_status.status = "cancelled"
                order_status.completion_time = time.time()
                
                self._sync_metrics["cancelled_orders"] += 1
                self._sync_metrics["last_sync_time"] = time.time()
                
                # Emit order cancelled event
                self._emit_sync_event(SyncEventType.ORDER_CANCELLED, order_id, metadata={
                    "reason": reason,
                    "collected_items": order_status.collected_items,
                    "missing_items": order_status.missing_items
                })
                
                return True
                
        except Exception as e:
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def validate_inventory_for_order(self, order_id: str) -> Dict:
        """
        Validate inventory availability for an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Dictionary with validation results
        """
        try:
            with self._lock:
                if order_id not in self._order_status:
                    return {"error": "Order not found"}
                
                order_status = self._order_status[order_id]
                validation_results = {
                    "order_id": order_id,
                    "required_items": order_status.required_items,
                    "available_items": [],
                    "unavailable_items": [],
                    "validation_passed": True
                }
                
                for item_id in order_status.required_items:
                    item = self.inventory_manager.get_item(item_id)
                    if item and item.quantity > 0:
                        validation_results["available_items"].append(item_id)
                    else:
                        validation_results["unavailable_items"].append(item_id)
                        validation_results["validation_passed"] = False
                
                # Emit validation event
                self._emit_sync_event(SyncEventType.INVENTORY_VALIDATION, order_id, metadata=validation_results)
                
                return validation_results
                
        except Exception as e:
            self._sync_metrics["sync_errors"] += 1
            return {"error": str(e)}
    
    def get_order_status(self, order_id: str) -> Optional[OrderInventoryStatus]:
        """
        Get current status of an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            OrderInventoryStatus if found, None otherwise
        """
        with self._lock:
            return self._order_status.get(order_id)
    
    def get_all_order_statuses(self) -> List[OrderInventoryStatus]:
        """
        Get status of all tracked orders.
        
        Returns:
            List of all order statuses
        """
        with self._lock:
            return list(self._order_status.values())
    
    def add_sync_listener(self, listener: Callable[[SyncEvent], None]) -> None:
        """
        Add synchronization event listener.
        
        Args:
            listener: Callback function for sync events
        """
        with self._lock:
            self._sync_listeners.append(listener)
    
    def remove_sync_listener(self, listener: Callable[[SyncEvent], None]) -> None:
        """
        Remove synchronization event listener.
        
        Args:
            listener: Callback function to remove
        """
        with self._lock:
            if listener in self._sync_listeners:
                self._sync_listeners.remove(listener)
    
    def get_sync_metrics(self) -> Dict:
        """
        Get synchronization metrics.
        
        Returns:
            Dictionary with sync metrics
        """
        with self._lock:
            return self._sync_metrics.copy()
    
    def get_sync_statistics(self) -> Dict:
        """
        Get comprehensive synchronization statistics.
        
        Returns:
            Dictionary with sync statistics
        """
        with self._lock:
            total_orders = len(self._order_status)
            completed_orders = sum(1 for status in self._order_status.values() 
                                if status.status == "completed")
            in_progress_orders = sum(1 for status in self._order_status.values() 
                                   if status.status == "in_progress")
            cancelled_orders = sum(1 for status in self._order_status.values() 
                                if status.status == "cancelled")
            
            # Calculate average completion time
            completion_times = []
            for status in self._order_status.values():
                if status.completion_time and status.status == "completed":
                    completion_times.append(status.completion_time - status.start_time)
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            return {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "in_progress_orders": in_progress_orders,
                "cancelled_orders": cancelled_orders,
                "completion_rate": completed_orders / total_orders if total_orders > 0 else 0,
                "average_completion_time_seconds": avg_completion_time,
                "sync_metrics": self._sync_metrics.copy(),
                "last_sync_time": self._sync_metrics["last_sync_time"]
            }
    
    def _complete_order(self, order_id: str) -> bool:
        """
        Mark an order as completed.
        
        Args:
            order_id: Order identifier
            
        Returns:
            True if order completed successfully, False otherwise
        """
        try:
            order_status = self._order_status[order_id]
            order_status.status = "completed"
            order_status.completion_time = time.time()
            
            self._sync_metrics["completed_orders"] += 1
            self._sync_metrics["last_sync_time"] = time.time()
            
            # Emit order completed event
            self._emit_sync_event(SyncEventType.ORDER_COMPLETED, order_id, metadata={
                "collected_items": order_status.collected_items,
                "completion_time": order_status.completion_time,
                "total_time": order_status.completion_time - order_status.start_time
            })
            
            return True
            
        except Exception as e:
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def _emit_sync_event(self, event_type: SyncEventType, order_id: str, 
                        item_id: Optional[str] = None, metadata: Dict = None) -> None:
        """
        Emit synchronization event to all listeners.
        
        Args:
            event_type: Type of sync event
            order_id: Order identifier
            item_id: Item identifier (optional)
            metadata: Additional event data (optional)
        """
        event = SyncEvent(
            event_type=event_type,
            order_id=order_id,
            item_id=item_id,
            metadata=metadata or {}
        )
        
        # Notify listeners (outside of lock to avoid deadlock)
        for listener in self._sync_listeners.copy():
            try:
                listener(event)
            except Exception as e:
                # Log error but don't break other listeners
                print(f"Error in sync event listener: {e}") 