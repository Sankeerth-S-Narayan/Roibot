"""
Comprehensive tests for InventoryItem class.

This module tests all aspects of the InventoryItem class including validation,
methods, serialization, and edge cases.
"""

import unittest
import time
from unittest.mock import patch
from core.inventory.inventory_item import InventoryItem
from core.layout.coordinate import Coordinate


class TestInventoryItem(unittest.TestCase):
    """Test cases for InventoryItem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_coordinate = Coordinate(10, 15)
        self.packout_coordinate = Coordinate(1, 1)
        self.valid_item_data = {
            "item_id": "ITEM_A1",
            "location": self.valid_coordinate,
            "quantity": 100,
            "category": "electronics"
        }
    
    def test_valid_inventory_item_creation(self):
        """Test creating a valid inventory item."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        self.assertEqual(item.item_id, "ITEM_A1")
        self.assertEqual(item.location, self.valid_coordinate)
        self.assertEqual(item.quantity, 100)
        self.assertEqual(item.category, "electronics")
        self.assertIsInstance(item.created_at, (int, float))
        self.assertIsInstance(item.last_updated, (int, float))
    
    def test_inventory_item_default_values(self):
        """Test inventory item creation with default values."""
        item = InventoryItem(
            item_id="ITEM_B2",
            location=self.valid_coordinate
        )
        
        self.assertEqual(item.quantity, 999999)  # Unlimited stock default
        self.assertEqual(item.category, "general")  # Default category
        self.assertIsInstance(item.created_at, (int, float))
        self.assertIsInstance(item.last_updated, (int, float))
    
    def test_item_id_validation(self):
        """Test item_id validation rules."""
        # Valid item IDs
        valid_ids = ["ITEM_A1", "ITEM_B3", "ITEM_Z9", "ITEM_X20"]
        for item_id in valid_ids:
            with self.subTest(item_id=item_id):
                item = InventoryItem(item_id=item_id, location=self.valid_coordinate)
                self.assertEqual(item.item_id, item_id)
        
        # Invalid item IDs
        invalid_ids = [
            "",  # Empty
            "ITEM_",  # No suffix
            "ITEM_A",  # No number
            "ITEM_1",  # No letter
            "ITEM_A1B",  # Invalid format
            "item_a1",  # Wrong case
            "ITEM_A1_",  # Extra underscore
            "ITEM_A1B2",  # Too many characters
        ]
        
        for item_id in invalid_ids:
            with self.subTest(item_id=item_id):
                with self.assertRaises(ValueError):
                    InventoryItem(item_id=item_id, location=self.valid_coordinate)
    
    def test_location_validation(self):
        """Test location validation rules."""
        # Valid locations
        valid_locations = [
            Coordinate(1, 2),  # Edge case
            Coordinate(25, 20),  # Edge case
            Coordinate(10, 15),  # Middle
        ]
        
        for location in valid_locations:
            with self.subTest(location=location):
                item = InventoryItem(item_id="ITEM_A1", location=location)
                self.assertEqual(item.location, location)
        
        # Invalid locations
        invalid_locations = [
            Coordinate(0, 1),  # Invalid aisle
            Coordinate(26, 1),  # Invalid aisle
            Coordinate(1, 0),  # Invalid rack
            Coordinate(1, 21),  # Invalid rack
            self.packout_coordinate,  # Packout zone
        ]
        
        for location in invalid_locations:
            with self.subTest(location=location):
                with self.assertRaises(ValueError):
                    InventoryItem(item_id="ITEM_A1", location=location)
    
    def test_quantity_validation(self):
        """Test quantity validation rules."""
        # Valid quantities
        valid_quantities = [0, 1, 100, 999999, 1000000]
        
        for quantity in valid_quantities:
            with self.subTest(quantity=quantity):
                item = InventoryItem(
                    item_id="ITEM_A1",
                    location=self.valid_coordinate,
                    quantity=quantity
                )
                self.assertEqual(item.quantity, quantity)
        
        # Invalid quantities
        invalid_quantities = [-1, -100, -999999]
        
        for quantity in invalid_quantities:
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    InventoryItem(
                        item_id="ITEM_A1",
                        location=self.valid_coordinate,
                        quantity=quantity
                    )
    
    def test_category_validation(self):
        """Test category validation rules."""
        # Valid categories
        valid_categories = [
            "electronics", "clothing", "books", "tools", "sports",
            "home", "kitchen", "garden", "automotive", "general"
        ]
        
        for category in valid_categories:
            with self.subTest(category=category):
                item = InventoryItem(
                    item_id="ITEM_A1",
                    location=self.valid_coordinate,
                    category=category
                )
                self.assertEqual(item.category, category.lower())
        
        # Invalid categories
        invalid_categories = [
            "",  # Empty
            "invalid_category",
            "ELECTRONICS",  # Wrong case (should be normalized)
            "Electronics",  # Mixed case
        ]
        
        for category in invalid_categories:
            with self.subTest(category=category):
                with self.assertRaises(ValueError):
                    InventoryItem(
                        item_id="ITEM_A1",
                        location=self.valid_coordinate,
                        category=category
                    )
    
    def test_timestamp_validation(self):
        """Test timestamp validation rules."""
        current_time = time.time()
        
        # Valid timestamps
        valid_timestamps = [
            current_time - 1000,  # Past
            current_time - 1,  # Recent past
            current_time,  # Current
        ]
        
        for timestamp in valid_timestamps:
            with self.subTest(timestamp=timestamp):
                item = InventoryItem(
                    item_id="ITEM_A1",
                    location=self.valid_coordinate,
                    created_at=timestamp,
                    last_updated=timestamp
                )
                self.assertEqual(item.created_at, timestamp)
                self.assertEqual(item.last_updated, timestamp)
        
        # Invalid timestamps
        invalid_timestamps = [
            current_time + 1,  # Future
            current_time + 1000,  # Far future
        ]
        
        for timestamp in invalid_timestamps:
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(ValueError):
                    InventoryItem(
                        item_id="ITEM_A1",
                        location=self.valid_coordinate,
                        created_at=timestamp
                    )
    
    def test_update_quantity(self):
        """Test quantity update functionality."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100
        )
        
        original_updated = item.last_updated
        
        # Update quantity
        new_quantity = 50
        item.update_quantity(new_quantity)
        
        self.assertEqual(item.quantity, new_quantity)
        self.assertGreater(item.last_updated, original_updated)
        
        # Test invalid quantity
        with self.assertRaises(ValueError):
            item.update_quantity(-1)
    
    def test_update_location(self):
        """Test location update functionality."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100
        )
        
        original_updated = item.last_updated
        new_location = Coordinate(15, 20)
        
        # Update location
        item.update_location(new_location)
        
        self.assertEqual(item.location, new_location)
        self.assertGreater(item.last_updated, original_updated)
        
        # Test invalid location (packout zone)
        with self.assertRaises(ValueError):
            item.update_location(self.packout_coordinate)
    
    def test_update_category(self):
        """Test category update functionality."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            category="electronics"
        )
        
        original_updated = item.last_updated
        
        # Update category
        new_category = "clothing"
        item.update_category(new_category)
        
        self.assertEqual(item.category, new_category)
        self.assertGreater(item.last_updated, original_updated)
        
        # Test invalid category
        with self.assertRaises(ValueError):
            item.update_category("invalid_category")
    
    def test_stock_status_methods(self):
        """Test stock status checking methods."""
        # Available item
        available_item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100
        )
        
        self.assertTrue(available_item.is_available())
        self.assertFalse(available_item.is_low_stock())
        self.assertFalse(available_item.is_out_of_stock())
        self.assertEqual(available_item.get_stock_status(), "available")
        
        # Low stock item
        low_stock_item = InventoryItem(
            item_id="ITEM_B2",
            location=self.valid_coordinate,
            quantity=5
        )
        
        self.assertTrue(low_stock_item.is_available())
        self.assertTrue(low_stock_item.is_low_stock())
        self.assertFalse(low_stock_item.is_out_of_stock())
        self.assertEqual(low_stock_item.get_stock_status(), "low_stock")
        
        # Out of stock item
        out_of_stock_item = InventoryItem(
            item_id="ITEM_C3",
            location=self.valid_coordinate,
            quantity=0
        )
        
        self.assertFalse(out_of_stock_item.is_available())
        self.assertFalse(out_of_stock_item.is_low_stock())
        self.assertTrue(out_of_stock_item.is_out_of_stock())
        self.assertEqual(out_of_stock_item.get_stock_status(), "out_of_stock")
    
    def test_low_stock_threshold(self):
        """Test low stock threshold functionality."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=5
        )
        
        # Test default threshold (10)
        self.assertTrue(item.is_low_stock())
        
        # Test custom threshold
        self.assertFalse(item.is_low_stock(threshold=3))
        self.assertTrue(item.is_low_stock(threshold=7))
    
    def test_serialization_to_dict(self):
        """Test serialization to dictionary."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        item_dict = item.to_dict()
        
        self.assertEqual(item_dict["item_id"], "ITEM_A1")
        self.assertEqual(item_dict["quantity"], 100)
        self.assertEqual(item_dict["category"], "electronics")
        self.assertEqual(item_dict["location"], self.valid_coordinate.to_dict())
        self.assertIn("created_at", item_dict)
        self.assertIn("last_updated", item_dict)
    
    def test_deserialization_from_dict(self):
        """Test deserialization from dictionary."""
        item_data = {
            "item_id": "ITEM_A1",
            "location": self.valid_coordinate.to_dict(),
            "quantity": 100,
            "category": "electronics",
            "created_at": time.time() - 1000,
            "last_updated": time.time() - 500
        }
        
        item = InventoryItem.from_dict(item_data)
        
        self.assertEqual(item.item_id, "ITEM_A1")
        self.assertEqual(item.location, self.valid_coordinate)
        self.assertEqual(item.quantity, 100)
        self.assertEqual(item.category, "electronics")
        self.assertEqual(item.created_at, item_data["created_at"])
        self.assertEqual(item.last_updated, item_data["last_updated"])
    
    def test_deserialization_validation(self):
        """Test deserialization validation."""
        # Missing required fields
        incomplete_data = {
            "item_id": "ITEM_A1",
            "location": self.valid_coordinate.to_dict()
            # Missing quantity and category
        }
        
        with self.assertRaises(ValueError):
            InventoryItem.from_dict(incomplete_data)
        
        # Invalid data type
        invalid_data = "not a dictionary"
        
        with self.assertRaises(ValueError):
            InventoryItem.from_dict(invalid_data)
    
    def test_string_representations(self):
        """Test string representation methods."""
        item = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        # Test __str__
        str_repr = str(item)
        self.assertIn("ITEM_A1", str_repr)
        self.assertIn("100", str_repr)
        self.assertIn("electronics", str_repr)
        
        # Test __repr__
        repr_repr = repr(item)
        self.assertIn("ITEM_A1", repr_repr)
        self.assertIn("100", repr_repr)
        self.assertIn("electronics", repr_repr)
        self.assertIn("created_at", repr_repr)
        self.assertIn("last_updated", repr_repr)
    
    def test_equality_comparison(self):
        """Test equality comparison between items."""
        item1 = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        item2 = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        item3 = InventoryItem(
            item_id="ITEM_B2",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        # Same items should be equal
        self.assertEqual(item1, item2)
        
        # Different items should not be equal
        self.assertNotEqual(item1, item3)
        
        # Compare with non-InventoryItem
        self.assertNotEqual(item1, "not an item")
    
    def test_hash_functionality(self):
        """Test hash functionality for set operations."""
        item1 = InventoryItem(
            item_id="ITEM_A1",
            location=self.valid_coordinate,
            quantity=100,
            category="electronics"
        )
        
        item2 = InventoryItem(
            item_id="ITEM_A1",
            location=Coordinate(5, 5),  # Different location
            quantity=50,  # Different quantity
            category="clothing"  # Different category
        )
        
        # Same item_id should have same hash
        self.assertEqual(hash(item1), hash(item2))
        
        # Test set functionality
        item_set = {item1, item2}
        self.assertEqual(len(item_set), 1)  # Should deduplicate by item_id
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Maximum valid coordinates
        max_coord = Coordinate(25, 20)
        item = InventoryItem(
            item_id="ITEM_A1",
            location=max_coord,
            quantity=0  # Out of stock
        )
        
        self.assertEqual(item.location, max_coord)
        self.assertTrue(item.is_out_of_stock())
        
        # Maximum quantity
        max_quantity_item = InventoryItem(
            item_id="ITEM_B2",
            location=self.valid_coordinate,
            quantity=999999999
        )
        
        self.assertTrue(max_quantity_item.is_available())
        self.assertFalse(max_quantity_item.is_low_stock())
    
    def test_type_validation(self):
        """Test type validation for all properties."""
        # Invalid item_id type
        with self.assertRaises(ValueError):
            InventoryItem(item_id=123, location=self.valid_coordinate)
        
        # Invalid location type
        with self.assertRaises(ValueError):
            InventoryItem(item_id="ITEM_A1", location="not a coordinate")
        
        # Invalid quantity type
        with self.assertRaises(ValueError):
            InventoryItem(
                item_id="ITEM_A1",
                location=self.valid_coordinate,
                quantity="not a number"
            )
        
        # Invalid category type
        with self.assertRaises(ValueError):
            InventoryItem(
                item_id="ITEM_A1",
                location=self.valid_coordinate,
                category=123
            )
    
    def test_timestamp_consistency(self):
        """Test timestamp consistency validation."""
        current_time = time.time()
        future_time = current_time + 1000
        
        # last_updated before created_at should fail
        with self.assertRaises(ValueError):
            InventoryItem(
                item_id="ITEM_A1",
                location=self.valid_coordinate,
                created_at=current_time,
                last_updated=current_time - 1000
            )
        
        # Future timestamps should fail
        with self.assertRaises(ValueError):
            InventoryItem(
                item_id="ITEM_A1",
                location=self.valid_coordinate,
                created_at=future_time
            )


if __name__ == "__main__":
    unittest.main() 