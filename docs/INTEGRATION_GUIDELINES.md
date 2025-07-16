# 🔗 Integration Guidelines for Future Phases

## Overview

This document provides specific guidelines for integrating new features and components into the Roibot simulation system. It covers best practices, common patterns, and step-by-step instructions for Phase 2 and beyond.

## Phase 2: Robot Movement & Navigation

### Step 1: Robot Entity Creation

#### Create Robot Class
```python
# entities/robot.py
from typing import Dict, Any, Tuple, Optional
import time

class Robot:
    """
    Robot entity for warehouse simulation.
    
    Represents a single robot in the warehouse with movement capabilities,
    state management, and event emission.
    """
    
    def __init__(self, robot_id: str, x: float, y: float, speed: float = 2.0):
        self.robot_id = robot_id
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = speed
        self.state = "idle"
        self.battery = 100.0
        self.last_update = time.time()
    
    def move_to(self, target_x: float, target_y: float):
        """Set movement target for robot."""
        self.target_x = target_x
        self.target_y = target_y
        self.state = "moving"
    
    def update(self, delta_time: float) -> Dict[str, Any]:
        """Update robot state and return current state."""
        if self.state == "moving":
            self._update_movement(delta_time)
        
        return self.get_state()
    
    def _update_movement(self, delta_time: float):
        """Update robot movement towards target."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 0.1:  # Close enough to target
            self.x = self.target_x
            self.y = self.target_y
            self.state = "idle"
        else:
            # Move towards target
            move_distance = self.speed * delta_time
            if move_distance > distance:
                move_distance = distance
            
            ratio = move_distance / distance
            self.x += dx * ratio
            self.y += dy * ratio
    
    def get_state(self) -> Dict[str, Any]:
        """Get current robot state."""
        return {
            "robot_id": self.robot_id,
            "x": self.x,
            "y": self.y,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "speed": self.speed,
            "state": self.state,
            "battery": self.battery
        }
```

#### Create Robot Manager
```python
# entities/robot_manager.py
from typing import Dict, List
from .robot import Robot
from core.events import EventSystem, EventType

class RobotManager:
    """
    Manages all robots in the simulation.
    
    Handles robot creation, updates, and event emission for robot-related
    activities like movement and collisions.
    """
    
    def __init__(self, event_system: EventSystem):
        self.robots: Dict[str, Robot] = {}
        self.event_system = event_system
    
    def add_robot(self, robot: Robot):
        """Add a robot to the manager."""
        self.robots[robot.robot_id] = robot
        
        # Emit robot added event
        asyncio.create_task(self.event_system.emit(EventType.ROBOT_ADDED, {
            "robot_id": robot.robot_id,
            "position": (robot.x, robot.y)
        }))
    
    def remove_robot(self, robot_id: str):
        """Remove a robot from the manager."""
        if robot_id in self.robots:
            del self.robots[robot_id]
            
            # Emit robot removed event
            asyncio.create_task(self.event_system.emit(EventType.ROBOT_REMOVED, {
                "robot_id": robot_id
            }))
    
    async def update_all(self, delta_time: float):
        """Update all robots and emit events."""
        for robot in self.robots.values():
            # Update robot
            robot.update(delta_time)
            
            # Emit movement event if robot moved
            if robot.state == "moving":
                await self.event_system.emit(EventType.ROBOT_MOVE, {
                    "robot_id": robot.robot_id,
                    "position": (robot.x, robot.y),
                    "target": (robot.target_x, robot.target_y),
                    "speed": robot.speed
                })
    
    def get_robot(self, robot_id: str) -> Optional[Robot]:
        """Get robot by ID."""
        return self.robots.get(robot_id)
    
    def get_all_robots(self) -> List[Robot]:
        """Get all robots."""
        return list(self.robots.values())
    
    def get_robot_count(self) -> int:
        """Get total number of robots."""
        return len(self.robots)
```

### Step 2: Event System Extension

