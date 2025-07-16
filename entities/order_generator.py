"""
Order Generation System for Phase 5: Order Management System

This module provides the OrderGenerator class that handles automatic order generation
with configurable timing and item selection. Orders are generated every 30 seconds
by default with 1-4 items per order.

Key Features:
- Automatic order generation with configurable intervals
- Random item selection (1-4 items per order)
- Order ID generation with timestamp format
- Integration with warehouse layout for valid item locations
- Start/stop control for continuous generation
- Comprehensive validation and error handling

Author: Roibot Development Team
Version: 1.0
"""

import time
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .robot_orders import Order, OrderStatus
from core.layout.warehouse_layout import WarehouseLayoutManager
from core.layout.coordinate import Coordinate


class GenerationStatus(Enum):
    """Enumeration for order generation status."""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class OrderGenerator:
    """
    Handles automatic order generation with configurable timing and item selection.
    
    Generates orders every 30 seconds by default with 1-4 items per order.
    Orders are created with valid warehouse coordinates and unique IDs.
    """
    
    def __init__(self, warehouse_layout: WarehouseLayoutManager):
        """
        Initialize the order generator.
        
        Args:
            warehouse_layout: Warehouse layout manager for coordinate validation
        """
        self.warehouse_layout = warehouse_layout
        
        # Generation settings
        self.generation_interval = 30.0  # seconds
        self.min_items_per_order = 1
        self.max_items_per_order = 4
        self.is_generating = False
        self.status = GenerationStatus.STOPPED
        
        # Timing control
        self.last_generation_time = 0.0
        self.generation_start_time = 0.0
        
        # Statistics
        self.total_orders_generated = 0
        self.orders_generated_this_session = 0
        self.generation_errors = 0
        
        # Item pool for random selection
        self._initialize_item_pool()
        
        print("📦 OrderGenerator initialized with 30-second generation interval")
    
    def _initialize_item_pool(self):
        """Initialize the pool of available items for random selection."""
        self.item_pool = []
        
        # Generate items for all valid warehouse locations (excluding packout zone)
        for aisle in range(1, 26):  # 1-25 aisles
            for rack in range(1, 21):  # 1-20 racks
                # Skip packout zone (1, 1)
                if aisle == 1 and rack == 1:
                    continue
                
                # Create item ID with format ITEM_A{aisle}R{rack}
                item_id = f"ITEM_A{aisle:02d}R{rack:02d}"
                position = (aisle, rack)
                
                self.item_pool.append({
                    'item_id': item_id,
                    'position': position,
                    'available': True
                })
        
        print(f"📋 Item pool initialized with {len(self.item_pool)} items")
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure the order generator with settings.
        
        Args:
            config: Configuration dictionary with generation settings
        """
        self.generation_interval = config.get('generation_interval', 30.0)
        self.min_items_per_order = config.get('min_items_per_order', 1)
        self.max_items_per_order = config.get('max_items_per_order', 4)
        
        # Validate configuration
        if self.generation_interval < 1.0:
            raise ValueError("Generation interval must be at least 1 second")
        
        if self.min_items_per_order < 1:
            raise ValueError("Minimum items per order must be at least 1")
        
        if self.max_items_per_order < self.min_items_per_order:
            raise ValueError("Maximum items per order must be >= minimum items")
        
        if self.max_items_per_order > 10:
            raise ValueError("Maximum items per order cannot exceed 10")
        
        print(f"⚙️  OrderGenerator configured: {self.generation_interval}s interval, "
              f"{self.min_items_per_order}-{self.max_items_per_order} items per order")
    
    def start_generation(self):
        """Start automatic order generation."""
        if self.is_generating:
            print("⚠️  Order generation is already running")
            return
        
        self.is_generating = True
        self.status = GenerationStatus.RUNNING
        self.generation_start_time = time.time()
        self.last_generation_time = time.time()
        
        print(f"🚀 Order generation started - generating orders every {self.generation_interval} seconds")
    
    def stop_generation(self):
        """Stop automatic order generation."""
        if not self.is_generating:
            print("⚠️  Order generation is not running")
            return
        
        self.is_generating = False
        self.status = GenerationStatus.STOPPED
        
        print("⏹️  Order generation stopped")
    
    def pause_generation(self):
        """Pause automatic order generation."""
        if not self.is_generating:
            print("⚠️  Order generation is not running")
            return
        
        self.status = GenerationStatus.PAUSED
        print("⏸️  Order generation paused")
    
    def resume_generation(self):
        """Resume automatic order generation."""
        if self.status != GenerationStatus.PAUSED:
            print("⚠️  Order generation is not paused")
            return
        
        self.status = GenerationStatus.RUNNING
        print("▶️  Order generation resumed")
    
    def should_generate_order(self, current_time: float) -> bool:
        """
        Check if an order should be generated based on timing.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            True if order should be generated, False otherwise
        """
        if not self.is_generating or self.status != GenerationStatus.RUNNING:
            return False
        
        time_since_last = current_time - self.last_generation_time
        return time_since_last >= self.generation_interval
    
    def generate_order(self, current_time: float) -> Optional[Order]:
        """
        Generate a new order with random items.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Generated Order object or None if generation failed
        """
        try:
            # Generate order ID with timestamp format
            order_id = self._generate_order_id()
            
            # Select random number of items
            num_items = random.randint(self.min_items_per_order, self.max_items_per_order)
            
            # Select random items from pool
            selected_items = self._select_random_items(num_items)
            
            if not selected_items:
                print("⚠️  No items available for order generation")
                return None
            
            # Extract item IDs and positions
            item_ids = [item['item_id'] for item in selected_items]
            item_positions = [item['position'] for item in selected_items]
            
            # Create order
            order = Order(order_id, item_ids, item_positions)
            
            # Update statistics
            self.total_orders_generated += 1
            self.orders_generated_this_session += 1
            self.last_generation_time = current_time
            
            print(f"📦 Generated order {order_id} with {len(item_ids)} items")
            
            return order
            
        except Exception as e:
            self.generation_errors += 1
            print(f"❌ Error generating order: {e}")
            return None
    
    def _generate_order_id(self) -> str:
        """
        Generate a unique order ID with timestamp format.
        
        Returns:
            Order ID in format ORD_YYYYMMDD_HHMMSS
        """
        timestamp = datetime.now()
        order_id = f"ORD_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Add unique suffix to prevent collisions
        unique_suffix = str(uuid.uuid4())[:8]
        return f"{order_id}_{unique_suffix}"
    
    def _select_random_items(self, num_items: int) -> List[Dict[str, Any]]:
        """
        Select random items from the item pool.
        
        Args:
            num_items: Number of items to select
            
        Returns:
            List of selected item dictionaries
        """
        if num_items > len(self.item_pool):
            print(f"⚠️  Requested {num_items} items but only {len(self.item_pool)} available")
            num_items = len(self.item_pool)
        
        # Select random items without replacement
        selected_items = random.sample(self.item_pool, num_items)
        
        return selected_items
    
    def update(self, current_time: float) -> Optional[Order]:
        """
        Update the order generator and generate orders if needed.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Generated Order object or None if no order generated
        """
        if self.should_generate_order(current_time):
            return self.generate_order(current_time)
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the order generator.
        
        Returns:
            Dictionary with generator status information
        """
        return {
            'status': self.status.value,
            'is_generating': self.is_generating,
            'generation_interval': self.generation_interval,
            'min_items_per_order': self.min_items_per_order,
            'max_items_per_order': self.max_items_per_order,
            'total_orders_generated': self.total_orders_generated,
            'orders_generated_this_session': self.orders_generated_this_session,
            'generation_errors': self.generation_errors,
            'time_since_last_generation': time.time() - self.last_generation_time if self.last_generation_time > 0 else None,
            'available_items': len(self.item_pool)
        }
    
    def reset_statistics(self):
        """Reset generation statistics."""
        self.orders_generated_this_session = 0
        self.generation_errors = 0
        print("📊 Order generation statistics reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information for the order generator.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'generator_status': self.get_status(),
            'item_pool_size': len(self.item_pool),
            'sample_items': self.item_pool[:5] if self.item_pool else [],
            'generation_timing': {
                'last_generation': self.last_generation_time,
                'generation_start': self.generation_start_time,
                'time_since_last': time.time() - self.last_generation_time if self.last_generation_time > 0 else 0
            }
        } 