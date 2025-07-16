# 🔌 Extension Points & Integration Guide

## Overview

The Roibot simulation system is designed with extensibility in mind. This document outlines the extension points and integration guidelines for adding new features and components in future phases.

## Architecture Overview

The system follows a modular, event-driven architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Simulation    │    │   Event         │    │   Configuration │
│   Engine        │◄──►│   System        │◄──►│   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Timing        │    │   State         │    │   Performance   │
│   Manager       │    │   Management    │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Extension Points

### 1. Component System

The simulation engine uses a component-based architecture where new entities can be easily added.

#### Adding New Components

```python
# Example: Adding a Robot component
class Robot:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 2.0
        self.state = "idle"
    
    def update(self, delta_time: float):
        # Update robot logic
        pass
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "speed": self.speed,
            "state": self.state
        }

# Register with simulation state
simulation_state.register_component("robot", robot_instance)
```

#### Component Lifecycle

1. **Initialization**: Component is created and registered
2. **Start**: Component is activated when simulation starts
3. **Update**: Component is updated every frame
4. **Stop**: Component is deactivated when simulation stops
5. **Cleanup**: Component resources are freed

### 2. Event System Extensions

The event system is designed to be extensible for new event types and handlers.

#### Adding New Event Types

```python
# In core/events.py
class EventType(Enum):
    # Existing events...
    SIMULATION_START = "simulation_start"
    SIMULATION_STOP = "simulation_stop"
    
    # New events for Phase 2
    ROBOT_MOVE = "robot_move"
    ROBOT_COLLISION = "robot_collision"
    ORDER_CREATED = "order_created"
    ORDER_COMPLETED = "order_completed"
```

#### Creating Event Handlers

```python
# Example: Robot movement event handler
class RobotEventHandler:
    def __init__(self, robot_manager):
        self.robot_manager = robot_manager
    
    async def handle_robot_move(self, event_data: Dict[str, Any]):
        robot_id = event_data["robot_id"]
        new_position = event_data["position"]
        
        # Update robot position
        self.robot_manager.update_robot_position(robot_id, new_position)
        
        # Emit collision check event
        await self.event_system.emit(EventType.COLLISION_CHECK, {
            "robot_id": robot_id,
            "position": new_position
        })

# Register handler
event_system.register_handler(EventType.ROBOT_MOVE, robot_handler.handle_robot_move)
```

### 3. Configuration Extensions

The configuration system supports adding new sections for new features.

#### Adding Configuration Sections

```python
# In core/config.py
class RobotConfiguration:
    def __init__(self):
        self.SPEED = 2.0
        self.ACCELERATION = 1.0
        self.DECELERATION = 1.0
        self.BATTERY_CAPACITY = 100.0
        self.CHARGE_RATE = 10.0

# Add to configuration manager
config_manager.add_section("robot", RobotConfiguration())
```

#### Configuration Validation

```python
def validate_robot_config(config: Dict[str, Any]) -> bool:
    """Validate robot configuration section."""
    robot_config = config.get("robot", {})
    
    # Validate speed
    speed = robot_config.get("SPEED", 2.0)
    if not (0.5 <= speed <= 10.0):
        raise ConfigurationError("Robot speed must be between 0.5 and 10.0")
    
    # Validate battery capacity
    battery = robot_config.get("BATTERY_CAPACITY", 100.0)
    if not (50.0 <= battery <= 500.0):
        raise ConfigurationError("Battery capacity must be between 50.0 and 500.0")
    
    return True
```

### 4. Performance Monitoring Extensions

The performance monitoring system can be extended for new metrics.

#### Adding Custom Metrics

```python
# Extend PerformanceMetrics
@dataclass
class ExtendedPerformanceMetrics(PerformanceMetrics):
    robot_update_time: float = 0.0
    pathfinding_time: float = 0.0
    collision_check_time: float = 0.0
    battery_usage: float = 0.0

# Record custom metrics
benchmark.record_metrics(
    frame_time=0.016,
    fps=60.0,
    event_processing_time=0.001,
    component_update_time=0.002,
    event_queue_size=10,
    robot_update_time=0.005,  # Custom metric
    pathfinding_time=0.003    # Custom metric
)
```

## Phase 2 Integration Points

### Robot Movement System

#### Integration Points
1. **Component Registration**: Register robot entities with simulation state
2. **Event Emission**: Emit movement and collision events
3. **Configuration**: Add robot-specific configuration
4. **Performance Monitoring**: Track robot update performance

#### Implementation Example

```python
# entities/robot.py
class Robot:
    def __init__(self, robot_id: str, x: float, y: float):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 2.0
        self.state = "idle"
    
    async def update(self, delta_time: float, event_system):
        if self.state == "moving":
            # Update position
            self._move_towards_target(delta_time)
            
            # Emit movement event
            await event_system.emit(EventType.ROBOT_MOVE, {
                "robot_id": self.robot_id,
                "position": (self.x, self.y),
                "target": (self.target_x, self.target_y)
            })
    
    def _move_towards_target(self, delta_time: float):
        # Movement logic
        pass

# Integration with simulation engine
class RobotManager:
    def __init__(self, event_system):
        self.robots = {}
        self.event_system = event_system
    
    def add_robot(self, robot: Robot):
        self.robots[robot.robot_id] = robot
    
    async def update_all(self, delta_time: float):
        for robot in self.robots.values():
            await robot.update(delta_time, self.event_system)
```