#### Add New Event Types
```python
# core/events.py - Add to EventType enum
class EventType(Enum):
    # Existing events...
    SIMULATION_START = "simulation_start"
    SIMULATION_STOP = "simulation_stop"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_RESUME = "simulation_resume"
    FRAME_UPDATE = "frame_update"
    TICK = "tick"
    
    # New robot events
    ROBOT_ADDED = "robot_added"
    ROBOT_REMOVED = "robot_removed"
    ROBOT_MOVE = "robot_move"
    ROBOT_COLLISION = "robot_collision"
    ROBOT_BATTERY_LOW = "robot_battery_low"
    
    # Pathfinding events
    PATHFINDING_REQUEST = "pathfinding_request"
    PATHFINDING_RESULT = "pathfinding_result"
    PATHFINDING_FAILED = "pathfinding_failed"
```

### Step 3: Configuration Extension

#### Add Robot Configuration
```python
# core/config.py - Add to existing configuration
class RobotConfiguration:
    """Configuration for robot behavior and capabilities."""
    
    def __init__(self):
        self.SPEED = 2.0
        self.ACCELERATION = 1.0
        self.DECELERATION = 1.0
        self.BATTERY_CAPACITY = 100.0
        self.CHARGE_RATE = 10.0
        self.DISCHARGE_RATE = 1.0
        self.COLLISION_DISTANCE = 0.5
        self.MAX_ROBOTS = 10

# Add to ConfigurationManager
def load_configuration(self):
    # Existing configuration loading...
    
    # Add robot configuration
    self.robot = RobotConfiguration()
    self._validate_robot_config()

def _validate_robot_config(self):
    """Validate robot configuration."""
    if not (0.5 <= self.robot.SPEED <= 10.0):
        raise ConfigurationError("Robot speed must be between 0.5 and 10.0")
    
    if not (50.0 <= self.robot.BATTERY_CAPACITY <= 500.0):
        raise ConfigurationError("Battery capacity must be between 50.0 and 500.0")
    
    if self.robot.DECELERATION > self.robot.ACCELERATION:
        raise ConfigurationError("Deceleration cannot exceed acceleration")
```

### Step 4: Integration with Simulation Engine

#### Update Simulation Engine
```python
# core/engine.py - Add to SimulationEngine class
def __init__(self):
    # Existing initialization...
    
    # Add robot manager
    self.robot_manager = None

async def load_config(self):
    # Existing configuration loading...
    
    # Initialize robot manager
    self.robot_manager = RobotManager(self.event_system)
    
    # Register robot manager as component
    self.state.register_component("robot_manager")

async def _update_components(self, delta_time: float):
    """Update all simulation components."""
    # Existing component updates...
    
    # Update robot manager
    if self.robot_manager:
        await self.robot_manager.update_all(delta_time)
```

### Step 5: Performance Monitoring Integration

#### Extend Performance Metrics
```python
# utils/performance.py - Update PerformanceMetrics
@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    frame_time: float
    fps: float
    event_processing_time: float
    component_update_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    event_queue_size: int
    timestamp: float
    # New metrics for Phase 2
    robot_update_time: float = 0.0
    pathfinding_time: float = 0.0
    collision_check_time: float = 0.0

# Update SimulationEngine to record new metrics
async def _main_loop(self):
    # Existing loop logic...
    
    # Update robot manager with timing
    robot_start = time.time()
    if self.robot_manager:
        await self.robot_manager.update_all(delta_time)
    robot_time = time.time() - robot_start
    
    # Record extended metrics
    self.performance_benchmark.record_metrics(
        frame_time=frame_time,
        fps=self.state.current_fps,
        event_processing_time=event_time,
        component_update_time=component_time,
        event_queue_size=queue_size,
        robot_update_time=robot_time  # New metric
    )
```

## Phase 3: Order Management

### Step 1: Order Entity Creation

