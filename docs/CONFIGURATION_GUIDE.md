# ⚙️ Configuration Guide for Bidirectional Navigation

## Overview

This guide provides detailed information about configuring the bidirectional navigation system, including timing settings, performance monitoring, and debugging options.

## Configuration File Location

The bidirectional navigation configuration is stored in `config/simulation.json` under the `simulation.bidirectional_navigation` section.

## Configuration Structure

```json
{
  "simulation": {
    "bidirectional_navigation": {
      "aisle_traversal_time": 7.0,
      "direction_change_cooldown": 0.5,
      "path_optimization": {
        "enable_shortest_path": true,
        "enable_direction_optimization": true,
        "enable_snake_pattern_integrity": true,
        "max_path_calculation_time": 0.1
      },
      "performance_monitoring": {
        "enable_path_calculation_timing": true,
        "enable_direction_change_tracking": true,
        "enable_movement_efficiency_tracking": true,
        "performance_warning_threshold": 0.05
      },
      "debugging": {
        "enable_path_visualization": false,
        "enable_direction_debug": false,
        "enable_timing_debug": false,
        "log_level": "info"
      }
    }
  }
}
```

## Timing Settings

### Aisle Traversal Time

**Parameter:** `aisle_traversal_time`  
**Type:** float  
**Default:** 7.0  
**Unit:** seconds  
**Range:** 1.0 - 60.0  

**Description:** The time it takes for the robot to traverse one complete aisle (from one end to the other).

**Usage Examples:**
- **Fast movement:** `3.0` - Robot moves quickly through aisles
- **Normal movement:** `7.0` - Standard warehouse operation speed
- **Slow movement:** `15.0` - Cautious movement for safety

**Impact:**
- Affects overall simulation speed
- Influences order completion times
- Determines robot movement realism

### Direction Change Cooldown

**Parameter:** `direction_change_cooldown`  
**Type:** float  
**Default:** 0.5  
**Unit:** seconds  
**Range:** 0.0 - 5.0  

**Description:** Minimum time required between direction changes to prevent rapid switching.

**Usage Examples:**
- **No cooldown:** `0.0` - Immediate direction changes (not recommended)
- **Quick changes:** `0.2` - Fast direction switching
- **Normal changes:** `0.5` - Standard cooldown period
- **Slow changes:** `1.0` - Conservative direction changes

**Impact:**
- Prevents unrealistic rapid direction changes
- Affects path smoothness
- Influences robot behavior realism

## Path Optimization Settings

### Enable Shortest Path

**Parameter:** `enable_shortest_path`  
**Type:** boolean  
**Default:** true  

**Description:** Enables calculation of shortest paths between coordinates.

**Usage:**
- **Enabled (true):** Robot follows optimal paths
- **Disabled (false):** Robot may take longer routes

### Enable Direction Optimization

**Parameter:** `enable_direction_optimization`  
**Type:** boolean  
**Default:** true  

**Description:** Enables intelligent direction choice based on path efficiency.

**Usage:**
- **Enabled (true):** Robot chooses optimal direction
- **Disabled (false):** Robot uses fixed direction rules

### Enable Snake Pattern Integrity

**Parameter:** `enable_snake_pattern_integrity`  
**Type:** boolean  
**Default:** true  

**Description:** Enforces snake pattern rules (odd aisles left→right, even aisles right→left).

**Usage:**
- **Enabled (true):** Maintains warehouse traffic flow
- **Disabled (false):** Allows any movement pattern

### Max Path Calculation Time

**Parameter:** `max_path_calculation_time`  
**Type:** float  
**Default:** 0.1  
**Unit:** seconds  
**Range:** 0.01 - 1.0  

**Description:** Maximum time allowed for path calculation to prevent performance issues.

**Usage Examples:**
- **Fast calculation:** `0.05` - Quick path finding
- **Normal calculation:** `0.1` - Standard calculation time
- **Thorough calculation:** `0.5` - More detailed path analysis

## Performance Monitoring Settings

### Enable Path Calculation Timing

**Parameter:** `enable_path_calculation_timing`  
**Type:** boolean  
**Default:** true  

**Description:** Tracks time spent calculating paths for performance analysis.

