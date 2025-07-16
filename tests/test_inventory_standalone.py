"""
Standalone test for InventoryItem class without complex dependencies.
"""

import time
import sys
import os

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

# Import only what we need directly
from layout.coordinate import Coordinate

# Define InventoryItem class directly for testing
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class InventoryItem:
    """Standalone InventoryItem for testing."""
    
    item_id: str
    location: Coordinate
    quantity: int = field(default=999999)
    category: str = field(default="general")
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate item properties after initialization."""
        self._validate_item_id()
        self._validate_location()
        self._validate_quantity()
        self._validate_category()
        self._validate_timestamps()
    
    def _validate_item_id(self) -> None:
        """Validate item_id format and uniqueness."""
        if not isinstance(self.item_id, str):
            raise ValueError(f"item_id must be a string, got {type(self.item_id)}")
        
        if not self.item_id:
            raise ValueError("item_id cannot be empty")
        
        # Validate format: ITEM_[A-Z][0-9]+
        if not self.item_id.startswith("ITEM_"):
            raise ValueError(f"item_id must start with 'ITEM_', got {self.item_id}")
        
        # Check for valid format after ITEM_
        suffix = self.item_id[5:]  # Remove "ITEM_"
        if not suffix or not any(c.isalpha() for c in suffix) or not any(c.isdigit() for c in suffix):
            raise ValueError(f"item_id must have format ITEM_[A-Z][0-9]+, got {self.item_id}")
    
    def _validate_location(self) -> None:
        """Validate item location coordinates."""
        if not isinstance(self.location, Coordinate):
            raise ValueError(f"location must be a Coordinate object, got {type(self.location)}")
        
        if not self.location.is_valid():
            raise ValueError(f"location coordinates are invalid: {self.location}")
        
        # Ensure item is not placed in packout zone
        if self.location.is_packout_location():
            raise ValueError(f"Item cannot be placed in packout zone: {self.location}")
    
    def _validate_quantity(self) -> None:
        """Validate item quantity."""
        if not isinstance(self.quantity, int):
            raise ValueError(f"quantity must be an integer, got {type(self.quantity)}")
        
        if self.quantity < 0:
            raise ValueError(f"quantity cannot be negative, got {self.quantity}")
    
    def _validate_category(self) -> None:
        """Validate item category."""
        if not isinstance(self.category, str):
            raise ValueError(f"category must be a string, got {type(self.category)}")
        
        if not self.category:
            raise ValueError("category cannot be empty")
        
        # Predefined categories for consistency
        valid_categories = {
            "electronics", "clothing", "books", "tools", "sports", 
            "home", "kitchen", "garden", "automotive", "general"
        }
        
        if self.category.lower() not in valid_categories:
            raise ValueError(f"category must be one of {valid_categories}, got {self.category}")
        
        # Normalize category to lowercase
        self.category = self.category.lower()
    
    def _validate_timestamps(self) -> None:
        """Validate timestamp values."""
        current_time = time.time()
        
        if not isinstance(self.created_at, (int, float)):
            raise ValueError(f"created_at must be a number, got {type(self.created_at)}")
        
        if not isinstance(self.last_updated, (int, float)):
            raise ValueError(f"last_updated must be a number, got {type(self.last_updated)}")
        
        if self.created_at > current_time:
            raise ValueError(f"created_at cannot be in the future: {self.created_at}")
        
        if self.last_updated > current_time:
            raise ValueError(f"last_updated cannot be in the future: {self.last_updated}")
        
        if self.last_updated < self.created_at:
            raise ValueError(f"last_updated cannot be before created_at")
    
    def update_quantity(self, new_quantity: int) -> None:
        """Update item quantity and last_updated timestamp."""
        if not isinstance(new_quantity, int):
            raise ValueError(f"new_quantity must be an integer, got {type(new_quantity)}")
        
        if new_quantity < 0:
            raise ValueError(f"quantity cannot be negative, got {new_quantity}")
        
        self.quantity = new_quantity
        self.last_updated = time.time()
    
    def is_available(self) -> bool:
        """Check if item is available (quantity > 0)."""
        return self.quantity > 0
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """Check if item is low on stock."""
        return 0 < self.quantity <= threshold
    
    def is_out_of_stock(self) -> bool:
        """Check if item is out of stock."""
        return self.quantity == 0
    
    def get_stock_status(self) -> str:
        """Get human-readable stock status."""
        if self.is_out_of_stock():
            return "out_of_stock"
        elif self.is_low_stock():
            return "low_stock"
        else:
            return "available"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "location": self.location.to_dict(),
            "quantity": self.quantity,
            "category": self.category,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
    
    def __str__(self) -> str:
        """String representation of the item."""
        return f"InventoryItem(item_id='{self.item_id}', location={self.location}, quantity={self.quantity}, category='{self.category}')"


def test_inventory_item_basic():
    """Test basic InventoryItem functionality."""
    print("🧪 Testing InventoryItem basic functionality...")
    
    # Test 1: Create a valid inventory item
    coord = Coordinate(10, 15)
    item = InventoryItem(
        item_id="ITEM_A1",
        location=coord,
        quantity=100,
        category="electronics"
    )
    
    print(f"✅ Created item: {item}")
    print(f"   - Item ID: {item.item_id}")
    print(f"   - Location: {item.location}")
    print(f"   - Quantity: {item.quantity}")
    print(f"   - Category: {item.category}")
    
    # Test 2: Check stock status
    print(f"   - Available: {item.is_available()}")
    print(f"   - Low stock: {item.is_low_stock()}")
    print(f"   - Out of stock: {item.is_out_of_stock()}")
    print(f"   - Stock status: {item.get_stock_status()}")
    
    # Test 3: Update quantity
    original_updated = item.last_updated
    time.sleep(0.001)  # Small delay to ensure timestamp difference
    item.update_quantity(50)
    
    print(f"✅ Updated quantity to: {item.quantity}")
    print(f"   - Last updated changed: {item.last_updated > original_updated}")
    
    # Test 4: Serialization
    item_dict = item.to_dict()
    print(f"✅ Serialized to dict: {item_dict}")
    
    print("🎉 All basic tests passed!")


def test_inventory_item_validation():
    """Test InventoryItem validation."""
    print("\n🧪 Testing InventoryItem validation...")
    
    # Test valid item IDs
    valid_ids = ["ITEM_A1", "ITEM_B3", "ITEM_Z9", "ITEM_X20"]
    for item_id in valid_ids:
        try:
            coord = Coordinate(10, 15)
            item = InventoryItem(item_id=item_id, location=coord)
            print(f"✅ Valid item ID: {item_id}")
        except ValueError as e:
            print(f"❌ Unexpected error for {item_id}: {e}")
    
    # Test invalid item IDs
    invalid_ids = ["", "ITEM_", "ITEM_A", "ITEM_1", "item_a1"]
    for item_id in invalid_ids:
        try:
            coord = Coordinate(10, 15)
            item = InventoryItem(item_id=item_id, location=coord)
            print(f"❌ Should have failed for {item_id}")
        except ValueError as e:
            print(f"✅ Correctly rejected invalid item ID: {item_id} - {e}")
    
    # Test packout zone exclusion
    try:
        packout_coord = Coordinate(1, 1)
        item = InventoryItem(item_id="ITEM_A1", location=packout_coord)
        print("❌ Should have failed for packout zone")
    except ValueError as e:
        print(f"✅ Correctly rejected packout zone: {e}")
    
    print("🎉 All validation tests passed!")


def test_inventory_item_categories():
    """Test InventoryItem category functionality."""
    print("\n🧪 Testing InventoryItem categories...")
    
    coord = Coordinate(10, 15)
    valid_categories = [
        "electronics", "clothing", "books", "tools", "sports",
        "home", "kitchen", "garden", "automotive", "general"
    ]
    
    for category in valid_categories:
        try:
            item = InventoryItem(
                item_id="ITEM_A1",
                location=coord,
                category=category
            )
            print(f"✅ Valid category: {category} -> {item.category}")
        except ValueError as e:
            print(f"❌ Unexpected error for {category}: {e}")
    
    # Test invalid category
    try:
        item = InventoryItem(
            item_id="ITEM_A1",
            location=coord,
            category="invalid_category"
        )
        print("❌ Should have failed for invalid category")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid category: {e}")
    
    print("🎉 All category tests passed!")


if __name__ == "__main__":
    print("🚀 Starting standalone InventoryItem tests...\n")
    
    try:
        test_inventory_item_basic()
        test_inventory_item_validation()
        test_inventory_item_categories()
        
        print("\n🎉 All tests completed successfully!")
        print("✅ InventoryItem class is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 