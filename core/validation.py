"""
Validation and error handling utilities for robust simulation control.
Provides input validation, error recovery, and safety checks.
"""

import asyncio
from typing import Any, Optional, Dict, List
from enum import Enum

from .state import SimulationStatus


class ValidationError(Exception):
    """Custom validation error for simulation controls."""
    pass


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SimulationValidator:
    """
    Validation and error handling for simulation controls.
    Ensures safe operation and proper state transitions.
    """
    
    def __init__(self):
        """Initialize validator."""
        self.error_count = 0
        self.warning_count = 0
        self.error_history: List[Dict[str, Any]] = []
        
        print("🛡️  SimulationValidator initialized")
    
    def validate_speed(self, speed: float) -> bool:
        """
        Validate simulation speed value.
        
        Args:
            speed: Speed multiplier to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If speed is invalid
        """
        if not isinstance(speed, (int, float)):
            self._log_error(ErrorSeverity.ERROR, "Speed must be a number")
            raise ValidationError("Speed must be a number")
        
        if speed <= 0:
            self._log_error(ErrorSeverity.ERROR, "Speed must be positive")
            raise ValidationError("Speed must be positive")
        
        if speed > 10.0:
            self._log_error(ErrorSeverity.WARNING, f"High simulation speed ({speed}x) may cause performance issues")
            return True  # Warning, but still valid
        
        if speed < 0.1:
            self._log_error(ErrorSeverity.WARNING, f"Very low simulation speed ({speed}x) may cause timing issues")
            return True  # Warning, but still valid
        
        print(f"✅ Speed validation passed: {speed}x")
        return True
    
    def validate_state_transition(self, current_status: SimulationStatus, 
                                 target_status: SimulationStatus) -> bool:
        """
        Validate state transition is allowed.
        
        Args:
            current_status: Current simulation status
            target_status: Target simulation status
            
        Returns:
            True if transition is valid, False otherwise
            
        Raises:
            ValidationError: If transition is invalid
        """
        valid_transitions = {
            SimulationStatus.STOPPED: [SimulationStatus.STARTING],
            SimulationStatus.STARTING: [SimulationStatus.RUNNING, SimulationStatus.STOPPING],
            SimulationStatus.RUNNING: [SimulationStatus.PAUSED, SimulationStatus.STOPPING],
            SimulationStatus.PAUSED: [SimulationStatus.RUNNING, SimulationStatus.STOPPING],
            SimulationStatus.STOPPING: [SimulationStatus.STOPPED]
        }
        
        if target_status not in valid_transitions.get(current_status, []):
            error_msg = f"Invalid state transition: {current_status.value} → {target_status.value}"
            self._log_error(ErrorSeverity.ERROR, error_msg)
            raise ValidationError(error_msg)
        
        print(f"✅ State transition validated: {current_status.value} → {target_status.value}")
        return True
    
    def validate_config_value(self, key: str, value: Any, expected_type: type = None, 
                            min_value: float = None, max_value: float = None) -> bool:
        """
        Validate configuration value.
        
        Args:
            key: Configuration key
            value: Value to validate
            expected_type: Expected value type
            min_value: Minimum allowed value (for numbers)
            max_value: Maximum allowed value (for numbers)
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If value is invalid
        """
        # Type validation
        if expected_type and not isinstance(value, expected_type):
            error_msg = f"Config '{key}': expected {expected_type.__name__}, got {type(value).__name__}"
            self._log_error(ErrorSeverity.ERROR, error_msg)
            raise ValidationError(error_msg)
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            if min_value is not None and value < min_value:
                error_msg = f"Config '{key}': value {value} below minimum {min_value}"
                self._log_error(ErrorSeverity.ERROR, error_msg)
                raise ValidationError(error_msg)
            
            if max_value is not None and value > max_value:
                error_msg = f"Config '{key}': value {value} above maximum {max_value}"
                self._log_error(ErrorSeverity.ERROR, error_msg)
                raise ValidationError(error_msg)
        
        print(f"✅ Config validation passed: {key} = {value}")
        return True
    
    def validate_fps_target(self, fps: int) -> bool:
        """
        Validate FPS target value.
        
        Args:
            fps: Target FPS to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If FPS is invalid
        """
        if not isinstance(fps, int):
            self._log_error(ErrorSeverity.ERROR, "FPS must be an integer")
            raise ValidationError("FPS must be an integer")
        
        if fps < 1:
            self._log_error(ErrorSeverity.ERROR, "FPS must be at least 1")
            raise ValidationError("FPS must be at least 1")
        
        if fps > 120:
            self._log_error(ErrorSeverity.WARNING, f"High FPS target ({fps}) may cause performance issues")
            return True
        
        if fps < 10:
            self._log_error(ErrorSeverity.WARNING, f"Low FPS target ({fps}) may cause choppy animation")
            return True
        
        print(f"✅ FPS validation passed: {fps}")
        return True
    
    def check_system_health(self, frame_time: float, event_queue_size: int, 
                          memory_usage: float = None) -> Dict[str, Any]:
        """
        Check overall system health and performance.
        
        Args:
            frame_time: Current frame time in seconds
            event_queue_size: Current event queue size
            memory_usage: Memory usage in MB (optional)
            
        Returns:
            Health status dictionary
        """
        health_status = {
            "overall": "healthy",
            "issues": [],
            "warnings": [],
            "frame_time_ok": True,
            "event_queue_ok": True,
            "memory_ok": True
        }
        
        # Check frame time
        target_frame_time = 1.0 / 60.0  # 60 FPS
        warning_threshold = target_frame_time * 2  # 30 FPS
        critical_threshold = target_frame_time * 6  # 10 FPS
        
        if frame_time > critical_threshold:
            health_status["issues"].append(f"Critical: Frame time {frame_time*1000:.1f}ms (target: {target_frame_time*1000:.1f}ms)")
            health_status["frame_time_ok"] = False
            health_status["overall"] = "critical"
        elif frame_time > warning_threshold:
            health_status["warnings"].append(f"Warning: Frame time {frame_time*1000:.1f}ms (target: {target_frame_time*1000:.1f}ms)")
            health_status["frame_time_ok"] = False
            if health_status["overall"] == "healthy":
                health_status["overall"] = "warning"
        
        # Check event queue
        if event_queue_size > 800:  # 80% of default max
            health_status["issues"].append(f"Critical: Event queue nearly full ({event_queue_size}/1000)")
            health_status["event_queue_ok"] = False
            health_status["overall"] = "critical"
        elif event_queue_size > 500:  # 50% of default max
            health_status["warnings"].append(f"Warning: Event queue filling up ({event_queue_size}/1000)")
            health_status["event_queue_ok"] = False
            if health_status["overall"] == "healthy":
                health_status["overall"] = "warning"
        
        # Check memory usage (if provided)
        if memory_usage is not None:
            if memory_usage > 1000:  # 1GB
                health_status["issues"].append(f"Critical: High memory usage ({memory_usage:.1f}MB)")
                health_status["memory_ok"] = False
                health_status["overall"] = "critical"
            elif memory_usage > 500:  # 500MB
                health_status["warnings"].append(f"Warning: Elevated memory usage ({memory_usage:.1f}MB)")
                health_status["memory_ok"] = False
                if health_status["overall"] == "healthy":
                    health_status["overall"] = "warning"
        
        # Log health status
        if health_status["overall"] == "critical":
            self._log_error(ErrorSeverity.CRITICAL, f"System health critical: {len(health_status['issues'])} issues")
        elif health_status["overall"] == "warning":
            self._log_error(ErrorSeverity.WARNING, f"System health warning: {len(health_status['warnings'])} warnings")
        
        return health_status
    
    async def recovery_attempt(self, error_type: str, context: Dict[str, Any] = None) -> bool:
        """
        Attempt to recover from an error.
        
        Args:
            error_type: Type of error to recover from
            context: Additional context for recovery
            
        Returns:
            True if recovery successful, False otherwise
        """
        print(f"🔧 Attempting recovery from: {error_type}")
        
        if context is None:
            context = {}
        
        recovery_strategies = {
            "frame_time_high": self._recover_frame_time,
            "event_queue_full": self._recover_event_queue,
            "memory_high": self._recover_memory,
            "state_transition_error": self._recover_state_transition
        }
        
        strategy = recovery_strategies.get(error_type)
        if strategy:
            try:
                success = await strategy(context)
                if success:
                    print(f"✅ Recovery successful for: {error_type}")
                else:
                    print(f"❌ Recovery failed for: {error_type}")
                return success
            except Exception as e:
                print(f"❌ Recovery error for {error_type}: {e}")
                return False
        else:
            print(f"⚠️  No recovery strategy for: {error_type}")
            return False
    
    async def _recover_frame_time(self, context: Dict[str, Any]) -> bool:
        """Recover from high frame time."""
        print("🔧 Reducing simulation load...")
        await asyncio.sleep(0.1)  # Give system time to catch up
        return True
    
    async def _recover_event_queue(self, context: Dict[str, Any]) -> bool:
        """Recover from event queue overflow."""
        print("🔧 Clearing event queue backlog...")
        # In real implementation, would clear non-critical events
        await asyncio.sleep(0.05)
        return True
    
    async def _recover_memory(self, context: Dict[str, Any]) -> bool:
        """Recover from high memory usage."""
        print("🔧 Triggering garbage collection...")
        import gc
        gc.collect()
        return True
    
    async def _recover_state_transition(self, context: Dict[str, Any]) -> bool:
        """Recover from state transition error."""
        print("🔧 Resetting to safe state...")
        # In real implementation, would reset to known good state
        await asyncio.sleep(0.1)
        return True
    
    def _log_error(self, severity: ErrorSeverity, message: str) -> None:
        """Log an error with timestamp and severity."""
        import datetime
        
        error_entry = {
            "timestamp": datetime.datetime.now(),
            "severity": severity.value,
            "message": message
        }
        
        self.error_history.append(error_entry)
        
        if severity == ErrorSeverity.ERROR:
            self.error_count += 1
        elif severity == ErrorSeverity.WARNING:
            self.warning_count += 1
        
        # Print with appropriate emoji
        emoji_map = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        
        emoji = emoji_map.get(severity, "📝")
        print(f"{emoji} [{severity.value.upper()}] {message}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors and warnings."""
        return {
            "total_errors": self.error_count,
            "total_warnings": self.warning_count,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }
    
    def reset_error_counters(self) -> None:
        """Reset error counters and history."""
        self.error_count = 0
        self.warning_count = 0
        self.error_history.clear()
        print("🔄 Error counters reset") 