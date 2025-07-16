# Order Management System - Usage Examples & Best Practices

## Overview

This document provides practical usage examples, best practices, and implementation patterns for the warehouse simulation order management system.

## Table of Contents

1. [Basic Usage Examples](#basic-usage-examples)
2. [Advanced Integration Patterns](#advanced-integration-patterns)
3. [Performance Optimization](#performance-optimization)
4. [Error Handling Best Practices](#error-handling-best-practices)
5. [Configuration Best Practices](#configuration-best-practices)
6. [Monitoring and Debugging](#monitoring-and-debugging)
7. [Testing Patterns](#testing-patterns)

---

## Basic Usage Examples

### 1. Simple Order Management Setup

```python
from entities.order_management_integration import OrderManagementIntegration
from entities.configuration_manager import ConfigurationManager
from core.engine import SimulationEngine
from core.events import EventSystem

# Initialize components
simulation_engine = SimulationEngine()
event_system = EventSystem()
config_manager = ConfigurationManager()

# Create integration
integration = OrderManagementIntegration(simulation_engine, event_system, config_manager)

# Start integration
await integration.integrate_with_simulation()

# Start order generation
integration.order_generator.start_generation()

# Monitor system
while True:
    integration.update_integration(0.1)
    time.sleep(0.1)
```

### 2. Custom Order Generation

```python
# Configure order generation
config = {
    'generation_interval': 45.0,  # Generate every 45 seconds
    'min_items_per_order': 2,     # Minimum 2 items per order
    'max_items_per_order': 6,     # Maximum 6 items per order
    'auto_start': True
}

integration.order_generator.configure(config)

# Generate orders manually
current_time = time.time()
order = integration.order_generator.generate_order(current_time)
if order:
    print(f"Generated order: {order.order_id}")
```

### 3. Queue Management

```python
# Check queue status
queue_status = integration.queue_manager.get_queue_status()
print(f"Queue size: {queue_status['queue_size']}/{queue_status['max_size']}")

# Get next order
next_order = integration.queue_manager.get_next_order()
if next_order:
    print(f"Processing order: {next_order.order_id}")

# Clear queue if needed
if queue_status['queue_size'] > 50:
    integration.queue_manager.clear_queue()
    print("Queue cleared due to overflow")
```

### 4. Robot Assignment

```python
# Check robot availability
if integration.robot_assigner.is_robot_available():
    # Get next order
    order = integration.queue_manager.get_next_order()
    if order:
        # Assign to robot
        success = integration.robot_assigner.assign_order_to_robot(order)
        if success:
            print(f"Order {order.order_id} assigned to robot")
        else:
            print(f"Failed to assign order {order.order_id}")
else:
    print("Robot not available")
```

### 5. Status Tracking

```python
# Track order status
order_id = "ORD_001"
status = integration.status_tracker.get_order_status(order_id)
print(f"Order {order_id} status: {status}")

# Update order status
integration.status_tracker.update_order_status(
    order_id, 
    "IN_PROGRESS", 
    robot_id="ROBOT_001"
)

# Mark item as collected
integration.status_tracker.mark_item_collected(
    order_id, 
    "ITEM_A1", 
    "ROBOT_001", 
    time.time()
)
```

### 6. Analytics and Metrics

```python
# Get real-time metrics
metrics = integration.analytics.get_real_time_metrics()
print(f"Success rate: {metrics.get('success_rate', 0):.1f}%")
print(f"Average completion time: {metrics.get('average_completion_time', 0):.1f}s")

# Export analytics
integration.analytics.export_metrics_to_csv("metrics.csv")
integration.analytics.export_metrics_to_json("metrics.json")

# Get analytics summary
summary = integration.analytics.get_analytics_summary()
print(f"Total orders analyzed: {summary.get('total_orders_analyzed', 0)}")
```

---

## Advanced Integration Patterns

### 1. Event-Driven Architecture

```python
# Register custom event handlers
async def handle_order_created(event_data):
    order_id = event_data.get('order_id')
    print(f"New order created: {order_id}")
    
    # Custom processing logic
    if event_data.get('priority') == 'high':
        # Prioritize high-priority orders
        order = integration.queue_manager.get_order_by_id(order_id)
        if order:
            integration.robot_assigner.assign_order_to_robot(order)

# Register handler
integration.event_system.register_handler(
    EventType.ORDER_CREATED, 
    handle_order_created
)
```

### 2. Custom Analytics Integration

```python
# Custom analytics callback
def custom_analytics_callback(analytics_data):
    # Process analytics data
    success_rate = analytics_data.get('success_rate', 0)
    if success_rate < 85:
        print("⚠️ Low success rate detected")
        # Trigger corrective action
        integration.order_generator.pause_generation()

# Register callback
integration.analytics.add_callback(custom_analytics_callback)
```

### 3. Performance Monitoring Integration

```python
from utils.performance_monitor import create_performance_monitor

# Create performance monitor
monitor = create_performance_monitor(integration)

# Add custom alert handler
def handle_performance_alert(alert):
    if alert.alert_level == AlertLevel.CRITICAL:
        print(f"🚨 Critical performance issue: {alert.message}")
        # Take immediate action
        integration.order_generator.pause_generation()

monitor.add_alert_callback(handle_performance_alert)
monitor.start_monitoring()
```

### 4. Custom Configuration Management

```python
# Custom configuration validator
def validate_custom_config(config):
    errors = []
    
    if config.get('generation_interval', 30) < 10:
        errors.append("Generation interval too low")
    
    if config.get('max_queue_size', 100) < 20:
        errors.append("Queue size too small")
    
    return errors

# Apply custom validation
config_manager = ConfigurationManager()
config_manager.add_validator(validate_custom_config)

# Load and validate configuration
if config_manager.load_config():
    print("✅ Configuration loaded and validated")
else:
    print("❌ Configuration validation failed")
```

---

## Performance Optimization

### 1. Optimize Order Generation

```python
# Dynamic generation interval based on queue size
def optimize_generation_interval():
    queue_size = integration.queue_manager.get_queue_size()
    
    if queue_size > 30:
        # Slow down generation
        integration.order_generator.configure({'generation_interval': 60})
    elif queue_size < 5:
        # Speed up generation
        integration.order_generator.configure({'generation_interval': 20})
    else:
        # Normal generation
        integration.order_generator.configure({'generation_interval': 30})

# Apply optimization periodically
import threading
def periodic_optimization():
    while True:
        optimize_generation_interval()
        time.sleep(60)  # Check every minute

optimization_thread = threading.Thread(target=periodic_optimization, daemon=True)
optimization_thread.start()
```

### 2. Queue Optimization

```python
# Implement priority queue
def prioritize_orders():
    orders = integration.queue_manager.queue
    
    # Sort by priority (custom field)
    high_priority = [order for order in orders if order.priority == 'high']
    normal_priority = [order for order in orders if order.priority == 'normal']
    
    # Reorder queue
    integration.queue_manager.clear_queue()
    
    # Add high priority first
    for order in high_priority:
        integration.queue_manager.add_order(order)
    
    # Add normal priority
    for order in normal_priority:
        integration.queue_manager.add_order(order)

# Apply prioritization
prioritize_orders()
```

### 3. Robot Assignment Optimization

```python
# Optimize robot assignment based on distance
def optimize_robot_assignment():
    if not integration.robot_assigner.is_robot_available():
        return
    
    # Get robot position
    robot_position = integration.robot_assigner.get_robot_position()
    
    # Find closest order
    closest_order = None
    min_distance = float('inf')
    
    for order in integration.queue_manager.queue:
        if order.status == "PENDING":
            for item in order.items:
                distance = calculate_distance(robot_position, item.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_order = order
    
    # Assign closest order
    if closest_order:
        integration.robot_assigner.assign_order_to_robot(closest_order)

def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
```

### 4. Memory Management

```python
# Clean up completed orders
def cleanup_completed_orders():
    completed_orders = []
    
    for order in integration.queue_manager.queue:
        if order.status == "COMPLETED":
            completed_orders.append(order.order_id)
    
    # Remove completed orders
    for order_id in completed_orders:
        integration.queue_manager.remove_order(order_id)
    
    # Clean up analytics data
    integration.analytics.cleanup_old_data()

# Run cleanup periodically
def periodic_cleanup():
    while True:
        cleanup_completed_orders()
        time.sleep(300)  # Every 5 minutes

cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()
```

---

## Error Handling Best Practices

### 1. Graceful Error Handling

```python
# Comprehensive error handling
def safe_order_processing():
    try:
        # Generate order
        order = integration.order_generator.generate_order(time.time())
        if order:
            # Add to queue
            success = integration.queue_manager.add_order(order)
            if not success:
                print(f"❌ Failed to add order {order.order_id} to queue")
                return False
            
            # Assign to robot
            if integration.robot_assigner.is_robot_available():
                assignment_success = integration.robot_assigner.assign_order_to_robot(order)
                if not assignment_success:
                    print(f"❌ Failed to assign order {order.order_id} to robot")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Order processing error: {e}")
        # Log error for debugging
        logging.error(f"Order processing failed: {e}")
        return False

# Use safe processing
if safe_order_processing():
    print("✅ Order processed successfully")
else:
    print("❌ Order processing failed")
```

### 2. Retry Mechanisms

```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"❌ Final attempt failed: {e}")
                        raise
                    else:
                        print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                        time.sleep(delay)
            return None
        return wrapper
    return decorator

# Apply retry to critical operations
@retry_on_failure(max_attempts=3, delay=2.0)
def assign_order_with_retry(order):
    return integration.robot_assigner.assign_order_to_robot(order)

# Use retry mechanism
order = integration.queue_manager.get_next_order()
if order:
    success = assign_order_with_retry(order)
    print(f"Assignment result: {success}")
```

### 3. Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e

# Use circuit breaker for critical operations
order_assignment_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

def safe_order_assignment(order):
    return order_assignment_breaker.call(
        integration.robot_assigner.assign_order_to_robot, 
        order
    )
```

---

## Configuration Best Practices

### 1. Environment-Specific Configuration

```python
import os

class EnvironmentConfig:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.configs = {
            'development': {
                'generation_interval': 30.0,
                'max_queue_size': 50,
                'debug_level': 'detailed'
            },
            'testing': {
                'generation_interval': 10.0,
                'max_queue_size': 20,
                'debug_level': 'verbose'
            },
            'production': {
                'generation_interval': 45.0,
                'max_queue_size': 100,
                'debug_level': 'basic'
            }
        }
    
    def get_config(self):
        return self.configs.get(self.environment, self.configs['development'])

# Apply environment-specific configuration
env_config = EnvironmentConfig()
config = env_config.get_config()
integration.order_generator.configure(config)
```

### 2. Configuration Validation

```python
def validate_configuration(config):
    """Validate configuration parameters."""
    errors = []
    
    # Check required fields
    required_fields = ['generation_interval', 'max_queue_size']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Check value ranges
    if config.get('generation_interval', 0) < 1:
        errors.append("Generation interval must be >= 1 second")
    
    if config.get('max_queue_size', 0) < 10:
        errors.append("Queue size must be >= 10")
    
    if config.get('min_items_per_order', 0) < 1:
        errors.append("Min items per order must be >= 1")
    
    if config.get('max_items_per_order', 0) < config.get('min_items_per_order', 0):
        errors.append("Max items must be >= min items")
    
    return errors

# Validate before applying
config = {
    'generation_interval': 30.0,
    'max_queue_size': 100,
    'min_items_per_order': 1,
    'max_items_per_order': 4
}

errors = validate_configuration(config)
if errors:
    print("❌ Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Configuration valid")
    integration.order_generator.configure(config)
```

### 3. Configuration Hot Reloading

```python
import json
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigReloadHandler(FileSystemEventHandler):
    def __init__(self, integration):
        self.integration = integration
        self.last_modified = 0
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('config.json'):
            # Prevent multiple reloads
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                self.reload_config()
    
    def reload_config(self):
        try:
            config_manager = ConfigurationManager()
            if config_manager.load_config():
                # Apply new configuration
                gen_config = config_manager.get_order_generation_config()
                self.integration.order_generator.configure({
                    'generation_interval': gen_config.generation_interval,
                    'min_items_per_order': gen_config.min_items_per_order,
                    'max_items_per_order': gen_config.max_items_per_order
                })
                print("✅ Configuration reloaded")
            else:
                print("❌ Failed to reload configuration")
        except Exception as e:
            print(f"❌ Configuration reload error: {e}")

# Set up file watching
config_handler = ConfigReloadHandler(integration)
observer = Observer()
observer.schedule(config_handler, path='config', recursive=False)
observer.start()
```

---

## Monitoring and Debugging

### 1. Comprehensive Monitoring Setup

```python
from utils.order_debug_tools import start_debug_monitoring, DebugLevel
from utils.performance_monitor import start_performance_monitoring
from utils.order_visualizer import start_visualization, VisualizationType

# Start comprehensive monitoring
def start_monitoring_suite(integration):
    # Debug monitoring
    debugger = start_debug_monitoring(integration, DebugLevel.DETAILED)
    
    # Performance monitoring
    performance_monitor = start_performance_monitoring(integration, display=True)
    
    # Visualization
    queue_viz = start_visualization(integration, VisualizationType.QUEUE_STATUS)
    overview_viz = start_visualization(integration, VisualizationType.SYSTEM_OVERVIEW)
    
    return debugger, performance_monitor, queue_viz, overview_viz

# Start monitoring
monitors = start_monitoring_suite(integration)
```

### 2. Custom Metrics Collection

```python
class CustomMetricsCollector:
    def __init__(self, integration):
        self.integration = integration
        self.metrics = {}
    
    def collect_custom_metrics(self):
        """Collect custom business metrics."""
        metrics = {}
        
        # Order processing efficiency
        total_orders = len(self.integration.queue_manager.queue)
        completed_orders = sum(1 for order in self.integration.queue_manager.queue 
                             if order.status == "COMPLETED")
        efficiency = (completed_orders / max(total_orders, 1)) * 100
        metrics['order_efficiency'] = efficiency
        
        # Robot utilization
        robot_status = self.integration.robot_assigner.get_assignment_status()
        utilization = 100 if robot_status.get('current_order') else 0
        metrics['robot_utilization'] = utilization
        
        # Queue health
        queue_status = self.integration.queue_manager.get_queue_status()
        queue_health = (queue_status['queue_size'] / queue_status['max_size']) * 100
        metrics['queue_health'] = queue_health
        
        self.metrics = metrics
        return metrics
    
    def export_metrics(self, filename):
        """Export custom metrics."""
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)

# Use custom metrics
collector = CustomMetricsCollector(integration)
metrics = collector.collect_custom_metrics()
print(f"Custom metrics: {metrics}")
```

### 3. Automated Health Checks

```python
def health_check():
    """Comprehensive health check."""
    health_status = {
        'integration': False,
        'order_generator': False,
        'queue_manager': False,
        'robot_assigner': False,
        'status_tracker': False,
        'analytics': False
    }
    
    # Check integration
    integration_status = integration.get_integration_status()
    health_status['integration'] = integration_status.get('is_integrated', False)
    
    # Check order generator
    gen_status = integration.order_generator.get_status()
    health_status['order_generator'] = gen_status.get('status') == 'RUNNING'
    
    # Check queue manager
    queue_status = integration.queue_manager.get_queue_status()
    health_status['queue_manager'] = queue_status['queue_size'] >= 0
    
    # Check robot assigner
    robot_status = integration.robot_assigner.get_assignment_status()
    health_status['robot_assigner'] = robot_status.get('is_active', False)
    
    # Check status tracker
    tracking_stats = integration.status_tracker.get_tracking_statistics()
    health_status['status_tracker'] = tracking_stats.get('total_orders_tracked', 0) >= 0
    
    # Check analytics
    analytics_summary = integration.analytics.get_analytics_summary()
    health_status['analytics'] = analytics_summary.get('is_active', False)
    
    # Overall health
    overall_health = all(health_status.values())
    
    return {
        'overall_health': overall_health,
        'component_health': health_status,
        'timestamp': time.time()
    }

# Run health check
health = health_check()
if health['overall_health']:
    print("✅ System healthy")
else:
    print("❌ System health issues detected")
    for component, status in health['component_health'].items():
        if not status:
            print(f"  - {component}: ❌")
```

---

## Testing Patterns

### 1. Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestOrderManagement(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.simulation_engine = Mock()
        self.event_system = Mock()
        self.config_manager = Mock()
        
        self.integration = OrderManagementIntegration(
            self.simulation_engine,
            self.event_system,
            self.config_manager
        )
    
    def test_order_generation(self):
        """Test order generation functionality."""
        # Mock warehouse layout
        mock_layout = Mock()
        self.integration.order_generator.warehouse_layout = mock_layout
        
        # Test order generation
        order = self.integration.order_generator.generate_order(time.time())
        self.assertIsNotNone(order)
        self.assertIsInstance(order.order_id, str)
        self.assertGreater(len(order.items), 0)
    
    def test_queue_management(self):
        """Test queue management functionality."""
        # Create test order
        order = Mock()
        order.order_id = "TEST_001"
        order.status = "PENDING"
        
        # Test adding order
        success = self.integration.queue_manager.add_order(order)
        self.assertTrue(success)
        
        # Test getting order
        retrieved_order = self.integration.queue_manager.get_order_by_id("TEST_001")
        self.assertEqual(retrieved_order.order_id, "TEST_001")
    
    def test_robot_assignment(self):
        """Test robot assignment functionality."""
        # Mock robot availability
        self.integration.robot_assigner.is_robot_available = Mock(return_value=True)
        
        # Create test order
        order = Mock()
        order.order_id = "TEST_002"
        
        # Test assignment
        success = self.integration.robot_assigner.assign_order_to_robot(order)
        self.assertTrue(success)
        
        # Verify assignment
        current_order = self.integration.robot_assigner.get_current_order()
        self.assertEqual(current_order.order_id, "TEST_002")

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Testing

```python
class TestOrderManagementIntegration(unittest.TestCase):
    def setUp(self):
        """Set up integration test fixtures."""
        self.simulation_engine = Mock()
        self.event_system = Mock()
        self.config_manager = Mock()
        
        # Configure mocks
        self.simulation_engine.warehouse_layout = Mock()
        self.event_system.emit = Mock()
        
        self.integration = OrderManagementIntegration(
            self.simulation_engine,
            self.event_system,
            self.config_manager
        )
    
    async def test_full_order_lifecycle(self):
        """Test complete order lifecycle."""
        # Start integration
        success = await self.integration.integrate_with_simulation()
        self.assertTrue(success)
        
        # Generate order
        order = self.integration.order_generator.generate_order(time.time())
        self.assertIsNotNone(order)
        
        # Add to queue
        success = self.integration.queue_manager.add_order(order)
        self.assertTrue(success)
        
        # Assign to robot
        success = self.integration.robot_assigner.assign_order_to_robot(order)
        self.assertTrue(success)
        
        # Track status
        self.integration.status_tracker.track_order(order)
        
        # Complete order
        success = self.integration.robot_assigner.complete_current_order()
        self.assertTrue(success)
        
        # Verify completion
        status = self.integration.status_tracker.get_order_status(order.order_id)
        self.assertEqual(status, "COMPLETED")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test invalid order generation
        self.integration.order_generator.warehouse_layout = None
        order = self.integration.order_generator.generate_order(time.time())
        self.assertIsNone(order)
        
        # Test queue overflow
        self.integration.queue_manager.max_size = 1
        order1 = Mock()
        order2 = Mock()
        
        success1 = self.integration.queue_manager.add_order(order1)
        success2 = self.integration.queue_manager.add_order(order2)
        
        self.assertTrue(success1)
        self.assertFalse(success2)  # Queue should be full
```

### 3. Performance Testing

```python
import time
import statistics

class TestOrderManagementPerformance(unittest.TestCase):
    def setUp(self):
        """Set up performance test fixtures."""
        self.integration = OrderManagementIntegration(
            Mock(), Mock(), Mock()
        )
    
    def test_order_generation_performance(self):
        """Test order generation performance."""
        start_time = time.time()
        orders = []
        
        # Generate 100 orders
        for _ in range(100):
            order = self.integration.order_generator.generate_order(time.time())
            if order:
                orders.append(order)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Performance assertions
        self.assertGreater(len(orders), 90)  # At least 90% success rate
        self.assertLess(generation_time, 10.0)  # Should complete within 10 seconds
        
        print(f"Generated {len(orders)} orders in {generation_time:.2f}s")
    
    def test_queue_processing_performance(self):
        """Test queue processing performance."""
        # Add orders to queue
        for i in range(50):
            order = Mock()
            order.order_id = f"PERF_{i:03d}"
            self.integration.queue_manager.add_order(order)
        
        # Measure processing time
        start_time = time.time()
        
        processed_orders = []
        while self.integration.queue_manager.get_queue_size() > 0:
            order = self.integration.queue_manager.get_next_order()
            if order:
                processed_orders.append(order)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(processed_orders), 50)
        self.assertLess(processing_time, 5.0)  # Should complete within 5 seconds
        
        print(f"Processed {len(processed_orders)} orders in {processing_time:.2f}s")
    
    def test_memory_usage(self):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate and process many orders
        for i in range(1000):
            order = self.integration.order_generator.generate_order(time.time())
            if order:
                self.integration.queue_manager.add_order(order)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory assertions
        self.assertLess(memory_increase, 100)  # Should not increase by more than 100MB
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
```

---

## Quick Reference

### Common Patterns

```python
# Initialize system
integration = OrderManagementIntegration(simulation_engine, event_system, config_manager)
await integration.integrate_with_simulation()

# Start monitoring
from utils.order_debug_tools import start_debug_monitoring
debugger = start_debug_monitoring(integration)

# Handle errors gracefully
try:
    order = integration.order_generator.generate_order(time.time())
    if order:
        integration.queue_manager.add_order(order)
except Exception as e:
    print(f"Error: {e}")
    # Log error and continue

# Monitor performance
metrics = integration.analytics.get_real_time_metrics()
if metrics.get('success_rate', 100) < 85:
    print("⚠️ Low success rate detected")

# Export data
integration.analytics.export_metrics_to_csv("metrics.csv")
```

### Best Practices Summary

1. **Always handle errors gracefully** - Use try-catch blocks and retry mechanisms
2. **Monitor performance continuously** - Set up alerts and monitoring
3. **Validate configuration** - Check parameters before applying
4. **Use appropriate logging** - Log important events and errors
5. **Test thoroughly** - Unit test, integration test, and performance test
6. **Optimize based on metrics** - Use analytics to improve performance
7. **Document your usage** - Keep track of custom implementations
8. **Plan for scale** - Design for future growth and requirements

This guide provides practical examples and best practices for using the order management system effectively. Adapt these patterns to your specific requirements and use cases. 