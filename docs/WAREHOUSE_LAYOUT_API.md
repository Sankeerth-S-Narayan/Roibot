# Warehouse Layout System API Documentation

## Overview

The Warehouse Layout System provides a comprehensive solution for managing warehouse grid coordinates, navigation patterns, packout zones, distance tracking, and visualization. This document provides detailed API documentation for all components.

## Table of Contents

1. [Coordinate System](#coordinate-system)
2. [Warehouse Layout Manager](#warehouse-layout-manager)
3. [Snake Pattern Navigation](#snake-pattern-navigation)
4. [Packout Zone Management](#packout-zone-management)
5. [Distance Tracking](#distance-tracking)
6. [Grid Visualization](#grid-visualization)
7. [Integration Manager](#integration-manager)

---

## Coordinate System

### Coordinate Class

Represents a warehouse grid coordinate with 1-based indexing.

#### Constructor
```python
Coordinate(aisle: int, rack: int)
```

**Parameters:**
- `aisle`: Aisle number (1-25)
- `rack`: Rack number (1-20)

**Raises:**
- `CoordinateError`: If coordinates are outside valid bounds

#### Methods

##### `is_valid() -> bool`
Check if coordinate is within warehouse bounds.

**Returns:**
- `True` if coordinate is valid, `False` otherwise

##### `distance_to(other: Coordinate) -> float`
Calculate Manhattan distance to another coordinate.

**Parameters:**
- `other`: Target coordinate

**Returns:**
- Manhattan distance between coordinates

##### `euclidean_distance_to(other: Coordinate) -> float`
Calculate Euclidean distance to another coordinate.

**Parameters:**
- `other`: Target coordinate

**Returns:**
- Euclidean distance between coordinates

##### `is_adjacent(other: Coordinate) -> bool`
Check if this coordinate is adjacent to another.

**Parameters:**
- `other`: Coordinate to check adjacency with

**Returns:**
- `True` if coordinates are adjacent (Manhattan distance = 1)

##### `is_packout_location() -> bool`
Check if this coordinate is the packout location (1, 1).

**Returns:**
- `True` if coordinate is packout location

##### `to_dict() -> dict`
Convert coordinate to dictionary.

**Returns:**
- Dictionary with 'aisle' and 'rack' keys

##### `from_dict(coord_dict: dict) -> Coordinate`
Create coordinate from dictionary.

**Parameters:**
- `coord_dict`: Dictionary with 'aisle' and 'rack' keys

**Returns:**
- Coordinate object

#### Usage Example
```python
from core.layout.coordinate import Coordinate

# Create coordinate
coord = Coordinate(10, 15)

# Check validity
print(coord.is_valid())  # True

# Calculate distance
other = Coordinate(5, 10)
distance = coord.distance_to(other)  # 10

# Check if packout location
packout = Coordinate(1, 1)
print(packout.is_packout_location())  # True
```

---

## Warehouse Layout Manager

### WarehouseLayoutManager Class

Manages warehouse grid state and coordinate validation.

#### Constructor
```python
WarehouseLayoutManager()
```

#### Methods

##### `is_valid_coordinate(coord: Coordinate) -> bool`
Check if coordinate is valid within warehouse bounds.

**Parameters:**
- `coord`: Coordinate to validate

**Returns:**
- `True` if coordinate is valid

##### `get_grid_dimensions() -> Tuple[int, int]`
Get warehouse grid dimensions.

**Returns:**
- Tuple of (max_aisle, max_rack)

##### `get_grid_snapshot() -> Dict[str, Any]`
Get current grid state snapshot.

**Returns:**
- Dictionary containing grid state

##### `load_grid_snapshot(snapshot: Dict[str, Any]) -> None`
Load grid state from snapshot.

**Parameters:**
- `snapshot`: Grid state dictionary

##### `set_grid_state(coord: Coordinate, state: GridState) -> None`
Set grid state for specific coordinate.

**Parameters:**
- `coord`: Target coordinate
- `state`: Grid state to set

#### Usage Example
```python
from core.layout.warehouse_layout import WarehouseLayoutManager
from core.layout.coordinate import Coordinate

# Create layout manager
layout = WarehouseLayoutManager()

# Validate coordinate
coord = Coordinate(10, 15)
print(layout.is_valid_coordinate(coord))  # True

# Get dimensions
dimensions = layout.get_grid_dimensions()  # (25, 20)
```

---

## Snake Pattern Navigation

### SnakePattern Class

Provides optimal navigation paths using snake pattern algorithm.

#### Constructor
```python
SnakePattern()
```

#### Methods

##### `get_path_to_target(start: Coordinate, target: Coordinate) -> List[Coordinate]`
Calculate optimal path from start to target using snake pattern.

**Parameters:**
- `start`: Starting coordinate
- `target`: Target coordinate

**Returns:**
- List of coordinates representing optimal path

##### `get_path_distance(path: List[Coordinate]) -> float`
Calculate total distance for a path.

**Parameters:**
- `path`: List of coordinates

**Returns:**
- Total path distance

#### Usage Example
```python
from core.layout.snake_pattern import SnakePattern
from core.layout.coordinate import Coordinate

# Create snake pattern
snake = SnakePattern()

# Calculate path
start = Coordinate(1, 1)
target = Coordinate(10, 10)
path = snake.get_path_to_target(start, target)

# Get path distance
distance = snake.get_path_distance(path)
```

---

## Packout Zone Management

### PackoutZoneManager Class

Manages packout zone functionality and special zone validation.

#### Constructor
```python
PackoutZoneManager(warehouse_layout: WarehouseLayoutManager)
```

**Parameters:**
- `warehouse_layout`: Warehouse layout manager instance

#### Methods

##### `get_packout_location() -> Coordinate`
Get the packout location coordinate.

**Returns:**
- Packout location coordinate (1, 1)

##### `is_packout_location(coord: Coordinate) -> bool`
Check if coordinate is the packout location.

**Parameters:**
- `coord`: Coordinate to check

**Returns:**
- `True` if coordinate is packout location

##### `is_restricted_zone(coord: Coordinate) -> bool`
Check if coordinate is in a restricted zone.

**Parameters:**
- `coord`: Coordinate to check

**Returns:**
- `True` if coordinate is in restricted zone

##### `calculate_distance_to_packout(coord: Coordinate) -> float`
Calculate distance from coordinate to packout location.

**Parameters:**
- `coord`: Starting coordinate

**Returns:**
- Manhattan distance to packout

##### `calculate_optimal_route_to_packout(start: Coordinate) -> List[Coordinate]`
Calculate optimal route from start position to packout.

**Parameters:**
- `start`: Starting coordinate

**Returns:**
- List of coordinates representing the optimal route

##### `can_pickup_item_at(coord: Coordinate) -> bool`
Check if item pickup is allowed at the coordinate.

**Parameters:**
- `coord`: Coordinate to check

**Returns:**
- `True` if pickup is allowed

##### `can_place_item_at(coord: Coordinate) -> bool`
Check if item placement is allowed at the coordinate.

**Parameters:**
- `coord`: Coordinate to check

**Returns:**
- `True` if placement is allowed

#### Usage Example
```python
from core.layout.packout_zone import PackoutZoneManager
from core.layout.warehouse_layout import WarehouseLayoutManager
from core.layout.coordinate import Coordinate

# Create packout manager
layout = WarehouseLayoutManager()
packout = PackoutZoneManager(layout)

# Get packout location
packout_loc = packout.get_packout_location()  # Coordinate(1, 1)

# Check if coordinate is packout
coord = Coordinate(1, 1)
print(packout.is_packout_location(coord))  # True

# Calculate distance to packout
test_coord = Coordinate(10, 10)
distance = packout.calculate_distance_to_packout(test_coord)  # 18
```

---

## Distance Tracking

### DistanceTracker Class

Tracks robot movements, order distances, and provides KPI metrics.

#### Constructor
```python
DistanceTracker()
```

#### Methods

##### `track_robot_move(robot_id: str, from_coord: Coordinate, to_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float`
Track a robot movement and calculate distance.

**Parameters:**
- `robot_id`: ID of the robot
- `from_coord`: Starting coordinate
- `to_coord`: Ending coordinate
- `direction`: Robot movement direction

**Returns:**
- Distance traveled in this move

##### `track_order_start(order_id: str, robot_id: str, start_coord: Coordinate) -> None`
Track the start of an order.

**Parameters:**
- `order_id`: ID of the order
- `robot_id`: ID of the robot handling the order
- `start_coord`: Starting coordinate for the order

##### `track_pickup_item(order_id: str, robot_id: str, from_coord: Coordinate, to_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float`
Track item pickup movement for an order.

**Parameters:**
- `order_id`: ID of the order
- `robot_id`: ID of the robot
- `from_coord`: Starting coordinate
- `to_coord`: Item pickup coordinate
- `direction`: Robot movement direction

**Returns:**
- Distance traveled for this pickup

##### `track_deliver_to_packout(order_id: str, robot_id: str, from_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float`
Track delivery to packout location.

**Parameters:**
- `order_id`: ID of the order
- `robot_id`: ID of the robot
- `from_coord`: Starting coordinate
- `direction`: Robot movement direction

**Returns:**
- Distance traveled to packout

##### `track_return_to_start(robot_id: str, from_coord: Coordinate, start_coord: Coordinate, direction: Direction = Direction.FORWARD) -> float`
Track robot return to start position.

**Parameters:**
- `robot_id`: ID of the robot
- `from_coord`: Current coordinate
- `start_coord`: Start coordinate to return to
- `direction`: Robot movement direction

**Returns:**
- Distance traveled to return to start

##### `track_order_complete(order_id: str, robot_id: str, final_coord: Coordinate) -> float`
Track order completion.

**Parameters:**
- `order_id`: ID of the order
- `robot_id`: ID of the robot
- `final_coord`: Final coordinate after order completion

**Returns:**
- Total distance for this order

##### `get_order_distance(order_id: str) -> float`
Get total distance for a specific order.

**Parameters:**
- `order_id`: ID of the order

**Returns:**
- Total distance for the order

##### `get_robot_distance(robot_id: str) -> float`
Get total distance for a specific robot.

**Parameters:**
- `robot_id`: ID of the robot

**Returns:**
- Total distance for the robot

##### `get_current_position(robot_id: str) -> Optional[Coordinate]`
Get current position of a robot.

**Parameters:**
- `robot_id`: ID of the robot

**Returns:**
- Current coordinate of the robot, or None if not tracked

##### `get_kpi_metrics() -> Dict[str, Any]`
Calculate KPI metrics based on distance tracking.

**Returns:**
- Dictionary containing various KPI metrics

#### Usage Example
```python
from core.layout.distance_tracker import DistanceTracker
from core.layout.coordinate import Coordinate

# Create distance tracker
tracker = DistanceTracker()

# Track order workflow
order_id = "order_001"
robot_id = "robot_001"
start_coord = Coordinate(1, 1)
item_coord = Coordinate(10, 10)

# Start order
tracker.track_order_start(order_id, robot_id, start_coord)

# Pickup item
pickup_distance = tracker.track_pickup_item(
    order_id, robot_id, start_coord, item_coord
)

# Deliver to packout
delivery_distance = tracker.track_deliver_to_packout(
    order_id, robot_id, item_coord
)

# Get order distance
total_distance = tracker.get_order_distance(order_id)

# Get KPI metrics
metrics = tracker.get_kpi_metrics()
```

---

## Grid Visualization

### GridVisualizer Class

Provides console-based grid visualization with robot positions and paths.

#### Constructor
```python
GridVisualizer()
```

#### Methods

##### `set_robot_position(robot_id: str, position: Coordinate) -> None`
Set robot position on the grid.

**Parameters:**
- `robot_id`: ID of the robot
- `position`: Robot position coordinate

##### `remove_robot_position(robot_id: str) -> None`
Remove robot position from the grid.

**Parameters:**
- `robot_id`: ID of the robot to remove

##### `set_path(path: List[Coordinate]) -> None`
Set path to visualize on the grid.

**Parameters:**
- `path`: List of coordinates representing the path

##### `clear_path() -> None`
Clear the current path visualization.

##### `set_start_cell(coord: Coordinate) -> None`
Set start cell for visualization.

**Parameters:**
- `coord`: Start coordinate

##### `set_target_cell(coord: Coordinate) -> None`
Set target cell for visualization.

**Parameters:**
- `coord`: Target coordinate

##### `clear_start_target() -> None`
Clear start and target cells.

##### `highlight_cell(coord: Coordinate) -> None`
Highlight a specific cell.

**Parameters:**
- `coord`: Coordinate to highlight

##### `clear_highlights() -> None`
Clear all highlighted cells.

##### `render_grid() -> str`
Render the warehouse grid as a string.

**Returns:**
- String representation of the grid

##### `export_grid_state() -> Dict[str, Any]`
Export current grid state.

**Returns:**
- Dictionary containing grid state

##### `import_grid_state(state: Dict[str, Any]) -> None`
Import grid state.

**Parameters:**
- `state`: Grid state dictionary

#### Usage Example
```python
from core.layout.grid_visualizer import GridVisualizer
from core.layout.coordinate import Coordinate

# Create visualizer
visualizer = GridVisualizer()

# Set robot positions
visualizer.set_robot_position("robot_001", Coordinate(5, 5))
visualizer.set_robot_position("robot_002", Coordinate(10, 10))

# Set path
path = [Coordinate(1, 1), Coordinate(5, 5), Coordinate(10, 10)]
visualizer.set_path(path)

# Render grid
grid_str = visualizer.render_grid()
print(grid_str)
```

---

## Integration Manager

### LayoutIntegrationManager Class

Integrates warehouse layout with external systems and manages events.

#### Constructor
```python
LayoutIntegrationManager()
```

#### Methods

##### `initialize_integration(simulation_engine=None, event_system=None, config_manager=None) -> bool`
Initialize integration with external systems.

**Parameters:**
- `simulation_engine`: Simulation engine instance
- `event_system`: Event system instance
- `config_manager`: Configuration manager instance

**Returns:**
- `True` if initialization successful

##### `_handle_robot_move(event_data: Dict[str, Any]) -> None`
Handle robot move events.

**Parameters:**
- `event_data`: Robot move event data

##### `_handle_order_start(event_data: Dict[str, Any]) -> None`
Handle order start events.

**Parameters:**
- `event_data`: Order start event data

##### `_handle_order_complete(event_data: Dict[str, Any]) -> None`
Handle order completion events.

**Parameters:**
- `event_data`: Order complete event data

##### `_handle_item_pickup(event_data: Dict[str, Any]) -> None`
Handle item pickup events.

**Parameters:**
- `event_data`: Item pickup event data

##### `_handle_item_delivery(event_data: Dict[str, Any]) -> None`
Handle item delivery events.

**Parameters:**
- `event_data`: Item delivery event data

##### `get_layout_state() -> Dict[str, Any]`
Get current layout state for persistence.

**Returns:**
- Dictionary containing layout state

##### `load_layout_state(state: Dict[str, Any]) -> bool`
Load layout state from persistence.

**Parameters:**
- `state`: Layout state dictionary

**Returns:**
- `True` if successful

##### `validate_grid_integrity() -> Dict[str, Any]`
Validate grid integrity and return validation results.

**Returns:**
- Dictionary containing validation results

##### `create_extension_points() -> Dict[str, Any]`
Create extension points for external systems.

**Returns:**
- Dictionary containing extension points

#### Usage Example
```python
from core.layout.integration import LayoutIntegrationManager

# Create integration manager
integration = LayoutIntegrationManager()

# Initialize with external systems
success = integration.initialize_integration()

# Handle robot move event
integration._handle_robot_move({
    'robot_id': 'robot_001',
    'from_coordinate': Coordinate(1, 1),
    'to_coordinate': Coordinate(5, 5),
    'direction': 'forward'
})

# Get layout state
state = integration.get_layout_state()

# Validate grid integrity
validation = integration.validate_grid_integrity()
```

---

## Error Handling

### Common Exceptions

#### CoordinateError
Raised when coordinate validation fails.

```python
from core.layout.coordinate import Coordinate, CoordinateError

try:
    coord = Coordinate(0, 1)  # Invalid aisle
except CoordinateError as e:
    print(f"Coordinate error: {e}")
```

#### ValueError
Raised when invalid parameters are provided.

```python
from core.layout.distance_tracker import DistanceTracker

tracker = DistanceTracker()
try:
    tracker.track_robot_move("robot_001", None, Coordinate(1, 1))
except ValueError as e:
    print(f"Value error: {e}")
```

---

## Performance Considerations

### Coordinate Operations
- Coordinate validation is O(1)
- Distance calculations are O(1)
- Path finding is O(n) where n is path length

### Distance Tracking
- Event storage is O(1) per event
- KPI calculations are O(n) where n is number of events
- Memory usage scales with number of tracked entities

### Grid Visualization
- Rendering is O(width × height)
- Cell type determination is O(1)
- State export/import is O(n) where n is grid size

---

## Best Practices

### Coordinate Usage
```python
# Good: Use Coordinate objects consistently
coord = Coordinate(10, 15)
distance = coord.distance_to(Coordinate(5, 10))

# Bad: Mix coordinate types
coord = (10, 15)  # Tuple instead of Coordinate object
```

### Distance Tracking
```python
# Good: Track complete workflows
tracker.track_order_start(order_id, robot_id, start_coord)
tracker.track_pickup_item(order_id, robot_id, from_coord, to_coord)
tracker.track_order_complete(order_id, robot_id, final_coord)

# Bad: Skip workflow steps
tracker.track_robot_move(robot_id, from_coord, to_coord)  # Missing order context
```

### Grid Visualization
```python
# Good: Clear state between operations
visualizer.clear_path()
visualizer.clear_highlights()
visualizer.set_robot_position(robot_id, new_position)

# Bad: Accumulate state without clearing
visualizer.set_robot_position(robot_id, old_position)  # Old position not cleared
visualizer.set_robot_position(robot_id, new_position)
```

---

## Version History

### v1.0.0
- Initial release with core warehouse layout functionality
- Coordinate system with validation
- Snake pattern navigation
- Packout zone management
- Distance tracking with KPI metrics
- Grid visualization
- Integration manager for external systems 