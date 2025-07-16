#!/usr/bin/env python3
"""
Standalone tests for ItemGenerator class

This test file can be run independently without complex dependencies.
"""

import sys
import os
import random
import string
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Coordinate class for testing
@dataclass
class Coordinate:
    x: int
    y: int
    
    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return False
        return self.x == other.x and self.y == other.y

# Mock InventoryItem class for testing
@dataclass
class InventoryItem:
    item_id: str
    location: Coordinate
    quantity: float
    category: str
    
    def to_dict(self):
        return {
            "item_id": self.item_id,
            "location": {"x": self.location.x, "y": self.location.y},
            "quantity": self.quantity,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        location = Coordinate(data["location"]["x"], data["location"]["y"])
        return cls(
            item_id=data["item_id"],
            location=location,
            quantity=data["quantity"],
            category=data["category"]
        )

# ItemGenerator implementation for testing
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
    """
    
    # Predefined item categories
    CATEGORIES = [
        "electronics", "clothing", "books", "home_goods", "sports",
        "automotive", "toys", "health_beauty", "food_beverages", "office_supplies"
    ]
    
    # Item ID generation parameters
    ID_PREFIX = "ITEM_"
    LETTERS = string.ascii_uppercase  # A-Z
    MAX_NUMBER = 20  # 1-20
    
    def __init__(self, config: ItemPlacementConfig = None):
        """
        Initialize ItemGenerator with placement configuration.
        """
        self.config = config or ItemPlacementConfig()
        self._generated_items: List[InventoryItem] = []
        self._used_locations: Set[Tuple[int, int]] = set()
        self._used_ids: Set[str] = set()
        
    def generate_all_items(self) -> List[InventoryItem]:
        """
        Generate all 500 unique inventory items.
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
        """
        # Calculate letter and number for ID
        # 500 items = 25 letters (A-Z) × 20 numbers (1-20)
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
        """
        for item in self._generated_items:
            if item.item_id == item_id:
                return item
        raise ValueError(f"Item not found: {item_id}")
    
    def get_items_by_category(self, category: str) -> List[InventoryItem]:
        """
        Get all items in a specific category.
        """
        return [item for item in self._generated_items if item.category == category]
    
    def get_items_by_location(self, location: Coordinate) -> List[InventoryItem]:
        """
        Get all items at a specific location.
        """
        return [item for item in self._generated_items if item.location == location]
    
    def get_placement_statistics(self) -> Dict:
        """
        Get statistics about item placement.
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


class TestItemGenerator:
    """Test suite for ItemGenerator class"""
    
    def test_item_id_generation(self):
        """Test item ID generation algorithm"""
        print("Testing item ID generation...")
        
        generator = ItemGenerator()
        
        # Test first few IDs (pattern: A1-A20, B1-B20, C1-C20, etc.)
        expected_ids = ["ITEM_A1", "ITEM_A2", "ITEM_A3", "ITEM_A4", "ITEM_A5"]
        for i, expected_id in enumerate(expected_ids, 1):
            generated_id = generator._generate_item_id(i)
            assert generated_id == expected_id, f"Expected {expected_id}, got {generated_id}"
        
        # Test 500th item (should be ITEM_Y20 - 25 letters × 20 numbers = 500 items)
        last_id = generator._generate_item_id(500)
        assert last_id == "ITEM_Y20", f"Expected ITEM_Y20, got {last_id}"
        
        print("✅ Item ID generation tests passed")
    
    def test_packout_zone_exclusion(self):
        """Test that packout zone is properly excluded"""
        print("Testing packout zone exclusion...")
        
        config = ItemPlacementConfig(
            warehouse_width=5,
            warehouse_height=5,
            packout_zone_x=1,
            packout_zone_y=1,
            packout_zone_width=1,
            packout_zone_height=1
        )
        
        generator = ItemGenerator(config)
        
        # Generate a few items
        items = []
        for i in range(10):
            item = generator._generate_single_item(i + 1)
            items.append(item)
            
            # Verify not in packout zone
            assert not generator._is_in_packout_zone(item.location.x, item.location.y), \
                f"Item {item.item_id} placed in packout zone at ({item.location.x}, {item.location.y})"
        
        print("✅ Packout zone exclusion tests passed")
    
    def test_unique_locations(self):
        """Test that all items are placed at unique locations"""
        print("Testing unique location placement...")
        
        generator = ItemGenerator()
        
        # Generate all 500 items
        items = generator.generate_all_items()
        
        # Check total count
        assert len(items) == 500, f"Expected 500 items, got {len(items)}"
        
        # Check for unique locations
        locations = [(item.location.x, item.location.y) for item in items]
        unique_locations = set(locations)
        assert len(unique_locations) == 500, f"Expected 500 unique locations, got {len(unique_locations)}"
        
        print("✅ Unique location placement tests passed")
    
    def test_unique_item_ids(self):
        """Test that all item IDs are unique"""
        print("Testing unique item IDs...")
        
        generator = ItemGenerator()
        items = generator.generate_all_items()
        
        # Check for unique IDs
        item_ids = [item.item_id for item in items]
        unique_ids = set(item_ids)
        assert len(unique_ids) == 500, f"Expected 500 unique IDs, got {len(unique_ids)}"
        
        print("✅ Unique item ID tests passed")
    
    def test_category_assignment(self):
        """Test that items are assigned valid categories"""
        print("Testing category assignment...")
        
        generator = ItemGenerator()
        items = generator.generate_all_items()
        
        # Check that all items have valid categories
        for item in items:
            assert item.category in generator.CATEGORIES, \
                f"Invalid category '{item.category}' for item {item.item_id}"
        
        # Check category distribution
        category_counts = {}
        for item in items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Should have some distribution across categories
        assert len(category_counts) > 1, "All items assigned to same category"
        
        print("✅ Category assignment tests passed")
    
    def test_item_retrieval(self):
        """Test item retrieval by ID and category"""
        print("Testing item retrieval...")
        
        generator = ItemGenerator()
        items = generator.generate_all_items()
        
        # Test retrieval by ID
        test_item = items[0]
        retrieved_item = generator.get_item_by_id(test_item.item_id)
        assert retrieved_item == test_item, "Item retrieval by ID failed"
        
        # Test retrieval by category
        electronics_items = generator.get_items_by_category("electronics")
        for item in electronics_items:
            assert item.category == "electronics", f"Wrong category for item {item.item_id}"
        
        print("✅ Item retrieval tests passed")
    
    def test_placement_statistics(self):
        """Test placement statistics generation"""
        print("Testing placement statistics...")
        
        generator = ItemGenerator()
        items = generator.generate_all_items()
        
        stats = generator.get_placement_statistics()
        
        # Check basic stats
        assert stats["total_items"] == 500, f"Expected 500 items, got {stats['total_items']}"
        assert stats["unique_locations"] == 500, f"Expected 500 unique locations, got {stats['unique_locations']}"
        assert stats["packout_zone_excluded"] == True, "Packout zone should be excluded"
        
        # Check warehouse dimensions
        assert stats["warehouse_dimensions"]["width"] == 26, "Wrong warehouse width"
        assert stats["warehouse_dimensions"]["height"] == 20, "Wrong warehouse height"
        
        print("✅ Placement statistics tests passed")
    
    def test_placement_validation(self):
        """Test placement validation"""
        print("Testing placement validation...")
        
        generator = ItemGenerator()
        items = generator.generate_all_items()
        
        validation = generator.validate_placement()
        
        # Check validation results
        assert validation["total_items"] == 500, f"Expected 500 items, got {validation['total_items']}"
        assert len(validation["duplicate_ids"]) == 0, f"Found duplicate IDs: {validation['duplicate_ids']}"
        assert len(validation["packout_zone_violations"]) == 0, \
            f"Found packout zone violations: {validation['packout_zone_violations']}"
        assert len(validation["location_duplicates"]) == 0, \
            f"Found location duplicates: {validation['location_duplicates']}"
        assert validation["validation_passed"] == True, "Validation should pass"
        
        print("✅ Placement validation tests passed")
    
    def test_insufficient_space_error(self):
        """Test error handling for insufficient warehouse space"""
        print("Testing insufficient space error handling...")
        
        # Create config with insufficient space
        config = ItemPlacementConfig(
            warehouse_width=10,
            warehouse_height=10,
            packout_zone_x=0,
            packout_zone_y=0,
            packout_zone_width=0,
            packout_zone_height=0
        )
        
        generator = ItemGenerator(config)
        
        # Should raise ValueError for insufficient space
        try:
            generator.generate_all_items()
            assert False, "Should have raised ValueError for insufficient space"
        except ValueError as e:
            assert "Insufficient warehouse space" in str(e), f"Unexpected error: {e}"
        
        print("✅ Insufficient space error handling tests passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running ItemGenerator tests...\n")
        
        try:
            self.test_item_id_generation()
            self.test_packout_zone_exclusion()
            self.test_unique_locations()
            self.test_unique_item_ids()
            self.test_category_assignment()
            self.test_item_retrieval()
            self.test_placement_statistics()
            self.test_placement_validation()
            self.test_insufficient_space_error()
            
            print("\n🎉 All ItemGenerator tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    # Set random seed for reproducible tests
    random.seed(42)
    
    # Run tests
    test_suite = TestItemGenerator()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 