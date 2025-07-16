# Order Management System API Documentation

## Overview

The Order Management System provides comprehensive order generation, queue management, robot assignment, status tracking, analytics, and integration capabilities for the warehouse simulation. This document provides detailed API documentation for all order management components.

## Table of Contents

1. [OrderGenerator](#ordergenerator)
2. [OrderQueueManager](#orderqueuemanager)
3. [RobotOrderAssigner](#robotorderassigner)
4. [OrderStatusTracker](#orderstatustracker)
5. [OrderAnalytics](#orderanalytics)
6. [AnalyticsDashboard](#analyticsdashboard)
7. [ConfigurationManager](#configurationmanager)
8. [OrderManagementIntegration](#ordermanagementintegration)

---

## OrderGenerator

**Purpose:** Handles automatic order generation with configurable timing and item selection.

### Class: `OrderGenerator`

#### Constructor
```python
def __init__(self, warehouse_layout: WarehouseLayoutManager)
```
**Parameters:**
- `warehouse_layout`: Warehouse layout manager for coordinate validation

#### Methods

##### `configure(config: Dict[str, Any])`
Configure the order generator with settings.

**Parameters:**
- `config`: Configuration dictionary with generation settings
  - `generation_interval`: Time between order generation (default: 30.0)
  - `min_items_per_order`: Minimum items per order (default: 1)
  - `max_items_per_order`: Maximum items per order (default: 4)

**Raises:**
- `ValueError`: If configuration parameters are invalid

##### `start_generation()`
Start automatic order generation.

##### `stop_generation()`
Stop automatic order generation.

##### `pause_generation()`
Pause automatic order generation.

##### `resume_generation()`
Resume automatic order generation.

##### `generate_order(current_time: float) -> Optional[Order]`
Generate a new order with random items.

**Parameters:**
- `current_time`: Current simulation time

**Returns:**
- `Order` object or `None` if generation failed

##### `update(current_time: float) -> Optional[Order]`
Update the order generator and generate orders based on timing.

**Parameters:**
- `current_time`: Current simulation time

**Returns:**
- Generated `Order` object or `None`

##### `get_status() -> Dict[str, Any]`
Get current generation status and statistics.

**Returns:**
- Dictionary with status information

#### Properties
- `is_generating`: Whether generation is active
- `status`: Current generation status (RUNNING, PAUSED, STOPPED)
- `total_orders_generated`: Total orders generated
- `generation_errors`: Number of generation errors

---

## OrderQueueManager

**Purpose:** Manages FIFO order queue with status tracking and validation.

### Class: `OrderQueueManager`

#### Constructor
```python
def __init__(self, max_queue_size: int = 100)
```
**Parameters:**
- `max_queue_size`: Maximum number of orders in queue

#### Methods

##### `add_order(order: Order) -> bool`
Add an order to the queue.

**Parameters:**
- `order`: Order object to add

**Returns:**
- `True` if order added successfully, `False` otherwise

##### `get_next_order() -> Optional[Order]`
Get the next order from the queue (FIFO).

**Returns:**
- Next `Order` object or `None` if queue is empty

##### `remove_order(order_id: str) -> bool`
Remove an order from the queue by ID.

**Parameters:**
- `order_id`: ID of order to remove

**Returns:**
- `True` if order removed successfully, `False` otherwise

##### `get_order_by_id(order_id: str) -> Optional[Order]`
Get an order by ID.

**Parameters:**
- `order_id`: ID of order to retrieve

**Returns:**
- `Order` object or `None` if not found

##### `get_queue_size() -> int`
Get current queue size.

**Returns:**
- Number of orders in queue

##### `clear_queue()`
Remove all orders from the queue.

##### `get_queue_status() -> Dict[str, Any]`
Get detailed queue status and statistics.

**Returns:**
- Dictionary with queue information

#### Properties
- `queue`: List of orders in queue
- `max_size`: Maximum queue size
- `total_orders_processed`: Total orders processed

---

## RobotOrderAssigner

**Purpose:** Handles robot assignment to orders with state management.

### Class: `RobotOrderAssigner`

#### Constructor
```python
def __init__(self, robot_id: str = "ROBOT_001")
```
**Parameters:**
- `robot_id`: ID of the robot to assign orders to

#### Methods

##### `assign_order_to_robot(order: Order) -> bool`
Assign an order to the robot.

**Parameters:**
- `order`: Order object to assign

**Returns:**
- `True` if assignment successful, `False` otherwise

##### `get_current_order() -> Optional[Order]`
Get the currently assigned order.

**Returns:**
- Currently assigned `Order` object or `None`

##### `complete_current_order() -> bool`
Mark the current order as completed.

**Returns:**
- `True` if order completed successfully, `False` otherwise

##### `is_robot_available() -> bool`
Check if robot is available for new assignments.

**Returns:**
- `True` if robot is available, `False` otherwise

##### `update()`
Update robot assignment state and process orders.

##### `get_assignment_status() -> Dict[str, Any]`
Get current assignment status and statistics.

**Returns:**
- Dictionary with assignment information

#### Properties
- `robot_id`: ID of assigned robot
- `current_order`: Currently assigned order
- `is_active`: Whether assigner is active
- `total_orders_assigned`: Total orders assigned

---

## OrderStatusTracker

**Purpose:** Tracks order status and completion verification.

### Class: `OrderStatusTracker`

#### Constructor
```python
def __init__(self, robot_assigner: RobotOrderAssigner, queue_manager: OrderQueueManager)
```
**Parameters:**
- `robot_assigner`: RobotOrderAssigner instance for robot integration
- `queue_manager`: OrderQueueManager instance for queue integration

#### Methods

##### `track_order(order: Order) -> bool`
Start tracking an order for status updates.

**Parameters:**
- `order`: Order object to track

**Returns:**
- `True` if tracking started successfully, `False` otherwise

##### `update_order_status(order_id: str, new_status: OrderStatus, robot_id: Optional[str] = None, collected_items: Optional[List[str]] = None) -> bool`
Update order status with real-time tracking.

**Parameters:**
- `order_id`: ID of the order to update
- `new_status`: New status for the order
- `robot_id`: Optional robot ID for assignment
- `collected_items`: Optional list of collected items

**Returns:**
- `True` if status updated successfully, `False` otherwise

##### `mark_item_collected(order_id: str, item_id: str, robot_id: str, collection_time: float) -> bool`
Mark an item as collected with real-time tracking.

**Parameters:**
- `order_id`: ID of the order
- `item_id`: ID of the collected item
- `robot_id`: ID of the robot that collected the item
- `collection_time`: Timestamp of collection

**Returns:**
- `True` if item marked as collected successfully, `False` otherwise

##### `get_order_status(order_id: str) -> Optional[OrderStatus]`
Get current status of an order.

**Parameters:**
- `order_id`: ID of the order

**Returns:**
- Current `OrderStatus` or `None` if order not found

##### `get_completion_metrics(order_id: str) -> Optional[OrderCompletionMetrics]`
Get completion metrics for an order.

**Parameters:**
- `order_id`: ID of the order

**Returns:**
- `OrderCompletionMetrics` object or `None` if not found

##### `get_tracking_statistics() -> Dict[str, Any]`
Get tracking statistics and performance metrics.

**Returns:**
- Dictionary with tracking statistics

#### Properties
- `active_orders`: Dictionary of currently tracked orders
- `completed_orders`: Dictionary of completed orders
- `total_orders_tracked`: Total orders tracked
- `total_completions`: Total orders completed

---

## OrderAnalytics

**Purpose:** Provides real-time performance metrics and analytics.

### Class: `OrderAnalytics`

#### Constructor
```python
def __init__(self, status_tracker: OrderStatusTracker, robot_assigner: RobotOrderAssigner, queue_manager: OrderQueueManager)
```
**Parameters:**
- `status_tracker`: OrderStatusTracker instance
- `robot_assigner`: RobotOrderAssigner instance
- `queue_manager`: OrderQueueManager instance

#### Methods

##### `update_order_metrics(order: Order)`
Update metrics for a specific order.

**Parameters:**
- `order`: Order object to update metrics for

##### `update_robot_metrics(robot_id: str, robot_data: Dict[str, Any])`
Update metrics for robot performance.

**Parameters:**
- `robot_id`: ID of the robot
- `robot_data`: Dictionary with robot performance data

##### `get_real_time_metrics() -> Dict[str, Any]`
Get real-time performance metrics.

**Returns:**
- Dictionary with current metrics

##### `get_analytics_summary() -> Dict[str, Any]`
Get comprehensive analytics summary.

**Returns:**
- Dictionary with analytics summary

##### `export_metrics_to_csv(filename: str) -> bool`
Export metrics to CSV file.

**Parameters:**
- `filename`: Output filename

**Returns:**
- `True` if export successful, `False` otherwise

##### `export_metrics_to_json(filename: str) -> bool`
Export metrics to JSON file.

**Parameters:**
- `filename`: Output filename

**Returns:**
- `True` if export successful, `False` otherwise

#### Properties
- `auto_export_interval`: Interval for automatic exports (seconds)
- `export_directory`: Directory for export files
- `total_orders_analyzed`: Total orders analyzed
- `average_completion_time`: Average order completion time

---

## AnalyticsDashboard

**Purpose:** Provides simple real-time dashboard for analytics display.

### Class: `AnalyticsDashboard`

#### Constructor
```python
def __init__(self, analytics: OrderAnalytics)
```
**Parameters:**
- `analytics`: OrderAnalytics instance

#### Methods

##### `display_dashboard() -> Dict[str, Any]`
Display current dashboard data.

**Returns:**
- Dictionary with dashboard information

##### `get_dashboard_summary() -> Dict[str, Any]`
Get dashboard summary information.

**Returns:**
- Dictionary with dashboard summary

##### `auto_refresh() -> bool`
Check if dashboard should auto-refresh.

**Returns:**
- `True` if refresh needed, `False` otherwise

#### Properties
- `last_refresh_time`: Timestamp of last refresh
- `refresh_interval`: Interval between refreshes (seconds)

---

## ConfigurationManager

**Purpose:** Manages system-wide configuration with validation.

### Class: `ConfigurationManager`

#### Constructor
```python
def __init__(self, config_file: str = "config/order_management.json")
```
**Parameters:**
- `config_file`: Path to configuration file

#### Methods

##### `load_config() -> bool`
Load configuration from file.

**Returns:**
- `True` if load successful, `False` otherwise

##### `save_config() -> bool`
Save current configuration to file.

**Returns:**
- `True` if save successful, `False` otherwise

##### `get_order_generation_config() -> OrderGenerationConfig`
Get order generation configuration.

**Returns:**
- `OrderGenerationConfig` object

##### `get_robot_config() -> RobotConfig`
Get robot configuration.

**Returns:**
- `RobotConfig` object

##### `get_analytics_config() -> AnalyticsConfig`
Get analytics configuration.

**Returns:**
- `AnalyticsConfig` object

##### `validate_config() -> bool`
Validate current configuration.

**Returns:**
- `True` if configuration is valid, `False` otherwise

#### Properties
- `config_file`: Path to configuration file
- `config_data`: Current configuration data
- `is_loaded`: Whether configuration is loaded

---

## OrderManagementIntegration

**Purpose:** Integrates all order management components with simulation system.

### Class: `OrderManagementIntegration`

#### Constructor
```python
def __init__(self, simulation_engine: SimulationEngine, event_system: EventSystem, config_manager: ConfigurationManager)
```
**Parameters:**
- `simulation_engine`: Main simulation engine
- `event_system`: Event system for communication
- `config_manager`: Configuration manager

#### Methods

##### `integrate_with_simulation() -> bool`
Integrate order management with simulation engine.

**Returns:**
- `True` if integration successful, `False` otherwise

##### `update_integration(delta_time: float)`
Update integration components.

**Parameters:**
- `delta_time`: Time delta for update

##### `get_integration_status() -> Dict[str, Any]`
Get integration status and metrics.

**Returns:**
- Dictionary with integration status

##### `shutdown_integration()`
Shutdown integration components.

##### `get_dashboard_data() -> Dict[str, Any]`
Get dashboard data for integration monitoring.

**Returns:**
- Dictionary with dashboard data

#### Properties
- `is_integrated`: Whether integration is active
- `integration_metrics`: Integration performance metrics
- `last_update_time`: Timestamp of last update

---

## Data Structures

### OrderStatus Enum
```python
class OrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

### OrderCompletionMetrics
```python
@dataclass
class OrderCompletionMetrics:
    completion_time: float = 0.0
    total_distance: float = 0.0
    efficiency_score: float = 0.0
    items_collected: int = 0
    total_items: int = 0
    direction_changes: int = 0
    path_optimization_savings: float = 0.0
```

### Configuration Classes
```python
@dataclass
class OrderGenerationConfig:
    generation_interval: float = 30.0
    min_items_per_order: int = 1
    max_items_per_order: int = 4
    auto_start: bool = True

@dataclass
class RobotConfig:
    robot_id: str = "ROBOT_001"

@dataclass
class AnalyticsConfig:
    auto_export_interval: float = 300.0
    export_directory: str = "exports"
```

---

## Usage Examples

### Basic Order Management Setup
```python
# Initialize components
warehouse_layout = WarehouseLayoutManager()
order_generator = OrderGenerator(warehouse_layout)
queue_manager = OrderQueueManager()
robot_assigner = RobotOrderAssigner()
status_tracker = OrderStatusTracker(robot_assigner, queue_manager)
analytics = OrderAnalytics(status_tracker, robot_assigner, queue_manager)

# Start order generation
order_generator.start_generation()

# Process orders
current_time = time.time()
order = order_generator.update(current_time)
if order:
    queue_manager.add_order(order)
```

### Integration with Simulation
```python
# Initialize integration
integration = OrderManagementIntegration(simulation_engine, event_system, config_manager)

# Integrate with simulation
success = await integration.integrate_with_simulation()

# Update integration
integration.update_integration(0.1)
```

### Analytics and Monitoring
```python
# Get real-time metrics
metrics = analytics.get_real_time_metrics()

# Export analytics
analytics.export_metrics_to_csv("order_metrics.csv")

# Display dashboard
dashboard = AnalyticsDashboard(analytics)
dashboard_data = dashboard.display_dashboard()
```

---

## Error Handling

All components include comprehensive error handling:

- **Configuration Errors:** Invalid parameters, missing files, validation failures
- **Integration Errors:** Connection failures, event system errors, component initialization failures
- **Runtime Errors:** Order processing failures, robot assignment errors, status update failures
- **Performance Errors:** Queue overflow, timeout errors, resource exhaustion

Error handling follows these principles:
- Graceful degradation when possible
- Detailed error messages for debugging
- Automatic retry mechanisms where appropriate
- Logging of all errors for analysis

---

## Performance Considerations

- **Order Generation:** Configurable intervals to balance system load
- **Queue Management:** FIFO implementation with O(1) operations
- **Robot Assignment:** Single robot design for simplicity and performance
- **Status Tracking:** Real-time updates with minimal overhead
- **Analytics:** Efficient metrics calculation with optional export
- **Integration:** Event-driven architecture for loose coupling

---

## Testing

All components include comprehensive test suites:

- **Unit Tests:** Individual component functionality
- **Integration Tests:** Component interaction and workflow
- **Performance Tests:** Load testing and optimization
- **Error Tests:** Error handling and recovery scenarios

Test coverage includes:
- Normal operation scenarios
- Edge cases and error conditions
- Performance under load
- Integration with simulation system 