# Order Management System - Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting information for common issues, error resolution, and system diagnostics for the warehouse simulation order management system.

## Table of Contents

1. [Common Issues](#common-issues)
2. [Error Codes and Messages](#error-codes-and-messages)
3. [Configuration Problems](#configuration-problems)
4. [Integration Issues](#integration-issues)
5. [Performance Problems](#performance-problems)
6. [Debugging Tools](#debugging-tools)
7. [Recovery Procedures](#recovery-procedures)
8. [Prevention Strategies](#prevention-strategies)

---

## Common Issues

### 1. Order Generation Problems

#### **Issue: No orders being generated**
**Symptoms:**
- Order queue remains empty
- No ORDER_CREATED events
- OrderGenerator status shows "STOPPED"

**Possible Causes:**
- OrderGenerator not started
- Invalid warehouse layout configuration
- Generation interval set too high
- Auto-start disabled

**Solutions:**
```python
# Check if order generator is running
if not integration.order_generator.is_generating:
    integration.order_generator.start_generation()

# Verify warehouse layout
warehouse_layout = integration.order_generator.warehouse_layout
if warehouse_layout is None:
    print("❌ Warehouse layout not configured")

# Check generation interval
config = integration.order_generator.get_status()
print(f"Generation interval: {config.get('generation_interval', 'unknown')}")

# Enable auto-start
integration.order_generator.configure({'auto_start': True})
```

#### **Issue: Orders generated with invalid coordinates**
**Symptoms:**
- Orders created with coordinates outside warehouse bounds
- Robot cannot reach order locations
- Invalid position errors

**Solutions:**
```python
# Validate warehouse layout
from core.layout.warehouse_layout import WarehouseLayoutManager
layout = WarehouseLayoutManager()

# Check if coordinates are valid
for order in integration.queue_manager.queue:
    for item in order.items:
        if not layout.is_valid_position(item.position):
            print(f"❌ Invalid position for item {item.item_id}: {item.position}")
```

### 2. Queue Management Issues

#### **Issue: Queue overflow**
**Symptoms:**
- Queue size exceeds maximum capacity
- New orders rejected
- "Queue full" errors

**Solutions:**
```python
# Check queue status
queue_status = integration.queue_manager.get_queue_status()
print(f"Queue size: {queue_status['queue_size']}/{queue_status['max_size']}")

# Increase queue capacity
integration.queue_manager.max_size = 200

# Process orders faster
# Check robot assignment efficiency
robot_status = integration.robot_assigner.get_assignment_status()
print(f"Robot available: {robot_status.get('is_available', False)}")
```

#### **Issue: Orders stuck in queue**
**Symptoms:**
- Orders remain in PENDING status
- Robot not assigned to orders
- Queue not processing

**Solutions:**
```python
# Check robot availability
if not integration.robot_assigner.is_robot_available():
    print("❌ Robot not available for assignment")
    
# Force order assignment
pending_orders = [order for order in integration.queue_manager.queue 
                 if order.status == "PENDING"]
for order in pending_orders:
    integration.robot_assigner.assign_order_to_robot(order)
```

### 3. Robot Assignment Problems

#### **Issue: Robot not assigned to orders**
**Symptoms:**
- Robot remains IDLE
- Orders not progressing from PENDING
- Assignment failures

**Solutions:**
```python
# Check robot state
robot_status = integration.robot_assigner.get_assignment_status()
print(f"Robot state: {robot_status.get('robot_state', 'UNKNOWN')}")

# Verify robot integration
if not integration.robot_assigner.is_active:
    print("❌ Robot assigner not active")

# Check for assignment errors
current_order = integration.robot_assigner.get_current_order()
if current_order is None and integration.queue_manager.get_queue_size() > 0:
    next_order = integration.queue_manager.get_next_order()
    if next_order:
        success = integration.robot_assigner.assign_order_to_robot(next_order)
        print(f"Assignment result: {success}")
```

#### **Issue: Robot stuck in processing**
**Symptoms:**
- Robot state not changing
- Orders not completing
- Robot position not updating

**Solutions:**
```python
# Check robot state machine
robot_state = integration.robot_assigner.get_assignment_status()
print(f"Current robot state: {robot_state.get('robot_state', 'UNKNOWN')}")

# Force state reset if needed
if robot_state.get('robot_state') == 'STUCK':
    integration.robot_assigner.reset_robot_state()

# Check order completion
current_order = integration.robot_assigner.get_current_order()
if current_order and current_order.is_completed():
    integration.robot_assigner.complete_current_order()
```

### 4. Status Tracking Issues

#### **Issue: Order status not updating**
**Symptoms:**
- Orders stuck in same status
- Status tracker not responding
- Missing status transitions

**Solutions:**
```python
# Check status tracker
tracking_stats = integration.status_tracker.get_tracking_statistics()
print(f"Active orders: {tracking_stats.get('active_orders', 0)}")

# Verify status updates
for order_id in integration.status_tracker.active_orders:
    order_status = integration.status_tracker.get_order_status(order_id)
    print(f"Order {order_id}: {order_status}")

# Force status update
integration.status_tracker.update_order_status(order_id, "IN_PROGRESS")
```

#### **Issue: Item collection not tracked**
**Symptoms:**
- Items not marked as collected
- Order completion not detected
- Collection events missing

**Solutions:**
```python
# Check item collection tracking
for order in integration.status_tracker.active_orders.values():
    print(f"Order {order.order_id}: {order.items_collected}/{order.total_items}")

# Manually mark items as collected
integration.status_tracker.mark_item_collected(order_id, item_id, robot_id, time.time())

# Verify collection events
# Check if robot is actually at item location
robot_position = integration.robot_assigner.get_robot_position()
item_position = get_item_position(item_id)
if distance(robot_position, item_position) < 1.0:
    # Robot is close enough to collect
    integration.status_tracker.mark_item_collected(order_id, item_id, robot_id, time.time())
```

### 5. Analytics and Performance Issues

#### **Issue: Performance metrics not updating**
**Symptoms:**
- Analytics dashboard showing stale data
- Metrics not reflecting current state
- Export data outdated

**Solutions:**
```python
# Force analytics update
integration.analytics.update_order_metrics(order)
integration.analytics.update_robot_metrics(robot_id, robot_data)

# Check analytics configuration
analytics_config = integration.analytics.get_analytics_summary()
print(f"Analytics active: {analytics_config.get('is_active', False)}")

# Export current metrics
integration.analytics.export_metrics_to_csv("current_metrics.csv")
```

#### **Issue: Dashboard not displaying data**
**Symptoms:**
- Dashboard showing empty or incorrect data
- Real-time updates not working
- Dashboard crashes

**Solutions:**
```python
# Check dashboard data
dashboard_data = integration.dashboard.display_dashboard()
print(f"Dashboard data: {dashboard_data}")

# Verify analytics connection
analytics_data = integration.analytics.get_real_time_metrics()
if not analytics_data:
    print("❌ No analytics data available")

# Restart dashboard if needed
integration.dashboard = AnalyticsDashboard(integration.analytics)
```

---

## Error Codes and Messages

### Configuration Errors

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `CONFIG_001` | Invalid configuration file format | JSON syntax error | Check JSON syntax and format |
| `CONFIG_002` | Missing required configuration parameter | Required field not provided | Add missing parameter to config |
| `CONFIG_003` | Configuration parameter out of range | Value exceeds valid range | Adjust parameter to valid range |
| `CONFIG_004` | Configuration file not found | File missing or inaccessible | Create or restore config file |

**Resolution:**
```python
# Validate configuration
config_manager = ConfigurationManager()
if not config_manager.validate_config():
    print("❌ Configuration validation failed")
    # Load default configuration
    config_manager.load_default_config()
```

### Integration Errors

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `INTEG_001` | Event system connection failed | Event system not available | Check event system status |
| `INTEG_002` | Simulation engine not responding | Engine not running or crashed | Restart simulation engine |
| `INTEG_003` | Robot state machine error | State machine in invalid state | Reset robot state machine |
| `INTEG_004` | Component initialization failed | Component dependencies not met | Check component dependencies |

**Resolution:**
```python
# Check integration status
integration_status = integration.get_integration_status()
if not integration_status.get('is_integrated', False):
    print("❌ Integration failed")
    # Re-attempt integration
    success = await integration.integrate_with_simulation()
    print(f"Integration result: {success}")
```

### Order Processing Errors

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `ORDER_001` | Order generation failed | Invalid warehouse layout | Verify warehouse configuration |
| `ORDER_002` | Order assignment failed | Robot not available | Check robot availability |
| `ORDER_003` | Order completion timeout | Order taking too long | Check for stuck orders |
| `ORDER_004` | Item collection failed | Robot cannot reach item | Verify item positions |

**Resolution:**
```python
# Handle order processing errors
try:
    order = integration.order_generator.generate_order(time.time())
    if order:
        success = integration.queue_manager.add_order(order)
        if not success:
            print("❌ Failed to add order to queue")
except Exception as e:
    print(f"❌ Order generation error: {e}")
    # Log error and continue
```

### Performance Errors

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `PERF_001` | Queue overflow | Too many orders in queue | Increase queue capacity |
| `PERF_002` | Low success rate | Many failed orders | Check order processing logic |
| `PERF_003` | High completion time | Orders taking too long | Optimize robot movement |
| `PERF_004` | Low throughput | System not processing enough orders | Check generation rate |

**Resolution:**
```python
# Monitor performance metrics
metrics = integration.analytics.get_real_time_metrics()
if metrics.get('success_rate', 100) < 85:
    print("⚠️ Low success rate detected")
    # Investigate failed orders
    failed_orders = [order for order in integration.queue_manager.queue 
                    if order.status == "FAILED"]
    print(f"Failed orders: {len(failed_orders)}")
```

---

## Configuration Problems

### 1. Invalid Configuration File

**Problem:** Configuration file contains invalid JSON or missing required fields.

**Diagnosis:**
```python
# Check configuration file
config_manager = ConfigurationManager()
try:
    config_manager.load_config()
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

**Solution:**
```python
# Create default configuration
config_manager.create_default_config()
config_manager.save_config()
print("✅ Default configuration created")
```

### 2. Configuration Parameter Conflicts

**Problem:** Configuration parameters conflict with each other or system limits.

**Diagnosis:**
```python
# Validate configuration parameters
config = config_manager.get_order_generation_config()
if config.generation_interval < 1.0:
    print("❌ Generation interval too low")
if config.max_items_per_order > 10:
    print("❌ Max items per order too high")
```

**Solution:**
```python
# Adjust conflicting parameters
config.generation_interval = max(1.0, config.generation_interval)
config.max_items_per_order = min(10, config.max_items_per_order)
config_manager.save_config()
```

### 3. Missing Configuration Files

**Problem:** Required configuration files are missing or corrupted.

**Diagnosis:**
```python
import os
config_file = "config/order_management.json"
if not os.path.exists(config_file):
    print(f"❌ Configuration file missing: {config_file}")
```

**Solution:**
```python
# Restore configuration from backup or create new
config_manager = ConfigurationManager()
config_manager.create_default_config()
config_manager.save_config()
print("✅ Configuration restored")
```

---

## Integration Issues

### 1. Event System Connection Problems

**Problem:** Order management system cannot communicate with event system.

**Diagnosis:**
```python
# Check event system status
try:
    await integration.event_system.emit(EventType.SYSTEM_WARNING, {"test": True})
    print("✅ Event system connection OK")
except Exception as e:
    print(f"❌ Event system error: {e}")
```

**Solution:**
```python
# Reconnect to event system
await integration.event_system.connect()
# Re-register event handlers
integration._register_event_handlers()
```

### 2. Simulation Engine Integration Issues

**Problem:** Order management cannot access simulation engine data.

**Diagnosis:**
```python
# Check simulation engine connection
if not hasattr(integration.simulation_engine, 'robot'):
    print("❌ Robot not available in simulation engine")
if not hasattr(integration.simulation_engine, 'warehouse_layout'):
    print("❌ Warehouse layout not available")
```

**Solution:**
```python
# Re-establish integration
await integration.integrate_with_simulation()
# Verify integration
integration_status = integration.get_integration_status()
print(f"Integration status: {integration_status.get('is_integrated', False)}")
```

### 3. Robot State Machine Issues

**Problem:** Robot state machine is in an invalid state or not responding.

**Diagnosis:**
```python
# Check robot state
robot_status = integration.robot_assigner.get_assignment_status()
current_state = robot_status.get('robot_state', 'UNKNOWN')
valid_states = ['IDLE', 'MOVING', 'COLLECTING', 'RETURNING']
if current_state not in valid_states:
    print(f"❌ Invalid robot state: {current_state}")
```

**Solution:**
```python
# Reset robot state machine
integration.robot_assigner.reset_robot_state()
# Verify reset
new_status = integration.robot_assigner.get_assignment_status()
print(f"Robot state after reset: {new_status.get('robot_state', 'UNKNOWN')}")
```

---

## Performance Problems

### 1. Slow Order Processing

**Problem:** Orders are taking too long to complete.

**Diagnosis:**
```python
# Check average completion time
metrics = integration.analytics.get_real_time_metrics()
avg_time = metrics.get('average_completion_time', 0.0)
if avg_time > 300:  # 5 minutes
    print(f"⚠️ Slow order processing: {avg_time:.1f}s average")
```

**Solutions:**
```python
# Optimize robot movement
# Check for inefficient paths
robot_position = integration.robot_assigner.get_robot_position()
for order in integration.queue_manager.queue:
    for item in order.items:
        distance = calculate_distance(robot_position, item.position)
        if distance > 50:  # Too far
            print(f"⚠️ Long distance to item: {distance}")

# Optimize order assignment
# Assign orders to closest robot position
```

### 2. High Error Rate

**Problem:** Many orders are failing or timing out.

**Diagnosis:**
```python
# Check error rate
metrics = integration.analytics.get_real_time_metrics()
error_rate = metrics.get('error_rate', 0.0)
if error_rate > 10:  # 10%
    print(f"⚠️ High error rate: {error_rate:.1f}%")
```

**Solutions:**
```python
# Investigate failed orders
failed_orders = [order for order in integration.queue_manager.queue 
                if order.status == "FAILED"]
for order in failed_orders:
    print(f"Failed order {order.order_id}: {order.error_message}")

# Check for common failure patterns
# - Invalid coordinates
# - Robot stuck
# - Timeout issues
```

### 3. Queue Bottlenecks

**Problem:** Orders are backing up in the queue.

**Diagnosis:**
```python
# Check queue status
queue_status = integration.queue_manager.get_queue_status()
queue_size = queue_status.get('queue_size', 0)
max_size = queue_status.get('max_size', 100)
if queue_size > max_size * 0.8:  # 80% full
    print(f"⚠️ Queue bottleneck: {queue_size}/{max_size}")
```

**Solutions:**
```python
# Increase processing capacity
# Check robot utilization
robot_status = integration.robot_assigner.get_assignment_status()
if robot_status.get('is_available', False):
    # Assign more orders
    pending_orders = [order for order in integration.queue_manager.queue 
                     if order.status == "PENDING"]
    for order in pending_orders[:5]:  # Process 5 at a time
        integration.robot_assigner.assign_order_to_robot(order)

# Optimize order generation rate
config = integration.order_generator.get_status()
if config.get('generation_interval', 30) < 60:
    # Slow down generation
    integration.order_generator.configure({'generation_interval': 60})
```

---

## Debugging Tools

### 1. Using the Debug Tracker

**Enable comprehensive debugging:**
```python
from utils.order_debug_tools import start_debug_monitoring, DebugLevel

# Start debug monitoring
debugger = start_debug_monitoring(integration, DebugLevel.DETAILED)

# Get debug report
report = debugger.get_debug_report()
print(f"Debug report: {report}")

# Export debug data
debugger.export_debug_report("debug_report.json")
```

### 2. Using Performance Monitor

**Monitor performance in real-time:**
```python
from utils.performance_monitor import start_performance_monitoring

# Start performance monitoring
monitor = start_performance_monitoring(integration, display=True)

# Get performance summary
summary = monitor.get_performance_summary()
print(f"Performance summary: {summary}")

# Export performance data
monitor.export_performance_data("performance_data.json")
```

### 3. Using Visualization Tools

**Visualize system status:**
```python
from utils.order_visualizer import start_visualization, VisualizationType

# Start queue visualization
queue_viz = start_visualization(integration, VisualizationType.QUEUE_STATUS)

# Start system overview
overview_viz = start_visualization(integration, VisualizationType.SYSTEM_OVERVIEW)

# Start real-time monitor
monitor_viz = start_visualization(integration, VisualizationType.REAL_TIME_MONITOR)
```

### 4. Logging and Diagnostics

**Enable detailed logging:**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('order_management.log'),
        logging.StreamHandler()
    ]
)

# Enable component-specific logging
logging.getLogger('OrderGenerator').setLevel(logging.DEBUG)
logging.getLogger('OrderQueueManager').setLevel(logging.DEBUG)
logging.getLogger('RobotOrderAssigner').setLevel(logging.DEBUG)
```

---

## Recovery Procedures

### 1. System Restart Procedure

**When to use:** System is unresponsive or in an invalid state.

**Steps:**
```python
# 1. Stop all components
integration.order_generator.stop_generation()
integration.queue_manager.clear_queue()
integration.robot_assigner.reset_robot_state()
integration.status_tracker.stop_tracking()

# 2. Reset integration
await integration.shutdown_integration()

# 3. Restart components
await integration.integrate_with_simulation()
integration.order_generator.start_generation()

# 4. Verify system status
integration_status = integration.get_integration_status()
print(f"System restarted: {integration_status.get('is_integrated', False)}")
```

### 2. Order Recovery Procedure

**When to use:** Orders are stuck or in invalid states.

**Steps:**
```python
# 1. Identify stuck orders
stuck_orders = []
for order in integration.queue_manager.queue:
    if order.status in ["PENDING", "IN_PROGRESS"]:
        # Check if order has been processing too long
        if time.time() - order.creation_time > 600:  # 10 minutes
            stuck_orders.append(order)

# 2. Reset stuck orders
for order in stuck_orders:
    integration.queue_manager.remove_order(order.order_id)
    # Recreate order if needed
    new_order = integration.order_generator.generate_order(time.time())
    if new_order:
        integration.queue_manager.add_order(new_order)

# 3. Verify recovery
queue_status = integration.queue_manager.get_queue_status()
print(f"Orders after recovery: {queue_status['queue_size']}")
```

### 3. Robot Recovery Procedure

**When to use:** Robot is stuck or in an invalid state.

**Steps:**
```python
# 1. Check robot state
robot_status = integration.robot_assigner.get_assignment_status()
print(f"Robot state: {robot_status.get('robot_state', 'UNKNOWN')}")

# 2. Reset robot if needed
if robot_status.get('robot_state') not in ['IDLE', 'MOVING', 'COLLECTING', 'RETURNING']:
    integration.robot_assigner.reset_robot_state()
    print("✅ Robot state reset")

# 3. Clear current assignment if stuck
current_order = integration.robot_assigner.get_current_order()
if current_order and current_order.status == "IN_PROGRESS":
    # Check if order has been processing too long
    if time.time() - current_order.assignment_time > 300:  # 5 minutes
        integration.robot_assigner.complete_current_order()
        print("✅ Stuck order cleared")

# 4. Verify robot availability
if integration.robot_assigner.is_robot_available():
    print("✅ Robot recovered and available")
```

### 4. Configuration Recovery Procedure

**When to use:** Configuration is corrupted or invalid.

**Steps:**
```python
# 1. Backup current configuration
config_manager = ConfigurationManager()
try:
    current_config = config_manager.config_data
    with open("config_backup.json", "w") as f:
        json.dump(current_config, f, indent=2)
except Exception as e:
    print(f"⚠️ Could not backup config: {e}")

# 2. Load default configuration
config_manager.create_default_config()
config_manager.save_config()

# 3. Restart components with new config
await integration.shutdown_integration()
await integration.integrate_with_simulation()

# 4. Verify configuration
if config_manager.validate_config():
    print("✅ Configuration recovered")
else:
    print("❌ Configuration recovery failed")
```

---

## Prevention Strategies

### 1. Regular Health Checks

**Implement automated health monitoring:**
```python
def health_check():
    """Regular health check function."""
    # Check integration status
    integration_status = integration.get_integration_status()
    if not integration_status.get('is_integrated', False):
        print("⚠️ Integration health check failed")
        return False
    
    # Check component status
    component_status = integration_status.get('component_status', {})
    for component, status in component_status.items():
        if status != "ACTIVE":
            print(f"⚠️ Component {component} not active: {status}")
            return False
    
    # Check performance metrics
    metrics = integration.analytics.get_real_time_metrics()
    if metrics.get('success_rate', 100) < 85:
        print("⚠️ Low success rate detected")
        return False
    
    print("✅ Health check passed")
    return True

# Run health check every 5 minutes
import threading
import time

def periodic_health_check():
    while True:
        health_check()
        time.sleep(300)  # 5 minutes

health_thread = threading.Thread(target=periodic_health_check, daemon=True)
health_thread.start()
```

### 2. Performance Monitoring

**Set up continuous performance monitoring:**
```python
from utils.performance_monitor import create_performance_monitor, PerformanceThresholds

# Create custom thresholds
thresholds = PerformanceThresholds()
thresholds.max_completion_time = 180.0  # 3 minutes
thresholds.min_success_rate = 90.0  # 90%
thresholds.max_error_rate = 5.0  # 5%

# Start monitoring
monitor = create_performance_monitor(integration, thresholds)

# Add alert handlers
def handle_performance_alert(alert):
    print(f"🚨 Performance alert: {alert.message}")
    # Take corrective action based on alert type

monitor.add_alert_callback(handle_performance_alert)
monitor.start_monitoring()
```

### 3. Automated Recovery

**Implement automatic recovery procedures:**
```python
def auto_recovery():
    """Automated recovery procedure."""
    # Check for stuck orders
    stuck_orders = []
    for order in integration.queue_manager.queue:
        if order.status in ["PENDING", "IN_PROGRESS"]:
            if time.time() - order.creation_time > 600:  # 10 minutes
                stuck_orders.append(order)
    
    if stuck_orders:
        print(f"🔄 Auto-recovering {len(stuck_orders)} stuck orders")
        for order in stuck_orders:
            integration.queue_manager.remove_order(order.order_id)
    
    # Check robot state
    robot_status = integration.robot_assigner.get_assignment_status()
    if robot_status.get('robot_state') not in ['IDLE', 'MOVING', 'COLLECTING', 'RETURNING']:
        print("🔄 Auto-resetting robot state")
        integration.robot_assigner.reset_robot_state()
    
    # Check queue overflow
    queue_status = integration.queue_manager.get_queue_status()
    if queue_status.get('queue_size', 0) > queue_status.get('max_size', 100) * 0.9:
        print("🔄 Queue overflow detected, slowing generation")
        integration.order_generator.configure({'generation_interval': 60})

# Run auto-recovery every 2 minutes
def periodic_auto_recovery():
    while True:
        auto_recovery()
        time.sleep(120)  # 2 minutes

recovery_thread = threading.Thread(target=periodic_auto_recovery, daemon=True)
recovery_thread.start()
```

### 4. Configuration Validation

**Implement configuration validation:**
```python
def validate_system_configuration():
    """Validate system configuration."""
    # Check order generation config
    gen_config = integration.order_generator.get_status()
    if gen_config.get('generation_interval', 30) < 1:
        print("❌ Generation interval too low")
        return False
    
    # Check queue config
    queue_status = integration.queue_manager.get_queue_status()
    if queue_status.get('max_size', 100) < 10:
        print("❌ Queue size too small")
        return False
    
    # Check robot config
    robot_status = integration.robot_assigner.get_assignment_status()
    if not robot_status.get('robot_id'):
        print("❌ Robot ID not configured")
        return False
    
    print("✅ Configuration validation passed")
    return True

# Run validation on startup
if not validate_system_configuration():
    print("❌ Configuration validation failed, using defaults")
    # Load default configuration
```

---

## Quick Reference

### Common Commands

```python
# Check system status
integration_status = integration.get_integration_status()
print(f"Integration: {integration_status.get('is_integrated', False)}")

# Check order queue
queue_status = integration.queue_manager.get_queue_status()
print(f"Queue: {queue_status['queue_size']}/{queue_status['max_size']}")

# Check robot status
robot_status = integration.robot_assigner.get_assignment_status()
print(f"Robot: {robot_status.get('robot_state', 'UNKNOWN')}")

# Check performance
metrics = integration.analytics.get_real_time_metrics()
print(f"Success rate: {metrics.get('success_rate', 0):.1f}%")

# Export debug data
from utils.order_debug_tools import generate_debug_report
generate_debug_report(integration, "debug_report.json")

# Start monitoring
from utils.performance_monitor import start_performance_monitoring
monitor = start_performance_monitoring(integration)
```

### Emergency Procedures

1. **System unresponsive:** Restart integration
2. **Orders stuck:** Clear queue and restart generation
3. **Robot stuck:** Reset robot state machine
4. **Performance issues:** Check metrics and adjust thresholds
5. **Configuration problems:** Load default configuration

### Contact Information

For additional support:
- Check the API documentation: `docs/ORDER_MANAGEMENT_API.md`
- Review architecture documentation: `docs/ORDER_MANAGEMENT_ARCHITECTURE.md`
- Use debugging tools: `utils/order_debug_tools.py`
- Monitor performance: `utils/performance_monitor.py`
- Visualize system: `utils/order_visualizer.py`

This troubleshooting guide should help resolve most common issues with the order management system. For complex problems, use the debugging tools and monitoring systems to gather detailed information about the issue. 