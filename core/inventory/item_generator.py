"""
Item Generator for Warehouse Inventory Management

This module provides the ItemGenerator class for creating 500 unique inventory items
with proper placement, distribution, and category assignment.
"""

import random
import string
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

from .inventory_item import InventoryItem
from core.layout.coordinate import Coordinate


@dataclass
class ItemPlacementConfig:
    """Configuration for item placement in warehouse"""
    warehouse_width: int = 26  # Increased to accommodate packout zone
    warehouse_height: int = 20
    packout_zone_x: int = 1
    packout_zone_y: int = 1
    packout_zone_width: int = 1
    packout_zone_height: int = 1


class ItemGenerator:
    """
    Generates 500 unique inventory items with proper placement and distribution.
    
    Features:
    - Generates 500 unique items with IDs (ITEM_A1 to ITEM_X20)
    - Even distribution across warehouse grid
    - Excludes packout zone from placement
    - Random category assignment
    - Validation and error handling
    """
    
    # Predefined item categories
    CATEGORIES = [
        "electronics", "clothing", "books", "home_goods", "sports",
        "automotive", "toys", "health_beauty", "food_beverages", "office_supplies"
    ]
    
    # Item ID generation parameters
    ID_PREFIX = "ITEM_"
    LETTERS = string.ascii_uppercase  # A-Z
    MAX_NUMBER = 20  # 1-20 (20 items per letter)
    
    def __init__(self, config: ItemPlacementConfig = None):
        """
        Initialize ItemGenerator with placement configuration.
        
        Args:
            config: ItemPlacementConfig for warehouse dimensions and packout zone
        """
        self.config = config or ItemPlacementConfig()
        self._generated_items: List[InventoryItem] = []
        self._used_locations: Set[Tuple[int, int]] = set()
        self._used_ids: Set[str] = set()
        
    def generate_all_items(self) -> List[InventoryItem]:
        """
        Generate all 500 unique inventory items.
        
        Returns:
            List of 500 InventoryItem instances
            
        Raises:
            ValueError: If unable to place all items due to space constraints
        """
        self._generated_items.clear()
        self._used_locations.clear()
        self._used_ids.clear()
        
        # Calculate available locations
        total_locations = self.config.warehouse_width * self.config.warehouse_height
        packout_locations = self.config.packout_zone_width * self.config.packout_zone_height
        available_locations = total_locations - packout_locations
        
        if available_locations < 500:
            raise ValueError(
                f"Insufficient warehouse space. Need 500 locations, "
                f"but only {available_locations} available."
            )
        
        # Generate items
        for i in range(500):
            item = self._generate_single_item(i + 1)
            self._generated_items.append(item)
            
        return self._generated_items.copy()
    
    def _generate_single_item(self, item_number: int) -> InventoryItem:
        """
        Generate a single inventory item.
        
        Args:
            item_number: Sequential number (1-500)
            
        Returns:
            InventoryItem instance
        """
        # Generate unique item ID
        item_id = self._generate_item_id(item_number)
        
        # Find available location
        location = self._find_available_location()
        
        # Assign random category
        category = random.choice(self.CATEGORIES)
        
        # Create inventory item
        item = InventoryItem(
            item_id=item_id,
            location=location,
            quantity=float('inf'),  # Unlimited stock
            category=category
        )
        
        return item
    
    def _generate_item_id(self, item_number: int) -> str:
        """
        Generate unique item ID in format ITEM_A1, ITEM_B3, etc.
        
        Args:
            item_number: Sequential number (1-500)
            
        Returns:
            Unique item ID string
        """
        # Calculate letter and number for ID
        # 500 items = 25 letters (A-Z) × 20 numbers (1-20)
        # Pattern: A1-A20, B1-B20, C1-C20, ..., Y1-Y20
        letter_index = (item_number - 1) // self.MAX_NUMBER
        number = (item_number - 1) % self.MAX_NUMBER + 1
        
        if letter_index >= len(self.LETTERS):
            raise ValueError(f"Cannot generate ID for item {item_number}: too many items")
        
        letter = self.LETTERS[letter_index]
        item_id = f"{self.ID_PREFIX}{letter}{number}"
        
        # Ensure uniqueness
        if item_id in self._used_ids:
            raise ValueError(f"Duplicate item ID generated: {item_id}")
        
        self._used_ids.add(item_id)
        return item_id
    
    def _find_available_location(self) -> Coordinate:
        """
        Find an available location in the warehouse.
        
        Returns:
            Coordinate for available location
            
        Raises:
            ValueError: If no available locations found
        """
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(0, self.config.warehouse_width - 1)
            y = random.randint(0, self.config.warehouse_height - 1)
            
            # Check if location is in packout zone
            if self._is_in_packout_zone(x, y):
                attempts += 1
                continue
            
            # Check if location is already used
            if (x, y) in self._used_locations:
                attempts += 1
                continue
            
            # Location is available
            self._used_locations.add((x, y))
            return Coordinate(x, y)
        
        raise ValueError(
            f"Unable to find available location after {max_attempts} attempts. "
            f"Used locations: {len(self._used_locations)}"
        )
    
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
    
    def get_item_by_id(self, item_id: str) -> InventoryItem:
        """
        Get item by its ID.
        
        Args:
            item_id: Item ID to search for
            
        Returns:
            InventoryItem if found
            
        Raises:
            ValueError: If item not found
        """
        for item in self._generated_items:
            if item.item_id == item_id:
                return item
        raise ValueError(f"Item not found: {item_id}")
    
    def get_items_by_category(self, category: str) -> List[InventoryItem]:
        """
        Get all items in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of items in the category
        """
        return [item for item in self._generated_items if item.category == category]
    
    def get_items_by_location(self, location: Coordinate) -> List[InventoryItem]:
        """
        Get all items at a specific location.
        
        Args:
            location: Coordinate to search
            
        Returns:
            List of items at the location
        """
        return [item for item in self._generated_items if item.location == location]
    
    def get_placement_statistics(self) -> Dict:
        """
        Get statistics about item placement.
        
        Returns:
            Dictionary with placement statistics
        """
        if not self._generated_items:
            return {"error": "No items generated"}
        
        # Category distribution
        category_counts = {}
        for item in self._generated_items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Location distribution
        location_counts = {}
        for item in self._generated_items:
            loc_key = f"({item.location.x},{item.location.y})"
            location_counts[loc_key] = location_counts.get(loc_key, 0) + 1
        
        return {
            "total_items": len(self._generated_items),
            "unique_locations": len(self._used_locations),
            "category_distribution": category_counts,
            "location_distribution": location_counts,
            "packout_zone_excluded": True,
            "warehouse_dimensions": {
                "width": self.config.warehouse_width,
                "height": self.config.warehouse_height
            }
        }
    
    def validate_placement(self) -> Dict:
        """
        Validate item placement for even distribution and constraints.
        
        Returns:
            Dictionary with validation results
        """
        if not self._generated_items:
            return {"error": "No items to validate"}
        
        # Check for duplicates
        item_ids = [item.item_id for item in self._generated_items]
        duplicate_ids = [id for id in item_ids if item_ids.count(id) > 1]
        
        # Check for packout zone violations
        packout_violations = []
        for item in self._generated_items:
            if self._is_in_packout_zone(item.location.x, item.location.y):
                packout_violations.append(item.item_id)
        
        # Check for location duplicates
        location_duplicates = []
        locations = [(item.location.x, item.location.y) for item in self._generated_items]
        for loc in set(locations):
            if locations.count(loc) > 1:
                location_duplicates.append(loc)
        
        return {
            "total_items": len(self._generated_items),
            "duplicate_ids": duplicate_ids,
            "packout_zone_violations": packout_violations,
            "location_duplicates": location_duplicates,
            "validation_passed": (
                len(duplicate_ids) == 0 and
                len(packout_violations) == 0 and
                len(location_duplicates) == 0
            )
        } 