### Pathfinding System

#### Integration Points
1. **Event Handling**: Handle pathfinding requests
2. **Configuration**: Pathfinding algorithm settings
3. **Performance**: Track pathfinding computation time

#### Implementation Example

```python
# utils/pathfinding.py
class Pathfinder:
    def __init__(self, warehouse_width: int, warehouse_height: int):
        self.width = warehouse_width
        self.height = warehouse_height
        self.obstacles = set()
    
    async def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        # A* pathfinding implementation
        pass
    
    def add_obstacle(self, x: int, y: int):
        self.obstacles.add((x, y))

# Event handler for pathfinding requests
async def handle_pathfinding_request(event_data: Dict[str, Any]):
    start = event_data["start"]
    end = event_data["end"]
    robot_id = event_data["robot_id"]
    
    path = await pathfinder.find_path(start, end)
    
    # Emit path found event
    await event_system.emit(EventType.PATH_FOUND, {
        "robot_id": robot_id,
        "path": path
    })
```

## Phase 3 Integration Points

### Order Management System

#### Integration Points
1. **Event System**: Order creation, assignment, completion events
2. **Configuration**: Order generation parameters
3. **State Management**: Order state tracking

#### Implementation Example

```python
# entities/order.py
class Order:
    def __init__(self, order_id: str, items: List[str], priority: int):
        self.order_id = order_id
        self.items = items
        self.priority = priority
        self.status = "pending"
        self.assigned_robot = None
        self.created_time = time.time()
    
    def assign_to_robot(self, robot_id: str):
        self.assigned_robot = robot_id
        self.status = "assigned"
    
    def complete(self):
        self.status = "completed"

# Order manager
class OrderManager:
    def __init__(self, event_system):
        self.orders = {}
        self.event_system = event_system
        self.generation_timer = 0
    
    async def update(self, delta_time: float):
        self.generation_timer += delta_time
        
        if self.generation_timer >= ORDER_GENERATION_INTERVAL:
            await self._generate_order()
            self.generation_timer = 0
    
    async def _generate_order(self):
        order = self._create_random_order()
        self.orders[order.order_id] = order
        
        # Emit order created event
        await self.event_system.emit(EventType.ORDER_CREATED, {
            "order_id": order.order_id,
            "items": order.items,
            "priority": order.priority
        })
```

## Integration Guidelines

### 1. Event-Driven Communication

Always use the event system for component communication:

```python
# ✅ Good: Use events for communication
await event_system.emit(EventType.ROBOT_MOVE, {"robot_id": "r1", "position": (x, y)})

# ❌ Bad: Direct component coupling
robot_manager.update_position("r1", x, y)
```

### 2. Configuration Management

Extend configuration systematically:

```python
# ✅ Good: Add configuration section
config_manager.add_section("robot", RobotConfiguration())

# ❌ Bad: Hard-coded values
ROBOT_SPEED = 2.0  # Hard-coded
```

### 3. Performance Monitoring

Track performance for new components:

```python
# ✅ Good: Track component performance
start_time = time.time()
robot_manager.update_all(delta_time)
update_time = time.time() - start_time

benchmark.record_metrics(
    # ... other metrics
    robot_update_time=update_time
)
```

### 4. Error Handling

Implement proper error handling:

```python
# ✅ Good: Comprehensive error handling
try:
    path = await pathfinder.find_path(start, end)
except PathfindingError as e:
    logger.error(f"Pathfinding failed: {e}")
    # Fallback behavior
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle gracefully
```

### 5. Testing

Create comprehensive tests for new components:

```python
# ✅ Good: Test new components
class TestRobotMovement(unittest.TestCase):
    def test_robot_movement(self):
        robot = Robot("r1", 0, 0)
        robot.move_to(5, 5)
        self.assertEqual(robot.target_x, 5)
        self.assertEqual(robot.target_y, 5)
    
    def test_robot_collision(self):
        # Test collision detection
        pass
```

## Future Phase Considerations

### Phase 4: Visualization
- **UI Integration**: Connect simulation to visualization system
- **Real-time Updates**: Stream simulation state to UI
- **User Interaction**: Handle user input and commands

### Phase 5: Advanced Features
- **Machine Learning**: AI-driven robot behavior
- **Optimization**: Advanced pathfinding and scheduling
- **Scalability**: Support for multiple warehouses

### Phase 6: Production Features
- **Persistence**: Save/load simulation state
- **Networking**: Multi-user simulation
- **Analytics**: Advanced performance analysis

## Best Practices

1. **Modularity**: Keep components loosely coupled
2. **Event-Driven**: Use events for all communication
3. **Configuration**: Make everything configurable
4. **Performance**: Monitor and optimize performance
5. **Testing**: Write comprehensive tests
6. **Documentation**: Document all new features
7. **Error Handling**: Implement robust error handling
8. **Extensibility**: Design for future expansion

## Conclusion

The Roibot simulation system provides a solid foundation for building complex warehouse simulations. By following these extension points and integration guidelines, new features can be added systematically while maintaining the system's performance, reliability, and extensibility.

For questions or assistance with integration, refer to the API documentation and test examples provided in the codebase. 