**Usage:**
- **Enabled (true):** Monitor path calculation performance
- **Disabled (false):** Skip timing measurements

### Enable Direction Change Tracking

**Parameter:** `enable_direction_change_tracking`  
**Type:** boolean  
**Default:** true  

**Description:** Tracks direction changes for analysis and debugging.

**Usage:**
- **Enabled (true):** Monitor direction change patterns
- **Disabled (false):** Skip direction tracking

### Enable Movement Efficiency Tracking

**Parameter:** `enable_movement_efficiency_tracking`  
**Type:** boolean  
**Default:** true  

**Description:** Tracks movement efficiency (actual vs optimal distance).

**Usage:**
- **Enabled (true):** Monitor movement efficiency
- **Disabled (false):** Skip efficiency calculations

### Performance Warning Threshold

**Parameter:** `performance_warning_threshold`  
**Type:** float  
**Default:** 0.05  
**Unit:** seconds  
**Range:** 0.01 - 1.0  

**Description:** Threshold for performance warnings (e.g., slow path calculations).

**Usage Examples:**
- **Strict monitoring:** `0.01` - Warn on any delay
- **Normal monitoring:** `0.05` - Standard warning threshold
- **Relaxed monitoring:** `0.1` - Only warn on significant delays

## Debugging Settings

### Enable Path Visualization

**Parameter:** `enable_path_visualization`  
**Type:** boolean  
**Default:** false  

**Description:** Enables visual representation of calculated paths.

**Usage:**
- **Enabled (true):** Show path visualization (may impact performance)
- **Disabled (false):** Skip visual path display

### Enable Direction Debug

**Parameter:** `enable_direction_debug`  
**Type:** boolean  
**Default:** false  

**Description:** Enables detailed logging for direction changes.

**Usage:**
- **Enabled (true):** Detailed direction change logging
- **Disabled (false):** Minimal direction logging

### Enable Timing Debug

**Parameter:** `enable_timing_debug`  
**Type:** boolean  
**Default:** false  

**Description:** Enables detailed timing analysis and logging.

**Usage:**
- **Enabled (true):** Detailed timing information
- **Disabled (false):** Basic timing only

### Log Level

**Parameter:** `log_level`  
**Type:** string  
**Default:** "info"  
**Options:** "debug", "info", "warning", "error"  

**Description:** Controls the verbosity of logging output.

**Usage:**
- **Debug:** `"debug"` - Maximum detail for development
- **Info:** `"info"` - Standard operational information
- **Warning:** `"warning"` - Only warnings and errors
- **Error:** `"error"` - Only error messages

## Configuration Profiles

### Development Profile

```json
{
  "aisle_traversal_time": 3.0,
  "direction_change_cooldown": 0.2,
  "path_optimization": {
    "enable_shortest_path": true,
    "enable_direction_optimization": true,
    "enable_snake_pattern_integrity": true,
    "max_path_calculation_time": 0.5
  },
  "performance_monitoring": {
    "enable_path_calculation_timing": true,
    "enable_direction_change_tracking": true,
    "enable_movement_efficiency_tracking": true,
    "performance_warning_threshold": 0.01
  },
  "debugging": {
    "enable_path_visualization": true,
    "enable_direction_debug": true,
    "enable_timing_debug": true,
    "log_level": "debug"
  }
}
```

### Production Profile

```json
{
  "aisle_traversal_time": 7.0,
  "direction_change_cooldown": 0.5,
  "path_optimization": {
    "enable_shortest_path": true,
    "enable_direction_optimization": true,
    "enable_snake_pattern_integrity": true,
    "max_path_calculation_time": 0.1
  },
  "performance_monitoring": {
    "enable_path_calculation_timing": true,
    "enable_direction_change_tracking": true,
    "enable_movement_efficiency_tracking": true,
    "performance_warning_threshold": 0.05
  },
  "debugging": {
    "enable_path_visualization": false,
    "enable_direction_debug": false,
    "enable_timing_debug": false,
    "log_level": "info"
  }
}
```

### Performance Testing Profile

