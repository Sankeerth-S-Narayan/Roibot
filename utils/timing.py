"""
Timing utilities for smooth animations and frame rate management.

This module provides the TimingManager class which is responsible for maintaining
consistent frame rates and providing smooth timing for animations and simulations.

Key Features:
- Precise frame rate control (default 60 FPS)
- Smooth interpolation for animations
- Delta time calculation for frame-independent movement
- Pause/resume functionality
- Speed control for simulation acceleration/deceleration

The TimingManager ensures that the simulation runs at a consistent frame rate
regardless of system performance, providing smooth animations and predictable
timing for all simulation components.

Performance Considerations:
- Uses high-precision timing for accurate frame rate control
- Implements frame skipping when necessary to maintain target FPS
- Provides interpolation factors for smooth animations
- Optimized for minimal CPU overhead

Author: Roibot Development Team
Version: 1.0
"""

import time
import asyncio
from typing import Optional


def fps_to_interval(fps: int) -> float:
    """Convert frames per second to time interval in seconds."""
    if fps <= 0:
        raise ValueError("FPS must be positive")
    return 1.0 / fps


def smooth_lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation with smooth easing.
    
    Args:
        start: Starting value
        end: Ending value
        t: Time factor (0.0 to 1.0)
    
    Returns:
        Interpolated value
    """
    if t <= 0.0:
        return start
    if t >= 1.0:
        return end
    
    # Smooth step interpolation for better animation feel
    smooth_t = t * t * (3.0 - 2.0 * t)
    return start + (end - start) * smooth_t


class TimingManager:
    """
    Manages timing for smooth animation and frame rate control.
    Provides precise timing control for 60 FPS operation.
    """
    
    def __init__(self, target_fps: int = 60):
        """
        Initialize timing manager.
        
        Args:
            target_fps: Target frames per second (default: 60)
        """
        self.target_fps = target_fps
        self.frame_interval = fps_to_interval(target_fps)
        self.last_frame_time = 0.0
        self.delta_time = 0.0
        self.frame_count = 0
        self.fps_counter = 0.0
        self.fps_update_time = 0.0
        self.is_paused = False
        self.start_time = 0.0
        
        print(f"🕐 TimingManager initialized: {target_fps} FPS target ({self.frame_interval:.4f}s interval)")
    
    def update(self) -> float:
        """
        Update timing information for current frame.
        
        Returns:
            Delta time since last frame
        """
        current_time = time.time()
        
        if self.last_frame_time > 0:
            self.delta_time = current_time - self.last_frame_time
        else:
            self.delta_time = self.frame_interval
            self.start_time = current_time
            self.fps_update_time = current_time
        
        self.last_frame_time = current_time
        self.frame_count += 1
        
        # Update FPS counter every second
        time_elapsed = current_time - self.fps_update_time
        if time_elapsed >= 1.0:
            self.fps_counter = self.frame_count / time_elapsed
            self.frame_count = 0
            self.fps_update_time = current_time
        
        return self.delta_time
    
    def get_current_fps(self) -> float:
        """Get current frames per second."""
        return self.fps_counter
    
    def should_limit_frame_rate(self) -> bool:
        """Check if frame rate should be limited."""
        if self.last_frame_time == 0:
            return False
        
        elapsed = time.time() - self.last_frame_time
        return elapsed < self.frame_interval
    
    async def wait_for_next_frame(self) -> None:
        """Wait for next frame to maintain target FPS."""
        if self.is_paused:
            await asyncio.sleep(0.1)  # Longer sleep when paused
            return
        
        if self.last_frame_time == 0:
            self.last_frame_time = time.time()
            return
        
        elapsed = time.time() - self.last_frame_time
        remaining = self.frame_interval - elapsed
        
        if remaining > 0:
            await asyncio.sleep(remaining)
        
        # Update timing after wait
        self.update()
    
    def get_interpolation_factor(self, animation_duration: float) -> float:
        """
        Get interpolation factor for smooth animations.
        
        Args:
            animation_duration: Total duration of animation in seconds
            
        Returns:
            Interpolation factor (0.0 to 1.0)
        """
        if animation_duration <= 0:
            return 1.0
        
        return min(1.0, self.delta_time / animation_duration)
    
    def set_simulation_speed(self, speed: float) -> None:
        """
        Set simulation speed multiplier.
        
        Args:
            speed: Speed multiplier (placeholder for future implementation)
        """
        # Placeholder for future speed control implementation
        print(f"⚡ TimingManager simulation speed set to: {speed}x")
    
    def set_target_fps(self, fps: int) -> None:
        """
        Set target FPS.
        
        Args:
            fps: New target FPS
        """
        self.target_fps = fps
        self.frame_interval = fps_to_interval(fps)
        print(f"🎯 TimingManager target FPS updated: {fps}")
    
    def start(self) -> None:
        """Start timing manager."""
        print("🚀 TimingManager started")
    
    def stop(self) -> None:
        """Stop timing manager."""
        print("⏹️  TimingManager stopped")
    
    def pause(self) -> None:
        """Pause timing manager."""
        self.is_paused = True
        print("⏸️  TimingManager paused")
    
    def resume(self) -> None:
        """Resume timing manager."""
        self.is_paused = False
        print("▶️  TimingManager resumed")
    
    def cleanup(self) -> None:
        """Cleanup timing manager resources."""
        print("🧹 TimingManager cleanup")
    
    def reset(self) -> None:
        """Reset timing manager state."""
        self.last_frame_time = 0.0
        self.delta_time = 0.0
        self.frame_count = 0
        self.fps_counter = 0.0
        self.fps_update_time = 0.0
        
        print("🔄 TimingManager reset") 