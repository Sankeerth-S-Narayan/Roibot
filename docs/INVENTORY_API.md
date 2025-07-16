# Inventory System API Documentation

## Overview

The Inventory System provides comprehensive inventory management capabilities for the warehouse simulation, including item generation, real-time tracking, order synchronization, and performance monitoring.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Item Management](#item-management)
3. [Configuration](#configuration)
4. [Integration](#integration)
5. [Performance Monitoring](#performance-monitoring)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## Core Classes

### InventoryItem

Represents an individual inventory item with location, quantity, and category information.

```python
@dataclass
class InventoryItem:
    item_id: str                    # Unique item identifier (e.g., "ITEM_A1")
    location: Coordinate            # Warehouse location (x, y coordinates)
    quantity: float                 # Current stock quantity
    category: str                   # Item category (electronics, clothing, etc.)
    created_at: float              # Creation timestamp
    last_updated: float            # Last update timestamp
```

**Properties:**
- `VALID_CATEGORIES`: Set of valid item categories
- `item_id`: Unique identifier following pattern ITEM_[Letter][Number]
- `location`: Coordinate object with x, y coordinates
- `quantity`: Current stock level (unlimited stock supported)
- `category`: Item category from predefined list

**Methods:**
- `to_dict()`: Convert item to dictionary for serialization
- `from_dict(data)`: Create item from dictionary
- `validate()`: Validate item properties
- `update_quantity(new_quantity)`: Update stock quantity

### ItemGenerator

Generates and places inventory items across the warehouse.

```python
class ItemGenerator:
    def __init__(self, warehouse_width, warehouse_height, total_items, ...)
    def generate_items() -> List[InventoryItem]
    def validate_placement(item, existing_items) -> bool
```

**Key Features:**
- Generates 500 unique items with proper ID sequencing
- Places items randomly but evenly across warehouse
- Excludes packout zone from placement
- Assigns categories based on distribution rules
- Validates placement constraints

### InventoryManager

Centralized inventory management with real-time updates and event integration.

```python
class InventoryManager:
    def __init__(self)
    def initialize_inventory(items: List[InventoryItem]) -> bool
    def get_item(item_id: str) -> Optional[InventoryItem]
    def update_item_quantity(item_id: str, quantity: float) -> bool
    def get_inventory_statistics() -> Dict
    def set_event_system(event_system)
```

**Key Features:**
- Thread-safe operations with atomic updates
- Real-time stock level tracking
- Event system integration for notifications
- Performance monitoring and metrics
- Comprehensive error handling

### InventorySyncManager

Synchronizes inventory with order management system.

```python
class InventorySyncManager:
    def __init__(self, inventory_manager: InventoryManager)
    def process_order(order_id: str, items: List[str]) -> bool
    def handle_order_completion(order_id: str) -> bool
    def handle_order_cancellation(order_id: str) -> bool
    def get_sync_statistics() -> Dict
```

**Key Features:**
- Order tracking and status management
- Item collection recording
- Inventory validation for orders
- Event-driven updates
- Completion rate monitoring

---

## Item Management

### Creating Items

```python
from core.inventory.inventory_item import InventoryItem, Coordinate

# Create a new inventory item
item = InventoryItem(
    item_id="ITEM_A1",
    location=Coordinate(5, 10),
    quantity=100.0,
    category="electronics",
    created_at=time.time(),
    last_updated=time.time()
)

# Validate the item
if item.validate():
    print(f"Item {item.item_id} is valid")
```

### Generating Multiple Items

```python
from core.inventory.item_generator import ItemGenerator

# Create item generator
generator = ItemGenerator(
    warehouse_width=26,
    warehouse_height=20,
    packout_zone_x=1,
    packout_zone_y=1,
    packout_zone_width=1,
    packout_zone_height=1,
    total_items=500,
    item_id_prefix="ITEM_",
    max_items_per_letter=20
)

# Generate items
items = generator.generate_items()
print(f"Generated {len(items)} items")
```

### Managing Inventory

```python
from core.inventory.inventory_manager import InventoryManager

# Initialize inventory manager
manager = InventoryManager()

# Initialize with items
success = manager.initialize_inventory(items)

# Get item
item = manager.get_item("ITEM_A1")
if item:
    print(f"Item quantity: {item.quantity}")

# Update quantity
success = manager.update_item_quantity("ITEM_A1", 95.0)

# Get statistics
stats = manager.get_inventory_statistics()
print(f"Total items: {stats['total_items']}")
```

---

## Configuration

### InventoryConfigManager

Manages configuration settings and performance monitoring.

```python
from core.inventory.inventory_config import InventoryConfigManager

# Create config manager
config_manager = InventoryConfigManager()

# Load configuration from file
success = config_manager.load_configuration()

# Validate configuration
validation = config_manager.validate_configuration()
if validation["valid"]:
    print("Configuration is valid")
else:
    print(f"Configuration errors: {validation['errors']}")

# Record performance metrics
config_manager.record_performance_metric(
    PerformanceMetricType.OPERATION_TIME, 5.0
)

# Get performance analytics
analytics = config_manager.get_performance_analytics()
```

### Configuration Settings

```python
# Warehouse dimensions
warehouse_width: int = 26
warehouse_height: int = 20

# Packout zone
packout_zone_x: int = 1
packout_zone_y: int = 1
packout_zone_width: int = 1
packout_zone_height: int = 1

# Item generation
total_items: int = 500
item_id_prefix: str = "ITEM_"
max_items_per_letter: int = 20

# Performance settings
max_operation_time_ms: float = 10.0
max_memory_usage_mb: float = 100.0
performance_monitoring_enabled: bool = True
debug_mode: bool = False
```

---

## Integration

### InventorySystemIntegration

Integrates inventory system with existing simulation components.

```python
from core.inventory.inventory_integration import InventorySystemIntegration

# Create integration
integration = InventorySystemIntegration()

# Integrate with simulation engine
success = integration.integrate_with_simulation_engine(simulation_engine)

# Integrate with event system
success = integration.integrate_with_event_system(event_system)

# Integrate with warehouse layout
success = integration.integrate_with_warehouse_layout(warehouse_layout)

# Integrate with order management
success = integration.integrate_with_order_management(order_management)

# Initialize complete system
success = integration.initialize_inventory_system()

# Get integration status
status = integration.get_integration_status()
```

### Event Handling

```python
# Register event handlers
event_system.register_handler('inventory_update', handle_inventory_event)
event_system.register_handler('order_completed', handle_order_completed)
event_system.register_handler('order_cancelled', handle_order_cancelled)

# Handle inventory events
def handle_inventory_event(event_data):
    item_id = event_data.get("item_id")
    quantity = event_data.get("quantity")
    print(f"Item {item_id} updated to quantity {quantity}")

# Handle order events
def handle_order_completed(event_data):
    order_id = event_data.get("order_id")
    print(f"Order {order_id} completed")
```

---

## Performance Monitoring

### Performance Metrics

```python
from core.inventory.inventory_config import PerformanceMetricType

# Available metric types
PerformanceMetricType.OPERATION_TIME    # Operation execution time
PerformanceMetricType.MEMORY_USAGE      # Memory consumption
PerformanceMetricType.THROUGHPUT        # Operations per second
PerformanceMetricType.ERROR_RATE        # Error frequency
PerformanceMetricType.RESPONSE_TIME     # Response latency
```

### Recording Metrics

```python
# Record operation time
config_manager.record_performance_metric(
    PerformanceMetricType.OPERATION_TIME, 5.0,
    {"operation": "item_update", "item_id": "ITEM_A1"}
)

# Record memory usage
config_manager.record_performance_metric(
    PerformanceMetricType.MEMORY_USAGE, 50.0,
    {"component": "inventory_manager"}
)
```

### Performance Analytics

```python
# Get comprehensive analytics
analytics = config_manager.get_performance_analytics(time_window_seconds=3600)

# Access specific metrics
op_time_stats = analytics["performance_summary"]["operation_time"]
print(f"Average operation time: {op_time_stats['average']}ms")
print(f"Max operation time: {op_time_stats['max']}ms")

# Check performance thresholds
violations = config_manager.check_performance_thresholds()
if violations["operation_time_violations"]:
    print("Performance threshold violations detected")
```

---

## Error Handling

### Validation Errors

```python
# Validate item
try:
    item.validate()
except ValidationError as e:
    print(f"Validation error: {e}")

# Validate configuration
validation = config_manager.validate_configuration()
if not validation["valid"]:
    for error in validation["errors"]:
        print(f"Configuration error: {error}")
```

### Integration Errors

```python
# Handle integration failures
try:
    success = integration.integrate_with_simulation_engine(simulation_engine)
    if not success:
        print("Integration failed - check component availability")
except Exception as e:
    print(f"Integration error: {e}")
```

### Recovery Strategies

```python
# Automatic retry for failed operations
def retry_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)  # Wait before retry

# Graceful degradation
def safe_get_item(manager, item_id):
    try:
        return manager.get_item(item_id)
    except Exception as e:
        print(f"Error getting item {item_id}: {e}")
        return None
```

---

## Examples

### Complete Inventory Workflow

```python
from core.inventory.inventory_manager import InventoryManager
from core.inventory.inventory_sync import InventorySyncManager
from core.inventory.inventory_config import InventoryConfigManager

# Initialize components
config_manager = InventoryConfigManager()
inventory_manager = InventoryManager()
sync_manager = InventorySyncManager(inventory_manager)

# Load configuration
config_manager.load_configuration()

# Initialize inventory
items = generate_items()  # Your item generation logic
inventory_manager.initialize_inventory(items)

# Process an order
order_id = "ORDER_001"
order_items = ["ITEM_A1", "ITEM_B2", "ITEM_C3"]

# Process order
success = sync_manager.process_order(order_id, order_items)
if success:
    print(f"Order {order_id} processed successfully")
    
    # Complete order
    sync_manager.handle_order_completion(order_id)
    print(f"Order {order_id} completed")

# Get statistics
stats = sync_manager.get_sync_statistics()
print(f"Completion rate: {stats['completion_rate']:.2%}")
```

### Performance Monitoring Setup

```python
# Enable performance monitoring
config_manager.config.performance_monitoring_enabled = True

# Set performance thresholds
config_manager.config.max_operation_time_ms = 10.0
config_manager.config.max_memory_usage_mb = 100.0

# Monitor operations
def monitored_operation():
    start_time = time.time()
    
    # Perform operation
    result = inventory_manager.update_item_quantity("ITEM_A1", 95.0)
    
    # Record performance
    operation_time = (time.time() - start_time) * 1000  # Convert to ms
    config_manager.record_performance_metric(
        PerformanceMetricType.OPERATION_TIME, operation_time
    )
    
    return result
```

### Debug Information

```python
# Get comprehensive debug information
debug_info = integration.get_debug_info()

# Print system status
status = debug_info["integration_status"]
print(f"System initialized: {status['initialized']}")
print(f"Components integrated: {sum(status['components'].values())}")

# Print configuration
config = debug_info["configuration"]
print(f"Warehouse dimensions: {config['warehouse_dimensions']}")
print(f"Total items: {config['item_generation']['total_items']}")

# Print performance metrics
metrics = debug_info["config_manager"]["performance_metrics"]
print(f"Total metrics recorded: {metrics['total_metrics']}")
```

---

## Best Practices

### 1. Error Handling
- Always validate items before operations
- Use try-catch blocks for integration operations
- Implement graceful degradation for failures

### 2. Performance
- Monitor operation times and memory usage
- Set appropriate performance thresholds
- Use background threads for long-running operations

### 3. Thread Safety
- Use thread-safe operations for concurrent access
- Implement proper locking mechanisms
- Avoid blocking operations in event handlers

### 4. Configuration
- Validate configuration on startup
- Use environment-specific settings
- Implement configuration hot-reloading

### 5. Testing
- Test all integration scenarios
- Validate error handling paths
- Monitor performance under load

---

## Troubleshooting

### Common Issues

1. **Item Placement Failures**
   - Check warehouse dimensions
   - Verify packout zone configuration
   - Ensure sufficient space for items

2. **Integration Failures**
   - Verify component availability
   - Check event system connectivity
   - Validate callback registration

3. **Performance Issues**
   - Monitor operation times
   - Check memory usage
   - Review thread safety

4. **Configuration Errors**
   - Validate configuration file format
   - Check parameter ranges
   - Verify file permissions

### Debug Commands

```python
# Get system status
status = integration.get_integration_status()

# Get debug information
debug_info = integration.get_debug_info()

# Check performance
analytics = config_manager.get_performance_analytics()

# Validate configuration
validation = config_manager.validate_configuration()
```

---

## API Reference

### Complete Method Signatures

```python
# InventoryItem
InventoryItem(item_id: str, location: Coordinate, quantity: float, category: str, created_at: float = 0.0, last_updated: float = 0.0)
to_dict() -> Dict
from_dict(data: Dict) -> InventoryItem
validate() -> bool
update_quantity(new_quantity: float) -> bool

# ItemGenerator
ItemGenerator(warehouse_width: int, warehouse_height: int, packout_zone_x: int, packout_zone_y: int, packout_zone_width: int, packout_zone_height: int, total_items: int, item_id_prefix: str, max_items_per_letter: int)
generate_items() -> List[InventoryItem]
validate_placement(item: InventoryItem, existing_items: List[InventoryItem]) -> bool

# InventoryManager
InventoryManager()
initialize_inventory(items: List[InventoryItem]) -> bool
get_item(item_id: str) -> Optional[InventoryItem]
update_item_quantity(item_id: str, quantity: float) -> bool
get_inventory_statistics() -> Dict
set_event_system(event_system)
shutdown()

# InventorySyncManager
InventorySyncManager(inventory_manager: InventoryManager)
process_order(order_id: str, items: List[str]) -> bool
handle_order_completion(order_id: str) -> bool
handle_order_cancellation(order_id: str) -> bool
get_sync_statistics() -> Dict
set_event_system(event_system)
set_order_tracker(order_tracker)
shutdown()

# InventoryConfigManager
InventoryConfigManager(config_file: str = "config/simulation.json")
load_configuration() -> bool
save_configuration() -> bool
validate_configuration() -> Dict
record_performance_metric(metric_type: PerformanceMetricType, value: float, metadata: Dict = None)
get_performance_analytics(time_window_seconds: float = 3600) -> Dict
check_performance_thresholds() -> Dict
get_debug_info(inventory_manager = None, sync_manager = None) -> Dict
export_configuration() -> Dict
import_configuration(config_data: Dict) -> bool

# InventorySystemIntegration
InventorySystemIntegration(config_manager: InventoryConfigManager = None)
integrate_with_simulation_engine(simulation_engine) -> bool
integrate_with_event_system(event_system) -> bool
integrate_with_warehouse_layout(warehouse_layout) -> bool
integrate_with_order_management(order_management) -> bool
integrate_with_configuration_manager(config_manager) -> bool
initialize_inventory_system() -> bool
get_integration_status() -> Dict
get_debug_info() -> Dict
shutdown()
```

This documentation provides comprehensive coverage of the inventory system API, including usage examples, best practices, and troubleshooting guidance. 