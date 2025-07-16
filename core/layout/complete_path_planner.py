"""
Complete Path Planning System for Phase 4 Bidirectional Navigation.

Handles upfront path calculation for all items, path optimization for multiple items,
path execution tracking, validation, and integration with robot navigation system.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .coordinate import Coordinate
from .bidirectional_path_calculator import BidirectionalPathCalculator, CompletePath, Direction
from .warehouse_layout import WarehouseLayoutManager
from .snake_pattern import SnakePattern
from .aisle_timing_manager import AisleTimingManager


class PathExecutionStatus(Enum):
    """Status of path execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class PathExecutionState:
    """State of path execution."""
    current_segment_index: int = 0
    current_item_index: int = 0
    start_time: float = 0.0
    elapsed_time: float = 0.0
    status: PathExecutionStatus = PathExecutionStatus.NOT_STARTED
    completed_segments: List[int] = None
    collected_items: List[Coordinate] = None
    
    def __post_init__(self):
        if self.completed_segments is None:
            self.completed_segments = []
        if self.collected_items is None:
            self.collected_items = []


class CompletePathPlanner:
    """
    Complete path planning system for robot navigation.
    
    Features:
    - Upfront path calculation for all items
    - Path optimization for multiple items
    - Path execution tracking
    - Path validation and error handling
    - Integration with robot navigation system
    """
    
    def __init__(self, warehouse_layout: WarehouseLayoutManager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize complete path planner.
        
        Args:
            warehouse_layout: Warehouse layout manager
            config: Configuration dictionary
        """
        self.warehouse_layout = warehouse_layout
        self.snake_pattern = SnakePattern(max_aisle=25, max_rack=20)
        self.path_calculator = BidirectionalPathCalculator(warehouse_layout, self.snake_pattern, config)
        self.timing_manager = AisleTimingManager(config)
        
        # Path execution state
        self.current_path: Optional[CompletePath] = None
        self.execution_state = PathExecutionState()
        
        # Path history and statistics
        self.path_history: List[CompletePath] = []
        self.execution_history: List[PathExecutionState] = []
        
        print("✅ CompletePathPlanner initialized")
    
    def plan_complete_path(self, start_pos: Coordinate, item_positions: List[Coordinate]) -> CompletePath:
        """
        Plan complete path for all items upfront.
        
        Args:
            start_pos: Starting position of robot
            item_positions: List of item positions to collect
            
        Returns:
            CompletePath object with optimized path
        """
        if not item_positions:
            return CompletePath([], 0.0, 0.0, 0, [], [])
        
        print(f"🎯 Planning complete path for {len(item_positions)} items...")
        
        # Calculate complete path using bidirectional path calculator
        complete_path = self.path_calculator.calculate_complete_path_for_items(start_pos, item_positions)
        
        # Validate the path
        if not self.validate_path(complete_path):
            raise ValueError("Generated path is invalid")
        
        # Store path for execution
        self.current_path = complete_path
        self.execution_state = PathExecutionState()
        
        # Print path statistics
        stats = self.get_path_statistics(complete_path)
        print(f"✅ Path planned: {stats['total_distance']:.1f} units, {stats['total_duration']:.1f}s")
        print(f"✅ Items to collect: {len(complete_path.items_to_collect)}")
        print(f"✅ Direction changes: {complete_path.direction_changes}")
        
        return complete_path
    
    def start_path_execution(self, start_time: Optional[float] = None) -> bool:
        """
        Start executing the planned path.
        
        Args:
            start_time: Optional start time (defaults to current time)
            
        Returns:
            True if execution started successfully
        """
        if not self.current_path:
            print("❌ No path available for execution")
            return False
        
        if self.execution_state.status == PathExecutionStatus.IN_PROGRESS:
            print("⚠️  Path execution already in progress")
            return False
        
        # Reset execution state if previous execution was completed
        if self.execution_state.status == PathExecutionStatus.COMPLETED:
            self.execution_state = PathExecutionState()
        
        # Initialize execution state
        self.execution_state.start_time = start_time or time.time()
        self.execution_state.status = PathExecutionStatus.IN_PROGRESS
        self.execution_state.current_segment_index = 0
        self.execution_state.current_item_index = 0
        self.execution_state.completed_segments = []
        self.execution_state.collected_items = []
        
        print(f"🚀 Starting path execution at {self.execution_state.start_time}")
        return True
    
    def update_path_execution(self, current_time: float) -> Dict[str, Any]:
        """
        Update path execution progress.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Dictionary with execution update data
        """
        if not self.current_path or self.execution_state.status != PathExecutionStatus.IN_PROGRESS:
            return {"status": "no_execution"}
        
        # Update elapsed time
        self.execution_state.elapsed_time = current_time - self.execution_state.start_time
        
        # Get current segment
        current_segment = self.current_path.segments[self.execution_state.current_segment_index]
        
        # Check if current segment is completed
        segment_start_time = self.execution_state.start_time
        for i in range(self.execution_state.current_segment_index):
            segment_start_time += self.current_path.segments[i].duration
        
        segment_elapsed = current_time - segment_start_time
        
        if segment_elapsed >= current_segment.duration:
            # Segment completed
            self._complete_current_segment()
            
            # Check if all segments are now completed
            if self.execution_state.current_segment_index >= len(self.current_path.segments):
                self._complete_path_execution()
                return {
                    "status": "completed",
                    "total_time": self.execution_state.elapsed_time,
                    "collected_items": len(self.execution_state.collected_items)
                }
            
            return {
                "status": "segment_completed",
                "segment_index": self.execution_state.current_segment_index - 1,
                "total_segments": len(self.current_path.segments),
                "progress": self.execution_state.current_segment_index / len(self.current_path.segments)
            }
        else:
            # Segment in progress
            progress = segment_elapsed / current_segment.duration
            return {
                "status": "in_progress",
                "segment_index": self.execution_state.current_segment_index,
                "progress": progress,
                "elapsed": segment_elapsed,
                "remaining": current_segment.duration - segment_elapsed
            }
    
    def pause_path_execution(self) -> bool:
        """Pause path execution."""
        if self.execution_state.status == PathExecutionStatus.IN_PROGRESS:
            self.execution_state.status = PathExecutionStatus.PAUSED
            print("⏸️  Path execution paused")
            return True
        return False
    
    def resume_path_execution(self) -> bool:
        """Resume path execution."""
        if self.execution_state.status == PathExecutionStatus.PAUSED:
            self.execution_state.status = PathExecutionStatus.IN_PROGRESS
            print("▶️  Path execution resumed")
            return True
        return False
    
    def stop_path_execution(self) -> bool:
        """Stop path execution."""
        if self.execution_state.status in [PathExecutionStatus.IN_PROGRESS, PathExecutionStatus.PAUSED]:
            self.execution_state.status = PathExecutionStatus.FAILED
            print("⏹️  Path execution stopped")
            return True
        return False
    
    def get_execution_progress(self) -> float:
        """Get overall execution progress (0.0 to 1.0)."""
        if not self.current_path:
            return 0.0
        
        return self.execution_state.current_segment_index / len(self.current_path.segments)
    
    def get_current_segment(self) -> Optional[Any]:
        """Get current path segment being executed."""
        if not self.current_path or self.execution_state.current_segment_index >= len(self.current_path.segments):
            return None
        
        return self.current_path.segments[self.execution_state.current_segment_index]
    
    def get_next_target_position(self) -> Optional[Coordinate]:
        """Get the next target position for the robot."""
        current_segment = self.get_current_segment()
        if current_segment:
            return current_segment.end
        return None
    
    def validate_path(self, path: CompletePath) -> bool:
        """
        Validate that a path is valid for execution.
        
        Args:
            path: CompletePath to validate
            
        Returns:
            True if path is valid
        """
        if not path.segments:
            return True  # Empty path is valid
        
        # Validate using path calculator
        return self.path_calculator.validate_path(path)
    
    def get_path_statistics(self, path: CompletePath) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a path.
        
        Args:
            path: CompletePath to analyze
            
        Returns:
            Dictionary with path statistics
        """
        return self.path_calculator.get_path_statistics(path)
    
    def optimize_item_order(self, item_positions: List[Coordinate]) -> List[Coordinate]:
        """
        Optimize the order of items for collection.
        
        Args:
            item_positions: List of item positions
            
        Returns:
            Optimized list of item positions
        """
        if not item_positions:
            return []
        
        # For now, use ascending order as per requirements
        # In future phases, this could implement more sophisticated optimization
        return sorted(item_positions, key=lambda pos: (pos.aisle, pos.rack))
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0.0,
                "total_items_collected": 0
            }
        
        total_executions = len(self.execution_history)
        successful = sum(1 for state in self.execution_history if state.status == PathExecutionStatus.COMPLETED)
        failed = sum(1 for state in self.execution_history if state.status == PathExecutionStatus.FAILED)
        
        total_time = sum(state.elapsed_time for state in self.execution_history if state.elapsed_time > 0)
        avg_time = total_time / total_executions if total_executions > 0 else 0.0
        
        total_items = sum(len(state.collected_items) for state in self.execution_history)
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "average_execution_time": avg_time,
            "total_items_collected": total_items
        }
    
    def _complete_current_segment(self) -> None:
        """Complete the current path segment."""
        if not self.current_path:
            return
        
        segment_index = self.execution_state.current_segment_index
        if segment_index >= len(self.current_path.segments):
            return
        
        # Mark segment as completed
        self.execution_state.completed_segments.append(segment_index)
        
        # Check if this segment leads to an item collection
        current_segment = self.current_path.segments[segment_index]
        if current_segment.end in self.current_path.items_to_collect:
            self.execution_state.collected_items.append(current_segment.end)
            print(f"📦 Item collected at {current_segment.end}")
        
        # Move to next segment
        self.execution_state.current_segment_index += 1
        
        print(f"✅ Segment {segment_index} completed")
    
    def _complete_path_execution(self) -> None:
        """Complete the entire path execution."""
        self.execution_state.status = PathExecutionStatus.COMPLETED
        
        # Add to history
        self.path_history.append(self.current_path)
        self.execution_history.append(self.execution_state)
        
        print(f"🎉 Path execution completed in {self.execution_state.elapsed_time:.2f}s")
        print(f"📦 Collected {len(self.execution_state.collected_items)} items")
        
        # Don't reset immediately - let the caller check the status first
        # Reset will happen when starting a new execution 