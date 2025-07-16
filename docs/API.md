# 🚀 Roibot Simulation Engine API Documentation

## Overview

The Roibot Simulation Engine provides a comprehensive framework for warehouse robot simulation with real-time performance monitoring, event-driven architecture, and extensible configuration management.

## Core Components

### SimulationEngine

The main simulation engine that coordinates all components and manages the simulation lifecycle.

#### Constructor
```python
SimulationEngine()
```
Creates a new simulation engine instance with default settings.

#### Methods

##### `async load_config() -> None`
Loads configuration and initializes all components.
- **Effects**: Initializes timing manager, event system, and state management
- **Required**: Must be called before starting simulation

##### `async start() -> None`
Starts the simulation engine.
- **Effects**: Begins simulation loop, starts all components
- **Prerequisites**: Configuration must be loaded
- **Events**: Emits `SIMULATION_START` event

##### `async stop() -> None`
Stops the simulation engine.
- **Effects**: Stops simulation loop, cleans up components
- **Events**: Emits `SIMULATION_STOP` event with statistics

##### `async pause() -> None`
Pauses the simulation.
- **Effects**: Pauses timing and state updates
- **Prerequisites**: Simulation must be running
- **Events**: Emits `SIMULATION_PAUSE` event

##### `async resume() -> None`
Resumes the simulation.
- **Effects**: Resumes timing and state updates
- **Prerequisites**: Simulation must be paused
- **Events**: Emits `SIMULATION_RESUME` event

##### `async run() -> None`
Runs the main simulation loop.
- **Effects**: Starts the main async loop
- **Prerequisites**: Simulation must be started

##### `get_simulation_speed() -> float`
Returns current simulation speed multiplier.
- **Returns**: Speed value (default: 1.0)

##### `set_simulation_speed(speed: float) -> None`
Sets simulation speed multiplier.
- **Parameters**: `speed` - Speed multiplier (0.1 to 10.0)
- **Validation**: Automatically clamps to valid range

##### `get_debug_info() -> Dict[str, Any]`
Returns comprehensive debug information.
- **Returns**: Dictionary with performance, events, timing, and state data

##### `async reload_config() -> None`
Reloads configuration from file.
- **Effects**: Updates all components with new settings

##### `async shutdown() -> None`
Performs clean shutdown.
- **Effects**: Stops simulation and cleans up all resources

### TimingManager

Manages timing for smooth animation and frame rate control.

#### Constructor
```python
TimingManager(target_fps: int = 60)
```
Creates timing manager with specified target FPS.

#### Methods

##### `update() -> float`
Updates timing information for current frame.
- **Returns**: Delta time since last frame
- **Effects**: Updates FPS counter and frame count

##### `get_current_fps() -> float`
Returns current frames per second.
- **Returns**: Current FPS value

##### `async wait_for_next_frame() -> None`
Waits for next frame to maintain target FPS.
- **Effects**: Sleeps if necessary to maintain frame rate

##### `set_simulation_speed(speed: float) -> None`
Sets simulation speed multiplier.
- **Parameters**: `speed` - Speed multiplier

##### `set_target_fps(fps: int) -> None`
Sets target FPS.
- **Parameters**: `fps` - New target FPS

### SimulationState

Manages simulation state and transitions.

#### Constructor
```python
SimulationState()
```
Creates new simulation state instance.

#### Methods

##### `start() -> None`
Starts the simulation state.
- **Effects**: Transitions to STARTING status

##### `stop() -> None`
Stops the simulation state.
- **Effects**: Transitions to STOPPED status

##### `pause() -> None`
Pauses the simulation state.
- **Effects**: Transitions to PAUSED status

##### `resume() -> None`
Resumes the simulation state.
- **Effects**: Transitions to RUNNING status

##### `update(delta_time: float) -> None`
Updates simulation state.
- **Parameters**: `delta_time` - Time elapsed since last update
- **Effects**: Updates simulation time and frame count

##### `is_paused() -> bool`
Checks if simulation is paused.
- **Returns**: True if paused, False otherwise

##### `get_simulation_speed() -> float`
Returns current simulation speed.
- **Returns**: Speed multiplier

##### `set_simulation_speed(speed: float) -> None`
Sets simulation speed.
- **Parameters**: `speed` - Speed multiplier

### EventSystem

Manages event-driven communication between components.

#### Constructor
```python
EventSystem()
```
Creates new event system instance.

#### Methods

##### `async start() -> None`
Starts the event system.
- **Effects**: Initializes event processing

##### `async stop() -> None`
Stops the event system.
- **Effects**: Stops event processing and cleans up

##### `async emit(event_type: EventType, data: Dict[str, Any] = None) -> None`
Emits an event.
- **Parameters**: 
  - `event_type` - Type of event to emit
  - `data` - Optional event data
- **Effects**: Adds event to processing queue

##### `async process_events() -> None`
Processes all pending events.
- **Effects**: Handles all queued events

