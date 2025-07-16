# Inventory System Usage Examples

## Overview

This document provides comprehensive usage examples for the inventory system, demonstrating common workflows, integration patterns, and best practices.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Item Management](#item-management)
3. [Order Processing](#order-processing)
4. [Performance Monitoring](#performance-monitoring)
5. [Integration Examples](#integration-examples)
6. [Advanced Workflows](#advanced-workflows)
7. [Best Practices](#best-practices)

---

## Basic Setup

### 1. Initialize Inventory System

```python
from core.inventory.inventory_integration import InventorySystemIntegration
from core.inventory.inventory_config import InventoryConfigManager

# Create configuration manager
config_manager = InventoryConfigManager("config/simulation.json")

# Load configuration
success = config_manager.load_configuration()
if not success:
    print("Failed to load configuration")
    exit(1)

# Create integration
integration = InventorySystemIntegration(config_manager)

# Initialize system
success = integration.initialize_inventory_system()
if not success:
    print("Failed to initialize inventory system")
    exit(1)

print("✅ Inventory system initialized successfully")
```

### 2. Generate and Load Items

```python
from core.inventory.item_generator import ItemGenerator
from core.inventory.inventory_manager import InventoryManager

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

# Initialize inventory manager
inventory_manager = InventoryManager()

# Load items into inventory
success = inventory_manager.initialize_inventory(items)
if success:
    print("✅ Items loaded into inventory")
else:
    print("❌ Failed to load items")
```

### 3. Setup Event System Integration

```python
from core.events import EventSystem

# Create event system
event_system = EventSystem()

# Register inventory event handlers
def handle_inventory_update(event_data):
    item_id = event_data.get("item_id")
    quantity = event_data.get("quantity")
    print(f"📦 Item {item_id} updated to quantity {quantity}")

def handle_order_completed(event_data):
    order_id = event_data.get("order_id")
    print(f"✅ Order {order_id} completed")

def handle_order_cancelled(event_data):
    order_id = event_data.get("order_id")
    print(f"❌ Order {order_id} cancelled")

# Register handlers
event_system.register_handler("inventory_update", handle_inventory_update)
event_system.register_handler("order_completed", handle_order_completed)
event_system.register_handler("order_cancelled", handle_order_cancelled)

# Integrate with inventory system
integration.integrate_with_event_system(event_system)
print("✅ Event system integrated")
```

---

## Item Management

### 1. Create Individual Items

```python
from core.inventory.inventory_item import InventoryItem, Coordinate
import time

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
    print(f"✅ Item {item.item_id} is valid")
    
    # Add to inventory
    inventory_manager.update_item_quantity(item.item_id, item.quantity)
else:
    print(f"❌ Item {item.item_id} is invalid")
```

### 2. Batch Item Operations

```python
# Create multiple items
items_to_add = [
    InventoryItem("ITEM_B1", Coordinate(10, 5), 50.0, "clothing"),
    InventoryItem("ITEM_B2", Coordinate(15, 8), 75.0, "electronics"),
    InventoryItem("ITEM_B3", Coordinate(20, 12), 25.0, "books")
]

# Add items to inventory
for item in items_to_add:
    if item.validate():
        inventory_manager.update_item_quantity(item.item_id, item.quantity)
        print(f"✅ Added {item.item_id}")

# Get inventory statistics
stats = inventory_manager.get_inventory_statistics()
print(f"📊 Inventory Statistics:")
print(f"  Total items: {stats['total_items']}")
print(f"  Categories: {stats['categories']}")
print(f"  Total quantity: {stats['total_quantity']}")
```

### 3. Item Search and Filtering

```python
# Get item by ID
item = inventory_manager.get_item("ITEM_A1")
if item:
    print(f"Found item: {item.item_id} at {item.location}")
    print(f"Quantity: {item.quantity}, Category: {item.category}")

# Get items by category
electronics_items = []
for item_id in inventory_manager.get_all_item_ids():
    item = inventory_manager.get_item(item_id)
    if item and item.category == "electronics":
        electronics_items.append(item)

print(f"Found {len(electronics_items)} electronics items")

# Get items by location range
items_in_area = []
for item_id in inventory_manager.get_all_item_ids():
    item = inventory_manager.get_item(item_id)
    if item and 0 <= item.location.x <= 10 and 0 <= item.location.y <= 10:
        items_in_area.append(item)

print(f"Found {len(items_in_area)} items in area (0,0) to (10,10)")
```

### 4. Update Item Quantities

```python
# Update single item quantity
success = inventory_manager.update_item_quantity("ITEM_A1", 95.0)
if success:
    print("✅ Updated ITEM_A1 quantity to 95.0")

# Batch update quantities
updates = [
    ("ITEM_A1", 90.0),
    ("ITEM_B1", 45.0),
    ("ITEM_B2", 70.0)
]

for item_id, new_quantity in updates:
    success = inventory_manager.update_item_quantity(item_id, new_quantity)
    if success:
        print(f"✅ Updated {item_id} to {new_quantity}")
    else:
        print(f"❌ Failed to update {item_id}")

# Check for low stock
low_stock_items = []
for item_id in inventory_manager.get_all_item_ids():
    item = inventory_manager.get_item(item_id)
    if item and item.quantity < 10:
        low_stock_items.append(item)

if low_stock_items:
    print(f"⚠️  Low stock items:")
    for item in low_stock_items:
        print(f"  - {item.item_id}: {item.quantity}")
```

---

## Order Processing

### 1. Basic Order Processing

```python
from core.inventory.inventory_sync import InventorySyncManager

# Create sync manager
sync_manager = InventorySyncManager(inventory_manager)

# Process an order
order_id = "ORDER_001"
order_items = ["ITEM_A1", "ITEM_B1", "ITEM_B2"]

success = sync_manager.process_order(order_id, order_items)
if success:
    print(f"✅ Order {order_id} processed successfully")
    
    # Complete the order
    sync_manager.handle_order_completion(order_id)
    print(f"✅ Order {order_id} completed")
else:
    print(f"❌ Failed to process order {order_id}")
```

### 2. Order Tracking

```python
# Track order status
order_status = sync_manager.get_order_status("ORDER_001")
print(f"Order status: {order_status}")

# Get order details
order_details = sync_manager.get_order_details("ORDER_001")
if order_details:
    print(f"Order items: {order_details['items']}")
    print(f"Order status: {order_details['status']}")
    print(f"Created at: {order_details['created_at']}")

# Get all active orders
active_orders = sync_manager.get_active_orders()
print(f"Active orders: {len(active_orders)}")
for order_id, status in active_orders.items():
    print(f"  - {order_id}: {status}")
```

### 3. Order Cancellation

```python
# Cancel an order
order_id = "ORDER_002"
success = sync_manager.handle_order_cancellation(order_id)
if success:
    print(f"✅ Order {order_id} cancelled")
else:
    print(f"❌ Failed to cancel order {order_id}")

# Check cancellation impact
cancelled_orders = sync_manager.get_cancelled_orders()
print(f"Cancelled orders: {len(cancelled_orders)}")
```

### 4. Order Statistics

```python
# Get sync statistics
stats = sync_manager.get_sync_statistics()
print(f"📊 Order Processing Statistics:")
print(f"  Total orders: {stats['total_orders']}")
print(f"  Completed orders: {stats['completed_orders']}")
print(f"  Cancelled orders: {stats['cancelled_orders']}")
print(f"  Completion rate: {stats['completion_rate']:.2%}")
print(f"  Average completion time: {stats['average_completion_time']:.2f}s")
```

---

## Performance Monitoring

### 1. Basic Performance Monitoring

```python
# Enable performance monitoring
config_manager.config.performance_monitoring_enabled = True
config_manager.config.debug_mode = True

# Record performance metrics
import time

def monitored_operation():
    start_time = time.time()
    
    # Perform operation
    result = inventory_manager.update_item_quantity("ITEM_A1", 95.0)
    
    # Record performance
    operation_time = (time.time() - start_time) * 1000  # Convert to ms
    config_manager.record_performance_metric(
        PerformanceMetricType.OPERATION_TIME, operation_time,
        {"operation": "item_update", "item_id": "ITEM_A1"}
    )
    
    return result

# Run monitored operation
success = monitored_operation()
print(f"Operation completed: {success}")
```

### 2. Performance Analytics

```python
# Get performance analytics
analytics = config_manager.get_performance_analytics(time_window_seconds=3600)

# Display performance summary
performance_summary = analytics.get("performance_summary", {})
for metric_type, stats in performance_summary.items():
    print(f"📊 {metric_type}:")
    print(f"  Count: {stats.get('count', 0)}")
    print(f"  Average: {stats.get('average', 0):.2f}")
    print(f"  Min: {stats.get('min', 0):.2f}")
    print(f"  Max: {stats.get('max', 0):.2f}")

# Check for violations
violations = config_manager.check_performance_thresholds()
if any(violations.values()):
    print("⚠️  Performance violations detected:")
    for violation_type, violations_list in violations.items():
        if violations_list:
            print(f"  - {violation_type}: {len(violations_list)} violations")
else:
    print("✅ No performance violations")
```

### 3. Memory Usage Monitoring

```python
import psutil

def monitor_memory_usage():
    """Monitor memory usage of the inventory system"""
    
    # Get current memory usage
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    # Record memory metric
    config_manager.record_performance_metric(
        PerformanceMetricType.MEMORY_USAGE, memory_mb,
        {"component": "inventory_system"}
    )
    
    # Check against threshold
    if memory_mb > config_manager.config.max_memory_usage_mb:
        print(f"⚠️  High memory usage: {memory_mb:.1f}MB")
    else:
        print(f"✅ Memory usage: {memory_mb:.1f}MB")
    
    return memory_mb

# Monitor memory periodically
for i in range(5):
    memory_usage = monitor_memory_usage()
    time.sleep(1)
```

---

## Integration Examples

### 1. Simulation Engine Integration

```python
from core.engine import SimulationEngine

# Create simulation engine
simulation_engine = SimulationEngine()

# Integrate with inventory system
success = integration.integrate_with_simulation_engine(simulation_engine)
if success:
    print("✅ Simulation engine integrated")
    
    # Start simulation
    simulation_engine.start()
    print("🚀 Simulation started")
else:
    print("❌ Failed to integrate simulation engine")
```

### 2. Warehouse Layout Integration

```python
from core.layout import WarehouseLayout

# Create warehouse layout
warehouse_layout = WarehouseLayout(
    width=26,
    height=20,
    packout_zone_x=1,
    packout_zone_y=1,
    packout_zone_width=1,
    packout_zone_height=1
)

# Integrate with inventory system
success = integration.integrate_with_warehouse_layout(warehouse_layout)
if success:
    print("✅ Warehouse layout integrated")
    
    # Get layout information
    layout_info = warehouse_layout.get_layout_info()
    print(f"Warehouse size: {layout_info['width']}x{layout_info['height']}")
    print(f"Packout zone: {layout_info['packout_zone']}")
else:
    print("❌ Failed to integrate warehouse layout")
```

### 3. Order Management Integration

```python
from core.order_management import OrderManagement

# Create order management system
order_management = OrderManagement()

# Integrate with inventory system
success = integration.integrate_with_order_management(order_management)
if success:
    print("✅ Order management integrated")
    
    # Create an order
    order_id = order_management.create_order(["ITEM_A1", "ITEM_B1"])
    print(f"Created order: {order_id}")
else:
    print("❌ Failed to integrate order management")
```

### 4. Complete System Integration

```python
def setup_complete_system():
    """Setup complete inventory system with all integrations"""
    
    print("🔧 Setting up complete inventory system...")
    
    # Initialize components
    config_manager = InventoryConfigManager()
    integration = InventorySystemIntegration(config_manager)
    
    # Load configuration
    config_manager.load_configuration()
    
    # Create and integrate components
    components = {
        "simulation_engine": SimulationEngine(),
        "event_system": EventSystem(),
        "warehouse_layout": WarehouseLayout(26, 20),
        "order_management": OrderManagement()
    }
    
    # Integrate each component
    for name, component in components.items():
        integration_method = getattr(integration, f"integrate_with_{name.lower().replace(' ', '_')}")
        success = integration_method(component)
        
        if success:
            print(f"✅ {name} integrated")
        else:
            print(f"❌ Failed to integrate {name}")
    
    # Initialize complete system
    success = integration.initialize_inventory_system()
    if success:
        print("✅ Complete system initialized")
        return integration
    else:
        print("❌ Failed to initialize complete system")
        return None

# Setup complete system
complete_system = setup_complete_system()
```

---

## Advanced Workflows

### 1. Automated Inventory Management

```python
class AutomatedInventoryManager:
    """Automated inventory management with monitoring and alerts"""
    
    def __init__(self, inventory_manager, config_manager):
        self.inventory_manager = inventory_manager
        self.config_manager = config_manager
        self.low_stock_threshold = 10
        self.high_stock_threshold = 200
    
    def check_stock_levels(self):
        """Check stock levels and generate alerts"""
        alerts = []
        
        for item_id in self.inventory_manager.get_all_item_ids():
            item = self.inventory_manager.get_item(item_id)
            if item:
                if item.quantity <= self.low_stock_threshold:
                    alerts.append(f"LOW_STOCK: {item_id} ({item.quantity})")
                elif item.quantity >= self.high_stock_threshold:
                    alerts.append(f"HIGH_STOCK: {item_id} ({item.quantity})")
        
        return alerts
    
    def auto_restock(self, item_id, target_quantity=100):
        """Automatically restock an item"""
        item = self.inventory_manager.get_item(item_id)
        if item and item.quantity < self.low_stock_threshold:
            new_quantity = item.quantity + (target_quantity - item.quantity)
            success = self.inventory_manager.update_item_quantity(item_id, new_quantity)
            if success:
                print(f"✅ Auto-restocked {item_id} to {new_quantity}")
                return True
        
        return False
    
    def generate_report(self):
        """Generate inventory report"""
        stats = self.inventory_manager.get_inventory_statistics()
        alerts = self.check_stock_levels()
        
        report = {
            "timestamp": time.time(),
            "total_items": stats["total_items"],
            "total_quantity": stats["total_quantity"],
            "categories": stats["categories"],
            "alerts": alerts,
            "low_stock_count": len([a for a in alerts if "LOW_STOCK" in a]),
            "high_stock_count": len([a for a in alerts if "HIGH_STOCK" in a])
        }
        
        return report

# Use automated inventory manager
auto_manager = AutomatedInventoryManager(inventory_manager, config_manager)

# Check stock levels
alerts = auto_manager.check_stock_levels()
if alerts:
    print("⚠️  Stock alerts:")
    for alert in alerts:
        print(f"  - {alert}")

# Generate report
report = auto_manager.generate_report()
print(f"📊 Inventory Report:")
print(f"  Total items: {report['total_items']}")
print(f"  Total quantity: {report['total_quantity']}")
print(f"  Categories: {report['categories']}")
print(f"  Alerts: {len(report['alerts'])}")
```

### 2. Real-time Monitoring Dashboard

```python
class InventoryDashboard:
    """Real-time inventory monitoring dashboard"""
    
    def __init__(self, integration, config_manager):
        self.integration = integration
        self.config_manager = config_manager
        self.monitoring_active = False
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        print("📊 Starting real-time monitoring...")
        
        while self.monitoring_active:
            self.update_dashboard()
            time.sleep(5)  # Update every 5 seconds
    
    def update_dashboard(self):
        """Update dashboard with current data"""
        # Get system status
        status = self.integration.get_integration_status()
        
        # Get performance metrics
        analytics = self.config_manager.get_performance_analytics(time_window_seconds=300)
        
        # Get inventory statistics
        inventory_stats = self.integration.inventory_manager.get_inventory_statistics()
        
        # Display dashboard
        print("\n" + "="*50)
        print("📊 INVENTORY DASHBOARD")
        print("="*50)
        
        # System status
        print(f"System Status: {'✅ HEALTHY' if status['initialized'] else '❌ UNHEALTHY'}")
        print(f"Components Integrated: {sum(status['components'].values())}/{len(status['components'])}")
        
        # Performance metrics
        performance_summary = analytics.get("performance_summary", {})
        if "operation_time" in performance_summary:
            op_time = performance_summary["operation_time"]
            print(f"Avg Operation Time: {op_time.get('average', 0):.2f}ms")
        
        # Inventory statistics
        print(f"Total Items: {inventory_stats.get('total_items', 0)}")
        print(f"Total Quantity: {inventory_stats.get('total_quantity', 0)}")
        print(f"Categories: {inventory_stats.get('categories', 0)}")
        
        print("="*50)
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        print("📊 Monitoring stopped")

# Create and start dashboard
dashboard = InventoryDashboard(integration, config_manager)

# Start monitoring (in a separate thread for real-time updates)
import threading
monitoring_thread = threading.Thread(target=dashboard.start_monitoring)
monitoring_thread.daemon = True
monitoring_thread.start()

# Let it run for a while
time.sleep(30)

# Stop monitoring
dashboard.stop_monitoring()
```

### 3. Batch Operations

```python
class BatchInventoryOperations:
    """Batch operations for inventory management"""
    
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
    
    def batch_update_quantities(self, updates):
        """Update multiple item quantities in batch"""
        results = []
        
        for item_id, new_quantity in updates:
            success = self.inventory_manager.update_item_quantity(item_id, new_quantity)
            results.append({
                "item_id": item_id,
                "success": success,
                "new_quantity": new_quantity
            })
        
        return results
    
    def batch_create_items(self, items_data):
        """Create multiple items in batch"""
        results = []
        
        for item_data in items_data:
            item = InventoryItem(**item_data)
            if item.validate():
                success = self.inventory_manager.update_item_quantity(item.item_id, item.quantity)
                results.append({
                    "item_id": item.item_id,
                    "success": success,
                    "valid": True
                })
            else:
                results.append({
                    "item_id": item_data.get("item_id", "unknown"),
                    "success": False,
                    "valid": False
                })
        
        return results
    
    def batch_process_orders(self, orders):
        """Process multiple orders in batch"""
        results = []
        
        for order_id, items in orders.items():
            success = self.inventory_manager.sync_manager.process_order(order_id, items)
            results.append({
                "order_id": order_id,
                "success": success,
                "items": items
            })
        
        return results

# Use batch operations
batch_ops = BatchInventoryOperations(inventory_manager)

# Batch quantity updates
updates = [
    ("ITEM_A1", 90.0),
    ("ITEM_B1", 45.0),
    ("ITEM_B2", 70.0),
    ("ITEM_C1", 25.0)
]

results = batch_ops.batch_update_quantities(updates)
print("📦 Batch Update Results:")
for result in results:
    status = "✅" if result["success"] else "❌"
    print(f"  {status} {result['item_id']}: {result['new_quantity']}")

# Batch order processing
orders = {
    "ORDER_001": ["ITEM_A1", "ITEM_B1"],
    "ORDER_002": ["ITEM_B2", "ITEM_C1"],
    "ORDER_003": ["ITEM_A1", "ITEM_B2", "ITEM_C1"]
}

order_results = batch_ops.batch_process_orders(orders)
print("📋 Batch Order Results:")
for result in order_results:
    status = "✅" if result["success"] else "❌"
    print(f"  {status} {result['order_id']}: {len(result['items'])} items")
```

---

## Best Practices

### 1. Error Handling

```python
def safe_inventory_operation(operation, *args, **kwargs):
    """Safely execute inventory operations with error handling"""
    try:
        result = operation(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        return {"success": False, "error": str(e)}

# Use safe operations
result = safe_inventory_operation(
    inventory_manager.update_item_quantity, "ITEM_A1", 95.0
)

if result["success"]:
    print("✅ Operation completed successfully")
else:
    print(f"❌ Operation failed: {result['error']}")
```

### 2. Performance Optimization

```python
def optimized_batch_operations(items, batch_size=100):
    """Optimize batch operations for better performance"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        # Process batch
        batch_results = []
        for item in batch:
            result = inventory_manager.update_item_quantity(item["id"], item["quantity"])
            batch_results.append(result)
        
        results.extend(batch_results)
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.01)
    
    return results
```

### 3. Configuration Management

```python
def validate_and_load_config(config_file):
    """Validate and load configuration with error handling"""
    try:
        config_manager = InventoryConfigManager(config_file)
        
        # Load configuration
        success = config_manager.load_configuration()
        if not success:
            print("❌ Failed to load configuration")
            return None
        
        # Validate configuration
        validation = config_manager.validate_configuration()
        if not validation["valid"]:
            print("❌ Configuration validation failed:")
            for error in validation["errors"]:
                print(f"  - {error}")
            return None
        
        print("✅ Configuration loaded and validated")
        return config_manager
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return None

# Use validated configuration
config_manager = validate_and_load_config("config/simulation.json")
if config_manager:
    # Continue with system setup
    integration = InventorySystemIntegration(config_manager)
else:
    print("❌ Cannot proceed without valid configuration")
```

### 4. Logging and Monitoring

```python
import logging

def setup_inventory_logging():
    """Setup comprehensive logging for inventory system"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('inventory_system.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create logger
    logger = logging.getLogger('inventory_system')
    
    return logger

# Setup logging
logger = setup_inventory_logging()

# Use logging in operations
def logged_inventory_operation(operation_name, operation_func, *args, **kwargs):
    """Execute operation with logging"""
    logger.info(f"Starting operation: {operation_name}")
    
    try:
        result = operation_func(*args, **kwargs)
        logger.info(f"Operation {operation_name} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Operation {operation_name} failed: {e}")
        raise

# Use logged operations
logged_inventory_operation(
    "update_item_quantity",
    inventory_manager.update_item_quantity,
    "ITEM_A1", 95.0
)
```

### 5. Testing and Validation

```python
def test_inventory_system():
    """Comprehensive testing of inventory system"""
    
    print("🧪 Testing inventory system...")
    
    tests = [
        ("Item Creation", test_item_creation),
        ("Item Updates", test_item_updates),
        ("Order Processing", test_order_processing),
        ("Performance", test_performance),
        ("Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"  ❌ {test_name}: {e}")
    
    # Summary
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    return passed == total

def test_item_creation():
    """Test item creation functionality"""
    item = InventoryItem("TEST_001", Coordinate(1, 1), 100.0, "test")
    return item.validate()

def test_item_updates():
    """Test item update functionality"""
    success = inventory_manager.update_item_quantity("ITEM_A1", 95.0)
    item = inventory_manager.get_item("ITEM_A1")
    return success and item.quantity == 95.0

def test_order_processing():
    """Test order processing functionality"""
    success = sync_manager.process_order("TEST_ORDER", ["ITEM_A1"])
    return success

def test_performance():
    """Test performance monitoring"""
    config_manager.record_performance_metric(PerformanceMetricType.OPERATION_TIME, 5.0)
    analytics = config_manager.get_performance_analytics()
    return analytics.get("total_metrics", 0) > 0

def test_integration():
    """Test system integration"""
    status = integration.get_integration_status()
    return status.get("initialized", False)

# Run tests
if test_inventory_system():
    print("✅ All tests passed")
else:
    print("❌ Some tests failed")
```

---

## Conclusion

These examples demonstrate the comprehensive capabilities of the inventory system. Key points to remember:

1. **Always validate** configurations and data before use
2. **Handle errors gracefully** with proper exception handling
3. **Monitor performance** to ensure optimal operation
4. **Use batch operations** for efficiency when processing multiple items
5. **Implement logging** for debugging and monitoring
6. **Test thoroughly** before deploying to production

The inventory system provides a robust foundation for warehouse simulation with comprehensive features for item management, order processing, performance monitoring, and system integration. 