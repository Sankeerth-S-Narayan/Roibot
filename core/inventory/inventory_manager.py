"""
Inventory Manager for Warehouse Inventory Management

This module provides the InventoryManager class for centralized inventory management
with real-time updates, atomic operations, and event system integration.
"""

import time
import threading
from typing import List, Dict, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

from .inventory_item import InventoryItem
from .item_generator import ItemGenerator, ItemPlacementConfig
from core.layout.coordinate import Coordinate

# Ensure Coordinate is hashable for use as dictionary key
if not hasattr(Coordinate, '__hash__'):
    def coordinate_hash(self):
        return hash((self.x, self.y))
    Coordinate.__hash__ = coordinate_hash


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


class InventoryManager:
    """
    Centralized inventory management system with real-time updates.
    
    Features:
    - Atomic inventory operations
    - Real-time stock level tracking
    - Event system integration
    - Performance monitoring
    - Thread-safe operations
    - Comprehensive validation
    """
    
    def __init__(self, config: ItemPlacementConfig = None):
        """
        Initialize InventoryManager with configuration.
        
        Args:
            config: ItemPlacementConfig for warehouse dimensions
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
        Initialize inventory with 500 items using ItemGenerator.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            with self._lock:
                if self._initialized:
                    return True
                
                start_time = time.time()
                
                # Generate items using ItemGenerator
                generator = ItemGenerator(self.config)
                items = generator.generate_all_items()
                
                # Populate inventory data structures
                for item in items:
                    self._items[item.item_id] = item
                    
                    # Index by location
                    if item.location not in self._items_by_location:
                        self._items_by_location[item.location] = []
                    self._items_by_location[item.location].append(item)
                    
                    # Index by category
                    if item.category not in self._items_by_category:
                        self._items_by_category[item.category] = []
                    self._items_by_category[item.category].append(item)
                
                self._initialized = True
                processing_time = (time.time() - start_time) * 1000
                
                # Update performance metrics
                self._update_performance_metrics(True, processing_time)
                
                # Emit initialization event
                self._emit_event(InventoryEventType.ITEM_ADDED, "INIT", {
                    "total_items": len(items),
                    "processing_time_ms": processing_time
                })
                
                return True
                
        except Exception as e:
            self._update_performance_metrics(False, 0.0)
            return False
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID to retrieve
            
        Returns:
            InventoryItem if found, None otherwise
        """
        with self._lock:
            return self._items.get(item_id)
    
    def get_items_by_category(self, category: str) -> List[InventoryItem]:
        """
        Get all items in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of items in the category
        """
        with self._lock:
            return self._items_by_category.get(category, []).copy()
    
    def get_items_by_location(self, location: Coordinate) -> List[InventoryItem]:
        """
        Get all items at a location.
        
        Args:
            location: Coordinate to search
            
        Returns:
            List of items at the location
        """
        with self._lock:
            return self._items_by_location.get(location, []).copy()
    
    def update_item_quantity(self, item_id: str, new_quantity: float) -> InventoryUpdateResult:
        """
        Update item quantity with atomic operation.
        
        Args:
            item_id: Item ID to update
            new_quantity: New quantity value
            
        Returns:
            InventoryUpdateResult with operation details
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
        
        Args:
            item_id: Item ID to update
            new_category: New category value
            
        Returns:
            InventoryUpdateResult with operation details
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
        
        Args:
            item_id: Item ID to update
            new_location: New location coordinate
            
        Returns:
            InventoryUpdateResult with operation details
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
        
        Args:
            listener: Callback function for inventory events
        """
        with self._lock:
            self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[InventoryEvent], None]) -> None:
        """
        Remove event listener.
        
        Args:
            listener: Callback function to remove
        """
        with self._lock:
            if listener in self._event_listeners:
                self._event_listeners.remove(listener)
    
    def get_performance_metrics(self) -> Dict:
        """
        Get performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        with self._lock:
            return self._performance_metrics.copy()
    
    def get_inventory_statistics(self) -> Dict:
        """
        Get comprehensive inventory statistics.
        
        Returns:
            Dictionary with inventory statistics
        """
        with self._lock:
            if not self._initialized:
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
            
            return {
                "total_items": total_items,
                "items_with_stock": items_with_stock,
                "items_out_of_stock": items_out_of_stock,
                "category_distribution": category_counts,
                "location_distribution": location_counts,
                "performance_metrics": self._performance_metrics.copy(),
                "initialized": self._initialized
            }
    
    def _emit_event(self, event_type: InventoryEventType, item_id: str, 
                   old_value: Optional[Dict] = None, new_value: Optional[Dict] = None) -> None:
        """
        Emit inventory event to all listeners.
        
        Args:
            event_type: Type of event
            item_id: Item ID involved
            old_value: Previous value (optional)
            new_value: New value (optional)
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
        
        Args:
            success: Whether operation was successful
            processing_time_ms: Processing time in milliseconds
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
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if in packout zone, False otherwise
        """
        return (
            x >= self.config.packout_zone_x and
            x < self.config.packout_zone_x + self.config.packout_zone_width and
            y >= self.config.packout_zone_y and
            y < self.config.packout_zone_y + self.config.packout_zone_height
        ) 