##### `get_statistics() -> Dict[str, Any]`
Returns event system statistics.
- **Returns**: Dictionary with event counts and queue sizes

### ConfigurationManager

Manages configuration loading and validation.

#### Methods

##### `load_configuration() -> None`
Loads configuration from file.
- **Effects**: Loads and validates configuration

##### `reload_configuration() -> None`
Reloads configuration from file.
- **Effects**: Updates configuration with fresh data

##### `get_value(section: str, key: str, default: Any = None) -> Any`
Gets configuration value.
- **Parameters**:
  - `section` - Configuration section
  - `key` - Configuration key
  - `default` - Default value if not found
- **Returns**: Configuration value

### SimulationController

Provides interactive command interface.

#### Constructor
```python
SimulationController(engine: SimulationEngine)
```
Creates controller for specified engine.

#### Methods

##### `process_command(command: str) -> str`
Processes user command.
- **Parameters**: `command` - User command string
- **Returns**: Response message

##### `get_command_history() -> List[str]`
Returns command history.
- **Returns**: List of previous commands

### SimulationValidator

Validates inputs and provides error handling.

#### Methods

##### `validate_speed(speed: float) -> bool`
Validates simulation speed.
- **Parameters**: `speed` - Speed to validate
- **Returns**: True if valid
- **Raises**: `ValidationError` if invalid

##### `validate_fps_target(fps: int) -> bool`
Validates FPS target.
- **Parameters**: `fps` - FPS to validate
- **Returns**: True if valid
- **Raises**: `ValidationError` if invalid

##### `get_error_summary() -> Dict[str, Any]`
Returns error summary.
- **Returns**: Dictionary with error counts and history

## Event Types

### EventType Enum
- `SIMULATION_START` - Simulation started
- `SIMULATION_STOP` - Simulation stopped
- `SIMULATION_PAUSE` - Simulation paused
- `SIMULATION_RESUME` - Simulation resumed
- `FRAME_UPDATE` - Frame update (every 60 frames)
- `TICK` - Regular tick event

## Configuration Structure

### Timing Configuration
```json
{
  "timing": {
    "TARGET_FPS": 60,
    "SIMULATION_SPEED": 1.0,
    "FRAME_INTERVAL": 0.0167
  }
}
```

### Warehouse Configuration
```json
{
  "warehouse": {
    "WIDTH": 25,
    "HEIGHT": 20,
    "CELL_SIZE": 1.0
  }
}
```

### Robot Configuration
```json
{
  "robot": {
    "SPEED": 2.0,
    "ACCELERATION": 1.0,
    "DECELERATION": 1.0
  }
}
```

### Order Configuration
```json
{
  "order": {
    "GENERATION_INTERVAL": 40,
    "MAX_ITEMS": 4,
    "PRIORITY_WEIGHTS": [0.6, 0.3, 0.1]
  }
}
```

## Performance Monitoring

### PerformanceBenchmark
Provides real-time performance monitoring and grading.

#### Methods
- `start_benchmark()` - Start performance monitoring
- `end_benchmark()` - End performance monitoring
- `record_metrics(...)` - Record frame metrics
- `get_performance_summary()` - Get performance report
- `print_performance_report()` - Print detailed report

### Performance Grades
- **A+**: Excellent performance (90+ score)
- **A**: Good performance (80-89 score)
- **B**: Acceptable performance (70-79 score)
- **C**: Below average (60-69 score)
- **D**: Poor performance (<60 score)

## Error Handling

### ValidationError
Custom exception for validation failures.

### ErrorSeverity Enum
- `INFO` - Informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## Usage Examples

### Basic Simulation Setup
```python
import asyncio
from core.engine import SimulationEngine

async def main():
    # Create engine
    engine = SimulationEngine()
    
    # Load configuration
    await engine.load_config()
    
    # Start simulation
    await engine.start()
    
    # Run for 10 seconds
    await asyncio.sleep(10)
    
    # Stop simulation
    await engine.stop()
    
    # Shutdown
    await engine.shutdown()

asyncio.run(main())
```

### Performance Monitoring
```python
from utils.performance import PerformanceBenchmark

# Create benchmark
benchmark = PerformanceBenchmark()

# Start monitoring
benchmark.start_benchmark()

# Record metrics
benchmark.record_metrics(
    frame_time=0.016,
    fps=60.0,
    event_processing_time=0.001,
    component_update_time=0.002,
    event_queue_size=10
)

# Get performance report
summary = benchmark.get_performance_summary()
print(f"Performance Grade: {summary['performance_grade']}")
```

### Event Handling
```python
from core.events import EventSystem, EventType

# Create event system
event_system = EventSystem()

# Emit event
await event_system.emit(EventType.SIMULATION_START, {
    "timestamp": time.time(),
    "config_loaded": True
})

# Get statistics
stats = event_system.get_statistics()
print(f"Events processed: {stats['event_count']}")
``` 