#### Create Order Class
```python
# entities/order.py
from typing import List, Dict, Any
import time
import uuid

class Order:
    """
    Order entity for warehouse simulation.
    
    Represents a customer order with items, priority, and status tracking.
    """
    
    def __init__(self, items: List[str], priority: int = 1):
        self.order_id = str(uuid.uuid4())
        self.items = items
        self.priority = priority
        self.status = "pending"
        self.assigned_robot = None
        self.created_time = time.time()
        self.completed_time = None
    
    def assign_to_robot(self, robot_id: str):
        """Assign order to a robot."""
        self.assigned_robot = robot_id
        self.status = "assigned"
    
    def complete(self):
        """Mark order as completed."""
        self.status = "completed"
        self.completed_time = time.time()
    
    def get_processing_time(self) -> float:
        """Get total processing time."""
        if self.completed_time:
            return self.completed_time - self.created_time
        return time.time() - self.created_time
    
    def get_state(self) -> Dict[str, Any]:
        """Get current order state."""
        return {
            "order_id": self.order_id,
            "items": self.items,
            "priority": self.priority,
            "status": self.status,
            "assigned_robot": self.assigned_robot,
            "created_time": self.created_time,
            "completed_time": self.completed_time
        }
```

#### Create Order Manager
```python
# entities/order_manager.py
from typing import Dict, List, Optional
from .order import Order
from core.events import EventSystem, EventType
import random

class OrderManager:
    """
    Manages order generation and processing.
    
    Handles order creation, assignment, and completion tracking.
    """
    
    def __init__(self, event_system: EventSystem, config):
        self.orders: Dict[str, Order] = {}
        self.event_system = event_system
        self.config = config
        self.generation_timer = 0.0
        self.order_counter = 0
    
    async def update(self, delta_time: float):
        """Update order manager."""
        self.generation_timer += delta_time
        
        # Generate new orders based on interval
        if self.generation_timer >= self.config.order.GENERATION_INTERVAL:
            await self._generate_order()
            self.generation_timer = 0.0
    
    async def _generate_order(self):
        """Generate a new random order."""
        # Create random items
        item_count = random.randint(1, self.config.order.MAX_ITEMS)
        items = [f"item_{random.randint(1, 100)}" for _ in range(item_count)]
        
        # Assign priority based on weights
        priority = self._assign_priority()
        
        # Create order
        order = Order(items, priority)
        self.orders[order.order_id] = order
        
        # Emit order created event
        await self.event_system.emit(EventType.ORDER_CREATED, {
            "order_id": order.order_id,
            "items": order.items,
            "priority": order.priority
        })
    
    def _assign_priority(self) -> int:
        """Assign priority based on configuration weights."""
        weights = self.config.order.PRIORITY_WEIGHTS
        rand = random.random()
        
        if rand < weights[0]:
            return 1  # High priority
        elif rand < weights[0] + weights[1]:
            return 2  # Medium priority
        else:
            return 3  # Low priority
    
    def assign_order_to_robot(self, order_id: str, robot_id: str):
        """Assign an order to a robot."""
        if order_id in self.orders:
            self.orders[order_id].assign_to_robot(robot_id)
            
            # Emit assignment event
            asyncio.create_task(self.event_system.emit(EventType.ORDER_ASSIGNED, {
                "order_id": order_id,
                "robot_id": robot_id
            }))
    
    def complete_order(self, order_id: str):
        """Mark an order as completed."""
        if order_id in self.orders:
            self.orders[order_id].complete()
            
            # Emit completion event
            asyncio.create_task(self.event_system.emit(EventType.ORDER_COMPLETED, {
                "order_id": order_id,
                "processing_time": self.orders[order_id].get_processing_time()
            }))
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return [order for order in self.orders.values() if order.status == "pending"]
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
```

### Step 2: Event System Extension

#### Add Order Events
```python
# core/events.py - Add to EventType enum
class EventType(Enum):
    # Existing events...
    
    # Order events
    ORDER_CREATED = "order_created"
    ORDER_ASSIGNED = "order_assigned"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
```

