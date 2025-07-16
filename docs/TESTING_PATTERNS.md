# Testing Patterns and Best Practices

## Overview

This guide provides comprehensive testing patterns and best practices for the Order Management System. Proper testing ensures system reliability, performance, and maintainability.

## Table of Contents

1. [Unit Testing Patterns](#unit-testing-patterns)
2. [Integration Testing Patterns](#integration-testing-patterns)
3. [Performance Testing Patterns](#performance-testing-patterns)
4. [Mock and Stub Patterns](#mock-and-stub-patterns)
5. [Test Data Management](#test-data-management)
6. [Test Organization](#test-organization)
7. [Continuous Testing](#continuous-testing)
8. [Best Practices](#best-practices)

## Unit Testing Patterns

### 1. Basic Unit Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from core.order_management import OrderGenerator, OrderQueueManager

class TestOrderGenerator:
    """Unit tests for OrderGenerator class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "enabled": True,
            "interval_seconds": 30,
            "max_orders": 100,
            "priority_distribution": {
                "high": 0.2,
                "medium": 0.5,
                "low": 0.3
            }
        }
        self.generator = OrderGenerator(self.config)
    
    def test_generate_single_order(self):
        """Test generating a single order."""
        order = self.generator.generate_order()
        
        assert order is not None
        assert "order_id" in order
        assert "priority" in order
        assert "timestamp" in order
        assert order["priority"] in ["high", "medium", "low"]
    
    def test_generate_multiple_orders(self):
        """Test generating multiple orders."""
        orders = self.generator.generate_orders(count=5)
        
        assert len(orders) == 5
        assert all("order_id" in order for order in orders)
        assert all("priority" in order for order in orders)
    
    def test_priority_distribution(self):
        """Test that priority distribution is respected."""
        orders = self.generator.generate_orders(count=1000)
        
        priorities = [order["priority"] for order in orders]
        high_count = priorities.count("high")
        medium_count = priorities.count("medium")
        low_count = priorities.count("low")
        
        # Allow some tolerance for randomness
        assert 150 <= high_count <= 250
        assert 450 <= medium_count <= 550
        assert 250 <= low_count <= 350
    
    def test_order_id_uniqueness(self):
        """Test that order IDs are unique."""
        orders = self.generator.generate_orders(count=100)
        order_ids = [order["order_id"] for order in orders]
        
        assert len(order_ids) == len(set(order_ids))
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        invalid_config = {
            "enabled": True,
            "max_orders": -1  # Invalid value
        }
        
        with pytest.raises(ValueError):
            OrderGenerator(invalid_config)
    
    def test_disabled_generator(self):
        """Test generator when disabled."""
        disabled_config = {"enabled": False}
        disabled_generator = OrderGenerator(disabled_config)
        
        orders = disabled_generator.generate_orders(count=5)
        assert len(orders) == 0
```

### 2. Advanced Unit Test Patterns

```python
class TestOrderQueueManager:
    """Unit tests for OrderQueueManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "max_queue_size": 10,
            "timeout_seconds": 300,
            "retry_attempts": 3
        }
        self.queue_manager = OrderQueueManager(self.config)
    
    def test_add_order_to_queue(self):
        """Test adding order to queue."""
        order = {"order_id": "order_001", "priority": "high"}
        
        success = self.queue_manager.add_order(order)
        
        assert success is True
        assert self.queue_manager.get_queue_size() == 1
        assert self.queue_manager.get_order("order_001") == order
    
    def test_queue_full_behavior(self):
        """Test behavior when queue is full."""
        # Fill the queue
        for i in range(10):
            order = {"order_id": f"order_{i:03d}", "priority": "medium"}
            self.queue_manager.add_order(order)
        
        # Try to add one more
        extra_order = {"order_id": "order_011", "priority": "high"}
        success = self.queue_manager.add_order(extra_order)
        
        assert success is False
        assert self.queue_manager.get_queue_size() == 10
    
    def test_priority_queue_ordering(self):
        """Test that orders are properly ordered by priority."""
        orders = [
            {"order_id": "order_001", "priority": "low"},
            {"order_id": "order_002", "priority": "high"},
            {"order_id": "order_003", "priority": "medium"},
            {"order_id": "order_004", "priority": "high"}
        ]
        
        for order in orders:
            self.queue_manager.add_order(order)
        
        # Get next order (should be high priority)
        next_order = self.queue_manager.get_next_order()
        assert next_order["priority"] == "high"
        
        # Get all orders in priority order
        all_orders = self.queue_manager.get_all_orders()
        priorities = [order["priority"] for order in all_orders]
        
        # High priority orders should come first
        high_indices = [i for i, p in enumerate(priorities) if p == "high"]
        medium_indices = [i for i, p in enumerate(priorities) if p == "medium"]
        low_indices = [i for i, p in enumerate(priorities) if p == "low"]
        
        assert all(h < m for h in high_indices for m in medium_indices)
        assert all(m < l for m in medium_indices for l in low_indices)
    
    def test_order_timeout(self):
        """Test order timeout functionality."""
        order = {"order_id": "order_001", "priority": "medium"}
        self.queue_manager.add_order(order)
        
        # Simulate timeout
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 400  # 400 seconds later
            
            timed_out_orders = self.queue_manager.get_timed_out_orders()
            assert len(timed_out_orders) == 1
            assert timed_out_orders[0]["order_id"] == "order_001"
    
    def test_remove_order(self):
        """Test removing order from queue."""
        order = {"order_id": "order_001", "priority": "high"}
        self.queue_manager.add_order(order)
        
        removed = self.queue_manager.remove_order("order_001")
        assert removed is True
        assert self.queue_manager.get_queue_size() == 0
        
        # Try to remove non-existent order
        removed = self.queue_manager.remove_order("non_existent")
        assert removed is False
```

### 3. Mock and Stub Patterns

```python
class TestRobotOrderAssigner:
    """Unit tests for RobotOrderAssigner class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "strategy": "nearest_available",
            "load_balancing": True,
            "max_orders_per_robot": 3
        }
        self.assigner = RobotOrderAssigner(self.config)
    
    @patch('core.order_management.RobotOrderAssigner._get_available_robots')
    def test_assign_order_to_robot(self, mock_get_robots):
        """Test assigning order to robot using mock."""
        # Mock available robots
        mock_get_robots.return_value = [
            {"robot_id": "robot_001", "status": "available"},
            {"robot_id": "robot_002", "status": "available"}
        ]
        
        order = {"order_id": "order_001", "priority": "high"}
        
        assignment = self.assigner.assign_order(order)
        
        assert assignment is not None
        assert assignment["order_id"] == "order_001"
        assert assignment["robot_id"] in ["robot_001", "robot_002"]
    
    @patch('core.order_management.RobotOrderAssigner._calculate_distance')
    def test_nearest_robot_assignment(self, mock_calculate_distance):
        """Test nearest robot assignment strategy."""
        # Mock distance calculations
        mock_calculate_distance.side_effect = lambda robot, order: {
            "robot_001": 10,
            "robot_002": 5,
            "robot_003": 15
        }[robot["robot_id"]]
        
        available_robots = [
            {"robot_id": "robot_001", "status": "available"},
            {"robot_id": "robot_002", "status": "available"},
            {"robot_id": "robot_003", "status": "available"}
        ]
        
        order = {"order_id": "order_001", "priority": "medium"}
        
        with patch.object(self.assigner, '_get_available_robots', return_value=available_robots):
            assignment = self.assigner.assign_order(order)
            
            assert assignment["robot_id"] == "robot_002"  # Nearest robot
    
    def test_no_available_robots(self):
        """Test behavior when no robots are available."""
        with patch.object(self.assigner, '_get_available_robots', return_value=[]):
            order = {"order_id": "order_001", "priority": "high"}
            
            assignment = self.assigner.assign_order(order)
            assert assignment is None
    
    def test_robot_load_balancing(self):
        """Test load balancing across robots."""
        # Mock robots with different loads
        robots = [
            {"robot_id": "robot_001", "current_orders": 1},
            {"robot_id": "robot_002", "current_orders": 3},
            {"robot_id": "robot_003", "current_orders": 0}
        ]
        
        with patch.object(self.assigner, '_get_available_robots', return_value=robots):
            order = {"order_id": "order_001", "priority": "medium"}
            
            assignment = self.assigner.assign_order(order)
            assert assignment["robot_id"] == "robot_003"  # Least loaded
```

## Integration Testing Patterns

### 1. System Integration Tests

```python
class TestOrderManagementIntegration:
    """Integration tests for OrderManagementSystem."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.event_manager = EventManager()
        self.order_system = OrderManagementSystem(self.event_manager)
    
    def test_complete_order_workflow(self):
        """Test complete order workflow from generation to completion."""
        # Generate orders
        orders = self.order_system.generate_orders(count=3)
        assert len(orders) == 3
        
        # Verify events were emitted
        events = self.event_manager.get_events(EventType.ORDER_CREATED)
        assert len(events) == 3
        
        # Process orders
        self.order_system.process_orders()
        
        # Verify queue status
        queue_status = self.order_system.get_queue_status()
        assert queue_status.total_orders > 0
        
        # Verify analytics
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders == 3
    
    def test_order_assignment_integration(self):
        """Test order assignment integration."""
        # Generate orders
        orders = self.order_system.generate_orders(count=2)
        
        # Assign orders to robots
        assignments = self.order_system.assign_orders_to_robots()
        
        assert len(assignments) > 0
        
        # Verify assignment events
        events = self.event_manager.get_events(EventType.ORDER_ASSIGNED)
        assert len(events) > 0
    
    def test_order_status_tracking(self):
        """Test order status tracking integration."""
        # Generate and process orders
        self.order_system.generate_orders(count=1)
        self.order_system.process_orders()
        
        # Update order statuses
        status_updates = self.order_system.update_order_statuses()
        
        assert len(status_updates) > 0
        
        # Verify status events
        events = self.event_manager.get_events(EventType.ORDER_STARTED)
        assert len(events) > 0
    
    def test_analytics_integration(self):
        """Test analytics integration."""
        # Generate multiple orders
        self.order_system.generate_orders(count=10)
        self.order_system.process_orders()
        
        # Get analytics
        analytics = self.order_system.get_analytics()
        
        assert analytics.total_orders == 10
        assert analytics.avg_processing_time >= 0
        assert analytics.orders_per_minute >= 0
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        # Update configuration
        new_config = {
            "order_generation": {
                "enabled": True,
                "interval_seconds": 15,
                "max_orders": 50
            }
        }
        
        self.order_system.update_configuration(new_config)
        
        # Verify configuration was applied
        current_config = self.order_system.get_configuration()
        assert current_config["order_generation"]["interval_seconds"] == 15
        assert current_config["order_generation"]["max_orders"] == 50
```

### 2. Component Integration Tests

```python
class TestComponentIntegration:
    """Integration tests for individual components."""
    
    def test_order_generator_queue_integration(self):
        """Test integration between OrderGenerator and OrderQueueManager."""
        generator = OrderGenerator({"enabled": True, "max_orders": 100})
        queue_manager = OrderQueueManager({"max_queue_size": 50})
        
        # Generate orders and add to queue
        orders = generator.generate_orders(count=10)
        
        for order in orders:
            success = queue_manager.add_order(order)
            assert success is True
        
        assert queue_manager.get_queue_size() == 10
        
        # Verify order retrieval
        retrieved_orders = queue_manager.get_all_orders()
        assert len(retrieved_orders) == 10
    
    def test_queue_assigner_integration(self):
        """Test integration between OrderQueueManager and RobotOrderAssigner."""
        queue_manager = OrderQueueManager({"max_queue_size": 20})
        assigner = RobotOrderAssigner({"strategy": "nearest_available"})
        
        # Add orders to queue
        orders = [
            {"order_id": "order_001", "priority": "high"},
            {"order_id": "order_002", "priority": "medium"},
            {"order_id": "order_003", "priority": "low"}
        ]
        
        for order in orders:
            queue_manager.add_order(order)
        
        # Assign orders from queue
        assignments = []
        while queue_manager.get_queue_size() > 0:
            order = queue_manager.get_next_order()
            if order:
                assignment = assigner.assign_order(order)
                if assignment:
                    assignments.append(assignment)
                    queue_manager.remove_order(order["order_id"])
        
        assert len(assignments) == 3
    
    def test_status_tracker_analytics_integration(self):
        """Test integration between OrderStatusTracker and OrderAnalytics."""
        status_tracker = OrderStatusTracker()
        analytics = OrderAnalytics()
        
        # Track order status changes
        order_id = "order_001"
        status_tracker.track_order_start(order_id, "robot_001")
        status_tracker.track_order_complete(order_id, "robot_001")
        
        # Get analytics
        order_history = status_tracker.get_order_history(order_id)
        analytics_data = analytics.calculate_order_metrics([order_history])
        
        assert analytics_data.total_orders == 1
        assert analytics_data.completed_orders == 1
        assert analytics_data.avg_processing_time > 0
```

## Performance Testing Patterns

### 1. Load Testing

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestOrderManagementPerformance:
    """Performance tests for OrderManagementSystem."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.event_manager = EventManager()
        self.order_system = OrderManagementSystem(self.event_manager)
    
    def test_order_generation_performance(self):
        """Test order generation performance."""
        start_time = time.time()
        
        # Generate large batch of orders
        orders = self.order_system.generate_orders(count=1000)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 1.0  # Should complete within 1 second
        assert len(orders) == 1000
        
        # Calculate throughput
        throughput = len(orders) / duration
        assert throughput > 1000  # At least 1000 orders per second
    
    def test_concurrent_order_processing(self):
        """Test concurrent order processing."""
        def process_orders_batch(batch_id):
            """Process a batch of orders."""
            orders = self.order_system.generate_orders(count=10)
            self.order_system.process_orders()
            return len(orders)
        
        start_time = time.time()
        
        # Process orders concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_orders_batch, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all batches were processed
        assert sum(results) == 100  # 10 batches * 10 orders each
        assert duration < 5.0  # Should complete within 5 seconds
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Generate and process many orders
        for i in range(10):
            self.order_system.generate_orders(count=100)
            self.order_system.process_orders()
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB
    
    def test_queue_performance_under_load(self):
        """Test queue performance under load."""
        queue_manager = OrderQueueManager({"max_queue_size": 1000})
        
        start_time = time.time()
        
        # Add orders rapidly
        for i in range(1000):
            order = {"order_id": f"order_{i:04d}", "priority": "medium"}
            success = queue_manager.add_order(order)
            assert success is True
        
        add_time = time.time() - start_time
        
        # Remove orders rapidly
        start_time = time.time()
        
        for i in range(1000):
            order = queue_manager.get_next_order()
            assert order is not None
        
        remove_time = time.time() - start_time
        
        # Performance assertions
        assert add_time < 1.0  # Add operations should be fast
        assert remove_time < 1.0  # Remove operations should be fast
        assert queue_manager.get_queue_size() == 0
    
    def test_analytics_performance(self):
        """Test analytics calculation performance."""
        # Generate large dataset
        self.order_system.generate_orders(count=10000)
        self.order_system.process_orders()
        
        start_time = time.time()
        
        # Calculate analytics
        analytics = self.order_system.get_analytics()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 0.1  # Analytics should be calculated quickly
        assert analytics.total_orders == 10000
```

### 2. Stress Testing

```python
class TestOrderManagementStress:
    """Stress tests for OrderManagementSystem."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.event_manager = EventManager()
        self.order_system = OrderManagementSystem(self.event_manager)
    
    def test_system_under_extreme_load(self):
        """Test system behavior under extreme load."""
        # Generate orders continuously for extended period
        start_time = time.time()
        total_orders = 0
        
        while time.time() - start_time < 30:  # 30 seconds
            orders = self.order_system.generate_orders(count=100)
            total_orders += len(orders)
            self.order_system.process_orders()
            
            # Small delay to prevent overwhelming
            time.sleep(0.01)
        
        # Verify system remained stable
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders == total_orders
        
        # Check for memory leaks
        import gc
        gc.collect()
        
        # System should still be responsive
        new_orders = self.order_system.generate_orders(count=10)
        assert len(new_orders) == 10
    
    def test_concurrent_access_stress(self):
        """Test system under concurrent access stress."""
        def worker(worker_id):
            """Worker function for concurrent access."""
            for i in range(100):
                orders = self.order_system.generate_orders(count=5)
                self.order_system.process_orders()
                time.sleep(0.001)  # Small delay
            return worker_id
        
        # Start multiple workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Verify all workers completed
        assert len(results) == 10
        assert all(isinstance(r, int) for r in results)
        
        # Verify system integrity
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders > 0
    
    def test_queue_stress_test(self):
        """Stress test the order queue."""
        queue_manager = OrderQueueManager({"max_queue_size": 10000})
        
        # Rapidly add and remove orders
        def add_orders():
            for i in range(1000):
                order = {"order_id": f"order_{i:04d}", "priority": "medium"}
                queue_manager.add_order(order)
        
        def remove_orders():
            for i in range(1000):
                order = queue_manager.get_next_order()
                if order:
                    queue_manager.remove_order(order["order_id"])
        
        # Run add and remove operations concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            add_future = executor.submit(add_orders)
            remove_future = executor.submit(remove_orders)
            
            add_future.result()
            remove_future.result()
        
        # Verify queue integrity
        assert queue_manager.get_queue_size() >= 0
```

## Mock and Stub Patterns

### 1. Event Manager Mocking

```python
class MockEventManager:
    """Mock event manager for testing."""
    
    def __init__(self):
        self.events = []
        self.subscribers = {}
    
    def emit(self, event_type, data):
        """Emit an event."""
        event = {"type": event_type, "data": data, "timestamp": time.time()}
        self.events.append(event)
        
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(event)
    
    def subscribe(self, event_type, callback):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def get_events(self, event_type=None):
        """Get events, optionally filtered by type."""
        if event_type:
            return [event for event in self.events if event["type"] == event_type]
        return self.events
    
    def clear_events(self):
        """Clear all events."""
        self.events.clear()

class TestWithMockEventManager:
    """Tests using mock event manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_event_manager = MockEventManager()
        self.order_system = OrderManagementSystem(self.mock_event_manager)
    
    def test_order_creation_emits_events(self):
        """Test that order creation emits appropriate events."""
        # Generate orders
        orders = self.order_system.generate_orders(count=3)
        
        # Verify events were emitted
        events = self.mock_event_manager.get_events(EventType.ORDER_CREATED)
        assert len(events) == 3
        
        for event in events:
            assert "order_id" in event["data"]
            assert "priority" in event["data"]
    
    def test_order_assignment_emits_events(self):
        """Test that order assignment emits appropriate events."""
        # Generate and process orders
        self.order_system.generate_orders(count=2)
        self.order_system.process_orders()
        
        # Verify assignment events
        events = self.mock_event_manager.get_events(EventType.ORDER_ASSIGNED)
        assert len(events) > 0
        
        for event in events:
            assert "order_id" in event["data"]
            assert "robot_id" in event["data"]
```

### 2. Configuration Mocking

```python
class MockConfigurationManager:
    """Mock configuration manager for testing."""
    
    def __init__(self, config=None):
        self.config = config or {
            "order_generation": {
                "enabled": True,
                "interval_seconds": 30,
                "max_orders": 100
            },
            "queue_management": {
                "max_queue_size": 50,
                "timeout_seconds": 300
            }
        }
    
    def get_configuration(self):
        """Get current configuration."""
        return self.config
    
    def update_configuration(self, new_config):
        """Update configuration."""
        self.config.update(new_config)
    
    def validate_configuration(self, config):
        """Validate configuration."""
        return True  # Always valid for testing

class TestWithMockConfiguration:
    """Tests using mock configuration manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_config_manager = MockConfigurationManager()
        self.order_system = OrderManagementSystem(
            EventManager(),
            config_manager=self.mock_config_manager
        )
    
    def test_configuration_loading(self):
        """Test configuration loading."""
        config = self.order_system.get_configuration()
        assert "order_generation" in config
        assert "queue_management" in config
    
    def test_configuration_updates(self):
        """Test configuration updates."""
        new_config = {
            "order_generation": {
                "enabled": False,
                "max_orders": 200
            }
        }
        
        self.order_system.update_configuration(new_config)
        
        updated_config = self.order_system.get_configuration()
        assert updated_config["order_generation"]["enabled"] is False
        assert updated_config["order_generation"]["max_orders"] == 200
```

## Test Data Management

### 1. Test Data Factories

```python
class OrderTestDataFactory:
    """Factory for creating test order data."""
    
    @staticmethod
    def create_order(order_id=None, priority="medium", **kwargs):
        """Create a test order."""
        if order_id is None:
            order_id = f"test_order_{int(time.time() * 1000)}"
        
        return {
            "order_id": order_id,
            "priority": priority,
            "timestamp": time.time(),
            "items": kwargs.get("items", []),
            "location": kwargs.get("location", "zone_a"),
            **kwargs
        }
    
    @staticmethod
    def create_orders(count, priorities=None):
        """Create multiple test orders."""
        if priorities is None:
            priorities = ["medium"] * count
        
        orders = []
        for i in range(count):
            order = OrderTestDataFactory.create_order(
                order_id=f"test_order_{i:03d}",
                priority=priorities[i % len(priorities)]
            )
            orders.append(order)
        
        return orders
    
    @staticmethod
    def create_robot(robot_id=None, status="available", **kwargs):
        """Create test robot data."""
        if robot_id is None:
            robot_id = f"test_robot_{int(time.time() * 1000)}"
        
        return {
            "robot_id": robot_id,
            "status": status,
            "current_orders": kwargs.get("current_orders", 0),
            "location": kwargs.get("location", {"x": 0, "y": 0}),
            **kwargs
        }
    
    @staticmethod
    def create_robots(count, statuses=None):
        """Create multiple test robots."""
        if statuses is None:
            statuses = ["available"] * count
        
        robots = []
        for i in range(count):
            robot = OrderTestDataFactory.create_robot(
                robot_id=f"test_robot_{i:03d}",
                status=statuses[i % len(statuses)]
            )
            robots.append(robot)
        
        return robots

class TestWithTestDataFactory:
    """Tests using test data factory."""
    
    def test_order_creation_with_factory(self):
        """Test order creation using factory."""
        order = OrderTestDataFactory.create_order(
            priority="high",
            items=["item_001", "item_002"]
        )
        
        assert "order_id" in order
        assert order["priority"] == "high"
        assert len(order["items"]) == 2
    
    def test_multiple_orders_with_factory(self):
        """Test creating multiple orders with factory."""
        orders = OrderTestDataFactory.create_orders(
            count=5,
            priorities=["high", "medium", "low"]
        )
        
        assert len(orders) == 5
        assert all("order_id" in order for order in orders)
        assert all("priority" in order for order in orders)
    
    def test_robot_creation_with_factory(self):
        """Test robot creation using factory."""
        robot = OrderTestDataFactory.create_robot(
            status="busy",
            current_orders=2
        )
        
        assert "robot_id" in robot
        assert robot["status"] == "busy"
        assert robot["current_orders"] == 2
```

### 2. Test Data Cleanup

```python
class TestDataCleanup:
    """Utilities for test data cleanup."""
    
    @staticmethod
    def cleanup_order_system(order_system):
        """Clean up order system state."""
        # Clear all orders
        queue_manager = order_system.queue_manager
        while queue_manager.get_queue_size() > 0:
            order = queue_manager.get_next_order()
            if order:
                queue_manager.remove_order(order["order_id"])
        
        # Clear analytics
        analytics = order_system.analytics
        analytics.clear_metrics()
        
        # Clear status tracker
        status_tracker = order_system.status_tracker
        status_tracker.clear_history()
    
    @staticmethod
    def cleanup_event_manager(event_manager):
        """Clean up event manager state."""
        if hasattr(event_manager, 'clear_events'):
            event_manager.clear_events()
    
    @staticmethod
    def reset_system_state(order_system, event_manager):
        """Reset entire system state."""
        TestDataCleanup.cleanup_order_system(order_system)
        TestDataCleanup.cleanup_event_manager(event_manager)

class TestWithCleanup:
    """Tests with automatic cleanup."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.event_manager = EventManager()
        self.order_system = OrderManagementSystem(self.event_manager)
    
    def teardown_method(self):
        """Cleanup after each test."""
        TestDataCleanup.reset_system_state(self.order_system, self.event_manager)
    
    def test_system_state_isolation(self):
        """Test that system state is isolated between tests."""
        # This test should start with clean state
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders == 0
        
        # Generate some orders
        self.order_system.generate_orders(count=5)
        
        # Verify orders were generated
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders == 5
```

## Test Organization

### 1. Test Suite Organization

```python
# tests/unit/test_order_generator.py
class TestOrderGenerator:
    """Unit tests for OrderGenerator."""
    pass

# tests/unit/test_order_queue.py
class TestOrderQueueManager:
    """Unit tests for OrderQueueManager."""
    pass

# tests/integration/test_order_management.py
class TestOrderManagementIntegration:
    """Integration tests for OrderManagementSystem."""
    pass

# tests/performance/test_performance.py
class TestOrderManagementPerformance:
    """Performance tests for OrderManagementSystem."""
    pass

# tests/stress/test_stress.py
class TestOrderManagementStress:
    """Stress tests for OrderManagementSystem."""
    pass
```

### 2. Test Configuration

```python
# tests/conftest.py
import pytest
from core.order_management import OrderManagementSystem
from core.events import EventManager

@pytest.fixture
def event_manager():
    """Provide event manager fixture."""
    return EventManager()

@pytest.fixture
def order_system(event_manager):
    """Provide order management system fixture."""
    return OrderManagementSystem(event_manager)

@pytest.fixture
def mock_event_manager():
    """Provide mock event manager fixture."""
    return MockEventManager()

@pytest.fixture
def test_data_factory():
    """Provide test data factory fixture."""
    return OrderTestDataFactory()

# tests/unit/conftest.py
@pytest.fixture
def order_generator_config():
    """Provide order generator configuration fixture."""
    return {
        "enabled": True,
        "interval_seconds": 30,
        "max_orders": 100,
        "priority_distribution": {
            "high": 0.2,
            "medium": 0.5,
            "low": 0.3
        }
    }

@pytest.fixture
def queue_manager_config():
    """Provide queue manager configuration fixture."""
    return {
        "max_queue_size": 50,
        "timeout_seconds": 300,
        "retry_attempts": 3
    }
```

## Continuous Testing

### 1. Automated Test Execution

```python
# scripts/run_tests.py
import subprocess
import sys
import os

def run_test_suite(test_type="all"):
    """Run test suite based on type."""
    if test_type == "unit":
        cmd = ["python", "-m", "pytest", "tests/unit/", "-v"]
    elif test_type == "integration":
        cmd = ["python", "-m", "pytest", "tests/integration/", "-v"]
    elif test_type == "performance":
        cmd = ["python", "-m", "pytest", "tests/performance/", "-v"]
    elif test_type == "stress":
        cmd = ["python", "-m", "pytest", "tests/stress/", "-v"]
    else:
        cmd = ["python", "-m", "pytest", "tests/", "-v"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    cmd = [
        "python", "-m", "pytest", "tests/",
        "--cov=core",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if test_type == "coverage":
        success = run_tests_with_coverage()
    else:
        success = run_test_suite(test_type)
    
    sys.exit(0 if success else 1)
```

### 2. Test Reporting

```python
# scripts/generate_test_report.py
import json
import datetime
from pathlib import Path

class TestReportGenerator:
    """Generate test reports."""
    
    def __init__(self, report_dir="reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_report(self, test_results, performance_metrics=None):
        """Generate comprehensive test report."""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "test_results": test_results,
            "performance_metrics": performance_metrics or {},
            "summary": self._generate_summary(test_results)
        }
        
        # Save report
        report_file = self.report_dir / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def _generate_summary(self, test_results):
        """Generate test summary."""
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r["status"] == "passed"])
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
```

## Best Practices

### 1. Test Naming and Organization

```python
class TestOrderManagement:
    """Comprehensive test suite for Order Management System."""
    
    class TestOrderGeneration:
        """Tests for order generation functionality."""
        
        def test_generate_single_order(self):
            """Test generating a single order."""
            pass
        
        def test_generate_multiple_orders(self):
            """Test generating multiple orders."""
            pass
        
        def test_priority_distribution(self):
            """Test that priority distribution is respected."""
            pass
    
    class TestOrderQueue:
        """Tests for order queue functionality."""
        
        def test_add_order_to_queue(self):
            """Test adding order to queue."""
            pass
        
        def test_queue_full_behavior(self):
            """Test behavior when queue is full."""
            pass
        
        def test_priority_queue_ordering(self):
            """Test that orders are properly ordered by priority."""
            pass
    
    class TestRobotAssignment:
        """Tests for robot assignment functionality."""
        
        def test_assign_order_to_robot(self):
            """Test assigning order to robot."""
            pass
        
        def test_nearest_robot_assignment(self):
            """Test nearest robot assignment strategy."""
            pass
        
        def test_no_available_robots(self):
            """Test behavior when no robots are available."""
            pass
```

### 2. Test Documentation

```python
class TestOrderManagementDocumentation:
    """Well-documented test examples."""
    
    def test_order_generation_with_documentation(self):
        """
        Test order generation with comprehensive documentation.
        
        This test verifies that:
        1. Orders are generated with unique IDs
        2. Orders have valid priority levels
        3. Orders include required fields
        4. Generation respects configuration limits
        
        Test data:
        - Configuration: enabled=True, max_orders=100
        - Expected: 5 orders with unique IDs and valid priorities
        
        Assertions:
        - All orders have required fields
        - Order IDs are unique
        - Priorities are valid
        - Count matches expected
        """
        # Arrange
        config = {"enabled": True, "max_orders": 100}
        generator = OrderGenerator(config)
        
        # Act
        orders = generator.generate_orders(count=5)
        
        # Assert
        assert len(orders) == 5
        assert all("order_id" in order for order in orders)
        assert all("priority" in order for order in orders)
        assert all(order["priority"] in ["high", "medium", "low"] for order in orders)
        
        # Verify uniqueness
        order_ids = [order["order_id"] for order in orders]
        assert len(order_ids) == len(set(order_ids))
```

### 3. Test Maintenance

```python
class TestMaintenance:
    """Examples of maintainable test patterns."""
    
    def test_with_clear_setup_and_teardown(self):
        """Test with clear setup and teardown."""
        # Setup
        self.setup_test_environment()
        
        try:
            # Test logic
            result = self.perform_test_action()
            
            # Assertions
            assert result is not None
            assert result["status"] == "success"
        
        finally:
            # Teardown
            self.cleanup_test_environment()
    
    def test_with_parameterized_data(self):
        """Test with parameterized test data."""
        test_cases = [
            {"input": 1, "expected": "single"},
            {"input": 5, "expected": "multiple"},
            {"input": 0, "expected": "empty"}
        ]
        
        for test_case in test_cases:
            with self.subTest(input=test_case["input"]):
                result = self.process_input(test_case["input"])
                assert result == test_case["expected"]
    
    def test_with_meaningful_assertions(self):
        """Test with meaningful assertion messages."""
        orders = self.generate_test_orders(5)
        
        assert len(orders) == 5, f"Expected 5 orders, got {len(orders)}"
        
        for i, order in enumerate(orders):
            assert "order_id" in order, f"Order {i} missing order_id"
            assert "priority" in order, f"Order {i} missing priority"
            assert order["priority"] in ["high", "medium", "low"], \
                f"Order {i} has invalid priority: {order['priority']}"
```

This comprehensive testing patterns guide provides the foundation for creating robust, maintainable, and effective tests for the Order Management System. Follow these patterns to ensure high-quality test coverage and reliable system behavior. 