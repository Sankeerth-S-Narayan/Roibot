from enum import Enum, auto

class RobotState(Enum):
    """Enumeration for robot states."""
    IDLE = auto()
    MOVING_TO_ITEM = auto()
    COLLECTING_ITEM = auto()
    RETURNING = auto() 