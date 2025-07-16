# Warehouse Layout System Troubleshooting Guide

## Overview

This guide provides solutions for common issues, error messages, and debugging techniques for the Warehouse Layout System. It covers problems you might encounter during development, testing, and production use.

## Table of Contents

1. [Common Error Messages](#common-error-messages)
2. [Coordinate System Issues](#coordinate-system-issues)
3. [Navigation Problems](#navigation-problems)
4. [Distance Tracking Issues](#distance-tracking-issues)
5. [Visualization Problems](#visualization-problems)
6. [Integration Issues](#integration-issues)
7. [Performance Problems](#performance-problems)
8. [Debugging Techniques](#debugging-techniques)
9. [Testing Issues](#testing-issues)
10. [Configuration Problems](#configuration-problems)

---

## Common Error Messages

### CoordinateError: Aisle must be between 1 and 25, got X

**Problem:** Invalid aisle number provided to Coordinate constructor.

**Cause:** Coordinate validation failed due to out-of-bounds aisle number.

**Solution:**
```python
from core.layout.coordinate import Coordinate, CoordinateError

# Check bounds before creating coordinate
def safe_create_coordinate(aisle: int, rack: int):
    if not (1 <= aisle <= 25):
        raise ValueError(f"Aisle {aisle} is outside valid range [1, 25]")
    if not (1 <= rack <= 20):
        raise ValueError(f"Rack {rack} is outside valid range [1, 20]")
    
    return Coordinate(aisle, rack)

# Usage
try:
    coord = safe_create_coordinate(10, 15)
except ValueError as e:
    print(f"Invalid coordinate: {e}")
```

### AttributeError: 'Coordinate' object has no attribute 'is_valid'

**Problem:** Using an older version of the Coordinate class that doesn't have the `is_valid()` method.

**Cause:** Method was added in a recent version.

**Solution:**
```python
# Update to use the correct method
from core.layout.coordinate import Coordinate

coord = Coordinate(10, 15)
# Use the method if available, otherwise check bounds manually
if hasattr(coord, 'is_valid'):
    is_valid = coord.is_valid()
else:
    is_valid = (1 <= coord.aisle <= 25) and (1 <= coord.rack <= 20)
```

### ValueError: Invalid from_coordinate

**Problem:** Invalid coordinate provided to distance tracking methods.

**Cause:** Coordinate validation failed in distance tracker.

**Solution:**
```python
from core.layout.distance_tracker import DistanceTracker
from core.layout.coordinate import Coordinate

def safe_track_movement(tracker, robot_id: str, from_coord, to_coord):
    """Safely track robot movement with coordinate validation."""
    # Validate coordinates first
    if not isinstance(from_coord, Coordinate) or not from_coord.is_valid():
        raise ValueError(f"Invalid from_coordinate: {from_coord}")
    if not isinstance(to_coord, Coordinate) or not to_coord.is_valid():
        raise ValueError(f"Invalid to_coordinate: {to_coord}")
    
    return tracker.track_robot_move(robot_id, from_coord, to_coord)

# Usage
tracker = DistanceTracker()
try:
    distance = safe_track_movement(tracker, "robot_001", Coordinate(1, 1), Coordinate(5, 5))
except ValueError as e:
    print(f"Movement tracking failed: {e}")
```

### AttributeError: 'PackoutZoneManager' object has no attribute 'calculate_distance_to_packout'

**Problem:** Using an older version of PackoutZoneManager that doesn't have the method.

**Cause:** Method was added in a recent version.

**Solution:**
```python
# Use alternative method or implement fallback
from core.layout.packout_zone import PackoutZoneManager
from core.layout.coordinate import Coordinate

def get_distance_to_packout(packout_manager, coord: Coordinate):
    """Get distance to packout with fallback for older versions."""
    if hasattr(packout_manager, 'calculate_distance_to_packout'):
        return packout_manager.calculate_distance_to_packout(coord)
    else:
        # Fallback: calculate manually
        packout_location = packout_manager.get_packout_location()
        return coord.distance_to(packout_location)
```

---

## Coordinate System Issues

### Issue: Coordinates not being created properly

**Symptoms:**
- CoordinateError exceptions
- Invalid coordinate values
- Type errors when using coordinates

**Debugging Steps:**
```python
from core.layout.coordinate import Coordinate

def debug_coordinate_creation(aisle: int, rack: int):
    """Debug coordinate creation process."""
    print(f"Attempting to create coordinate: ({aisle}, {rack})")
    
    # Check input types
    if not isinstance(aisle, int):
        print(f"Warning: aisle is {type(aisle)}, expected int")
    if not isinstance(rack, int):
        print(f"Warning: rack is {type(rack)}, expected int")
    
    # Check bounds
    if not (1 <= aisle <= 25):
        print(f"Error: aisle {aisle} is outside bounds [1, 25]")
    if not (1 <= rack <= 20):
        print(f"Error: rack {rack} is outside bounds [1, 20]")
    
    try:
        coord = Coordinate(aisle, rack)
        print(f"Successfully created coordinate: {coord}")
        return coord
    except Exception as e:
        print(f"Failed to create coordinate: {e}")
        return None

# Usage
debug_coordinate_creation(10, 15)
debug_coordinate_creation(0, 1)  # This will fail
```

### Issue: Coordinate comparison not working

**Symptoms:**
- Coordinates not comparing equal when they should
- Set operations not working with coordinates
- Dictionary keys not working with coordinates

**Solution:**
```python
from core.layout.coordinate import Coordinate

def test_coordinate_comparison():
    """Test coordinate comparison functionality."""
    coord1 = Coordinate(10, 15)
    coord2 = Coordinate(10, 15)
    coord3 = Coordinate(5, 10)
    
    # Test equality
    print(f"coord1 == coord2: {coord1 == coord2}")
    print(f"coord1 == coord3: {coord1 == coord3}")
    
    # Test hash functionality
    coord_set = {coord1, coord2, coord3}
    print(f"Set size: {len(coord_set)}")  # Should be 2 (coord1/coord2 are equal)
    
    # Test dictionary keys
    coord_dict = {coord1: "value1", coord3: "value3"}
    print(f"Dictionary size: {len(coord_dict)}")
    print(f"coord2 in dict: {coord2 in coord_dict}")

test_coordinate_comparison()
```

---

## Navigation Problems

### Issue: Snake pattern not finding optimal path

**Symptoms:**
- Paths longer than expected
- Suboptimal routes
- Paths not reaching target

**Debugging Steps:**
```python
from core.layout.snake_pattern import SnakePattern
from core.layout.coordinate import Coordinate

def debug_snake_pattern(start: Coordinate, target: Coordinate):
    """Debug snake pattern pathfinding."""
    snake = SnakePattern()
    
    print(f"Debugging path from {start} to {target}")
    
    # Calculate path
    path = snake.get_path_to_target(start, target)
    
    # Verify path properties
    print(f"Path length: {len(path)}")
    print(f"Start: {path[0]}")
    print(f"End: {path[-1]}")
    
    # Check if path is valid
    for i, coord in enumerate(path):
        if not coord.is_valid():
            print(f"Invalid coordinate at step {i}: {coord}")
    
    # Check if consecutive coordinates are adjacent
    for i in range(len(path) - 1):
        curr = path[i]
        next_coord = path[i + 1]
        if not curr.is_adjacent(next_coord):
            print(f"Non-adjacent coordinates at step {i}: {curr} → {next_coord}")
    
    # Calculate expected distance
    expected_distance = start.distance_to(target)
    actual_distance = len(path) - 1
    print(f"Expected distance: {expected_distance}")
    print(f"Actual distance: {actual_distance}")
    
    return path

# Usage
debug_snake_pattern(Coordinate(1, 1), Coordinate(10, 10))
```

### Issue: Path finding taking too long

**Symptoms:**
- Slow performance with large coordinate ranges
- Timeout errors
- Unresponsive system

**Solutions:**
```python
from core.layout.snake_pattern import SnakePattern
from core.layout.coordinate import Coordinate
import time

def optimize_snake_performance():
    """Optimize snake pattern performance."""
    snake = SnakePattern()
    
    # Test performance with different scenarios
    test_cases = [
        (Coordinate(1, 1), Coordinate(25, 20)),
        (Coordinate(1, 1), Coordinate(13, 10)),
        (Coordinate(25, 20), Coordinate(1, 1)),
    ]
    
    for start, target in test_cases:
        start_time = time.time()
        path = snake.get_path_to_target(start, target)
        end_time = time.time()
        
        elapsed = end_time - start_time
        print(f"Path {start} → {target}: {elapsed:.3f}s, {len(path)} steps")
        
        if elapsed > 1.0:  # More than 1 second
            print(f"WARNING: Slow path calculation for {start} → {target}")

# Usage
optimize_snake_performance()
```

---

## Distance Tracking Issues

### Issue: Order distances not being calculated correctly

**Symptoms:**
- Order distances always 0
- Incorrect distance calculations
- Missing distance tracking

**Debugging Steps:**
```python
from core.layout.distance_tracker import DistanceTracker
from core.layout.coordinate import Coordinate

def debug_distance_tracking():
    """Debug distance tracking functionality."""
    tracker = DistanceTracker()
    
    # Test complete order workflow
    order_id = "test_order"
    robot_id = "test_robot"
    start_coord = Coordinate(1, 1)
    item_coord = Coordinate(10, 10)
    
    print("Testing distance tracking workflow:")
    
    # Step 1: Start order
    tracker.track_order_start(order_id, robot_id, start_coord)
    print(f"1. Order started: {tracker.get_order_distance(order_id)}")
    
    # Step 2: Pickup item
    pickup_distance = tracker.track_pickup_item(order_id, robot_id, start_coord, item_coord)
    print(f"2. Item pickup: {pickup_distance} (total: {tracker.get_order_distance(order_id)})")
    
    # Step 3: Deliver to packout
    delivery_distance = tracker.track_deliver_to_packout(order_id, robot_id, item_coord)
    print(f"3. Delivery: {delivery_distance} (total: {tracker.get_order_distance(order_id)})")
    
    # Step 4: Complete order
    total_distance = tracker.track_order_complete(order_id, robot_id, tracker.get_current_position(robot_id))
    print(f"4. Order complete: {total_distance}")
    
    # Verify final results
    final_order_distance = tracker.get_order_distance(order_id)
    final_robot_distance = tracker.get_robot_distance(robot_id)
    
    print(f"Final order distance: {final_order_distance}")
    print(f"Final robot distance: {final_robot_distance}")
    
    # Check if distances make sense
    expected_pickup = start_coord.distance_to(item_coord)
    expected_delivery = item_coord.distance_to(Coordinate(1, 1))  # Packout location
    
    print(f"Expected pickup distance: {expected_pickup}")
    print(f"Expected delivery distance: {expected_delivery}")
    print(f"Expected total: {expected_pickup + expected_delivery}")

# Usage
debug_distance_tracking()
```

### Issue: Robot positions not updating correctly

**Symptoms:**
- Robot positions not reflecting actual movement
- Incorrect current position tracking
- Position tracking not working

**Solution:**
```python
from core.layout.distance_tracker import DistanceTracker
from core.layout.coordinate import Coordinate

def debug_robot_position_tracking():
    """Debug robot position tracking."""
    tracker = DistanceTracker()
    robot_id = "test_robot"
    
    # Test robot movement
    positions = [
        Coordinate(1, 1),
        Coordinate(5, 5),
        Coordinate(10, 10),
        Coordinate(15, 15),
    ]
    
    print("Testing robot position tracking:")
    
    for i, position in enumerate(positions):
        if i == 0:
            # First position - no movement
            print(f"Initial position: {position}")
        else:
            # Move from previous position
            from_pos = positions[i-1]
            distance = tracker.track_robot_move(robot_id, from_pos, position)
            current_pos = tracker.get_current_position(robot_id)
            
            print(f"Move {from_pos} → {position}: {distance} units")
            print(f"Current position: {current_pos}")
            
            # Verify position is correct
            if current_pos != position:
                print(f"ERROR: Position mismatch! Expected {position}, got {current_pos}")

# Usage
debug_robot_position_tracking()
```

---

## Visualization Problems

### Issue: Grid not rendering correctly

**Symptoms:**
- Grid display errors
- Missing robot positions
- Incorrect cell types
- Rendering crashes

**Debugging Steps:**
```python
from core.layout.grid_visualizer import GridVisualizer
from core.layout.coordinate import Coordinate

def debug_grid_visualization():
    """Debug grid visualization."""
    visualizer = GridVisualizer()
    
    # Test basic functionality
    print("Testing basic grid visualization:")
    
    # Set robot positions
    visualizer.set_robot_position("robot_001", Coordinate(5, 5))
    visualizer.set_robot_position("robot_002", Coordinate(10, 10))
    
    # Set path
    path = [Coordinate(1, 1), Coordinate(5, 5), Coordinate(10, 10)]
    visualizer.set_path(path)
    
    # Set start and target
    visualizer.set_start_cell(Coordinate(1, 1))
    visualizer.set_target_cell(Coordinate(20, 20))
    
    # Highlight cells
    visualizer.highlight_cell(Coordinate(8, 8))
    
    # Render grid
    try:
        grid_str = visualizer.render_grid()
        print("Grid rendered successfully")
        print("Grid preview (first 10 lines):")
        lines = grid_str.split('\n')[:10]
        for line in lines:
            print(f"  {line}")
    except Exception as e:
        print(f"Grid rendering failed: {e}")
    
    # Test cell type determination
    test_coords = [
        (Coordinate(1, 1), "packout"),
        (Coordinate(5, 5), "robot"),
        (Coordinate(8, 8), "highlight"),
        (Coordinate(20, 20), "target"),
    ]
    
    print("\nTesting cell type determination:")
    for coord, expected_type in test_coords:
        cell_type = visualizer.get_cell_type(coord)
        print(f"  {coord}: {cell_type} (expected: {expected_type})")

# Usage
debug_grid_visualization()
```

### Issue: Performance problems with large grids

**Symptoms:**
- Slow rendering
- Memory issues
- Unresponsive visualization

**Solutions:**
```python
from core.layout.grid_visualizer import GridVisualizer
from core.layout.coordinate import Coordinate
import time

def optimize_visualization_performance():
    """Optimize grid visualization performance."""
    visualizer = GridVisualizer()
    
    # Test with many robot positions
    print("Testing visualization performance:")
    
    # Add many robots
    start_time = time.time()
    for i in range(10):
        robot_id = f"robot_{i:03d}"
        coord = Coordinate(i + 1, i + 1)
        visualizer.set_robot_position(robot_id, coord)
    
    setup_time = time.time() - start_time
    print(f"Setup time: {setup_time:.3f}s")
    
    # Test rendering performance
    render_times = []
    for i in range(5):
        start_time = time.time()
        grid_str = visualizer.render_grid()
        end_time = time.time()
        render_times.append(end_time - start_time)
    
    avg_render_time = sum(render_times) / len(render_times)
    print(f"Average render time: {avg_render_time:.3f}s")
    
    if avg_render_time > 1.0:
        print("WARNING: Slow rendering detected")
        print("Consider using compact mode or reducing robot count")

# Usage
optimize_visualization_performance()
```

---

## Integration Issues

### Issue: Integration manager not initializing

**Symptoms:**
- Integration initialization fails
- External systems not connecting
- Event handling not working

**Debugging Steps:**
```python
from core.layout.integration import LayoutIntegrationManager

def debug_integration_initialization():
    """Debug integration manager initialization."""
    integration = LayoutIntegrationManager()
    
    print("Testing integration initialization:")
    
    # Test basic initialization
    try:
        success = integration.initialize_integration()
        print(f"Basic initialization: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Basic initialization failed: {e}")
    
    # Test with external systems
    try:
        # Mock external systems
        mock_sim_engine = None
        mock_event_system = None
        mock_config_manager = None
        
        success = integration.initialize_integration(
            simulation_engine=mock_sim_engine,
            event_system=mock_event_system,
            config_manager=mock_config_manager
        )
        print(f"Integration with external systems: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Integration with external systems failed: {e}")
    
    # Test component access
    try:
        components = [
            integration.warehouse_layout,
            integration.snake_pattern,
            integration.packout_manager,
            integration.distance_tracker,
            integration.grid_visualizer,
        ]
        
        for i, component in enumerate(components):
            if component is not None:
                print(f"Component {i+1}: OK")
            else:
                print(f"Component {i+1}: MISSING")
    except Exception as e:
        print(f"Component access failed: {e}")

# Usage
debug_integration_initialization()
```

### Issue: Event handling not working

**Symptoms:**
- Events not being processed
- No response to robot movements
- Order events not tracked

**Solution:**
```python
from core.layout.integration import LayoutIntegrationManager
from core.layout.coordinate import Coordinate

def debug_event_handling():
    """Debug event handling functionality."""
    integration = LayoutIntegrationManager()
    integration.initialize_integration()
    
    print("Testing event handling:")
    
    # Test robot move event
    try:
        integration._handle_robot_move({
            'robot_id': 'test_robot',
            'from_coordinate': Coordinate(1, 1),
            'to_coordinate': Coordinate(5, 5),
            'direction': 'forward'
        })
        print("Robot move event: SUCCESS")
    except Exception as e:
        print(f"Robot move event failed: {e}")
    
    # Test order start event
    try:
        integration._handle_order_start({
            'order_id': 'test_order',
            'robot_id': 'test_robot',
            'start_coordinate': Coordinate(1, 1)
        })
        print("Order start event: SUCCESS")
    except Exception as e:
        print(f"Order start event failed: {e}")
    
    # Test item pickup event
    try:
        integration._handle_item_pickup({
            'order_id': 'test_order',
            'robot_id': 'test_robot',
            'from_coordinate': Coordinate(1, 1),
            'to_coordinate': Coordinate(10, 10)
        })
        print("Item pickup event: SUCCESS")
    except Exception as e:
        print(f"Item pickup event failed: {e}")
    
    # Test order complete event
    try:
        integration._handle_order_complete({
            'order_id': 'test_order',
            'robot_id': 'test_robot',
            'final_coordinate': Coordinate(1, 1)
        })
        print("Order complete event: SUCCESS")
    except Exception as e:
        print(f"Order complete event failed: {e}")
    
    # Verify results
    order_distance = integration.distance_tracker.get_order_distance('test_order')
    robot_distance = integration.distance_tracker.get_robot_distance('test_robot')
    
    print(f"Final order distance: {order_distance}")
    print(f"Final robot distance: {robot_distance}")

# Usage
debug_event_handling()
```

---

## Performance Problems

### Issue: System running slowly

**Symptoms:**
- Slow response times
- High memory usage
- CPU spikes
- Unresponsive interface

**Diagnostic Steps:**
```python
import time
import psutil
import os
from core.layout.integration import LayoutIntegrationManager

def diagnose_performance_issues():
    """Diagnose performance issues."""
    print("Performance Diagnosis:")
    
    # Check system resources
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    cpu_percent = process.cpu_percent()
    
    print(f"Memory usage: {memory_usage:.1f} MB")
    print(f"CPU usage: {cpu_percent:.1f}%")
    
    # Test component performance
    integration = LayoutIntegrationManager()
    integration.initialize_integration()
    
    # Test snake pattern performance
    from core.layout.snake_pattern import SnakePattern
    snake = SnakePattern()
    
    start_time = time.time()
    for i in range(100):
        start = Coordinate(i % 25 + 1, i % 20 + 1)
        target = Coordinate((i + 10) % 25 + 1, (i + 10) % 20 + 1)
        path = snake.get_path_to_target(start, target)
    
    snake_time = time.time() - start_time
    print(f"Snake pattern (100 paths): {snake_time:.3f}s")
    
    # Test distance tracking performance
    start_time = time.time()
    for i in range(1000):
        robot_id = f"robot_{i % 10:03d}"
        from_coord = Coordinate(i % 25 + 1, i % 20 + 1)
        to_coord = Coordinate((i + 1) % 25 + 1, (i + 1) % 20 + 1)
        integration.distance_tracker.track_robot_move(robot_id, from_coord, to_coord)
    
    tracking_time = time.time() - start_time
    print(f"Distance tracking (1000 events): {tracking_time:.3f}s")
    
    # Test visualization performance
    start_time = time.time()
    for i in range(10):
        integration.grid_visualizer.render_grid()
    
    viz_time = time.time() - start_time
    print(f"Grid visualization (10 renders): {viz_time:.3f}s")
    
    # Performance recommendations
    print("\nPerformance Recommendations:")
    if snake_time > 1.0:
        print("- Snake pattern is slow, consider caching")
    if tracking_time > 1.0:
        print("- Distance tracking is slow, consider batching")
    if viz_time > 1.0:
        print("- Visualization is slow, consider compact mode")
    if memory_usage > 100:
        print("- High memory usage, consider cleanup")

# Usage
diagnose_performance_issues()
```

### Issue: Memory leaks

**Symptoms:**
- Increasing memory usage over time
- System slowdown
- Out of memory errors

**Solutions:**
```python
from core.layout.distance_tracker import DistanceTracker
from core.layout.grid_visualizer import GridVisualizer
import gc

def prevent_memory_leaks():
    """Implement memory leak prevention."""
    tracker = DistanceTracker()
    visualizer = GridVisualizer()
    
    # Monitor memory usage
    import psutil
    process = psutil.Process()
    
    print("Memory leak prevention:")
    
    # Test with many events
    initial_memory = process.memory_info().rss / 1024 / 1024
    print(f"Initial memory: {initial_memory:.1f} MB")
    
    # Generate many events
    for i in range(10000):
        robot_id = f"robot_{i % 10:03d}"
        from_coord = Coordinate(i % 25 + 1, i % 20 + 1)
        to_coord = Coordinate((i + 1) % 25 + 1, (i + 1) % 20 + 1)
        
        tracker.track_robot_move(robot_id, from_coord, to_coord)
        
        # Periodically cleanup
        if i % 1000 == 0:
            # Clear old events
            if len(tracker.events) > 5000:
                tracker._events = tracker.events[-5000:]
            
            # Force garbage collection
            gc.collect()
    
    # Check memory usage
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"Final memory: {final_memory:.1f} MB")
    print(f"Memory increase: {final_memory - initial_memory:.1f} MB")
    
    if final_memory - initial_memory > 50:
        print("WARNING: Significant memory increase detected")

# Usage
prevent_memory_leaks()
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging
from core.layout.integration import LayoutIntegrationManager

def enable_debug_logging():
    """Enable debug logging for troubleshooting."""
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('warehouse_debug.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create integration manager with debug logging
    integration = LayoutIntegrationManager()
    integration.initialize_integration()
    
    # Test with debug logging
    integration._handle_robot_move({
        'robot_id': 'debug_robot',
        'from_coordinate': Coordinate(1, 1),
        'to_coordinate': Coordinate(5, 5),
        'direction': 'forward'
    })
    
    print("Debug logging enabled. Check 'warehouse_debug.log' for details.")

# Usage
enable_debug_logging()
```

### State Inspection

```python
from core.layout.integration import LayoutIntegrationManager

def inspect_system_state():
    """Inspect current system state for debugging."""
    integration = LayoutIntegrationManager()
    integration.initialize_integration()
    
    print("System State Inspection:")
    
    # Check integration status
    status = integration.get_integration_status()
    print(f"Integration initialized: {status.get('initialized', False)}")
    print(f"Components loaded: {status.get('components_loaded', 0)}")
    
    # Check grid integrity
    validation = integration.validate_grid_integrity()
    print(f"Grid integrity: {'VALID' if validation['valid'] else 'INVALID'}")
    
    if not validation['valid']:
        print("Grid integrity errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    # Check extension points
    extension_points = integration.create_extension_points()
    print(f"Available extension points: {len(extension_points)}")
    
    # Check component states
    components = [
        ('Warehouse Layout', integration.warehouse_layout),
        ('Snake Pattern', integration.snake_pattern),
        ('Packout Manager', integration.packout_manager),
        ('Distance Tracker', integration.distance_tracker),
        ('Grid Visualizer', integration.grid_visualizer),
    ]
    
    print("\nComponent Status:")
    for name, component in components:
        status = "OK" if component is not None else "MISSING"
        print(f"  {name}: {status}")

# Usage
inspect_system_state()
```

### Performance Profiling

```python
import cProfile
import pstats
from core.layout.integration import LayoutIntegrationManager

def profile_performance():
    """Profile system performance."""
    profiler = cProfile.Profile()
    
    def run_workload():
        integration = LayoutIntegrationManager()
        integration.initialize_integration()
        
        # Simulate workload
        for i in range(1000):
            integration._handle_robot_move({
                'robot_id': f'robot_{i % 10:03d}',
                'from_coordinate': Coordinate(i % 25 + 1, i % 20 + 1),
                'to_coordinate': Coordinate((i + 1) % 25 + 1, (i + 1) % 20 + 1),
                'direction': 'forward'
            })
    
    # Run profiling
    profiler.enable()
    run_workload()
    profiler.disable()
    
    # Print statistics
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Usage
profile_performance()
```

---

## Testing Issues

### Issue: Tests failing unexpectedly

**Symptoms:**
- Tests passing locally but failing in CI
- Intermittent test failures
- Environment-specific test issues

**Debugging Steps:**
```python
import unittest
from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import SnakePattern

class TestDebugger(unittest.TestCase):
    """Debug test failures."""
    
    def test_coordinate_creation(self):
        """Test coordinate creation with detailed debugging."""
        print("Testing coordinate creation...")
        
        # Test valid coordinates
        test_cases = [
            (1, 1), (25, 20), (13, 10)
        ]
        
        for aisle, rack in test_cases:
            print(f"Testing coordinate ({aisle}, {rack})")
            try:
                coord = Coordinate(aisle, rack)
                self.assertTrue(coord.is_valid())
                print(f"  ✓ Coordinate {coord} created successfully")
            except Exception as e:
                print(f"  ✗ Failed to create coordinate ({aisle}, {rack}): {e}")
                self.fail(f"Coordinate creation failed: {e}")
    
    def test_snake_pattern(self):
        """Test snake pattern with debugging."""
        print("Testing snake pattern...")
        
        snake = SnakePattern()
        start = Coordinate(1, 1)
        target = Coordinate(10, 10)
        
        try:
            path = snake.get_path_to_target(start, target)
            print(f"  Path length: {len(path)}")
            print(f"  Start: {path[0]}")
            print(f"  End: {path[-1]}")
            
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], target)
            print("  ✓ Snake pattern test passed")
        except Exception as e:
            print(f"  ✗ Snake pattern test failed: {e}")
            self.fail(f"Snake pattern test failed: {e}")

# Run debug tests
if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### Issue: Test environment differences

**Symptoms:**
- Tests work on one machine but not another
- Different results in different environments
- Platform-specific issues

**Solution:**
```python
import platform
import sys
from core.layout.integration import LayoutIntegrationManager

def check_test_environment():
    """Check test environment for differences."""
    print("Test Environment Check:")
    
    # System information
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {sys.version}")
    print(f"Architecture: {platform.architecture()}")
    
    # Test basic functionality
    try:
        integration = LayoutIntegrationManager()
        success = integration.initialize_integration()
        print(f"Integration initialization: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"Integration initialization failed: {e}")
    
    # Test coordinate system
    try:
        from core.layout.coordinate import Coordinate
        coord = Coordinate(10, 15)
        print(f"Coordinate system: OK ({coord})")
    except Exception as e:
        print(f"Coordinate system failed: {e}")
    
    # Test snake pattern
    try:
        from core.layout.snake_pattern import SnakePattern
        snake = SnakePattern()
        path = snake.get_path_to_target(Coordinate(1, 1), Coordinate(5, 5))
        print(f"Snake pattern: OK ({len(path)} steps)")
    except Exception as e:
        print(f"Snake pattern failed: {e}")

# Usage
check_test_environment()
```

---

## Configuration Problems

### Issue: Configuration not loading

**Symptoms:**
- Default values being used instead of custom config
- Configuration errors
- Missing configuration files

**Debugging Steps:**
```python
import json
from core.layout.integration import LayoutIntegrationManager

def debug_configuration_loading():
    """Debug configuration loading issues."""
    print("Configuration Debug:")
    
    # Test default configuration
    try:
        integration = LayoutIntegrationManager()
        integration.initialize_integration()
        print("✓ Default configuration loaded")
    except Exception as e:
        print(f"✗ Default configuration failed: {e}")
    
    # Test custom configuration
    custom_config = {
        "warehouse": {
            "dimensions": [25, 20],
            "packout_location": [1, 1]
        },
        "visualization": {
            "show_coordinates": True,
            "show_legend": True
        }
    }
    
    try:
        # Save custom config
        with open('test_config.json', 'w') as f:
            json.dump(custom_config, f, indent=2)
        print("✓ Custom configuration saved")
        
        # Load custom config
        with open('test_config.json', 'r') as f:
            loaded_config = json.load(f)
        print("✓ Custom configuration loaded")
        
        # Verify configuration
        if loaded_config == custom_config:
            print("✓ Configuration verification passed")
        else:
            print("✗ Configuration verification failed")
            
    except Exception as e:
        print(f"✗ Custom configuration failed: {e}")

# Usage
debug_configuration_loading()
```

### Issue: Configuration validation errors

**Symptoms:**
- Invalid configuration values
- Configuration schema errors
- Missing required fields

**Solution:**
```python
def validate_configuration(config: dict):
    """Validate configuration structure and values."""
    print("Configuration Validation:")
    
    # Check required sections
    required_sections = ['warehouse', 'visualization', 'tracking']
    for section in required_sections:
        if section not in config:
            print(f"✗ Missing required section: {section}")
        else:
            print(f"✓ Found section: {section}")
    
    # Validate warehouse configuration
    if 'warehouse' in config:
        warehouse = config['warehouse']
        
        # Check dimensions
        if 'dimensions' in warehouse:
            dims = warehouse['dimensions']
            if len(dims) == 2 and 1 <= dims[0] <= 50 and 1 <= dims[1] <= 50:
                print(f"✓ Valid dimensions: {dims}")
            else:
                print(f"✗ Invalid dimensions: {dims}")
        else:
            print("✗ Missing warehouse dimensions")
        
        # Check packout location
        if 'packout_location' in warehouse:
            packout = warehouse['packout_location']
            if len(packout) == 2 and 1 <= packout[0] <= 25 and 1 <= packout[1] <= 20:
                print(f"✓ Valid packout location: {packout}")
            else:
                print(f"✗ Invalid packout location: {packout}")
        else:
            print("✗ Missing packout location")
    
    # Validate visualization configuration
    if 'visualization' in config:
        viz = config['visualization']
        viz_options = ['show_coordinates', 'show_legend', 'compact_mode']
        
        for option in viz_options:
            if option in viz:
                if isinstance(viz[option], bool):
                    print(f"✓ Valid {option}: {viz[option]}")
                else:
                    print(f"✗ Invalid {option}: {viz[option]} (should be boolean)")
            else:
                print(f"✗ Missing visualization option: {option}")

# Usage
test_config = {
    "warehouse": {
        "dimensions": [25, 20],
        "packout_location": [1, 1]
    },
    "visualization": {
        "show_coordinates": True,
        "show_legend": True,
        "compact_mode": False
    },
    "tracking": {
        "enable_kpi_metrics": True
    }
}

validate_configuration(test_config)
```

---

## Getting Help

### When to Seek Help

- **Critical errors** that prevent system operation
- **Performance issues** that can't be resolved with optimization
- **Integration problems** with external systems
- **Test failures** that can't be reproduced locally

### Information to Provide

When reporting issues, include:

1. **Error messages** and stack traces
2. **System information** (OS, Python version, etc.)
3. **Steps to reproduce** the issue
4. **Expected vs actual behavior**
5. **Relevant code snippets**
6. **Performance metrics** if applicable

### Support Channels

- **Documentation**: Check API docs and usage examples
- **Testing**: Run comprehensive tests to isolate issues
- **Debugging**: Use provided debugging tools
- **Community**: Seek help from development community

---

## Conclusion

This troubleshooting guide covers the most common issues you might encounter with the Warehouse Layout System. For issues not covered here, use the debugging techniques and diagnostic tools provided to identify and resolve problems.

Remember to:
- **Test thoroughly** before deploying
- **Monitor performance** in production
- **Keep backups** of working configurations
- **Document custom solutions** for future reference 