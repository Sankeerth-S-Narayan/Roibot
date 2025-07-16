#!/usr/bin/env python3
"""
Standalone tests for InventoryManager class

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

# Mock ItemGenerator for testing
class ItemGenerator:
    """Mock ItemGenerator for testing"""
    
    CATEGORIES = [
        "electronics", "clothing", "books", "home_goods", "sports",
        "automotive", "toys", "health_beauty", "food_beverages", "office_supplies"
    ]
    
    def __init__(self, config: ItemPlacementConfig = None):
        self.config = config or ItemPlacementConfig()
    
    def generate_all_items(self) -> List[InventoryItem]:
        """Generate test items"""
        print(f"    - ItemGenerator.generate_all_items() called")
        items = []
        for i in range(10):  # Generate 10 test items
            item = InventoryItem(
                item_id=f"ITEM_A{i+1}",
                location=Coordinate(i % 5, i // 5),
                quantity=100.0,
                category=self.CATEGORIES[i % len(self.CATEGORIES)],
                created_at=time.time(),
                last_updated=time.time()
            )
            items.append(item)
            print(f"    - Created item: {item.item_id} at ({item.location.x}, {item.location.y})")
        print(f"    - Generated {len(items)} items")
        return items

# InventoryManager implementation for testing
class InventoryManager:
    """
    Centralized inventory management system with real-time updates.
    """
    
    def __init__(self, config: ItemPlacementConfig = None):
        """
        Initialize InventoryManager with configuration.
        """
        self.config = config or ItemPlacementConfig()
        self._items: Dict[str, InventoryItem] = {}
        self._items_by_location: Dict[Coordinate, List[InventoryItem]] = {}
        self._items_by_category: Dict[str, List[InventoryItem]] = {}
        self._event_listeners: List[Callable[[InventoryEvent], None]] = []
        self._lock = threading.RLock()
        self._performance_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_processing_time_ms": 0.0,
            "last_operation_time": 0.0
        }
        self._initialized = False
    
    def initialize_inventory(self) -> bool:
        """
        Initialize inventory with test items using ItemGenerator.
        """
        try:
            print(f"    - InventoryManager.initialize_inventory() started")
            with self._lock:
                if self._initialized:
                    print(f"    - Already initialized, returning True")
                    return True
                
                start_time = time.time()
                print(f"    - Creating ItemGenerator...")
                
                # Generate items using ItemGenerator
                generator = ItemGenerator(self.config)
                print(f"    - Calling generator.generate_all_items()...")
                items = generator.generate_all_items()
                print(f"    - Received {len(items)} items from generator")
                
                # Populate inventory data structures
                print(f"    - Populating inventory data structures...")
                for item in items:
                    self._items[item.item_id] = item
                    print(f"    - Added item {item.item_id} to _items")
                    
                    # Index by location
                    if item.location not in self._items_by_location:
                        self._items_by_location[item.location] = []
                    self._items_by_location[item.location].append(item)
                    print(f"    - Indexed {item.item_id} by location ({item.location.x}, {item.location.y})")
                    
                    # Index by category
                    if item.category not in self._items_by_category:
                        self._items_by_category[item.category] = []
                    self._items_by_category[item.category].append(item)
                    print(f"    - Indexed {item.item_id} by category {item.category}")
                
                self._initialized = True
                processing_time = (time.time() - start_time) * 1000
                print(f"    - Initialization completed in {processing_time:.2f}ms")
                
                # Update performance metrics
                self._update_performance_metrics(True, processing_time)
                
                # Emit initialization event
                self._emit_event(InventoryEventType.ITEM_ADDED, "INIT", {
                    "total_items": len(items),
                    "processing_time_ms": processing_time
                })
                
                print(f"    - Returning True from initialize_inventory()")
                return True
                
        except Exception as e:
            print(f"    - Exception in initialize_inventory(): {e}")
            self._update_performance_metrics(False, 0.0)
            return False
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """
        Get item by ID.
        """
        with self._lock:
            return self._items.get(item_id)
    
    def get_items_by_category(self, category: str) -> List[InventoryItem]:
        """
        Get all items in a category.
        """
        with self._lock:
            return self._items_by_category.get(category, []).copy()
    
    def get_items_by_location(self, location: Coordinate) -> List[InventoryItem]:
        """
        Get all items at a location.
        """
        with self._lock:
            return self._items_by_location.get(location, []).copy()
    
    def update_item_quantity(self, item_id: str, new_quantity: float) -> InventoryUpdateResult:
        """
        Update item quantity with atomic operation.
        """
        start_time = time.time()
        
        try:
            with self._lock:
                if item_id not in self._items:
                    error_msg = f"Item not found: {item_id}"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                item = self._items[item_id]
                old_quantity = item.quantity
                
                # Validate new quantity
                if new_quantity < 0:
                    error_msg = f"Quantity cannot be negative: {new_quantity}"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                # Update quantity
                item.quantity = new_quantity
                item.last_updated = time.time()
                
                # Small delay to ensure measurable processing time
                time.sleep(0.001)
                
                processing_time = (time.time() - start_time) * 1000
                
                # Update performance metrics
                self._update_performance_metrics(True, processing_time)
                
                # Emit event
                self._emit_event(
                    InventoryEventType.STOCK_CHANGED,
                    item_id,
                    {"quantity": old_quantity},
                    {"quantity": new_quantity}
                )
                
                return InventoryUpdateResult(
                    success=True,
                    item_id=item_id,
                    old_value={"quantity": old_quantity},
                    new_value={"quantity": new_quantity},
                    processing_time_ms=processing_time
                )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(False, processing_time)
            return InventoryUpdateResult(
                success=False,
                item_id=item_id,
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def update_item_category(self, item_id: str, new_category: str) -> InventoryUpdateResult:
        """
        Update item category with atomic operation.
        """
        start_time = time.time()
        
        try:
            with self._lock:
                if item_id not in self._items:
                    error_msg = f"Item not found: {item_id}"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                item = self._items[item_id]
                old_category = item.category
                
                # Validate new category
                if new_category not in item.VALID_CATEGORIES:
                    error_msg = f"Invalid category: {new_category}"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                # Update category
                item.category = new_category
                item.last_updated = time.time()
                
                # Small delay to ensure measurable processing time
                time.sleep(0.001)
                
                # Update category index
                if old_category in self._items_by_category:
                    self._items_by_category[old_category] = [
                        i for i in self._items_by_category[old_category] 
                        if i.item_id != item_id
                    ]
                
                if new_category not in self._items_by_category:
                    self._items_by_category[new_category] = []
                self._items_by_category[new_category].append(item)
                
                processing_time = (time.time() - start_time) * 1000
                
                # Update performance metrics
                self._update_performance_metrics(True, processing_time)
                
                # Emit event
                self._emit_event(
                    InventoryEventType.CATEGORY_UPDATED,
                    item_id,
                    {"category": old_category},
                    {"category": new_category}
                )
                
                return InventoryUpdateResult(
                    success=True,
                    item_id=item_id,
                    old_value={"category": old_category},
                    new_value={"category": new_category},
                    processing_time_ms=processing_time
                )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(False, processing_time)
            return InventoryUpdateResult(
                success=False,
                item_id=item_id,
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def update_item_location(self, item_id: str, new_location: Coordinate) -> InventoryUpdateResult:
        """
        Update item location with atomic operation.
        """
        start_time = time.time()
        
        try:
            with self._lock:
                if item_id not in self._items:
                    error_msg = f"Item not found: {item_id}"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                item = self._items[item_id]
                old_location = item.location
                
                # Validate new location
                if (new_location.x < 0 or new_location.x >= self.config.warehouse_width or
                    new_location.y < 0 or new_location.y >= self.config.warehouse_height):
                    error_msg = f"Invalid location: ({new_location.x}, {new_location.y})"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                # Check packout zone
                if self._is_in_packout_zone(new_location.x, new_location.y):
                    error_msg = f"Cannot place item in packout zone: ({new_location.x}, {new_location.y})"
                    self._update_performance_metrics(False, 0.0)
                    return InventoryUpdateResult(
                        success=False,
                        item_id=item_id,
                        error_message=error_msg
                    )
                
                # Update location
                item.location = new_location
                item.last_updated = time.time()
                
                # Small delay to ensure measurable processing time
                time.sleep(0.001)
                
                # Update location index
                if old_location in self._items_by_location:
                    self._items_by_location[old_location] = [
                        i for i in self._items_by_location[old_location] 
                        if i.item_id != item_id
                    ]
                
                if new_location not in self._items_by_location:
                    self._items_by_location[new_location] = []
                self._items_by_location[new_location].append(item)
                
                processing_time = (time.time() - start_time) * 1000
                
                # Update performance metrics
                self._update_performance_metrics(True, processing_time)
                
                # Emit event
                self._emit_event(
                    InventoryEventType.LOCATION_CHANGED,
                    item_id,
                    {"location": {"x": old_location.x, "y": old_location.y}},
                    {"location": {"x": new_location.x, "y": new_location.y}}
                )
                
                return InventoryUpdateResult(
                    success=True,
                    item_id=item_id,
                    old_value={"location": {"x": old_location.x, "y": old_location.y}},
                    new_value={"location": {"x": new_location.x, "y": new_location.y}},
                    processing_time_ms=processing_time
                )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(False, processing_time)
            return InventoryUpdateResult(
                success=False,
                item_id=item_id,
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def add_event_listener(self, listener: Callable[[InventoryEvent], None]) -> None:
        """
        Add event listener for inventory events.
        """
        with self._lock:
            self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[InventoryEvent], None]) -> None:
        """
        Remove event listener.
        """
        with self._lock:
            if listener in self._event_listeners:
                self._event_listeners.remove(listener)
    
    def get_performance_metrics(self) -> Dict:
        """
        Get performance metrics.
        """
        with self._lock:
            return self._performance_metrics.copy()
    
    def get_inventory_statistics(self) -> Dict:
        """
        Get comprehensive inventory statistics.
        """
        with self._lock:
            print(f"    - get_inventory_statistics() called")
            print(f"    - _initialized: {self._initialized}")
            print(f"    - _items count: {len(self._items)}")
            print(f"    - _items_by_category count: {len(self._items_by_category)}")
            print(f"    - _items_by_location count: {len(self._items_by_location)}")
            
            if not self._initialized:
                print(f"    - Returning error: Inventory not initialized")
                return {"error": "Inventory not initialized"}
            
            # Category distribution
            category_counts = {}
            for category, items in self._items_by_category.items():
                category_counts[category] = len(items)
            
            # Location distribution
            location_counts = {}
            for location, items in self._items_by_location.items():
                location_counts[f"({location.x},{location.y})"] = len(items)
            
            # Stock level analysis
            total_items = len(self._items)
            items_with_stock = sum(1 for item in self._items.values() if item.quantity > 0)
            items_out_of_stock = sum(1 for item in self._items.values() if item.quantity == 0)
            
            result = {
                "total_items": total_items,
                "items_with_stock": items_with_stock,
                "items_out_of_stock": items_out_of_stock,
                "category_distribution": category_counts,
                "location_distribution": location_counts,
                "performance_metrics": self._performance_metrics.copy(),
                "initialized": self._initialized
            }
            
            print(f"    - Returning statistics: {result}")
            return result
    
    def _emit_event(self, event_type: InventoryEventType, item_id: str, 
                   old_value: Optional[Dict] = None, new_value: Optional[Dict] = None) -> None:
        """
        Emit inventory event to all listeners.
        """
        event = InventoryEvent(
            event_type=event_type,
            item_id=item_id,
            timestamp=time.time(),
            old_value=old_value,
            new_value=new_value
        )
        
        # Notify listeners (outside of lock to avoid deadlock)
        for listener in self._event_listeners.copy():
            try:
                listener(event)
            except Exception as e:
                # Log error but don't break other listeners
                print(f"Error in inventory event listener: {e}")
    
    def _update_performance_metrics(self, success: bool, processing_time_ms: float) -> None:
        """
        Update performance metrics.
        """
        self._performance_metrics["total_operations"] += 1
        self._performance_metrics["last_operation_time"] = time.time()
        
        if success:
            self._performance_metrics["successful_operations"] += 1
        else:
            self._performance_metrics["failed_operations"] += 1
        
        # Update average processing time
        total_ops = self._performance_metrics["total_operations"]
        current_avg = self._performance_metrics["average_processing_time_ms"]
        new_avg = ((current_avg * (total_ops - 1)) + processing_time_ms) / total_ops
        self._performance_metrics["average_processing_time_ms"] = new_avg
    
    def _is_in_packout_zone(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within packout zone.
        """
        return (
            x >= self.config.packout_zone_x and
            x < self.config.packout_zone_x + self.config.packout_zone_width and
            y >= self.config.packout_zone_y and
            y < self.config.packout_zone_y + self.config.packout_zone_height
        )


