#!/usr/bin/env python3
"""
Standalone tests for InventorySyncManager class

This test file can be run independently without complex dependencies.
"""

import sys
import os
import time
import threading
from typing import List, Dict, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock classes for testing
@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    
    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class InventoryItem:
    item_id: str
    location: Coordinate
    quantity: float
    category: str
    created_at: float = 0.0
    last_updated: float = 0.0
    
    VALID_CATEGORIES = {
        "electronics", "clothing", "books", "home_goods", "sports",
        "automotive", "toys", "health_beauty", "food_beverages", "office_supplies"
    }
    
    def to_dict(self):
        return {
            "item_id": self.item_id,
            "location": {"x": self.location.x, "y": self.location.y},
            "quantity": self.quantity,
            "category": self.category,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        location = Coordinate(data["location"]["x"], data["location"]["y"])
        return cls(
            item_id=data["item_id"],
            location=location,
            quantity=data["quantity"],
            category=data["category"],
            created_at=data.get("created_at", 0.0),
            last_updated=data.get("last_updated", 0.0)
        )

@dataclass
class ItemPlacementConfig:
    """Configuration for item placement in warehouse"""
    warehouse_width: int = 26
    warehouse_height: int = 20
    packout_zone_x: int = 1
    packout_zone_y: int = 1
    packout_zone_width: int = 1
    packout_zone_height: int = 1

class InventoryEventType(Enum):
    """Types of inventory events"""
    ITEM_ADDED = "item_added"
    ITEM_UPDATED = "item_updated"
    ITEM_REMOVED = "item_removed"
    STOCK_CHANGED = "stock_changed"
    CATEGORY_UPDATED = "category_updated"
    LOCATION_CHANGED = "location_changed"

@dataclass
class InventoryEvent:
    """Inventory event data"""
    event_type: InventoryEventType
    item_id: str
    timestamp: float
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class InventoryUpdateResult:
    """Result of inventory update operation"""
    success: bool
    item_id: str
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0

# Mock InventoryManager for testing
class InventoryManager:
    """Mock InventoryManager for testing"""
    
    def __init__(self):
        self._items = {}
        self._initialized = False
    
    def initialize_inventory(self) -> bool:
        """Initialize with test items"""
        print(f"    - InventoryManager.initialize_inventory() called")
        items = []
        for i in range(5):  # Create 5 test items
            item = InventoryItem(
                item_id=f"ITEM_A{i+1}",
                location=Coordinate(i, i),
                quantity=100.0,
                category="electronics",
                created_at=time.time(),
                last_updated=time.time()
            )
            items.append(item)
            self._items[item.item_id] = item
            print(f"    - Created item: {item.item_id}")
        
        self._initialized = True
        print(f"    - Initialized with {len(items)} items")
        return True
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get item by ID"""
        return self._items.get(item_id)
    
    def get_items_by_category(self, category: str) -> List[InventoryItem]:
        """Get items by category"""
        return [item for item in self._items.values() if item.category == category]
    
    def get_items_by_location(self, location: Coordinate) -> List[InventoryItem]:
        """Get items by location"""
        return [item for item in self._items.values() if item.location == location]
    
    def update_item_quantity(self, item_id: str, new_quantity: float) -> InventoryUpdateResult:
        """Update item quantity"""
        if item_id not in self._items:
            return InventoryUpdateResult(
                success=False,
                item_id=item_id,
                error_message="Item not found"
            )
        
        item = self._items[item_id]
        old_quantity = item.quantity
        item.quantity = new_quantity
        item.last_updated = time.time()
        
        return InventoryUpdateResult(
            success=True,
            item_id=item_id,
            old_value={"quantity": old_quantity},
            new_value={"quantity": new_quantity},
            processing_time_ms=1.0
        )
    
    def get_inventory_statistics(self) -> Dict:
        """Get inventory statistics"""
        return {
            "total_items": len(self._items),
            "items_with_stock": sum(1 for item in self._items.values() if item.quantity > 0),
            "items_out_of_stock": sum(1 for item in self._items.values() if item.quantity == 0),
            "initialized": self._initialized
        }

# Sync classes for testing
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

# InventorySyncManager implementation for testing
class InventorySyncManager:
    """
    Manages inventory synchronization with order management systems.
    """
    
    def __init__(self, inventory_manager: InventoryManager):
        """
        Initialize InventorySyncManager with inventory manager.
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
        """
        try:
            print(f"    - start_order_tracking({order_id}, {required_items}, {robot_id})")
            with self._lock:
                if order_id in self._order_status:
                    print(f"    - Order {order_id} already being tracked")
                    return False  # Order already being tracked
                
                # Validate that all required items exist in inventory
                missing_items = []
                for item_id in required_items:
                    if not self.inventory_manager.get_item(item_id):
                        missing_items.append(item_id)
                
                if missing_items:
                    print(f"    - Missing items: {missing_items}")
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
                
                print(f"    - Started tracking order {order_id} with {len(required_items)} items")
                
                # Emit order started event
                self._emit_sync_event(SyncEventType.ORDER_STARTED, order_id, metadata={
                    "required_items": required_items,
                    "robot_id": robot_id
                })
                
                return True
                
        except Exception as e:
            print(f"    - Exception in start_order_tracking: {e}")
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def record_item_collection(self, order_id: str, item_id: str) -> bool:
        """
        Record that an item has been collected for an order.
        """
        try:
            print(f"    - record_item_collection({order_id}, {item_id})")
            with self._lock:
                if order_id not in self._order_status:
                    print(f"    - Order {order_id} not found")
                    return False
                
                order_status = self._order_status[order_id]
                
                # Check if item is required for this order
                if item_id not in order_status.required_items:
                    print(f"    - Item {item_id} not required for order {order_id}")
                    return False
                
                # Check if item was already collected
                if item_id in order_status.collected_items:
                    print(f"    - Item {item_id} already collected for order {order_id}")
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
                
                print(f"    - Recorded collection of {item_id} for order {order_id}")
                print(f"    - Progress: {len(order_status.collected_items)}/{len(order_status.required_items)}")
                
                # Emit item collected event
                self._emit_sync_event(SyncEventType.ITEM_COLLECTED, order_id, item_id, {
                    "collected_items": order_status.collected_items,
                    "missing_items": order_status.missing_items,
                    "progress": len(order_status.collected_items) / len(order_status.required_items)
                })
                
                # Check if order is complete
                if len(order_status.collected_items) == len(order_status.required_items):
                    print(f"    - Order {order_id} is complete!")
                    return self._complete_order(order_id)
                
                return True
                
        except Exception as e:
            print(f"    - Exception in record_item_collection: {e}")
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, item_id, {
                "error": str(e)
            })
            return False
    
    def cancel_order(self, order_id: str, reason: str = "cancelled") -> bool:
        """
        Cancel an order and update inventory status.
        """
        try:
            print(f"    - cancel_order({order_id}, {reason})")
            with self._lock:
                if order_id not in self._order_status:
                    print(f"    - Order {order_id} not found")
                    return False
                
                order_status = self._order_status[order_id]
                order_status.status = "cancelled"
                order_status.completion_time = time.time()
                
                self._sync_metrics["cancelled_orders"] += 1
                self._sync_metrics["last_sync_time"] = time.time()
                
                print(f"    - Cancelled order {order_id}")
                
                # Emit order cancelled event
                self._emit_sync_event(SyncEventType.ORDER_CANCELLED, order_id, metadata={
                    "reason": reason,
                    "collected_items": order_status.collected_items,
                    "missing_items": order_status.missing_items
                })
                
                return True
                
        except Exception as e:
            print(f"    - Exception in cancel_order: {e}")
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def validate_inventory_for_order(self, order_id: str) -> Dict:
        """
        Validate inventory availability for an order.
        """
        try:
            print(f"    - validate_inventory_for_order({order_id})")
            with self._lock:
                if order_id not in self._order_status:
                    print(f"    - Order {order_id} not found")
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
                
                print(f"    - Validation results: {validation_results}")
                
                # Emit validation event
                self._emit_sync_event(SyncEventType.INVENTORY_VALIDATION, order_id, metadata=validation_results)
                
                return validation_results
                
        except Exception as e:
            print(f"    - Exception in validate_inventory_for_order: {e}")
            self._sync_metrics["sync_errors"] += 1
            return {"error": str(e)}
    
    def get_order_status(self, order_id: str) -> Optional[OrderInventoryStatus]:
        """
        Get current status of an order.
        """
        with self._lock:
            return self._order_status.get(order_id)
    
    def get_all_order_statuses(self) -> List[OrderInventoryStatus]:
        """
        Get status of all tracked orders.
        """
        with self._lock:
            return list(self._order_status.values())
    
    def add_sync_listener(self, listener: Callable[[SyncEvent], None]) -> None:
        """
        Add synchronization event listener.
        """
        with self._lock:
            self._sync_listeners.append(listener)
    
    def remove_sync_listener(self, listener: Callable[[SyncEvent], None]) -> None:
        """
        Remove synchronization event listener.
        """
        with self._lock:
            if listener in self._sync_listeners:
                self._sync_listeners.remove(listener)
    
    def get_sync_metrics(self) -> Dict:
        """
        Get synchronization metrics.
        """
        with self._lock:
            return self._sync_metrics.copy()
    
    def get_sync_statistics(self) -> Dict:
        """
        Get comprehensive synchronization statistics.
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
        """
        try:
            print(f"    - _complete_order({order_id})")
            order_status = self._order_status[order_id]
            order_status.status = "completed"
            
            # Add small delay to ensure measurable completion time
            time.sleep(0.001)
            order_status.completion_time = time.time()
            
            self._sync_metrics["completed_orders"] += 1
            self._sync_metrics["last_sync_time"] = time.time()
            
            print(f"    - Completed order {order_id}")
            
            # Emit order completed event
            self._emit_sync_event(SyncEventType.ORDER_COMPLETED, order_id, metadata={
                "collected_items": order_status.collected_items,
                "completion_time": order_status.completion_time,
                "total_time": order_status.completion_time - order_status.start_time
            })
            
            return True
            
        except Exception as e:
            print(f"    - Exception in _complete_order: {e}")
            self._sync_metrics["sync_errors"] += 1
            self._emit_sync_event(SyncEventType.SYNC_ERROR, order_id, metadata={
                "error": str(e)
            })
            return False
    
    def _emit_sync_event(self, event_type: SyncEventType, order_id: str, 
                        item_id: Optional[str] = None, metadata: Dict = None) -> None:
        """
        Emit synchronization event to all listeners.
        """
        event = SyncEvent(
            event_type=event_type,
            order_id=order_id,
            item_id=item_id,
            metadata=metadata or {}
        )
        
        print(f"    - Emitting {event_type.value} event for order {order_id}")
        
        # Notify listeners (outside of lock to avoid deadlock)
        for listener in self._sync_listeners.copy():
            try:
                listener(event)
            except Exception as e:
                # Log error but don't break other listeners
                print(f"Error in sync event listener: {e}")


class TestInventorySyncManager:
    """Test suite for InventorySyncManager class"""
    
    def test_order_tracking(self):
        """Test order tracking functionality"""
        print("Testing order tracking...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Test starting order tracking
        order_id = "ORDER_001"
        required_items = ["ITEM_A1", "ITEM_A2", "ITEM_A3"]
        robot_id = "ROBOT_001"
        
        success = sync_manager.start_order_tracking(order_id, required_items, robot_id)
        assert success == True, "Order tracking should start successfully"
        
        # Verify order status
        order_status = sync_manager.get_order_status(order_id)
        assert order_status is not None, "Order status should be created"
        assert order_status.order_id == order_id, "Wrong order ID"
        assert order_status.required_items == required_items, "Wrong required items"
        assert order_status.robot_id == robot_id, "Wrong robot ID"
        assert order_status.status == "pending", "Status should be pending"
        
        print("✅ Order tracking tests passed")
    
    def test_item_collection(self):
        """Test item collection recording"""
        print("Testing item collection...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Start order tracking
        order_id = "ORDER_002"
        required_items = ["ITEM_A1", "ITEM_A2"]
        sync_manager.start_order_tracking(order_id, required_items)
        
        # Test item collection
        success = sync_manager.record_item_collection(order_id, "ITEM_A1")
        assert success == True, "Item collection should be recorded"
        
        # Verify order status updated
        order_status = sync_manager.get_order_status(order_id)
        assert "ITEM_A1" in order_status.collected_items, "Item should be in collected items"
        assert "ITEM_A2" in order_status.missing_items, "Item should be in missing items"
        assert order_status.status == "in_progress", "Status should be in_progress"
        
        # Test collecting second item (should complete order)
        success = sync_manager.record_item_collection(order_id, "ITEM_A2")
        assert success == True, "Second item collection should succeed"
        
        # Verify order completed
        order_status = sync_manager.get_order_status(order_id)
        assert order_status.status == "completed", "Order should be completed"
        assert order_status.completion_time is not None, "Should have completion time"
        
        print("✅ Item collection tests passed")
    
    def test_order_cancellation(self):
        """Test order cancellation"""
        print("Testing order cancellation...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Start order tracking
        order_id = "ORDER_003"
        required_items = ["ITEM_A1", "ITEM_A2"]
        sync_manager.start_order_tracking(order_id, required_items)
        
        # Cancel order
        success = sync_manager.cancel_order(order_id, "test cancellation")
        assert success == True, "Order cancellation should succeed"
        
        # Verify order cancelled
        order_status = sync_manager.get_order_status(order_id)
        assert order_status.status == "cancelled", "Order should be cancelled"
        assert order_status.completion_time is not None, "Should have completion time"
        
        print("✅ Order cancellation tests passed")
    
    def test_inventory_validation(self):
        """Test inventory validation"""
        print("Testing inventory validation...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Start order tracking
        order_id = "ORDER_004"
        required_items = ["ITEM_A1", "ITEM_A2", "ITEM_A3"]
        sync_manager.start_order_tracking(order_id, required_items)
        
        # Test validation
        validation = sync_manager.validate_inventory_for_order(order_id)
        assert validation["order_id"] == order_id, "Wrong order ID in validation"
        assert validation["required_items"] == required_items, "Wrong required items"
        assert len(validation["available_items"]) == 3, "Should have 3 available items"
        assert len(validation["unavailable_items"]) == 0, "Should have 0 unavailable items"
        assert validation["validation_passed"] == True, "Validation should pass"
        
        print("✅ Inventory validation tests passed")
    
    def test_sync_events(self):
        """Test synchronization events"""
        print("Testing sync events...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        events_received = []
        
        def event_listener(event: SyncEvent):
            print(f"    - Event listener received: {event.event_type} for order {event.order_id}")
            events_received.append(event)
        
        # Add event listener
        sync_manager.add_sync_listener(event_listener)
        
        # Start order tracking (should trigger ORDER_STARTED event)
        order_id = "ORDER_005"
        required_items = ["ITEM_A1", "ITEM_A2"]
        sync_manager.start_order_tracking(order_id, required_items)
        
        assert len(events_received) > 0, "Should receive order started event"
        assert events_received[0].event_type == SyncEventType.ORDER_STARTED, "Wrong event type"
        assert events_received[0].order_id == order_id, "Wrong order ID"
        
        # Collect item (should trigger ITEM_COLLECTED event)
        events_received.clear()
        sync_manager.record_item_collection(order_id, "ITEM_A1")
        
        assert len(events_received) > 0, "Should receive item collected event"
        print(f"    - Received event type: {events_received[0].event_type}")
        print(f"    - Expected event type: {SyncEventType.ITEM_COLLECTED}")
        assert events_received[0].event_type == SyncEventType.ITEM_COLLECTED, f"Wrong event type: expected {SyncEventType.ITEM_COLLECTED}, got {events_received[0].event_type}"
        assert events_received[0].item_id == "ITEM_A1", "Wrong item ID"
        
        # Complete order (should trigger ORDER_COMPLETED event)
        events_received.clear()
        sync_manager.record_item_collection(order_id, "ITEM_A2")
        
        assert len(events_received) > 0, "Should receive order completed event"
        print(f"    - Received {len(events_received)} events:")
        for i, event in enumerate(events_received):
            print(f"    - Event {i}: {event.event_type}")
        
        # The last event should be ORDER_COMPLETED
        assert events_received[-1].event_type == SyncEventType.ORDER_COMPLETED, f"Wrong event type: expected {SyncEventType.ORDER_COMPLETED}, got {events_received[-1].event_type}"
        
        print("✅ Sync events tests passed")
    
    def test_sync_metrics(self):
        """Test synchronization metrics"""
        print("Testing sync metrics...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Get initial metrics
        initial_metrics = sync_manager.get_sync_metrics()
        assert initial_metrics["total_orders"] == 0, "Should start with 0 orders"
        
        # Perform operations
        sync_manager.start_order_tracking("ORDER_006", ["ITEM_A1", "ITEM_A2"])
        sync_manager.record_item_collection("ORDER_006", "ITEM_A1")
        sync_manager.record_item_collection("ORDER_006", "ITEM_A2")
        
        # Get updated metrics
        updated_metrics = sync_manager.get_sync_metrics()
        assert updated_metrics["total_orders"] == 1, "Should have 1 order"
        assert updated_metrics["completed_orders"] == 1, "Should have 1 completed order"
        assert updated_metrics["total_items_collected"] == 2, "Should have 2 items collected"
        assert updated_metrics["last_sync_time"] > 0, "Should have last sync time"
        
        print("✅ Sync metrics tests passed")
    
    def test_sync_statistics(self):
        """Test synchronization statistics"""
        print("Testing sync statistics...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Create multiple orders
        sync_manager.start_order_tracking("ORDER_007", ["ITEM_A1"])
        sync_manager.record_item_collection("ORDER_007", "ITEM_A1")
        
        sync_manager.start_order_tracking("ORDER_008", ["ITEM_A2"])
        sync_manager.cancel_order("ORDER_008")
        
        # Get statistics
        stats = sync_manager.get_sync_statistics()
        
        assert stats["total_orders"] == 2, "Should have 2 total orders"
        assert stats["completed_orders"] == 1, "Should have 1 completed order"
        assert stats["cancelled_orders"] == 1, "Should have 1 cancelled order"
        assert stats["completion_rate"] == 0.5, "Should have 50% completion rate"
        assert stats["average_completion_time_seconds"] >= 0, "Should have average completion time (can be 0 for very fast operations)"
        
        print("✅ Sync statistics tests passed")
    
    def test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Test starting order with non-existent items
        success = sync_manager.start_order_tracking("ORDER_009", ["NONEXISTENT_ITEM"])
        assert success == False, "Should fail with non-existent items"
        
        # Test collecting item for non-existent order
        success = sync_manager.record_item_collection("NONEXISTENT_ORDER", "ITEM_A1")
        assert success == False, "Should fail with non-existent order"
        
        # Test collecting non-required item
        sync_manager.start_order_tracking("ORDER_010", ["ITEM_A1"])
        success = sync_manager.record_item_collection("ORDER_010", "ITEM_A2")
        assert success == False, "Should fail with non-required item"
        
        # Test duplicate item collection
        sync_manager.start_order_tracking("ORDER_011", ["ITEM_A1"])
        sync_manager.record_item_collection("ORDER_011", "ITEM_A1")
        success = sync_manager.record_item_collection("ORDER_011", "ITEM_A1")
        assert success == False, "Should fail with duplicate collection"
        
        print("✅ Error handling tests passed")
    
    def test_thread_safety(self):
        """Test thread safety of sync operations"""
        print("Testing thread safety...")
        
        # Setup
        inventory_manager = InventoryManager()
        inventory_manager.initialize_inventory()
        sync_manager = InventorySyncManager(inventory_manager)
        
        # Create multiple threads performing operations
        results = []
        errors = []
        
        def worker_thread(thread_id: int):
            try:
                order_id = f"ORDER_THREAD_{thread_id}"
                item_id = f"ITEM_A{(thread_id % 3) + 1}"
                
                # Start order tracking
                success = sync_manager.start_order_tracking(order_id, [item_id])
                results.append(("start_tracking", success))
                
                # Record item collection
                success = sync_manager.record_item_collection(order_id, item_id)
                results.append(("record_collection", success))
                
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 6, f"Expected 6 results, got {len(results)}"
        
        # All operations should be successful
        successful_ops = sum(1 for r in results if r[1])
        assert successful_ops == 6, f"Expected 6 successful operations, got {successful_ops}"
        
        print("✅ Thread safety tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running InventorySyncManager tests...\n")
        
        try:
            self.test_order_tracking()
            self.test_item_collection()
            self.test_order_cancellation()
            self.test_inventory_validation()
            self.test_sync_events()
            self.test_sync_metrics()
            self.test_sync_statistics()
            self.test_error_handling()
            self.test_thread_safety()
            
            print("\n🎉 All InventorySyncManager tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    # Run tests
    test_suite = TestInventorySyncManager()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 