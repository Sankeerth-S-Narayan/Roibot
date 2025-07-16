# ⚙️ Configuration Guide

## Overview

The Roibot simulation system uses a JSON-based configuration system that provides flexible and extensible settings for all simulation parameters. The configuration is validated on load to ensure all values are within acceptable ranges.

## Configuration File Location

The main configuration file is located at:
```
config/simulation.json
```

## Configuration Structure

### Root Configuration
```json
{
  "timing": { ... },
  "warehouse": { ... },
  "robot": { ... },
  "order": { ... },
  "engine": { ... }
}
```

## Timing Configuration

Controls simulation timing and frame rate settings.

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `TARGET_FPS` | int | 60 | 1-120 | Target frames per second |
| `SIMULATION_SPEED` | float | 1.0 | 0.1-10.0 | Simulation speed multiplier |
| `FRAME_INTERVAL` | float | 0.0167 | Calculated | Time per frame (1/TARGET_FPS) |

### Example
```json
{
  "timing": {
    "TARGET_FPS": 60,
    "SIMULATION_SPEED": 1.0,
    "FRAME_INTERVAL": 0.0167
  }
}
```

### Validation Rules
- `TARGET_FPS` must be between 1 and 120
- `SIMULATION_SPEED` must be between 0.1 and 10.0
- `FRAME_INTERVAL` is automatically calculated from `TARGET_FPS`

## Warehouse Configuration

Defines the warehouse layout and dimensions.

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `WIDTH` | int | 25 | 10-100 | Warehouse width in cells |
| `HEIGHT` | int | 20 | 10-100 | Warehouse height in cells |
| `CELL_SIZE` | float | 1.0 | 0.5-5.0 | Size of each cell in units |

### Example
```json
{
  "warehouse": {
    "WIDTH": 25,
    "HEIGHT": 20,
    "CELL_SIZE": 1.0
  }
}
```

### Validation Rules
- `WIDTH` and `HEIGHT` must be between 10 and 100
- `CELL_SIZE` must be between 0.5 and 5.0
- Total warehouse area must not exceed 10,000 cells

## Robot Configuration

Defines robot movement and behavior parameters.

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `SPEED` | float | 2.0 | 0.5-10.0 | Robot movement speed (units/second) |
| `ACCELERATION` | float | 1.0 | 0.1-5.0 | Robot acceleration rate |
| `DECELERATION` | float | 1.0 | 0.1-5.0 | Robot deceleration rate |

### Example
```json
{
  "robot": {
    "SPEED": 2.0,
    "ACCELERATION": 1.0,
    "DECELERATION": 1.0
  }
}
```

### Validation Rules
- `SPEED` must be between 0.5 and 10.0 units/second
- `ACCELERATION` and `DECELERATION` must be between 0.1 and 5.0
- Deceleration should not exceed acceleration for safety

## Order Configuration

Defines order generation and processing parameters.

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `GENERATION_INTERVAL` | int | 40 | 10-300 | Seconds between order generation |
| `MAX_ITEMS` | int | 4 | 1-10 | Maximum items per order |
| `PRIORITY_WEIGHTS` | array | [0.6, 0.3, 0.1] | 0.0-1.0 | Priority distribution weights |

### Example
```json
{
  "order": {
    "GENERATION_INTERVAL": 40,
    "MAX_ITEMS": 4,
    "PRIORITY_WEIGHTS": [0.6, 0.3, 0.1]
  }
}
```

### Validation Rules
- `GENERATION_INTERVAL` must be between 10 and 300 seconds
- `MAX_ITEMS` must be between 1 and 10
- `PRIORITY_WEIGHTS` must sum to 1.0 and contain 3 values

## Engine Configuration

Defines engine-specific settings and performance parameters.

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `event_queue_size` | int | 1000 | 100-10000 | Maximum event queue size |
| `max_concurrent_events` | int | 50 | 10-200 | Maximum concurrent event processing |
| `debug_prints` | bool | true | true/false | Enable debug print statements |

### Example
```json
{
  "engine": {
    "event_queue_size": 1000,
    "max_concurrent_events": 50,
    "debug_prints": true
  }
}
```

### Validation Rules
- `event_queue_size` must be between 100 and 10000
- `max_concurrent_events` must be between 10 and 200
- `debug_prints` must be a boolean value

## Configuration Loading

### Automatic Loading
The configuration is automatically loaded when the simulation engine starts:

```python
engine = SimulationEngine()
await engine.load_config()  # Loads config/simulation.json
```

### Manual Loading
You can also load configuration manually:

```python
from core.config import ConfigurationManager

config_manager = ConfigurationManager()
config_manager.load_configuration()
```

### Configuration Validation
All configuration values are validated on load:

```python
# Valid configuration
config = {
    "timing": {"TARGET_FPS": 60},
    "warehouse": {"WIDTH": 25, "HEIGHT": 20}
}

# Invalid configuration (will raise ConfigurationError)
config = {
    "timing": {"TARGET_FPS": 200}  # Exceeds maximum
}
```

## Configuration Reloading

The configuration can be reloaded at runtime:

```python
await engine.reload_config()  # Reloads and applies new settings
```

### Hot Reloading
Some configuration changes take effect immediately:
- Timing settings (FPS, speed)
- Engine settings (queue size, debug prints)

Other changes require restart:
- Warehouse dimensions
- Robot/order parameters (in future phases)

## Configuration Constants

The system uses predefined constants for validation:

### SimulationTimingConstants
- `MIN_FPS`: 1
- `MAX_FPS`: 120
- `MIN_SPEED`: 0.1
- `MAX_SPEED`: 10.0

### WarehouseConstants
- `MIN_WIDTH`: 10
- `MAX_WIDTH`: 100
- `MIN_HEIGHT`: 10
- `MAX_HEIGHT`: 100
- `MIN_CELL_SIZE`: 0.5
- `MAX_CELL_SIZE`: 5.0

### RobotConstants
- `MIN_SPEED`: 0.5
- `MAX_SPEED`: 10.0
- `MIN_ACCELERATION`: 0.1
- `MAX_ACCELERATION`: 5.0

### OrderConstants
- `MIN_GENERATION_INTERVAL`: 10
- `MAX_GENERATION_INTERVAL`: 300
- `MIN_ITEMS`: 1
- `MAX_ITEMS`: 10

## Error Handling

### ConfigurationError
Raised when configuration validation fails:

```python
try:
    config_manager.load_configuration()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Common Validation Errors
- **Invalid FPS**: Must be between 1 and 120
- **Invalid speed**: Must be between 0.1 and 10.0
- **Invalid dimensions**: Warehouse size must be reasonable
- **Missing required fields**: All sections must be present
- **Type errors**: Values must match expected types

## Best Practices

### Performance Optimization
- Use `TARGET_FPS` of 60 for smooth animations
- Keep `event_queue_size` reasonable (1000-2000)
- Enable `debug_prints` only during development

### Safety Considerations
- Ensure `DECELERATION` <= `ACCELERATION`
- Keep warehouse dimensions manageable
- Use reasonable order generation intervals

### Extensibility
- Add new configuration sections for future features
- Use consistent naming conventions
- Provide sensible defaults for all parameters

## Future Extensions

The configuration system is designed to be extensible for future phases:

### Phase 2: Robot Movement
- Robot pathfinding algorithms
- Collision detection settings
- Battery management parameters

### Phase 3: Order Management
- Order priority systems
- Inventory management
- Order fulfillment strategies

### Phase 4: Visualization
- Display settings
- UI configuration
- Animation parameters 