## Testing Guidelines

### Unit Testing
```python
# tests/test_robot.py
import unittest
from entities.robot import Robot

class TestRobot(unittest.TestCase):
    def setUp(self):
        self.robot = Robot("r1", 0, 0)
    
    def test_robot_initialization(self):
        """Test robot initialization."""
        self.assertEqual(self.robot.robot_id, "r1")
        self.assertEqual(self.robot.x, 0)
        self.assertEqual(self.robot.y, 0)
        self.assertEqual(self.robot.state, "idle")
    
    def test_robot_movement(self):
        """Test robot movement."""
        self.robot.move_to(5, 5)
        self.assertEqual(self.robot.target_x, 5)
        self.assertEqual(self.robot.target_y, 5)
        self.assertEqual(self.robot.state, "moving")
    
    def test_robot_state(self):
        """Test robot state retrieval."""
        state = self.robot.get_state()
        self.assertIn("robot_id", state)
        self.assertIn("x", state)
        self.assertIn("y", state)
        self.assertIn("state", state)
```

### Integration Testing
```python
# tests/test_integration.py
import asyncio
import unittest
from core.engine import SimulationEngine
from entities.robot import Robot
from entities.robot_manager import RobotManager

class TestRobotIntegration(unittest.TestCase):
    async def test_robot_integration(self):
        """Test robot integration with simulation engine."""
        engine = SimulationEngine()
        await engine.load_config()
        
        # Add robot
        robot = Robot("r1", 0, 0)
        engine.robot_manager.add_robot(robot)
        
        # Start simulation
        await engine.start()
        
        # Run for a short time
        await asyncio.sleep(0.1)
        
        # Check robot was added
        self.assertEqual(engine.robot_manager.get_robot_count(), 1)
        
        await engine.stop()
```

## Performance Considerations

### Memory Management
- Use object pooling for frequently created/destroyed objects
- Implement proper cleanup in component destructors
- Monitor memory usage with performance metrics

### Event System Optimization
- Use event filtering to reduce unnecessary processing
- Implement event batching for high-frequency events
- Monitor event queue size and processing time

### Update Frequency
- Consider different update frequencies for different components
- Use delta time for frame-independent updates
- Implement update skipping for distant objects

## Error Handling

### Robot Errors
```python
class RobotError(Exception):
    """Base exception for robot-related errors."""
    pass

class CollisionError(RobotError):
    """Raised when robots collide."""
    pass

class BatteryError(RobotError):
    """Raised when robot battery is depleted."""
    pass

# In robot update method
def update(self, delta_time: float):
    try:
        # Update logic
        pass
    except CollisionError as e:
        # Handle collision
        self.state = "collision"
        raise
    except BatteryError as e:
        # Handle battery depletion
        self.state = "charging"
        raise
```

### Order Errors
```python
class OrderError(Exception):
    """Base exception for order-related errors."""
    pass

class OrderAssignmentError(OrderError):
    """Raised when order assignment fails."""
    pass

# In order manager
def assign_order_to_robot(self, order_id: str, robot_id: str):
    if order_id not in self.orders:
        raise OrderAssignmentError(f"Order {order_id} not found")
    
    if self.orders[order_id].status != "pending":
        raise OrderAssignmentError(f"Order {order_id} is not pending")
    
    # Proceed with assignment
    self.orders[order_id].assign_to_robot(robot_id)
```

## Configuration Best Practices

### Validation
- Always validate configuration on load
- Provide sensible defaults for all parameters
- Use type checking for configuration values

### Documentation
- Document all configuration parameters
- Provide examples for common configurations
- Include validation rules in documentation

### Extensibility
- Use consistent naming conventions
- Group related parameters in sections
- Design for future parameter additions

## Conclusion

Following these integration guidelines ensures that new features are added systematically and maintain the system's performance, reliability, and extensibility. Always test thoroughly and monitor performance when adding new components.

For additional assistance, refer to the API documentation and existing test examples in the codebase. 