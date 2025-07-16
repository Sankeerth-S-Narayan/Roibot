"""
Inventory Item Entity

This module provides the core InventoryItem class for representing inventory items
in the warehouse simulation with comprehensive validation and serialization capabilities.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from core.layout.coordinate import Coordinate


@dataclass
class InventoryItem:
    """
    Represents an inventory item in the warehouse simulation.
    
    Attributes:
        item_id: Unique identifier for the item (e.g., ITEM_A1, ITEM_B3)
        location: Warehouse coordinates where item is located
        quantity: Current stock quantity (unlimited stock configurable)
        category: Item category (electronics, clothing, books, tools, etc.)
        created_at: Timestamp when item was created
        last_updated: Timestamp when item was last updated
    """
    
    item_id: str
    location: Coordinate
    quantity: int = field(default=999999)  # Unlimited stock by default
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
        """
        Update item quantity and last_updated timestamp.
        
        Args:
            new_quantity: New quantity value
            
        Raises:
            ValueError: If new_quantity is invalid
        """
        if not isinstance(new_quantity, int):
            raise ValueError(f"new_quantity must be an integer, got {type(new_quantity)}")
        
        if new_quantity < 0:
            raise ValueError(f"quantity cannot be negative, got {new_quantity}")
        
        self.quantity = new_quantity
        self.last_updated = time.time()
    
    def update_location(self, new_location: Coordinate) -> None:
        """
        Update item location and last_updated timestamp.
        
        Args:
            new_location: New location coordinates
            
        Raises:
            ValueError: If new_location is invalid
        """
        if not isinstance(new_location, Coordinate):
            raise ValueError(f"new_location must be a Coordinate object, got {type(new_location)}")
        
        if not new_location.is_valid():
            raise ValueError(f"new_location coordinates are invalid: {new_location}")
        
        if new_location.is_packout_location():
            raise ValueError(f"Item cannot be moved to packout zone: {new_location}")
        
        self.location = new_location
        self.last_updated = time.time()
    
    def update_category(self, new_category: str) -> None:
        """
        Update item category and last_updated timestamp.
        
        Args:
            new_category: New category value
            
        Raises:
            ValueError: If new_category is invalid
        """
        if not isinstance(new_category, str):
            raise ValueError(f"new_category must be a string, got {type(new_category)}")
        
        if not new_category:
            raise ValueError("new_category cannot be empty")
        
        # Validate category
        valid_categories = {
            "electronics", "clothing", "books", "tools", "sports", 
            "home", "kitchen", "garden", "automotive", "general"
        }
        
        if new_category.lower() not in valid_categories:
            raise ValueError(f"category must be one of {valid_categories}, got {new_category}")
        
        self.category = new_category.lower()
        self.last_updated = time.time()
    
    def is_available(self) -> bool:
        """
        Check if item is available (quantity > 0).
        
        Returns:
            True if item is available, False otherwise
        """
        return self.quantity > 0
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """
        Check if item is low on stock.
        
        Args:
            threshold: Stock threshold for low stock warning
            
        Returns:
            True if quantity is below threshold, False otherwise
        """
        return 0 < self.quantity <= threshold
    
    def is_out_of_stock(self) -> bool:
        """
        Check if item is out of stock.
        
        Returns:
            True if quantity is 0, False otherwise
        """
        return self.quantity == 0
    
    def get_stock_status(self) -> str:
        """
        Get human-readable stock status.
        
        Returns:
            Stock status string
        """
        if self.is_out_of_stock():
            return "out_of_stock"
        elif self.is_low_stock():
            return "low_stock"
        else:
            return "available"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert item to dictionary for serialization.
        
        Returns:
            Dictionary representation of the item
        """
        return {
            "item_id": self.item_id,
            "location": self.location.to_dict(),
            "quantity": self.quantity,
            "category": self.category,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """
        Create item from dictionary.
        
        Args:
            data: Dictionary containing item data
            
        Returns:
            InventoryItem instance
            
        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError(f"data must be a dictionary, got {type(data)}")
        
        required_fields = ["item_id", "location", "quantity", "category"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert location dict to Coordinate
        location_data = data["location"]
        if isinstance(location_data, dict):
            location = Coordinate.from_dict(location_data)
        else:
            location = location_data
        
        return cls(
            item_id=data["item_id"],
            location=location,
            quantity=data["quantity"],
            category=data["category"],
            created_at=data.get("created_at", time.time()),
            last_updated=data.get("last_updated", time.time())
        )
    
    def __str__(self) -> str:
        """String representation of the item."""
        return f"InventoryItem(item_id='{self.item_id}', location={self.location}, quantity={self.quantity}, category='{self.category}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the item."""
        return f"InventoryItem(item_id='{self.item_id}', location={self.location}, quantity={self.quantity}, category='{self.category}', created_at={self.created_at}, last_updated={self.last_updated})"
    
    def __eq__(self, other: Any) -> bool:
        """Check if two items are equal."""
        if not isinstance(other, InventoryItem):
            return False
        
        return (
            self.item_id == other.item_id and
            self.location == other.location and
            self.quantity == other.quantity and
            self.category == other.category
        )
    
    def __hash__(self) -> int:
        """Hash based on item_id for set operations."""
        return hash(self.item_id) 