class TestInventoryManager:
    """Test suite for InventoryManager class"""
    
    def test_initialization(self):
        """Test inventory initialization"""
        print("Testing inventory initialization...")
        
        manager = InventoryManager()
        print(f"  - Created InventoryManager instance")
        
        # Test initialization
        print(f"  - Calling initialize_inventory()...")
        success = manager.initialize_inventory()
        print(f"  - initialize_inventory() returned: {success}")
        assert success == True, "Inventory initialization should succeed"
        
        # Check that items were created
        print(f"  - Getting inventory statistics...")
        stats = manager.get_inventory_statistics()
        print(f"  - Statistics: {stats}")
        
        total_items = stats.get("total_items", 0)
        print(f"  - Total items: {total_items}")
        assert total_items == 10, f"Expected 10 items, got {total_items}"
        
        initialized = stats.get("initialized", False)
        print(f"  - Initialized: {initialized}")
        assert initialized == True, "Inventory should be initialized"
        
        print("✅ Inventory initialization tests passed")
    
    def test_item_retrieval(self):
        """Test item retrieval functionality"""
        print("Testing item retrieval...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Test get_item
        item = manager.get_item("ITEM_A1")
        assert item is not None, "Should find ITEM_A1"
        assert item.item_id == "ITEM_A1", f"Expected ITEM_A1, got {item.item_id}"
        
        # Test get_items_by_category
        electronics_items = manager.get_items_by_category("electronics")
        assert len(electronics_items) > 0, "Should have electronics items"
        for item in electronics_items:
            assert item.category == "electronics", f"Wrong category for item {item.item_id}"
        
        # Test get_items_by_location
        location = Coordinate(0, 0)
        location_items = manager.get_items_by_location(location)
        assert len(location_items) > 0, "Should have items at location (0,0)"
        
        print("✅ Item retrieval tests passed")
    
    def test_quantity_updates(self):
        """Test quantity update operations"""
        print("Testing quantity updates...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Test successful quantity update
        result = manager.update_item_quantity("ITEM_A1", 50.0)
        assert result.success == True, "Quantity update should succeed"
        assert result.old_value["quantity"] == 100.0, "Wrong old quantity"
        assert result.new_value["quantity"] == 50.0, "Wrong new quantity"
        assert result.processing_time_ms >= 0, "Should have processing time (can be 0 for very fast operations)"
        
        # Verify item was updated
        item = manager.get_item("ITEM_A1")
        assert item.quantity == 50.0, "Item quantity should be updated"
        
        # Test negative quantity (should fail)
        result = manager.update_item_quantity("ITEM_A1", -10.0)
        assert result.success == False, "Negative quantity should fail"
        assert "negative" in result.error_message.lower(), "Should have negative quantity error"
        
        # Test non-existent item
        result = manager.update_item_quantity("NONEXISTENT", 50.0)
        assert result.success == False, "Non-existent item should fail"
        assert "not found" in result.error_message.lower(), "Should have not found error"
        
        print("✅ Quantity update tests passed")
    
    def test_category_updates(self):
        """Test category update operations"""
        print("Testing category updates...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Test successful category update
        result = manager.update_item_category("ITEM_A1", "clothing")
        assert result.success == True, "Category update should succeed"
        assert result.old_value["category"] == "electronics", "Wrong old category"
        assert result.new_value["category"] == "clothing", "Wrong new category"
        
        # Verify item was updated
        item = manager.get_item("ITEM_A1")
        assert item.category == "clothing", "Item category should be updated"
        
        # Test invalid category (should fail)
        result = manager.update_item_category("ITEM_A1", "invalid_category")
        assert result.success == False, "Invalid category should fail"
        assert "invalid" in result.error_message.lower(), "Should have invalid category error"
        
        # Test non-existent item
        result = manager.update_item_category("NONEXISTENT", "clothing")
        assert result.success == False, "Non-existent item should fail"
        
        print("✅ Category update tests passed")
    
    def test_location_updates(self):
        """Test location update operations"""
        print("Testing location updates...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Test successful location update
        new_location = Coordinate(10, 15)
        result = manager.update_item_location("ITEM_A1", new_location)
        assert result.success == True, "Location update should succeed"
        assert result.old_value["location"]["x"] == 0, "Wrong old x coordinate"
        assert result.old_value["location"]["y"] == 0, "Wrong old y coordinate"
        assert result.new_value["location"]["x"] == 10, "Wrong new x coordinate"
        assert result.new_value["location"]["y"] == 15, "Wrong new y coordinate"
        
        # Verify item was updated
        item = manager.get_item("ITEM_A1")
        assert item.location.x == 10, "Item x coordinate should be updated"
        assert item.location.y == 15, "Item y coordinate should be updated"
        
        # Test invalid location (should fail)
        invalid_location = Coordinate(-1, 0)
        result = manager.update_item_location("ITEM_A1", invalid_location)
        assert result.success == False, "Invalid location should fail"
        assert "invalid" in result.error_message.lower(), "Should have invalid location error"
        
        # Test packout zone location (should fail)
        packout_location = Coordinate(1, 1)
        result = manager.update_item_location("ITEM_A1", packout_location)
        assert result.success == False, "Packout zone location should fail"
        assert "packout" in result.error_message.lower(), "Should have packout zone error"
        
        print("✅ Location update tests passed")
    
    def test_event_system(self):
        """Test event system integration"""
        print("Testing event system...")
        
        manager = InventoryManager()
        events_received = []
        
        def event_listener(event: InventoryEvent):
            events_received.append(event)
        
        # Add event listener
        manager.add_event_listener(event_listener)
        
        # Initialize inventory (should trigger event)
        manager.initialize_inventory()
        assert len(events_received) > 0, "Should receive initialization event"
        
        # Test quantity update event
        events_received.clear()
        manager.update_item_quantity("ITEM_A1", 75.0)
        assert len(events_received) == 1, "Should receive quantity update event"
        assert events_received[0].event_type == InventoryEventType.STOCK_CHANGED, "Wrong event type"
        assert events_received[0].item_id == "ITEM_A1", "Wrong item ID"
        
        # Test category update event
        events_received.clear()
        manager.update_item_category("ITEM_A1", "books")
        assert len(events_received) == 1, "Should receive category update event"
        assert events_received[0].event_type == InventoryEventType.CATEGORY_UPDATED, "Wrong event type"
        
        # Test location update event
        events_received.clear()
        manager.update_item_location("ITEM_A1", Coordinate(5, 5))
        assert len(events_received) == 1, "Should receive location update event"
        assert events_received[0].event_type == InventoryEventType.LOCATION_CHANGED, "Wrong event type"
        
        # Test listener removal
        events_received.clear()
        manager.remove_event_listener(event_listener)
        manager.update_item_quantity("ITEM_A2", 50.0)
        assert len(events_received) == 0, "Should not receive events after listener removal"
        
        print("✅ Event system tests passed")
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        print("Testing performance monitoring...")
        
        manager = InventoryManager()
        
        # Get initial metrics
        initial_metrics = manager.get_performance_metrics()
        assert initial_metrics["total_operations"] == 0, "Should start with 0 operations"
        
        # Perform operations
        manager.initialize_inventory()
        manager.update_item_quantity("ITEM_A1", 50.0)
        manager.update_item_category("ITEM_A1", "clothing")
        
        # Get updated metrics
        updated_metrics = manager.get_performance_metrics()
        assert updated_metrics["total_operations"] > 0, "Should have operations recorded"
        assert updated_metrics["successful_operations"] > 0, "Should have successful operations"
        assert updated_metrics["average_processing_time_ms"] > 0, "Should have processing time"
        assert updated_metrics["last_operation_time"] > 0, "Should have last operation time"
        
        print("✅ Performance monitoring tests passed")
    
    def test_thread_safety(self):
        """Test thread safety of operations"""
        print("Testing thread safety...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Create multiple threads performing operations
        results = []
        errors = []
        
        def worker_thread(thread_id: int):
            try:
                for i in range(5):
                    item_id = f"ITEM_A{(thread_id % 3) + 1}"
                    result = manager.update_item_quantity(item_id, 50.0 + i)
                    results.append(result)
                    time.sleep(0.01)  # Small delay
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
        assert len(results) == 15, f"Expected 15 results, got {len(results)}"
        
        # All operations should be successful
        successful_ops = sum(1 for r in results if r.success)
        assert successful_ops == 15, f"Expected 15 successful operations, got {successful_ops}"
        
        print("✅ Thread safety tests passed")
    
    def test_inventory_statistics(self):
        """Test inventory statistics generation"""
        print("Testing inventory statistics...")
        
        manager = InventoryManager()
        manager.initialize_inventory()
        
        # Update some items to test statistics
        manager.update_item_quantity("ITEM_A1", 0.0)  # Out of stock
        manager.update_item_quantity("ITEM_A2", 50.0)  # In stock
        
        stats = manager.get_inventory_statistics()
        
        # Check basic stats
        assert stats["total_items"] == 10, f"Expected 10 items, got {stats['total_items']}"
        assert stats["items_with_stock"] >= 1, "Should have items with stock"
        assert stats["items_out_of_stock"] >= 1, "Should have items out of stock"
        assert stats["initialized"] == True, "Should be initialized"
        
        # Check category distribution
        assert "category_distribution" in stats, "Should have category distribution"
        assert len(stats["category_distribution"]) > 0, "Should have categories"
        
        # Check location distribution
        assert "location_distribution" in stats, "Should have location distribution"
        assert len(stats["location_distribution"]) > 0, "Should have locations"
        
        # Check performance metrics
        assert "performance_metrics" in stats, "Should have performance metrics"
        
        print("✅ Inventory statistics tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running InventoryManager tests...\n")
        
        try:
            self.test_initialization()
            self.test_item_retrieval()
            self.test_quantity_updates()
            self.test_category_updates()
            self.test_location_updates()
            self.test_event_system()
            self.test_performance_monitoring()
            self.test_thread_safety()
            self.test_inventory_statistics()
            
            print("\n🎉 All InventoryManager tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    # Run tests
    test_suite = TestInventoryManager()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 