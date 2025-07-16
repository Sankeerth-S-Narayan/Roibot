# Order Management System Integration Guide

## Overview

This guide provides comprehensive instructions for integrating the Order Management System into your warehouse simulation project. The system is designed to be modular and extensible, allowing seamless integration with existing robot and warehouse components.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [API Integration](#api-integration)
6. [Event System Integration](#event-system-integration)
7. [Testing Integration](#testing-integration)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Quick Start

### 1. Basic Integration

```python
from core.order_management import OrderManagementSystem
from core.events import EventManager

# Initialize the system
event_manager = EventManager()
order_system = OrderManagementSystem(event_manager)

# Start the system
order_system.start()
```

### 2. Generate and Process Orders

```python
# Generate orders
order_system.generate_orders(count=5)

# Process orders
order_system.process_orders()

# Get analytics
analytics = order_system.get_analytics()
print(f"Total orders: {analytics.total_orders}")
```

## System Architecture

### Core Components

```
OrderManagementSystem
├── OrderGenerator
├── OrderQueueManager
├── RobotOrderAssigner
├── OrderStatusTracker
├── OrderAnalytics
├── ConfigurationManager
└── EventManager (external)
```

### Data Flow

```
Order Generation → Queue Management → Robot Assignment → Status Tracking → Analytics
```

## Installation & Setup

### 1. Dependencies

Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration Files

Create configuration files in the `config/` directory:

```json
// config/order_management.json
{
  "order_generation": {
    "enabled": true,
    "interval_seconds": 30,
    "max_orders": 100,
    "priority_distribution": {
      "high": 0.2,
      "medium": 0.5,
      "low": 0.3
    }
  },
  "queue_management": {
    "max_queue_size": 50,
    "timeout_seconds": 300,
    "retry_attempts": 3
  },
  "robot_assignment": {
    "assignment_strategy": "nearest_available",
    "load_balancing": true,
    "max_orders_per_robot": 3
  }
}
```

### 3. Environment Setup

```python
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
```

## Configuration

### 1. Order Generation Configuration

```python
from core.order_management import OrderGenerator

config = {
    "enabled": True,
    "interval_seconds": 30,
    "max_orders": 100,
    "priority_distribution": {
        "high": 0.2,
        "medium": 0.5,
        "low": 0.3
    },
    "order_types": {
        "pick": 0.6,
        "pack": 0.3,
        "ship": 0.1
    }
}

generator = OrderGenerator(config)
```

### 2. Queue Management Configuration

```python
from core.order_management import OrderQueueManager

queue_config = {
    "max_queue_size": 50,
    "timeout_seconds": 300,
    "retry_attempts": 3,
    "priority_queues": {
        "high": {"max_size": 10, "timeout": 60},
        "medium": {"max_size": 25, "timeout": 300},
        "low": {"max_size": 15, "timeout": 600}
    }
}

queue_manager = OrderQueueManager(queue_config)
```

### 3. Robot Assignment Configuration

```python
from core.order_management import RobotOrderAssigner

assignment_config = {
    "strategy": "nearest_available",
    "load_balancing": True,
    "max_orders_per_robot": 3,
    "assignment_timeout": 30,
    "retry_on_failure": True
}

assigner = RobotOrderAssigner(assignment_config)
```

## API Integration

### 1. Basic API Usage

```python
from core.order_management import OrderManagementSystem

# Initialize system
order_system = OrderManagementSystem(event_manager)

# Generate orders
orders = order_system.generate_orders(count=5)

# Get queue status
queue_status = order_system.get_queue_status()

# Assign orders to robots
assignments = order_system.assign_orders_to_robots()

# Track order status
status_updates = order_system.update_order_statuses()

# Get analytics
analytics = order_system.get_analytics()
```

### 2. Advanced API Usage

```python
# Custom order generation
custom_orders = order_system.generate_custom_orders(
    count=10,
    priority="high",
    order_type="pick",
    location="zone_a"
)

# Batch processing
order_system.process_orders_batch(batch_size=5)

# Priority queue management
high_priority_orders = order_system.get_orders_by_priority("high")

# Robot-specific assignments
robot_assignments = order_system.assign_orders_to_robot(robot_id="robot_001")
```

### 3. Event-Driven Integration

```python
from core.events import EventType

# Subscribe to order events
def handle_order_created(event):
    print(f"New order created: {event.data}")

def handle_order_assigned(event):
    print(f"Order assigned to robot: {event.data}")

def handle_order_completed(event):
    print(f"Order completed: {event.data}")

event_manager.subscribe(EventType.ORDER_CREATED, handle_order_created)
event_manager.subscribe(EventType.ORDER_ASSIGNED, handle_order_assigned)
event_manager.subscribe(EventType.ORDER_COMPLETED, handle_order_completed)
```

## Event System Integration

### 1. Event Types

The system emits the following events:

- `ORDER_CREATED`: When a new order is generated
- `ORDER_QUEUED`: When an order is added to the queue
- `ORDER_ASSIGNED`: When an order is assigned to a robot
- `ORDER_STARTED`: When a robot starts processing an order
- `ORDER_COMPLETED`: When an order is completed
- `ORDER_FAILED`: When an order processing fails
- `ORDER_TIMEOUT`: When an order times out
- `QUEUE_FULL`: When the order queue is full
- `ROBOT_AVAILABLE`: When a robot becomes available

### 2. Event Data Structure

```python
{
    "order_id": "order_001",
    "robot_id": "robot_001",
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "assigned",
    "priority": "high",
    "location": "zone_a",
    "metadata": {
        "estimated_duration": 300,
        "items_count": 5
    }
}
```

### 3. Custom Event Handlers

```python
class CustomOrderHandler:
    def __init__(self, order_system):
        self.order_system = order_system
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        event_manager = self.order_system.event_manager
        event_manager.subscribe(EventType.ORDER_CREATED, self.on_order_created)
        event_manager.subscribe(EventType.ORDER_COMPLETED, self.on_order_completed)
    
    def on_order_created(self, event):
        # Custom logic for order creation
        order = event.data
        print(f"Processing new order: {order['order_id']}")
        
        # Update external systems
        self.update_inventory(order)
        self.notify_warehouse_staff(order)
    
    def on_order_completed(self, event):
        # Custom logic for order completion
        order = event.data
        print(f"Order completed: {order['order_id']}")
        
        # Update metrics
        self.update_performance_metrics(order)
        self.generate_completion_report(order)
```

## Testing Integration

### 1. Unit Testing

```python
import pytest
from core.order_management import OrderManagementSystem

class TestOrderManagementIntegration:
    def setup_method(self):
        self.event_manager = EventManager()
        self.order_system = OrderManagementSystem(self.event_manager)
    
    def test_order_generation_integration(self):
        # Test order generation
        orders = self.order_system.generate_orders(count=3)
        assert len(orders) == 3
        
        # Verify events were emitted
        events = self.event_manager.get_events(EventType.ORDER_CREATED)
        assert len(events) == 3
    
    def test_order_assignment_integration(self):
        # Test order assignment
        orders = self.order_system.generate_orders(count=2)
        assignments = self.order_system.assign_orders_to_robots()
        
        assert len(assignments) > 0
        
        # Verify assignment events
        events = self.event_manager.get_events(EventType.ORDER_ASSIGNED)
        assert len(events) > 0
```

### 2. Integration Testing

```python
class TestFullOrderWorkflow:
    def test_complete_order_workflow(self):
        # Generate orders
        orders = self.order_system.generate_orders(count=5)
        
        # Process orders
        self.order_system.process_orders()
        
        # Verify queue status
        queue_status = self.order_system.get_queue_status()
        assert queue_status.total_orders > 0
        
        # Verify analytics
        analytics = self.order_system.get_analytics()
        assert analytics.total_orders == 5
```

### 3. Performance Testing

```python
import time

class TestOrderManagementPerformance:
    def test_order_generation_performance(self):
        start_time = time.time()
        
        # Generate large batch of orders
        orders = self.order_system.generate_orders(count=1000)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion
        assert duration < 1.0  # Should complete within 1 second
        assert len(orders) == 1000
```

## Performance Optimization

### 1. Configuration Optimization

```python
# Optimize for high throughput
high_throughput_config = {
    "order_generation": {
        "interval_seconds": 10,  # Faster generation
        "max_orders": 500,       # Larger capacity
        "batch_size": 50         # Batch processing
    },
    "queue_management": {
        "max_queue_size": 200,   # Larger queue
        "timeout_seconds": 600   # Longer timeout
    },
    "robot_assignment": {
        "max_orders_per_robot": 5,  # More orders per robot
        "assignment_timeout": 15     # Faster assignment
    }
}
```

### 2. Memory Management

```python
# Configure memory limits
memory_config = {
    "max_orders_in_memory": 1000,
    "cleanup_interval": 300,
    "persist_to_disk": True,
    "disk_cache_size": 10000
}

order_system.configure_memory_management(memory_config)
```

### 3. Caching Strategy

```python
# Enable caching for better performance
cache_config = {
    "enable_analytics_cache": True,
    "cache_ttl_seconds": 300,
    "max_cache_size": 1000
}

order_system.enable_caching(cache_config)
```

## Troubleshooting

### 1. Common Issues

#### Issue: Orders not being generated
```python
# Check configuration
config = order_system.get_configuration()
print(f"Order generation enabled: {config['order_generation']['enabled']}")

# Check event manager
events = event_manager.get_events(EventType.ORDER_CREATED)
print(f"Generated orders: {len(events)}")
```

#### Issue: Orders stuck in queue
```python
# Check queue status
queue_status = order_system.get_queue_status()
print(f"Queue size: {queue_status.total_orders}")
print(f"Available robots: {queue_status.available_robots}")

# Check for timeouts
timeout_orders = order_system.get_timed_out_orders()
print(f"Timed out orders: {len(timeout_orders)}")
```

#### Issue: Poor performance
```python
# Check performance metrics
performance = order_system.get_performance_metrics()
print(f"Average processing time: {performance.avg_processing_time}")
print(f"Orders per minute: {performance.orders_per_minute}")

# Optimize configuration
order_system.optimize_configuration()
```

### 2. Debug Tools

```python
from utils.order_debug_tools import OrderDebugger

# Initialize debugger
debugger = OrderDebugger(order_system)

# Analyze system state
debugger.analyze_system_state()

# Check for issues
issues = debugger.detect_issues()
for issue in issues:
    print(f"Issue: {issue.description}")
    print(f"Severity: {issue.severity}")
    print(f"Recommendation: {issue.recommendation}")
```

### 3. Logging and Monitoring

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('order_management.log'),
        logging.StreamHandler()
    ]
)

# Monitor system health
from utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor(order_system)
monitor.start_monitoring()

# Get health report
health_report = monitor.get_health_report()
print(f"System health: {health_report.overall_health}")
```

## Best Practices

### 1. Configuration Management

- Use environment variables for sensitive configuration
- Implement configuration validation
- Use configuration templates for different environments
- Version control your configuration files

```python
import os
from core.config import ConfigManager

# Load configuration from environment
config = ConfigManager()
config.load_from_environment()

# Validate configuration
config.validate()

# Use environment-specific config
env = os.getenv('ENVIRONMENT', 'development')
config.load_environment_config(env)
```

### 2. Error Handling

```python
from core.order_management import OrderManagementSystem

class RobustOrderSystem:
    def __init__(self, event_manager):
        self.order_system = OrderManagementSystem(event_manager)
        self.setup_error_handling()
    
    def setup_error_handling(self):
        # Handle order generation errors
        try:
            self.order_system.generate_orders(count=5)
        except Exception as e:
            logging.error(f"Order generation failed: {e}")
            self.handle_generation_error(e)
    
    def handle_generation_error(self, error):
        # Implement retry logic
        if self.should_retry(error):
            self.retry_order_generation()
        else:
            self.notify_admin(error)
```

### 3. Monitoring and Alerting

```python
from utils.performance_monitor import PerformanceMonitor

class OrderSystemMonitor:
    def __init__(self, order_system):
        self.order_system = order_system
        self.monitor = PerformanceMonitor(order_system)
        self.setup_alerts()
    
    def setup_alerts(self):
        # Monitor queue size
        self.monitor.alert_on_queue_full(threshold=0.9)
        
        # Monitor processing time
        self.monitor.alert_on_slow_processing(threshold=300)
        
        # Monitor error rate
        self.monitor.alert_on_high_error_rate(threshold=0.05)
    
    def handle_alert(self, alert):
        if alert.type == "queue_full":
            self.scale_up_processing()
        elif alert.type == "slow_processing":
            self.optimize_robot_assignment()
        elif alert.type == "high_error_rate":
            self.investigate_errors()
```

### 4. Testing Strategy

- Write comprehensive unit tests
- Implement integration tests
- Use performance benchmarks
- Test error scenarios
- Validate configuration changes

```python
class ComprehensiveOrderTests:
    def test_all_order_scenarios(self):
        # Test normal operation
        self.test_normal_order_flow()
        
        # Test error scenarios
        self.test_order_generation_failure()
        self.test_queue_overflow()
        self.test_robot_unavailable()
        
        # Test performance
        self.test_high_load_scenario()
        self.test_concurrent_orders()
        
        # Test configuration changes
        self.test_configuration_updates()
```

### 5. Documentation

- Keep API documentation updated
- Document configuration options
- Maintain troubleshooting guides
- Create usage examples
- Document performance characteristics

This integration guide provides a comprehensive foundation for integrating the Order Management System into your warehouse simulation. Follow the best practices outlined here to ensure a robust and maintainable implementation. 