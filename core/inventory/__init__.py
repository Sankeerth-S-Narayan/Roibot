"""
Inventory Management System

This module provides comprehensive inventory management capabilities for the warehouse simulation,
including item tracking, real-time updates, and integration with order management.

Components:
- InventoryItem: Core inventory item entity
- ItemGenerator: 500 unique item generation and placement
- InventoryManager: Centralized inventory management
- InventorySync: Order management integration
- InventoryAnalytics: Performance metrics and analytics
"""

from .inventory_item import InventoryItem
from .item_generator import ItemGenerator
from .inventory_manager import InventoryManager
from .inventory_sync import InventorySyncManager
__all__ = [
    'InventoryItem',
    'ItemGenerator', 
    'InventoryManager',
    'InventorySyncManager'
] 