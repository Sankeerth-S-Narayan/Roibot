# Inventory System Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting procedures for the inventory system, including common issues, diagnostic tools, and step-by-step solutions.

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Issues](#common-issues)
3. [Diagnostic Tools](#diagnostic-tools)
4. [Performance Issues](#performance-issues)
5. [Integration Problems](#integration-problems)
6. [Configuration Errors](#configuration-errors)
7. [Debug Procedures](#debug-procedures)
8. [Emergency Procedures](#emergency-procedures)

---

## Quick Diagnosis

### System Health Check

```python
from utils.inventory_debug_tools import quick_diagnosis
from core.inventory.inventory_integration import InventorySystemIntegration

# Perform quick diagnosis
integration = InventorySystemIntegration()
result = quick_diagnosis(integration)

print(f"System Health: {result['overall_health']}")
print(f"Health Score: {result['health_score']:.2f}")
```

### Health Status Levels

- **HEALTHY** (0.8-1.0): System operating normally
- **DEGRADED** (0.5-0.79): Some issues detected, but functional
- **UNHEALTHY** (0.0-0.49): Critical issues requiring immediate attention

---

## Common Issues

### 1. Initialization Failures

**Symptoms:**
- System not starting
- Configuration errors
- Missing components

**Diagnosis:**
```python
from utils.inventory_debug_tools import InventoryTroubleshooter

troubleshooter = InventoryTroubleshooter()
context = {"config_manager": config_manager}
result = troubleshooter.troubleshoot_issue("initialization_failure", context)
```

**Solutions:**
1. **Check Configuration File**
   ```python
   # Validate configuration
   validation = config_manager.validate_configuration()
   if not validation["valid"]:
       for error in validation["errors"]:
           print(f"Fix: {error}")
   ```

2. **Verify Warehouse Dimensions**
   ```python
   # Check warehouse size
   if config.warehouse_width <= 0 or config.warehouse_height <= 0:
       print("Set valid warehouse dimensions")
   ```

3. **Check Item Generation**
   ```python
   # Verify item count vs available space
   available_space = (config.warehouse_width * config.warehouse_height - 
                     config.packout_zone_width * config.packout_zone_height)
   if config.total_items > available_space:
       print(f"Reduce total_items from {config.total_items} to {available_space}")
   ```

### 2. Integration Failures

**Symptoms:**
- Components not connecting
- Event system not working
- Order management disconnected

**Diagnosis:**
```python
# Check integration status
status = integration.get_integration_status()
components = status.get("components", {})

for component, integrated in components.items():
    if not integrated:
        print(f"Missing integration: {component}")
```

**Solutions:**
1. **Verify Component Availability**
   ```python
   # Check if components exist
   if not simulation_engine:
       print("Simulation engine not available")
   if not event_system:
       print("Event system not available")
   ```

2. **Re-establish Connections**
   ```python
   # Re-integrate components
   success = integration.integrate_with_simulation_engine(simulation_engine)
   success = integration.integrate_with_event_system(event_system)
   ```

3. **Check Event Handlers**
   ```python
   # Verify event registration
   handlers = event_system.get_registered_handlers()
   required_handlers = ['inventory_update', 'order_completed']
   for handler in required_handlers:
       if handler not in handlers:
           print(f"Missing handler: {handler}")
   ```

### 3. Performance Issues

**Symptoms:**
- Slow operations
- High memory usage
- Timeout errors

**Diagnosis:**
```python
from utils.inventory_debug_tools import InventoryPerformanceAnalyzer

analyzer = InventoryPerformanceAnalyzer()
analysis = analyzer.analyze_performance(config_manager)
```

**Solutions:**
1. **Check Performance Thresholds**
   ```python
   # Review threshold violations
   violations = config_manager.check_performance_thresholds()
   for violation_type, violations_list in violations.items():
       if violations_list:
           print(f"Address {violation_type} violations")
   ```

2. **Optimize Operations**
   ```python
   # Monitor operation times
   analytics = config_manager.get_performance_analytics()
   op_time_stats = analytics["performance_summary"]["operation_time"]
   if op_time_stats["average"] > 5.0:
       print("Optimize operation performance")
   ```

3. **Enable Performance Monitoring**
   ```python
   # Enable monitoring
   config_manager.config.performance_monitoring_enabled = True
   config_manager.config.debug_mode = True
   ```

### 4. Configuration Errors

**Symptoms:**
- Invalid parameters
- File not found errors
- Validation failures

**Diagnosis:**
```python
# Validate configuration
validation = config_manager.validate_configuration()
if not validation["valid"]:
    print("Configuration errors detected")
    for error in validation["errors"]:
        print(f"  - {error}")
```

**Solutions:**
1. **Check File Path**
   ```python
   import os
   config_file = "config/simulation.json"
   if not os.path.exists(config_file):
       print(f"Configuration file not found: {config_file}")
   ```

2. **Validate JSON Format**
   ```python
   import json
   try:
       with open(config_file, 'r') as f:
           json.load(f)
   except json.JSONDecodeError as e:
       print(f"Invalid JSON format: {e}")
   ```

3. **Check Parameter Ranges**
   ```python
   # Validate warehouse dimensions
   if config.warehouse_width < 1 or config.warehouse_height < 1:
       print("Warehouse dimensions must be positive")
   
   # Validate item count
   if config.total_items < 1:
       print("Total items must be positive")
   ```

---

## Diagnostic Tools

### Comprehensive Debug Report

```python
from utils.inventory_debug_tools import create_debug_report

# Create comprehensive debug report
report = create_debug_report(integration, config_manager, "warehouse_simulation.log")
print(f"Debug report created with {len(report)} sections")
```

### System Health Diagnosis

```python
from utils.inventory_debug_tools import InventoryDebugger

debugger = InventoryDebugger()
diagnosis = debugger.diagnose_system_health(integration)

print(f"Errors: {len(diagnosis.error_log)}")
print(f"Warnings: {len(diagnosis.warnings)}")
print(f"Recommendations: {len(diagnosis.recommendations)}")
```

### Log Analysis

```python
from utils.inventory_debug_tools import InventoryLogAnalyzer

analyzer = InventoryLogAnalyzer()
log_analysis = analyzer.analyze_logs("warehouse_simulation.log")

print(f"Total log entries: {log_analysis['total_lines']}")
print(f"Errors: {log_analysis['error_count']}")
print(f"Warnings: {log_analysis['warning_count']}")
```

---

## Performance Issues

### 1. High Operation Times

**Problem:** Operations taking longer than expected

**Diagnosis:**
```python
# Check operation time violations
violations = config_manager.check_performance_thresholds()
op_time_violations = violations.get("operation_time_violations", [])

if op_time_violations:
    print(f"Found {len(op_time_violations)} operation time violations")
    for violation in op_time_violations[:5]:  # Show first 5
        print(f"  - {violation}")
```

**Solutions:**
1. **Optimize Item Lookups**
   ```python
   # Use efficient data structures
   # Consider caching frequently accessed items
   # Implement batch operations
   ```

2. **Reduce Event Overhead**
   ```python
   # Batch event notifications
   # Use async operations where possible
   # Implement event filtering
   ```

3. **Monitor Memory Usage**
   ```python
   # Check memory consumption
   import psutil
   memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
   if memory_usage > config_manager.config.max_memory_usage_mb:
       print(f"High memory usage: {memory_usage:.1f}MB")
   ```

### 2. Memory Leaks

**Problem:** Memory usage increasing over time

**Diagnosis:**
```python
# Monitor memory trends
import psutil
import time

memory_samples = []
for i in range(10):
    memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_samples.append(memory)
    time.sleep(1)

# Check for increasing trend
if memory_samples[-1] > memory_samples[0] * 1.5:
    print("Potential memory leak detected")
```

**Solutions:**
1. **Clean Up Resources**
   ```python
   # Ensure proper cleanup
   integration.shutdown()
   inventory_manager.shutdown()
   sync_manager.shutdown()
   ```

2. **Review Event Handlers**
   ```python
   # Check for circular references
   # Ensure proper event unregistration
   # Monitor event handler memory usage
   ```

3. **Optimize Data Structures**
   ```python
   # Use more efficient data structures
   # Implement object pooling where appropriate
   # Consider weak references for caches
   ```

### 3. Thread Safety Issues

**Problem:** Concurrent access causing data corruption

**Diagnosis:**
```python
# Check for thread safety
import threading

def test_thread_safety():
    results = []
    def worker():
        try:
            item = inventory_manager.get_item("ITEM_A1")
            results.append(item is not None)
        except Exception as e:
            results.append(False)
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    success_rate = sum(results) / len(results)
    if success_rate < 1.0:
        print(f"Thread safety issues detected: {success_rate:.2%} success rate")
```

**Solutions:**
1. **Use Thread-Safe Operations**
   ```python
   # Ensure all operations are thread-safe
   # Use proper locking mechanisms
   # Implement atomic operations
   ```

2. **Review Concurrent Access**
   ```python
   # Identify concurrent access points
   # Implement proper synchronization
   # Use thread-safe data structures
   ```

---

## Integration Problems

### 1. Event System Disconnection

**Problem:** Events not being processed

**Diagnosis:**
```python
# Check event system status
status = integration.get_integration_status()
event_system_status = status.get("components", {}).get("event_system", False)

if not event_system_status:
    print("Event system not integrated")
```

**Solutions:**
1. **Reconnect Event System**
   ```python
   # Re-integrate event system
   success = integration.integrate_with_event_system(event_system)
   if success:
       print("Event system reconnected")
   ```

2. **Verify Event Handlers**
   ```python
   # Check registered handlers
   handlers = event_system.get_registered_handlers()
   required_handlers = ['inventory_update', 'order_completed', 'order_cancelled']
   
   for handler in required_handlers:
       if handler not in handlers:
           print(f"Missing handler: {handler}")
           # Register missing handler
   ```

3. **Test Event Flow**
   ```python
   # Test event processing
   test_event = {"type": "test", "data": {"test": True}}
   event_system.emit_event("test_event", test_event)
   ```

### 2. Order Management Issues

**Problem:** Orders not being processed correctly

**Diagnosis:**
```python
# Check order processing
sync_stats = sync_manager.get_sync_statistics()
completion_rate = sync_stats.get("completion_rate", 0)

if completion_rate < 0.9:
    print(f"Low completion rate: {completion_rate:.2%}")
```

**Solutions:**
1. **Verify Order Tracking**
   ```python
   # Check order status
   active_orders = sync_manager.get_active_orders()
   for order_id, status in active_orders.items():
       if status == "stuck":
           print(f"Order {order_id} is stuck")
   ```

2. **Check Item Availability**
   ```python
   # Verify item availability
   for order_id, items in sync_manager.get_order_items().items():
       for item_id in items:
           item = inventory_manager.get_item(item_id)
           if not item or item.quantity <= 0:
               print(f"Item {item_id} unavailable for order {order_id}")
   ```

3. **Review Order Flow**
   ```python
   # Trace order processing
   order_flow = sync_manager.get_order_flow("ORDER_001")
   for step in order_flow:
       print(f"Step: {step['action']} - Status: {step['status']}")
   ```

---

## Configuration Errors

### 1. Invalid Parameters

**Problem:** Configuration parameters out of valid ranges

**Diagnosis:**
```python
# Validate configuration parameters
validation = config_manager.validate_configuration()
if not validation["valid"]:
    print("Configuration validation failed:")
    for error in validation["errors"]:
        print(f"  - {error}")
```

**Solutions:**
1. **Check Parameter Ranges**
   ```python
   # Warehouse dimensions
   if config.warehouse_width < 1 or config.warehouse_height < 1:
       print("Warehouse dimensions must be positive")
       config.warehouse_width = max(1, config.warehouse_width)
       config.warehouse_height = max(1, config.warehouse_height)
   
   # Item count
   if config.total_items < 1:
       print("Total items must be positive")
       config.total_items = max(1, config.total_items)
   ```

2. **Validate File Paths**
   ```python
   import os
   
   # Check configuration file
   if not os.path.exists(config_manager.config_file):
       print(f"Configuration file not found: {config_manager.config_file}")
       # Create default configuration
   ```

3. **Check JSON Format**
   ```python
   import json
   
   try:
       with open(config_manager.config_file, 'r') as f:
           config_data = json.load(f)
   except json.JSONDecodeError as e:
       print(f"Invalid JSON in configuration file: {e}")
       # Fix JSON syntax
   ```

### 2. Missing Dependencies

**Problem:** Required components not available

**Diagnosis:**
```python
# Check component availability
components = {
    "simulation_engine": simulation_engine,
    "event_system": event_system,
    "warehouse_layout": warehouse_layout,
    "order_management": order_management
}

missing_components = []
for name, component in components.items():
    if component is None:
        missing_components.append(name)

if missing_components:
    print(f"Missing components: {', '.join(missing_components)}")
```

**Solutions:**
1. **Initialize Missing Components**
   ```python
   # Create missing components
   if "simulation_engine" in missing_components:
       simulation_engine = SimulationEngine()
   
   if "event_system" in missing_components:
       event_system = EventSystem()
   ```

2. **Check Import Errors**
   ```python
   # Verify imports
   try:
       from core.engine import SimulationEngine
   except ImportError as e:
       print(f"Missing simulation engine: {e}")
   
   try:
       from core.events import EventSystem
   except ImportError as e:
       print(f"Missing event system: {e}")
   ```

---

## Debug Procedures

### 1. Step-by-Step Debugging

```python
def debug_inventory_system():
    """Comprehensive debugging procedure"""
    
    print("🔍 Starting inventory system debug...")
    
    # Step 1: Check configuration
    print("\n1. Checking configuration...")
    validation = config_manager.validate_configuration()
    if not validation["valid"]:
        print("❌ Configuration errors found")
        return False
    print("✅ Configuration valid")
    
    # Step 2: Check integration
    print("\n2. Checking integration...")
    status = integration.get_integration_status()
    if not status.get("initialized", False):
        print("❌ System not initialized")
        return False
    print("✅ System initialized")
    
    # Step 3: Check components
    print("\n3. Checking components...")
    components = status.get("components", {})
    for component, integrated in components.items():
        status_icon = "✅" if integrated else "❌"
        print(f"   {status_icon} {component}")
    
    # Step 4: Check performance
    print("\n4. Checking performance...")
    violations = config_manager.check_performance_thresholds()
    if any(violations.values()):
        print("⚠️  Performance violations detected")
    else:
        print("✅ Performance within thresholds")
    
    # Step 5: Check inventory
    print("\n5. Checking inventory...")
    stats = inventory_manager.get_inventory_statistics()
    print(f"   Total items: {stats.get('total_items', 0)}")
    print(f"   Categories: {stats.get('categories', 0)}")
    
    print("\n✅ Debug complete")
    return True
```

### 2. Interactive Debugging

```python
def interactive_debug():
    """Interactive debugging session"""
    
    print("🔧 Interactive Debug Mode")
    print("Available commands:")
    print("  status - Show system status")
    print("  config - Show configuration")
    print("  performance - Show performance metrics")
    print("  inventory - Show inventory statistics")
    print("  test - Run diagnostic tests")
    print("  quit - Exit debug mode")
    
    while True:
        command = input("\nDebug> ").strip().lower()
        
        if command == "quit":
            break
        elif command == "status":
            status = integration.get_integration_status()
            print(json.dumps(status, indent=2))
        elif command == "config":
            config = config_manager.export_configuration()
            print(json.dumps(config, indent=2))
        elif command == "performance":
            analytics = config_manager.get_performance_analytics()
            print(json.dumps(analytics, indent=2))
        elif command == "inventory":
            stats = inventory_manager.get_inventory_statistics()
            print(json.dumps(stats, indent=2))
        elif command == "test":
            debug_inventory_system()
        else:
            print("Unknown command")
```

---

## Emergency Procedures

### 1. System Recovery

```python
def emergency_recovery():
    """Emergency system recovery procedure"""
    
    print("🚨 Emergency Recovery Mode")
    
    # Step 1: Stop all operations
    print("1. Stopping all operations...")
    integration.shutdown()
    
    # Step 2: Reset configuration
    print("2. Resetting configuration...")
    config_manager.reset_to_defaults()
    
    # Step 3: Reinitialize components
    print("3. Reinitializing components...")
    success = integration.initialize_inventory_system()
    
    if success:
        print("✅ Recovery successful")
        return True
    else:
        print("❌ Recovery failed")
        return False
```

### 2. Data Recovery

```python
def recover_inventory_data():
    """Recover inventory data from backup"""
    
    print("📦 Inventory Data Recovery")
    
    # Check for backup files
    backup_files = [
        "inventory_backup.json",
        "config_backup.json",
        "performance_backup.json"
    ]
    
    for backup_file in backup_files:
        if os.path.exists(backup_file):
            print(f"Found backup: {backup_file}")
            # Restore from backup
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                # Apply backup data
                print(f"Restored from {backup_file}")
            except Exception as e:
                print(f"Failed to restore {backup_file}: {e}")
    
    print("✅ Data recovery complete")
```

### 3. Performance Reset

```python
def reset_performance_monitoring():
    """Reset performance monitoring data"""
    
    print("📊 Resetting Performance Monitoring")
    
    # Clear performance metrics
    config_manager.clear_performance_metrics()
    
    # Reset thresholds
    config_manager.config.max_operation_time_ms = 10.0
    config_manager.config.max_memory_usage_mb = 100.0
    
    # Re-enable monitoring
    config_manager.config.performance_monitoring_enabled = True
    config_manager.config.debug_mode = True
    
    print("✅ Performance monitoring reset")
```

---

## Best Practices

### 1. Regular Maintenance

- Run diagnostics weekly
- Monitor performance metrics daily
- Review logs for errors
- Update configuration as needed

### 2. Proactive Monitoring

- Set up automated health checks
- Monitor performance thresholds
- Track error rates
- Watch for memory leaks

### 3. Documentation

- Keep detailed logs of issues
- Document solutions for future reference
- Maintain troubleshooting procedures
- Update this guide with new issues

### 4. Testing

- Test all integration scenarios
- Validate error handling
- Monitor performance under load
- Verify recovery procedures

---

## Contact Information

For additional support:

1. **Check the logs** for detailed error information
2. **Review the API documentation** for usage patterns
3. **Run diagnostic tools** to identify issues
4. **Consult this troubleshooting guide** for common solutions

Remember: Always backup your configuration and data before making changes! 