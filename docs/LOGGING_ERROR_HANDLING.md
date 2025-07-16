# Logging and Error Handling Guide

## Overview

This guide provides comprehensive documentation for logging and error handling in the Order Management System. Proper logging and error handling are critical for maintaining system reliability, debugging issues, and monitoring performance.

## Table of Contents

1. [Logging Configuration](#logging-configuration)
2. [Log Levels and Usage](#log-levels-and-usage)
3. [Error Types and Handling](#error-types-and-handling)
4. [Debugging Strategies](#debugging-strategies)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Performance Logging](#performance-logging)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Logging Configuration

### 1. Basic Logging Setup

```python
import logging
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """Configure logging for the order management system."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create module-specific loggers
    loggers = {
        'order_generator': logging.getLogger('order_generator'),
        'order_queue': logging.getLogger('order_queue'),
        'robot_assigner': logging.getLogger('robot_assigner'),
        'status_tracker': logging.getLogger('status_tracker'),
        'analytics': logging.getLogger('analytics'),
        'performance': logging.getLogger('performance')
    }
    
    return loggers

# Usage
loggers = setup_logging(
    log_level=logging.INFO,
    log_file='order_management.log'
)
```

### 2. Advanced Logging Configuration

```python
import logging.config
import os

def setup_advanced_logging(config_path=None):
    """Setup advanced logging with configuration file."""
    
    # Default configuration
    default_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'logs/order_management.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3
            }
        },
        'loggers': {
            'order_generator': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'order_queue': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'robot_assigner': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'status_tracker': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'analytics': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'performance': {
                'level': 'DEBUG',
                'handlers': ['file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console', 'error_file']
        }
    }
    
    # Load custom configuration if provided
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            custom_config = json.load(f)
            # Merge configurations
            default_config.update(custom_config)
    
    # Apply configuration
    logging.config.dictConfig(default_config)
    
    return logging.getLogger()

# Usage
logger = setup_advanced_logging('config/logging_config.json')
```

### 3. Environment-Specific Logging

```python
import os

def setup_environment_logging():
    """Setup logging based on environment."""
    
    environment = os.getenv('ENVIRONMENT', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    if environment == 'production':
        # Production: Log to files only, minimal console output
        setup_logging(
            log_level=getattr(logging, log_level),
            log_file='logs/production.log',
            console_output=False
        )
    elif environment == 'staging':
        # Staging: Log to files and console
        setup_logging(
            log_level=getattr(logging, log_level),
            log_file='logs/staging.log'
        )
    else:
        # Development: Verbose console output
        setup_logging(
            log_level=getattr(logging, log_level),
            log_file='logs/development.log'
        )
```

## Log Levels and Usage

### 1. Log Level Guidelines

```python
import logging

class OrderManagementLogger:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
    
    def debug(self, message, **kwargs):
        """Log debug information for development."""
        self.logger.debug(f"{message} | {kwargs}")
    
    def info(self, message, **kwargs):
        """Log general information about system operation."""
        self.logger.info(f"{message} | {kwargs}")
    
    def warning(self, message, **kwargs):
        """Log warnings about potential issues."""
        self.logger.warning(f"{message} | {kwargs}")
    
    def error(self, message, error=None, **kwargs):
        """Log errors that don't stop system operation."""
        if error:
            self.logger.error(f"{message} | Error: {error} | {kwargs}")
        else:
            self.logger.error(f"{message} | {kwargs}")
    
    def critical(self, message, error=None, **kwargs):
        """Log critical errors that may stop system operation."""
        if error:
            self.logger.critical(f"{message} | Error: {error} | {kwargs}")
        else:
            self.logger.critical(f"{message} | {kwargs}")

# Usage examples
logger = OrderManagementLogger('order_generator')

# Debug: Detailed information for debugging
logger.debug("Generating order", order_id="order_001", priority="high")

# Info: General operational information
logger.info("Order generated successfully", order_id="order_001", count=1)

# Warning: Potential issues
logger.warning("Queue approaching capacity", current_size=45, max_size=50)

# Error: Issues that don't stop operation
logger.error("Failed to assign order to robot", order_id="order_001", robot_id="robot_001")

# Critical: Serious issues that may stop operation
logger.critical("System out of memory", available_memory="100MB", required_memory="500MB")
```

### 2. Contextual Logging

```python
import logging
from contextlib import contextmanager

class ContextualLogger:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.context = {}
    
    def add_context(self, **kwargs):
        """Add context to all subsequent log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context."""
        self.context.clear()
    
    def log(self, level, message, **kwargs):
        """Log message with context."""
        context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
        kwargs_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        
        full_message = f"{message}"
        if context_str:
            full_message += f" | Context: {context_str}"
        if kwargs_str:
            full_message += f" | {kwargs_str}"
        
        getattr(self.logger, level)(full_message)
    
    @contextmanager
    def operation_context(self, operation_name, **kwargs):
        """Context manager for operation logging."""
        self.add_context(operation=operation_name, **kwargs)
        self.log('info', f"Starting {operation_name}")
        
        try:
            yield
            self.log('info', f"Completed {operation_name}")
        except Exception as e:
            self.log('error', f"Failed {operation_name}", error=str(e))
            raise
        finally:
            self.clear_context()

# Usage
logger = ContextualLogger('order_processing')

# Add context for a session
logger.add_context(session_id="session_001", user_id="user_123")

# Log with context
logger.log('info', "Processing orders", batch_size=10)

# Use operation context
with logger.operation_context("order_generation", count=5):
    # Generate orders
    orders = generate_orders(5)
    logger.log('info', "Orders generated", order_count=len(orders))
```

## Error Types and Handling

### 1. Custom Exception Classes

```python
class OrderManagementError(Exception):
    """Base exception for order management system."""
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class OrderGenerationError(OrderManagementError):
    """Raised when order generation fails."""
    pass

class OrderQueueError(OrderManagementError):
    """Raised when queue operations fail."""
    pass

class RobotAssignmentError(OrderManagementError):
    """Raised when robot assignment fails."""
    pass

class OrderStatusError(OrderManagementError):
    """Raised when status tracking fails."""
    pass

class ConfigurationError(OrderManagementError):
    """Raised when configuration is invalid."""
    pass

class PerformanceError(OrderManagementError):
    """Raised when performance thresholds are exceeded."""
    pass
```

### 2. Error Handling Strategies

```python
import logging
from functools import wraps
import time

class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger
    
    def handle_errors(self, error_types=None, max_retries=3, backoff_factor=2):
        """Decorator for error handling with retry logic."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        # Check if this is a retryable error
                        if error_types and not any(isinstance(e, error_type) for error_type in error_types):
                            raise e
                        
                        if attempt < max_retries:
                            wait_time = backoff_factor ** attempt
                            self.logger.warning(
                                f"Attempt {attempt + 1} failed, retrying in {wait_time}s",
                                error=str(e),
                                function=func.__name__
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"All {max_retries + 1} attempts failed",
                                error=str(e),
                                function=func.__name__
                            )
                            raise e
                
                return None
            return wrapper
        return decorator
    
    def safe_execute(self, func, *args, **kwargs):
        """Safely execute a function with error handling."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(
                f"Function execution failed",
                function=func.__name__,
                error=str(e),
                args=args,
                kwargs=kwargs
            )
            raise

# Usage
error_handler = ErrorHandler(logging.getLogger('error_handler'))

@error_handler.handle_errors(
    error_types=[OrderGenerationError, OrderQueueError],
    max_retries=3
)
def generate_orders_safely(count):
    """Generate orders with error handling."""
    return generate_orders(count)

# Safe execution
try:
    result = error_handler.safe_execute(generate_orders, 5)
except Exception as e:
    print(f"Failed to generate orders: {e}")
```

### 3. Error Recovery Strategies

```python
class ErrorRecovery:
    def __init__(self, logger):
        self.logger = logger
        self.recovery_strategies = {}
    
    def register_recovery_strategy(self, error_type, strategy_func):
        """Register a recovery strategy for a specific error type."""
        self.recovery_strategies[error_type] = strategy_func
    
    def recover_from_error(self, error, context=None):
        """Attempt to recover from an error using registered strategies."""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            strategy = self.recovery_strategies[error_type]
            self.logger.info(
                f"Attempting recovery for {error_type.__name__}",
                error=str(error),
                context=context
            )
            
            try:
                result = strategy(error, context)
                self.logger.info(
                    f"Recovery successful for {error_type.__name__}",
                    context=context
                )
                return result
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery failed for {error_type.__name__}",
                    original_error=str(error),
                    recovery_error=str(recovery_error),
                    context=context
                )
                raise recovery_error
        else:
            self.logger.warning(
                f"No recovery strategy for {error_type.__name__}",
                error=str(error),
                context=context
            )
            raise error

# Usage
recovery = ErrorRecovery(logging.getLogger('recovery'))

# Register recovery strategies
def queue_recovery_strategy(error, context):
    """Recovery strategy for queue errors."""
    # Clear queue and retry
    clear_queue()
    return "Queue cleared and retry initiated"

def assignment_recovery_strategy(error, context):
    """Recovery strategy for assignment errors."""
    # Reset robot assignments and retry
    reset_robot_assignments()
    return "Robot assignments reset"

recovery.register_recovery_strategy(OrderQueueError, queue_recovery_strategy)
recovery.register_recovery_strategy(RobotAssignmentError, assignment_recovery_strategy)

# Use recovery
try:
    result = process_orders()
except OrderQueueError as e:
    recovery.recover_from_error(e, context={"operation": "process_orders"})
```

## Debugging Strategies

### 1. Debug Mode Configuration

```python
class DebugMode:
    def __init__(self, logger):
        self.logger = logger
        self.debug_enabled = False
        self.debug_levels = {
            'order_generation': True,
            'queue_management': True,
            'robot_assignment': True,
            'status_tracking': True,
            'performance': True
        }
    
    def enable_debug(self, components=None):
        """Enable debug mode for specific components."""
        if components:
            for component in components:
                self.debug_levels[component] = True
        else:
            self.debug_enabled = True
            for component in self.debug_levels:
                self.debug_levels[component] = True
    
    def disable_debug(self, components=None):
        """Disable debug mode for specific components."""
        if components:
            for component in components:
                self.debug_levels[component] = False
        else:
            self.debug_enabled = False
            for component in self.debug_levels:
                self.debug_levels[component] = False
    
    def debug_log(self, component, message, **kwargs):
        """Log debug message if debug is enabled for component."""
        if self.debug_enabled and self.debug_levels.get(component, False):
            self.logger.debug(f"[{component.upper()}] {message} | {kwargs}")
    
    def trace_execution(self, component, func_name, **kwargs):
        """Trace function execution in debug mode."""
        if self.debug_enabled and self.debug_levels.get(component, False):
            self.logger.debug(f"[{component.upper()}] Entering {func_name} | {kwargs}")

# Usage
debug_mode = DebugMode(logging.getLogger('debug'))

# Enable debug for specific components
debug_mode.enable_debug(['order_generation', 'queue_management'])

# Debug logging
debug_mode.debug_log('order_generation', 'Generating order', order_id='order_001')

# Trace execution
debug_mode.trace_execution('queue_management', 'add_order', order_id='order_001')
```

### 2. State Inspection Tools

```python
class StateInspector:
    def __init__(self, order_system, logger):
        self.order_system = order_system
        self.logger = logger
    
    def inspect_system_state(self):
        """Inspect current system state for debugging."""
        state = {
            'queue_status': self.order_system.get_queue_status(),
            'robot_status': self.order_system.get_robot_status(),
            'order_status': self.order_system.get_order_status(),
            'performance_metrics': self.order_system.get_performance_metrics()
        }
        
        self.logger.info("System state inspection", state=state)
        return state
    
    def inspect_order_flow(self, order_id):
        """Inspect the flow of a specific order."""
        order_history = self.order_system.get_order_history(order_id)
        
        self.logger.info(
            f"Order flow inspection for {order_id}",
            history=order_history
        )
        return order_history
    
    def inspect_robot_activity(self, robot_id):
        """Inspect robot activity and assignments."""
        robot_activity = self.order_system.get_robot_activity(robot_id)
        
        self.logger.info(
            f"Robot activity inspection for {robot_id}",
            activity=robot_activity
        )
        return robot_activity
    
    def compare_states(self, state1, state2):
        """Compare two system states and log differences."""
        differences = {}
        
        for key in state1:
            if key in state2:
                if state1[key] != state2[key]:
                    differences[key] = {
                        'before': state1[key],
                        'after': state2[key]
                    }
            else:
                differences[key] = {'before': state1[key], 'after': None}
        
        for key in state2:
            if key not in state1:
                differences[key] = {'before': None, 'after': state2[key]}
        
        if differences:
            self.logger.info("State differences detected", differences=differences)
        
        return differences

# Usage
inspector = StateInspector(order_system, logging.getLogger('inspector'))

# Inspect current state
current_state = inspector.inspect_system_state()

# Inspect specific order
order_flow = inspector.inspect_order_flow('order_001')

# Compare states
differences = inspector.compare_states(previous_state, current_state)
```

## Monitoring and Alerting

### 1. Performance Monitoring

```python
import time
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.metrics = defaultdict(list)
        self.thresholds = {}
    
    def start_timer(self, operation_name):
        """Start timing an operation."""
        return {
            'operation': operation_name,
            'start_time': time.time()
        }
    
    def end_timer(self, timer):
        """End timing an operation and record metrics."""
        duration = time.time() - timer['start_time']
        operation = timer['operation']
        
        self.metrics[operation].append(duration)
        
        # Check thresholds
        if operation in self.thresholds:
            threshold = self.thresholds[operation]
            if duration > threshold:
                self.logger.warning(
                    f"Operation {operation} exceeded threshold",
                    duration=duration,
                    threshold=threshold
                )
        
        self.logger.debug(
            f"Operation {operation} completed",
            duration=duration
        )
        
        return duration
    
    def set_threshold(self, operation, threshold):
        """Set performance threshold for an operation."""
        self.thresholds[operation] = threshold
    
    def get_average_duration(self, operation):
        """Get average duration for an operation."""
        if operation in self.metrics:
            return sum(self.metrics[operation]) / len(self.metrics[operation])
        return 0
    
    def get_performance_summary(self):
        """Get performance summary for all operations."""
        summary = {}
        
        for operation, durations in self.metrics.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'average': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'threshold': self.thresholds.get(operation, None)
                }
        
        return summary

# Usage
monitor = PerformanceMonitor(logging.getLogger('performance'))

# Set thresholds
monitor.set_threshold('order_generation', 1.0)  # 1 second
monitor.set_threshold('order_assignment', 0.5)  # 0.5 seconds

# Monitor operations
timer = monitor.start_timer('order_generation')
orders = generate_orders(10)
duration = monitor.end_timer(timer)

# Get performance summary
summary = monitor.get_performance_summary()
```

### 2. Alert System

```python
class AlertSystem:
    def __init__(self, logger):
        self.logger = logger
        self.alerts = []
        self.alert_handlers = {}
    
    def register_alert_handler(self, alert_type, handler_func):
        """Register a handler for a specific alert type."""
        self.alert_handlers[alert_type] = handler_func
    
    def raise_alert(self, alert_type, message, severity='warning', **kwargs):
        """Raise an alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': time.time(),
            'details': kwargs
        }
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = 'critical' if severity == 'critical' else severity
        self.logger.log(
            getattr(logging, log_level.upper()),
            f"ALERT [{alert_type}]: {message}",
            **kwargs
        )
        
        # Call handler if registered
        if alert_type in self.alert_handlers:
            try:
                self.alert_handlers[alert_type](alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed for {alert_type}", error=str(e))
        
        return alert
    
    def get_active_alerts(self, severity=None):
        """Get active alerts, optionally filtered by severity."""
        if severity:
            return [alert for alert in self.alerts if alert['severity'] == severity]
        return self.alerts
    
    def clear_alerts(self, alert_type=None):
        """Clear alerts, optionally filtered by type."""
        if alert_type:
            self.alerts = [alert for alert in self.alerts if alert['type'] != alert_type]
        else:
            self.alerts.clear()

# Usage
alert_system = AlertSystem(logging.getLogger('alerts'))

# Register alert handlers
def queue_full_handler(alert):
    """Handle queue full alerts."""
    print(f"Queue is full! Current size: {alert['details'].get('queue_size')}")

def performance_handler(alert):
    """Handle performance alerts."""
    print(f"Performance issue: {alert['message']}")

alert_system.register_alert_handler('queue_full', queue_full_handler)
alert_system.register_alert_handler('performance', performance_handler)

# Raise alerts
alert_system.raise_alert(
    'queue_full',
    'Order queue is at capacity',
    severity='warning',
    queue_size=50,
    max_size=50
)

alert_system.raise_alert(
    'performance',
    'Order generation taking too long',
    severity='error',
    duration=5.2,
    threshold=3.0
)
```

## Performance Logging

### 1. Memory Usage Monitoring

```python
import psutil
import gc

class MemoryMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.process = psutil.Process()
    
    def log_memory_usage(self):
        """Log current memory usage."""
        memory_info = self.process.memory_info()
        
        self.logger.info(
            "Memory usage",
            rss_mb=memory_info.rss / 1024 / 1024,  # RSS in MB
            vms_mb=memory_info.vms / 1024 / 1024,  # VMS in MB
            percent=self.process.memory_percent()
        )
    
    def check_memory_threshold(self, threshold_mb=500):
        """Check if memory usage exceeds threshold."""
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        if memory_mb > threshold_mb:
            self.logger.warning(
                "Memory usage exceeds threshold",
                current_mb=memory_mb,
                threshold_mb=threshold_mb
            )
            return True
        return False
    
    def force_garbage_collection(self):
        """Force garbage collection and log results."""
        before_count = len(gc.get_objects())
        before_memory = self.process.memory_info().rss
        
        gc.collect()
        
        after_count = len(gc.get_objects())
        after_memory = self.process.memory_info().rss
        
        self.logger.info(
            "Garbage collection completed",
            objects_freed=before_count - after_count,
            memory_freed_mb=(before_memory - after_memory) / 1024 / 1024
        )

# Usage
memory_monitor = MemoryMonitor(logging.getLogger('memory'))

# Monitor memory usage
memory_monitor.log_memory_usage()

# Check for memory issues
if memory_monitor.check_memory_threshold(1000):  # 1GB threshold
    memory_monitor.force_garbage_collection()
```

### 2. Performance Profiling

```python
import cProfile
import pstats
import io

class PerformanceProfiler:
    def __init__(self, logger):
        self.logger = logger
        self.profiler = None
    
    def start_profiling(self):
        """Start performance profiling."""
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.info("Performance profiling started")
    
    def stop_profiling(self):
        """Stop performance profiling and log results."""
        if self.profiler:
            self.profiler.disable()
            
            # Get profiling stats
            s = io.StringIO()
            stats = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            
            self.logger.info("Performance profiling results", stats=s.getvalue())
            
            # Reset profiler
            self.profiler = None
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a specific function."""
        self.start_profiling()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.stop_profiling()

# Usage
profiler = PerformanceProfiler(logging.getLogger('profiler'))

# Profile a function
result = profiler.profile_function(generate_orders, 100)
```

## Best Practices

### 1. Logging Best Practices

```python
class LoggingBestPractices:
    @staticmethod
    def use_structured_logging(logger, event_type, **kwargs):
        """Use structured logging for better analysis."""
        logger.info(f"Event: {event_type}", **kwargs)
    
    @staticmethod
    def include_context(logger, message, context=None, **kwargs):
        """Include relevant context in log messages."""
        if context:
            kwargs['context'] = context
        logger.info(message, **kwargs)
    
    @staticmethod
    def log_exceptions(logger, func):
        """Decorator to log exceptions properly."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}",
                    error=str(e),
                    error_type=type(e).__name__,
                    args=args,
                    kwargs=kwargs
                )
                raise
        return wrapper
    
    @staticmethod
    def use_appropriate_levels(logger):
        """Use appropriate log levels."""
        # DEBUG: Detailed information for debugging
        logger.debug("Processing order details", order_id="order_001")
        
        # INFO: General operational information
        logger.info("Order processed successfully", order_id="order_001")
        
        # WARNING: Potential issues
        logger.warning("Queue approaching capacity", current_size=45, max_size=50)
        
        # ERROR: Issues that don't stop operation
        logger.error("Failed to assign order", order_id="order_001", reason="no_available_robots")
        
        # CRITICAL: Serious issues that may stop operation
        logger.critical("System out of memory", available="100MB", required="500MB")
```

### 2. Error Handling Best Practices

```python
class ErrorHandlingBestPractices:
    @staticmethod
    def handle_specific_exceptions():
        """Handle specific exceptions rather than catching all."""
        try:
            result = risky_operation()
            return result
        except OrderGenerationError as e:
            # Handle order generation errors specifically
            logger.error("Order generation failed", error=str(e))
            return None
        except OrderQueueError as e:
            # Handle queue errors specifically
            logger.error("Queue operation failed", error=str(e))
            raise  # Re-raise if it's critical
        except Exception as e:
            # Handle unexpected errors
            logger.critical("Unexpected error", error=str(e))
            raise
    
    @staticmethod
    def provide_useful_error_messages():
        """Provide useful error messages with context."""
        try:
            result = process_order(order_id="order_001")
            return result
        except Exception as e:
            logger.error(
                "Failed to process order",
                order_id="order_001",
                error=str(e),
                error_type=type(e).__name__,
                stack_trace=True
            )
            raise
    
    @staticmethod
    def implement_retry_logic(max_retries=3, backoff_factor=2):
        """Implement retry logic for transient failures."""
        def retry_decorator(func):
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except (OrderQueueError, RobotAssignmentError) as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                f"Attempt {attempt + 1} failed, retrying in {wait_time}s",
                                error=str(e)
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(
                                f"All {max_retries + 1} attempts failed",
                                error=str(e)
                            )
                            raise e
                
                return None
            return wrapper
        return retry_decorator
```

## Troubleshooting

### 1. Common Logging Issues

```python
class LoggingTroubleshooting:
    @staticmethod
    def diagnose_logging_issues():
        """Diagnose common logging issues."""
        issues = []
        
        # Check if logging is configured
        if not logging.getLogger().handlers:
            issues.append("No logging handlers configured")
        
        # Check log level
        root_level = logging.getLogger().level
        if root_level > logging.INFO:
            issues.append(f"Root log level too high: {root_level}")
        
        # Check file permissions
        try:
            with open('test.log', 'w') as f:
                f.write('test')
            os.remove('test.log')
        except Exception as e:
            issues.append(f"Cannot write to log files: {e}")
        
        return issues
    
    @staticmethod
    def fix_logging_configuration():
        """Fix common logging configuration issues."""
        # Ensure basic logging is configured
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Add file handler
        file_handler = logging.FileHandler('logs/application.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)
```

### 2. Performance Debugging

```python
class PerformanceDebugging:
    @staticmethod
    def identify_slow_operations(monitor):
        """Identify slow operations using performance monitor."""
        summary = monitor.get_performance_summary()
        slow_operations = []
        
        for operation, metrics in summary.items():
            if metrics['average'] > 1.0:  # More than 1 second
                slow_operations.append({
                    'operation': operation,
                    'average_duration': metrics['average'],
                    'max_duration': metrics['max'],
                    'count': metrics['count']
                })
        
        return sorted(slow_operations, key=lambda x: x['average_duration'], reverse=True)
    
    @staticmethod
    def analyze_memory_usage(memory_monitor):
        """Analyze memory usage patterns."""
        memory_monitor.log_memory_usage()
        
        if memory_monitor.check_memory_threshold(1000):
            memory_monitor.force_garbage_collection()
            memory_monitor.log_memory_usage()
    
    @staticmethod
    def profile_critical_path(profiler, critical_functions):
        """Profile critical path functions."""
        for func_name, func in critical_functions.items():
            profiler.profile_function(func)
```

This comprehensive logging and error handling guide provides the foundation for maintaining a robust and debuggable order management system. Follow these practices to ensure reliable operation and effective troubleshooting. 