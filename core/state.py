"""
Enhanced simulation state management with configuration integration.
Provides centralized state handling with configuration-driven behavior.
"""

import json
import time
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field

from .main_config import ConfigurationManager, get_config


class SimulationStatus(Enum):
    """Simulation execution status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    frame_time: float = 0.0
    target_frame_time: float = 16.67  # 60 FPS target
    fps: float = 0.0
    event_processing_time: float = 0.0
    component_update_time: float = 0.0
    total_frames: int = 0
    dropped_frames: int = 0
    
    def update_frame_time(self, frame_time: float) -> None:
        """Update frame time metrics."""
        self.frame_time = frame_time
        self.fps = 1.0 / frame_time if frame_time > 0 else 0.0
        self.total_frames += 1
        
        # Count dropped frames
        if frame_time > (self.target_frame_time * 2):
            self.dropped_frames += 1


@dataclass
class ComponentState:
    """State tracking for simulation components."""
    name: str
    is_active: bool = False
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    
    def update(self) -> None:
        """Update component state."""
        self.last_update = time.time()
        self.update_count += 1
    
    def record_error(self) -> None:
        """Record an error for this component."""
        self.error_count += 1


class SimulationState:
    """
    Enhanced centralized simulation state management.
    Integrates with configuration system for dynamic behavior.
    """
    
    def __init__(self):
        """Initialize simulation state."""
        self.status = SimulationStatus.STOPPED
        self.simulation_time = 0.0
        self.real_time_start = 0.0
        self.frame_count = 0
        self.current_fps = 0.0
        
        # Configuration integration
        self.config_manager: Optional[ConfigurationManager] = None
        self.config_loaded = False
        
        # Performance tracking
        self.performance = PerformanceMetrics()
        
        # Component tracking
        self.components: Dict[str, ComponentState] = {}
        
        # State history for debugging
        self.state_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # Speed control
        self.simulation_speed = 1.0
        
        print("🎯 SimulationState initialized")
    
    def load_configuration(self) -> None:
        """Load configuration and update state accordingly."""
        if self.config_loaded:
            return
        
        print("⚙️  Loading configuration into state...")
        
        self.config_manager = get_config()
        if not self.config_manager.is_loaded:
            self.config_manager.load_configuration()
        
        # Update state with configuration values
        self.simulation_speed = self.config_manager.timing.SIMULATION_SPEED
        self.performance.target_frame_time = self.config_manager.timing.TARGET_FPS
        
        # Update FPS calculation
        target_fps = self.config_manager.timing.TARGET_FPS
        self.performance.target_frame_time = 1000.0 / target_fps  # Convert to milliseconds
        
        self.config_loaded = True
        print("✅ Configuration loaded into state")
    
    def get_config(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., "timing.target_fps")
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if not self.config_loaded:
            self.load_configuration()
        
        parts = path.split('.')
        if len(parts) != 2:
            return default
        
        section, key = parts
        return self.config_manager.get_value(section, key, default)
    
    def set_config(self, path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., "timing.target_fps")
            value: New value
        """
        if not self.config_loaded:
            self.load_configuration()
        
        parts = path.split('.')
        if len(parts) != 2:
            return
        
        section, key = parts
        self.config_manager.set_value(section, key, value)
        print(f"🔧 Configuration updated: {path} = {value}")
    
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self.status == SimulationStatus.RUNNING
    
    def is_paused(self) -> bool:
        """Check if simulation is paused."""
        return self.status == SimulationStatus.PAUSED
    
    def is_stopped(self) -> bool:
        """Check if simulation is stopped."""
        return self.status == SimulationStatus.STOPPED
    
    def is_active(self) -> bool:
        """Check if simulation is active (running or paused)."""
        return self.status in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]
    
    def start(self) -> None:
        """Start the simulation."""
        if self.status != SimulationStatus.STOPPED:
            print(f"⚠️  Cannot start: current status is {self.status.value}")
            return
        
        print("🚀 Starting simulation...")
        self.status = SimulationStatus.STARTING
        self.real_time_start = time.time()
        self.simulation_time = 0.0
        self.frame_count = 0
        
        # Reset performance metrics
        self.performance = PerformanceMetrics()
        if self.config_loaded:
            target_fps = self.config_manager.timing.TARGET_FPS
            self.performance.target_frame_time = 1000.0 / target_fps
        
        # Activate components
        for component in self.components.values():
            component.is_active = True
        
        self.status = SimulationStatus.RUNNING
        self._record_state_change("started")
        print("✅ Simulation started")
    
    def stop(self) -> None:
        """Stop the simulation."""
        if self.status == SimulationStatus.STOPPED:
            print("⚠️  Simulation is already stopped")
            return
        
        print("⏹️  Stopping simulation...")
        self.status = SimulationStatus.STOPPING
        
        # Deactivate components
        for component in self.components.values():
            component.is_active = False
        
        self.status = SimulationStatus.STOPPED
        self._record_state_change("stopped")
        print("✅ Simulation stopped")
    
    def pause(self) -> None:
        """Pause the simulation."""
        if self.status != SimulationStatus.RUNNING:
            print(f"⚠️  Cannot pause: current status is {self.status.value}")
            return
        
        print("⏸️  Pausing simulation...")
        self.status = SimulationStatus.PAUSED
        self._record_state_change("paused")
        print("✅ Simulation paused")
    
    def resume(self) -> None:
        """Resume the simulation."""
        if self.status != SimulationStatus.PAUSED:
            print(f"⚠️  Cannot resume: current status is {self.status.value}")
            return
        
        print("▶️  Resuming simulation...")
        self.status = SimulationStatus.RUNNING
        self._record_state_change("resumed")
        print("✅ Simulation resumed")
    
    def update(self, delta_time: float) -> None:
        """
        Update simulation state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if not self.is_running():
            return
        
        # Apply simulation speed
        adjusted_delta = delta_time * self.simulation_speed
        
        # Update simulation time
        self.simulation_time += adjusted_delta
        
        # Update frame count
        self.frame_count += 1
        
        # Update performance metrics
        self.performance.update_frame_time(delta_time)
        self.current_fps = self.performance.fps
        
        # Update component states
        for component in self.components.values():
            if component.is_active:
                component.update()
        
        # Check for performance warnings
        if self.config_loaded:
            frame_time_ms = delta_time * 1000.0
            warning_threshold = self.config_manager.timing.FRAME_TIME_WARNING
            critical_threshold = self.config_manager.timing.FRAME_TIME_CRITICAL
            
            if frame_time_ms > critical_threshold:
                print(f"🚨 CRITICAL: Frame time {frame_time_ms:.2f}ms exceeds threshold {critical_threshold:.2f}ms")
            elif frame_time_ms > warning_threshold:
                print(f"⚠️  WARNING: Frame time {frame_time_ms:.2f}ms exceeds threshold {warning_threshold:.2f}ms")
    
    def set_simulation_speed(self, speed: float) -> None:
        """
        Set simulation speed multiplier.
        
        Args:
            speed: Speed multiplier (1.0 = normal speed)
        """
        # Clamp speed to valid range (0.1 to 10.0)
        clamped_speed = max(0.1, min(10.0, speed))
        
        if speed != clamped_speed:
            print(f"⚠️  Simulation speed {speed} clamped to valid range: {clamped_speed}")
        
        old_speed = self.simulation_speed
        self.simulation_speed = clamped_speed
        
        # Update configuration if loaded
        if self.config_loaded:
            self.config_manager.set_value("timing", "simulation_speed", clamped_speed)
        
        self._record_state_change(f"speed_changed", {"old_speed": old_speed, "new_speed": clamped_speed})
        print(f"⚡ Simulation speed changed: {old_speed}x → {clamped_speed}x")
    
    def get_simulation_speed(self) -> float:
        """Get current simulation speed multiplier."""
        return self.simulation_speed
    
    def register_component(self, name: str) -> None:
        """
        Register a simulation component.
        
        Args:
            name: Component name
        """
        if name in self.components:
            print(f"⚠️  Component '{name}' already registered")
            return
        
        self.components[name] = ComponentState(name)
        print(f"📋 Component registered: {name}")
    
    def unregister_component(self, name: str) -> None:
        """
        Unregister a simulation component.
        
        Args:
            name: Component name
        """
        if name not in self.components:
            print(f"⚠️  Component '{name}' not found")
            return
        
        del self.components[name]
        print(f"🗑️  Component unregistered: {name}")
    
    def get_component_state(self, name: str) -> Optional[ComponentState]:
        """
        Get component state.
        
        Args:
            name: Component name
            
        Returns:
            Component state or None if not found
        """
        return self.components.get(name)
    
    def get_active_components(self) -> List[str]:
        """Get list of active component names."""
        return [name for name, component in self.components.items() if component.is_active]
    
    def _record_state_change(self, action: str, details: Dict[str, Any] = None) -> None:
        """
        Record a state change for debugging.
        
        Args:
            action: Action performed
            details: Additional details
        """
        if details is None:
            details = {}
        
        state_record = {
            "timestamp": time.time(),
            "action": action,
            "status": self.status.value,
            "simulation_time": self.simulation_time,
            "frame_count": self.frame_count,
            "fps": self.current_fps,
            "details": details
        }
        
        self.state_history.append(state_record)
        
        # Limit history size
        if len(self.state_history) > self.max_history_size:
            self.state_history.pop(0)
        
        print(f"📝 State change recorded: {action}")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive state summary."""
        return {
            "status": self.status.value,
            "simulation_time": self.simulation_time,
            "real_time_elapsed": time.time() - self.real_time_start if self.real_time_start > 0 else 0,
            "frame_count": self.frame_count,
            "current_fps": self.current_fps,
            "simulation_speed": self.simulation_speed,
            "performance": {
                "frame_time": self.performance.frame_time,
                "target_frame_time": self.performance.target_frame_time,
                "fps": self.performance.fps,
                "total_frames": self.performance.total_frames,
                "dropped_frames": self.performance.dropped_frames,
                "event_processing_time": self.performance.event_processing_time,
                "component_update_time": self.performance.component_update_time
            },
            "components": {
                name: {
                    "is_active": component.is_active,
                    "last_update": component.last_update,
                    "update_count": component.update_count,
                    "error_count": component.error_count
                }
                for name, component in self.components.items()
            },
            "config_loaded": self.config_loaded,
            "state_history_size": len(self.state_history)
        }
    
    def reset(self) -> None:
        """Reset simulation state to initial values."""
        print("🔄 Resetting simulation state...")
        
        self.status = SimulationStatus.STOPPED
        self.simulation_time = 0.0
        self.real_time_start = 0.0
        self.frame_count = 0
        self.current_fps = 0.0
        
        # Reset performance metrics
        self.performance = PerformanceMetrics()
        if self.config_loaded:
            target_fps = self.config_manager.timing.TARGET_FPS
            self.performance.target_frame_time = 1000.0 / target_fps
        
        # Reset component states
        for component in self.components.values():
            component.is_active = False
            component.last_update = 0.0
            component.update_count = 0
            component.error_count = 0
        
        # Clear state history
        self.state_history.clear()
        
        self._record_state_change("reset")
        print("✅ Simulation state reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information."""
        debug_info = self.get_state_summary()
        
        # Add recent state history
        debug_info["recent_state_history"] = self.state_history[-5:] if self.state_history else []
        
        # Add configuration summary if loaded
        if self.config_loaded:
            debug_info["configuration"] = self.config_manager.get_configuration_summary()
        
        return debug_info 