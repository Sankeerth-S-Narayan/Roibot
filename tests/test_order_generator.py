"""
Comprehensive tests for OrderGenerator class.

Tests order generation functionality, timing, configuration,
error handling, and integration with warehouse layout.

Author: Roibot Development Team
Version: 1.0
"""

import unittest
import time
from unittest.mock import Mock, patch
from datetime import datetime

from entities.order_generator import OrderGenerator, GenerationStatus
from entities.robot_orders import Order, OrderStatus
from core.layout.warehouse_layout import WarehouseLayoutManager


class TestOrderGenerator(unittest.TestCase):
    """Test cases for OrderGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock warehouse layout
        self.mock_warehouse_layout = Mock(spec=WarehouseLayoutManager)
        self.mock_warehouse_layout.is_valid_coordinate.return_value = True
        
        # Create order generator
        self.order_generator = OrderGenerator(self.mock_warehouse_layout)
    
    def test_initialization(self):
        """Test OrderGenerator initialization."""
        self.assertEqual(self.order_generator.generation_interval, 30.0)
        self.assertEqual(self.order_generator.min_items_per_order, 1)
        self.assertEqual(self.order_generator.max_items_per_order, 4)
        self.assertFalse(self.order_generator.is_generating)
        self.assertEqual(self.order_generator.status, GenerationStatus.STOPPED)
        self.assertEqual(self.order_generator.total_orders_generated, 0)
        self.assertEqual(self.order_generator.orders_generated_this_session, 0)
        self.assertEqual(self.order_generator.generation_errors, 0)
        self.assertIsNotNone(self.order_generator.item_pool)
        self.assertGreater(len(self.order_generator.item_pool), 0)
    
    def test_item_pool_initialization(self):
        """Test item pool initialization."""
        # Should have items for all valid warehouse locations except packout zone
        expected_items = 25 * 20 - 1  # 25 aisles * 20 racks - 1 packout zone
        self.assertEqual(len(self.order_generator.item_pool), expected_items)
        
        # Check item format
        for item in self.order_generator.item_pool:
            self.assertIn('item_id', item)
            self.assertIn('position', item)
            self.assertIn('available', item)
            self.assertTrue(item['available'])
            
            # Check item ID format
            self.assertTrue(item['item_id'].startswith('ITEM_A'))
            
            # Check position format
            aisle, rack = item['position']
            self.assertIsInstance(aisle, int)
            self.assertIsInstance(rack, int)
            self.assertGreaterEqual(aisle, 1)
            self.assertLessEqual(aisle, 25)
            self.assertGreaterEqual(rack, 1)
            self.assertLessEqual(rack, 20)
            
            # Check that packout zone (1, 1) is not included
            self.assertNotEqual(item['position'], (1, 1))
    
    def test_configure_valid_settings(self):
        """Test configuration with valid settings."""
        config = {
            'generation_interval': 45.0,
            'min_items_per_order': 2,
            'max_items_per_order': 6
        }
        
        self.order_generator.configure(config)
        
        self.assertEqual(self.order_generator.generation_interval, 45.0)
        self.assertEqual(self.order_generator.min_items_per_order, 2)
        self.assertEqual(self.order_generator.max_items_per_order, 6)
    
    def test_configure_invalid_interval(self):
        """Test configuration with invalid generation interval."""
        config = {'generation_interval': 0.5}
        
        with self.assertRaises(ValueError, msg="Generation interval must be at least 1 second"):
            self.order_generator.configure(config)
    
    def test_configure_invalid_min_items(self):
        """Test configuration with invalid minimum items."""
        config = {'min_items_per_order': 0}
        
        with self.assertRaises(ValueError, msg="Minimum items per order must be at least 1"):
            self.order_generator.configure(config)
    
    def test_configure_invalid_max_items(self):
        """Test configuration with invalid maximum items."""
        config = {'min_items_per_order': 3, 'max_items_per_order': 2}
        
        with self.assertRaises(ValueError, msg="Maximum items per order must be >= minimum items"):
            self.order_generator.configure(config)
    
    def test_configure_max_items_too_high(self):
        """Test configuration with maximum items too high."""
        config = {'max_items_per_order': 15}
        
        with self.assertRaises(ValueError, msg="Maximum items per order cannot exceed 10"):
            self.order_generator.configure(config)
    
    def test_start_generation(self):
        """Test starting order generation."""
        self.order_generator.start_generation()
        
        self.assertTrue(self.order_generator.is_generating)
        self.assertEqual(self.order_generator.status, GenerationStatus.RUNNING)
        self.assertGreater(self.order_generator.generation_start_time, 0)
        self.assertGreater(self.order_generator.last_generation_time, 0)
    
    def test_start_generation_already_running(self):
        """Test starting generation when already running."""
        self.order_generator.start_generation()
        initial_time = self.order_generator.last_generation_time
        
        # Try to start again
        self.order_generator.start_generation()
        
        # Should not change the timing
        self.assertEqual(self.order_generator.last_generation_time, initial_time)
    
    def test_stop_generation(self):
        """Test stopping order generation."""
        self.order_generator.start_generation()
        self.order_generator.stop_generation()
        
        self.assertFalse(self.order_generator.is_generating)
        self.assertEqual(self.order_generator.status, GenerationStatus.STOPPED)
    
    def test_stop_generation_not_running(self):
        """Test stopping generation when not running."""
        # Should not raise an error
        self.order_generator.stop_generation()
        
        self.assertFalse(self.order_generator.is_generating)
        self.assertEqual(self.order_generator.status, GenerationStatus.STOPPED)
    
    def test_pause_resume_generation(self):
        """Test pausing and resuming order generation."""
        self.order_generator.start_generation()
        
        # Pause
        self.order_generator.pause_generation()
        self.assertEqual(self.order_generator.status, GenerationStatus.PAUSED)
        
        # Resume
        self.order_generator.resume_generation()
        self.assertEqual(self.order_generator.status, GenerationStatus.RUNNING)
    
    def test_pause_generation_not_running(self):
        """Test pausing generation when not running."""
        # Should print warning instead of raising exception
        self.order_generator.pause_generation()
        # Verify status remains stopped
        self.assertEqual(self.order_generator.status, GenerationStatus.STOPPED)
    
    def test_resume_generation_not_paused(self):
        """Test resuming generation when not paused."""
        # Should print warning instead of raising exception
        self.order_generator.resume_generation()
        # Verify status remains stopped
        self.assertEqual(self.order_generator.status, GenerationStatus.STOPPED)
    
    def test_should_generate_order_not_running(self):
        """Test should_generate_order when generation is not running."""
        current_time = time.time()
        self.assertFalse(self.order_generator.should_generate_order(current_time))
    
    def test_should_generate_order_paused(self):
        """Test should_generate_order when generation is paused."""
        self.order_generator.start_generation()
        self.order_generator.pause_generation()
        
        current_time = time.time()
        self.assertFalse(self.order_generator.should_generate_order(current_time))
    
    def test_should_generate_order_before_interval(self):
        """Test should_generate_order before interval has elapsed."""
        self.order_generator.start_generation()
        current_time = time.time()
        
        # Should not generate immediately after starting
        self.assertFalse(self.order_generator.should_generate_order(current_time))
    
    def test_should_generate_order_after_interval(self):
        """Test should_generate_order after interval has elapsed."""
        self.order_generator.start_generation()
        
        # Advance time past the generation interval
        current_time = time.time() + self.order_generator.generation_interval + 1
        
        self.assertTrue(self.order_generator.should_generate_order(current_time))
    
    def test_generate_order_id_format(self):
        """Test order ID generation format."""
        order_id = self.order_generator._generate_order_id()
        
        # Should start with ORD_ and contain timestamp
        self.assertTrue(order_id.startswith('ORD_'))
        self.assertIn('_', order_id)  # Should have unique suffix
        
        # Check timestamp format (YYYYMMDD_HHMMSS)
        parts = order_id.split('_')
        self.assertGreaterEqual(len(parts), 3)  # ORD, timestamp, unique_suffix (may have more parts)
        
        # Check that we have ORD prefix and timestamp part
        self.assertEqual(parts[0], 'ORD')
        timestamp_part = parts[1]
        # Check that timestamp part has reasonable length (8 for YYYYMMDD or 14 for YYYYMMDD_HHMMSS)
        self.assertIn(len(timestamp_part), [8, 14])  # Allow both formats
    
    def test_select_random_items(self):
        """Test random item selection."""
        num_items = 3
        selected_items = self.order_generator._select_random_items(num_items)
        
        self.assertEqual(len(selected_items), num_items)
        
        # Check that all items are from the pool
        for item in selected_items:
            self.assertIn(item, self.order_generator.item_pool)
        
        # Check that items are unique
        item_ids = [item['item_id'] for item in selected_items]
        self.assertEqual(len(item_ids), len(set(item_ids)))
    
    def test_select_random_items_maximum(self):
        """Test random item selection with maximum available items."""
        num_items = len(self.order_generator.item_pool) + 10
        selected_items = self.order_generator._select_random_items(num_items)
        
        # Should return all available items
        self.assertEqual(len(selected_items), len(self.order_generator.item_pool))
    
    def test_generate_order_success(self):
        """Test successful order generation."""
        self.order_generator.start_generation()
        current_time = time.time()
        
        order = self.order_generator.generate_order(current_time)
        
        self.assertIsNotNone(order)
        self.assertIsInstance(order, Order)
        self.assertIn(order.order_id, order.order_id)
        self.assertGreaterEqual(len(order.item_ids), self.order_generator.min_items_per_order)
        self.assertLessEqual(len(order.item_ids), self.order_generator.max_items_per_order)
        self.assertEqual(order.status, OrderStatus.ASSIGNED)
        self.assertEqual(self.order_generator.total_orders_generated, 1)
        self.assertEqual(self.order_generator.orders_generated_this_session, 1)
    
    def test_generate_order_no_items_available(self):
        """Test order generation when no items are available."""
        # Clear the item pool
        self.order_generator.item_pool = []
        
        self.order_generator.start_generation()
        current_time = time.time()
        
        order = self.order_generator.generate_order(current_time)
        
        self.assertIsNone(order)
        self.assertEqual(self.order_generator.generation_errors, 0)  # Not an error, just no items
    
    def test_generate_order_with_exception(self):
        """Test order generation with exception handling."""
        # Mock the _generate_order_id method to raise an exception
        with patch.object(self.order_generator, '_generate_order_id', side_effect=Exception("Test error")):
            self.order_generator.start_generation()
            current_time = time.time()
            
            order = self.order_generator.generate_order(current_time)
            
            self.assertIsNone(order)
            self.assertEqual(self.order_generator.generation_errors, 1)
    
    def test_update_generation_timing(self):
        """Test update method with proper generation timing."""
        self.order_generator.start_generation()
        
        # First update - should not generate (too soon)
        current_time = time.time()
        order = self.order_generator.update(current_time)
        self.assertIsNone(order)
        
        # Advance time and update - should generate
        current_time += self.order_generator.generation_interval + 1
        order = self.order_generator.update(current_time)
        self.assertIsNotNone(order)
    
    def test_get_status(self):
        """Test get_status method."""
        self.order_generator.start_generation()
        status = self.order_generator.get_status()
        
        self.assertIn('status', status)
        self.assertIn('is_generating', status)
        self.assertIn('generation_interval', status)
        self.assertIn('min_items_per_order', status)
        self.assertIn('max_items_per_order', status)
        self.assertIn('total_orders_generated', status)
        self.assertIn('orders_generated_this_session', status)
        self.assertIn('generation_errors', status)
        self.assertIn('time_since_last_generation', status)
        self.assertIn('available_items', status)
        
        self.assertEqual(status['status'], GenerationStatus.RUNNING.value)
        self.assertTrue(status['is_generating'])
        self.assertEqual(status['generation_interval'], 30.0)
    
    def test_reset_statistics(self):
        """Test reset_statistics method."""
        self.order_generator.orders_generated_this_session = 10
        self.order_generator.generation_errors = 5
        
        self.order_generator.reset_statistics()
        
        self.assertEqual(self.order_generator.orders_generated_this_session, 0)
        self.assertEqual(self.order_generator.generation_errors, 0)
        # total_orders_generated should not be reset
        self.assertEqual(self.order_generator.total_orders_generated, 0)
    
    def test_get_debug_info(self):
        """Test get_debug_info method."""
        debug_info = self.order_generator.get_debug_info()
        
        self.assertIn('generator_status', debug_info)
        self.assertIn('item_pool_size', debug_info)
        self.assertIn('sample_items', debug_info)
        self.assertIn('generation_timing', debug_info)
        
        self.assertEqual(debug_info['item_pool_size'], len(self.order_generator.item_pool))
        self.assertIsInstance(debug_info['sample_items'], list)
        self.assertLessEqual(len(debug_info['sample_items']), 5)


if __name__ == '__main__':
    unittest.main() 