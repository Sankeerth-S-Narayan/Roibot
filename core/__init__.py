"""
Core simulation engine package for Roibot warehouse robot simulation.

This package contains the fundamental components for the simulation engine:
- SimulationEngine: Main simulation coordinator
- State management: Centralized state handling with configuration integration
- Event system: Event-driven architecture components
- Configuration: Robust configuration management with validation
- Controls: Enhanced simulation controls and interactive interface
- Validation: Input validation and error handling
"""

from .engine import SimulationEngine
from .state import SimulationState, SimulationStatus
from .events import EventSystem, EventType, Event
from .main_config import ConfigurationManager, ConfigSection, get_config
from .controls import SimulationController, ControlCommand
from .validation import SimulationValidator, ValidationError, ErrorSeverity

__all__ = [
    'SimulationEngine',
    'SimulationState',
    'SimulationStatus',
    'EventSystem',
    'EventType',
    'Event',
    'ConfigurationManager',
    'ConfigSection',
    'get_config',
    'SimulationController',
    'ControlCommand',
    'SimulationValidator',
    'ValidationError',
    'ErrorSeverity'
] 