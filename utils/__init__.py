"""
Utilities package for Roibot warehouse robot simulation.

This package contains utility functions and helpers:
- Timing utilities for smooth animations
- Math utilities for calculations
- Helper functions for common operations
"""

from .timing import TimingManager, fps_to_interval, smooth_lerp

__all__ = [
    'TimingManager',
    'fps_to_interval', 
    'smooth_lerp'
] 