```json
{
  "aisle_traversal_time": 1.0,
  "direction_change_cooldown": 0.0,
  "path_optimization": {
    "enable_shortest_path": true,
    "enable_direction_optimization": true,
    "enable_snake_pattern_integrity": false,
    "max_path_calculation_time": 1.0
  },
  "performance_monitoring": {
    "enable_path_calculation_timing": true,
    "enable_direction_change_tracking": true,
    "enable_movement_efficiency_tracking": true,
    "performance_warning_threshold": 0.001
  },
  "debugging": {
    "enable_path_visualization": false,
    "enable_direction_debug": true,
    "enable_timing_debug": true,
    "log_level": "debug"
  }
}
```

## Configuration Validation

The system automatically validates configuration values:

### Validation Rules

1. **Aisle Traversal Time:**
   - Must be positive (> 0)
   - Must be reasonable (< 60 seconds)

2. **Direction Change Cooldown:**
   - Must be non-negative (≥ 0)
   - Must be reasonable (< 5 seconds)

3. **Max Path Calculation Time:**
   - Must be positive (> 0)
   - Must be reasonable (< 1 second)

4. **Performance Warning Threshold:**
   - Must be positive (> 0)
   - Must be reasonable (< 1 second)

5. **Log Level:**
   - Must be one of: "debug", "info", "warning", "error"

### Validation Errors

If validation fails, the system will:
1. Log error messages
2. Use default values
3. Continue operation with safe defaults

## Runtime Configuration Updates

Configuration can be updated at runtime:

```python
from core.config.bidirectional_config import get_bidirectional_config

config_manager = get_bidirectional_config()

# Update timing settings
config_manager.config.aisle_traversal_time = 5.0
config_manager.config.direction_change_cooldown = 0.3

# Validate changes
if config_manager.validate_configuration():
    print("Configuration updated successfully")
else:
    print("Configuration validation failed")
```

## Performance Impact

### High Performance Impact Settings

- `enable_path_visualization: true` - Visual rendering overhead
- `log_level: "debug"` - Extensive logging
- `max_path_calculation_time: 1.0` - Long calculation times
- `performance_warning_threshold: 0.001` - Frequent warnings

### Low Performance Impact Settings

- `enable_path_visualization: false` - No visual overhead
- `log_level: "error"` - Minimal logging
- `max_path_calculation_time: 0.05` - Quick calculations
- `performance_warning_threshold: 0.1` - Few warnings

## Troubleshooting

### Common Issues

1. **Slow Performance:**
   - Reduce `max_path_calculation_time`
   - Disable path visualization
   - Use higher log level

2. **Frequent Warnings:**
   - Increase `performance_warning_threshold`
   - Check system resources
   - Optimize path calculation algorithms

3. **Configuration Errors:**
   - Validate configuration values
   - Check JSON syntax
   - Use default values as fallback

### Debug Commands

```python
# Check current configuration
from core.config.bidirectional_config import get_bidirectional_config
config = get_bidirectional_config()
print(config.get_configuration_summary())

# Validate configuration
if config.validate_configuration():
    print("Configuration is valid")
else:
    print("Configuration has errors")

# Test timing settings
print(f"Aisle traversal time: {config.get_aisle_traversal_time()}")
print(f"Direction change cooldown: {config.get_direction_change_cooldown()}")
```

## Best Practices

### Timing Configuration

1. **Start with Defaults:** Use default values for initial setup
2. **Test Incrementally:** Make small changes and test
3. **Monitor Performance:** Watch for performance warnings
4. **Document Changes:** Keep track of configuration changes

### Performance Monitoring

1. **Enable Monitoring:** Always enable performance monitoring in production
2. **Set Appropriate Thresholds:** Use realistic warning thresholds
3. **Review Logs:** Regularly check performance logs
4. **Optimize Gradually:** Make performance improvements incrementally

### Debugging

1. **Use Debug Mode Sparingly:** Debug mode impacts performance
2. **Enable Specific Features:** Only enable needed debugging features
3. **Monitor Log Levels:** Use appropriate log levels for environment
4. **Clear Debug Data:** Clear debug data periodically

---

*This configuration guide is maintained as part of the Roibot warehouse simulation project. For questions or contributions, please refer to the project guidelines.* 