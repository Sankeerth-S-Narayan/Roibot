"""
Robot Performance Analytics Module

This module provides specialized analytics for robot performance operations,
including movement efficiency, path optimization, utilization tracking, and state transitions.
"""

import time
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from .analytics_engine import AnalyticsEngine, MetricData, KPICalculation


class RobotState(Enum):
    """Robot state enumeration for analytics tracking."""
    IDLE = "idle"
    MOVING = "moving"
    PICKING = "picking"
    COLLECTING = "collecting"
    RETURNING = "returning"
    CHARGING = "charging"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class RobotAnalyticsData:
    """Data structure for robot analytics information."""
    robot_id: str
    current_state: RobotState
    current_position: Tuple[int, int]
    start_time: float
    last_state_change: float
    total_distance_moved: float = 0.0
    total_items_collected: int = 0
    total_orders_completed: int = 0
    idle_time: float = 0.0
    moving_time: float = 0.0
    picking_time: float = 0.0
    collecting_time: float = 0.0
    charging_time: float = 0.0
    error_time: float = 0.0
    path_optimization_savings: float = 0.0
    metadata: Dict = field(default_factory=dict)


class RobotAnalytics:
    """
    Specialized analytics for robot performance operations.
    
    Provides real-time tracking of robot efficiency, path optimization,
    utilization rates, and performance metrics.
    """
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        """
        Initialize RobotAnalytics with analytics engine.
        
        Args:
            analytics_engine: Core analytics engine for data collection
        """
        self.analytics = analytics_engine
        self.robots: Dict[str, RobotAnalyticsData] = {}
        self.state_transitions: List[Tuple[str, RobotState, RobotState, float]] = []
        self.movement_distances: List[float] = []
        self.path_optimizations: List[float] = []
        
        # Performance tracking
        self.last_calculation_time = time.time()
        self.calculation_interval = 5.0  # seconds
        
        # Initialize metrics
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize robot-specific metrics in the analytics engine."""
        # Robot performance metrics
        self.analytics.record_metric("total_robots", 0, "robot_performance")
        self.analytics.record_metric("active_robots", 0, "robot_performance")
        self.analytics.record_metric("idle_robots", 0, "robot_performance")
        
        # Movement metrics
        self.analytics.record_metric("total_distance_moved", 0.0, "robot_performance")
        self.analytics.record_metric("average_movement_speed", 0.0, "robot_performance")
        self.analytics.record_metric("movement_efficiency", 0.0, "robot_performance")
        
        # Utilization metrics
        self.analytics.record_metric("robot_utilization", 0.0, "robot_performance")
        self.analytics.record_metric("average_idle_time", 0.0, "robot_performance")
        self.analytics.record_metric("average_working_time", 0.0, "robot_performance")
        
        # Path optimization metrics
        self.analytics.record_metric("path_optimization_savings", 0.0, "robot_performance")
        self.analytics.record_metric("optimization_efficiency", 0.0, "robot_performance")
        self.analytics.record_metric("average_path_length", 0.0, "robot_performance")
        
        # Collection metrics
        self.analytics.record_metric("total_items_collected", 0, "robot_performance")
        self.analytics.record_metric("items_per_robot", 0.0, "robot_performance")
        self.analytics.record_metric("collection_efficiency", 0.0, "robot_performance")
        
        # Initialize internal counters
        self._total_robots = 0
        self._active_robots = 0
        self._idle_robots = 0
        self._total_distance = 0.0
        self._total_items_collected = 0
        self._total_path_savings = 0.0
    
    def track_robot_created(self, robot_id: str, initial_position: Tuple[int, int], metadata: Dict = None):
        """
        Track robot creation event.
        
        Args:
            robot_id: Unique robot identifier
            initial_position: Starting position (x, y)
            metadata: Additional robot metadata
        """
        current_time = time.time()
        
        robot_data = RobotAnalyticsData(
            robot_id=robot_id,
            current_state=RobotState.IDLE,
            current_position=initial_position,
            start_time=current_time,
            last_state_change=current_time,
            metadata=metadata or {}
        )
        
        self.robots[robot_id] = robot_data
        self._total_robots = len(self.robots)
        self._idle_robots += 1
        
        # Update metrics
        self.analytics.record_metric("total_robots", self._total_robots, "robot_performance")
        self.analytics.record_metric("idle_robots", self._idle_robots, "robot_performance")
        
        self._update_robot_utilization()
    
    def track_robot_state_change(self, robot_id: str, new_state: RobotState, position: Tuple[int, int] = None):
        """
        Track robot state change event.
        
        Args:
            robot_id: Robot identifier
            new_state: New robot state
            position: Current position (optional)
        """
        if robot_id not in self.robots:
            return
        
        current_time = time.time()
        robot_data = self.robots[robot_id]
        old_state = robot_data.current_state
        
        # Calculate time spent in previous state
        time_in_previous_state = current_time - robot_data.last_state_change
        
        # Update state-specific time counters
        if old_state == RobotState.IDLE:
            robot_data.idle_time += time_in_previous_state
        elif old_state == RobotState.MOVING:
            robot_data.moving_time += time_in_previous_state
        elif old_state == RobotState.PICKING:
            robot_data.picking_time += time_in_previous_state
        elif old_state == RobotState.COLLECTING:
            robot_data.collecting_time += time_in_previous_state
        elif old_state == RobotState.CHARGING:
            robot_data.charging_time += time_in_previous_state
        elif old_state == RobotState.ERROR:
            robot_data.error_time += time_in_previous_state
        
        # Update robot state
        robot_data.current_state = new_state
        robot_data.last_state_change = current_time
        
        if position:
            robot_data.current_position = position
        
        # Record state transition
        self.state_transitions.append((robot_id, old_state, new_state, current_time))
        
        # Update robot counts
        self._update_robot_counts(old_state, new_state)
        
        # Update metrics
        self._update_robot_utilization()
        self._update_average_times()
    
    def track_robot_movement(self, robot_id: str, distance: float, path_optimization_savings: float = 0.0):
        """
        Track robot movement event.
        
        Args:
            robot_id: Robot identifier
            distance: Distance moved in units
            path_optimization_savings: Distance/time saved through path optimization
        """
        if robot_id not in self.robots:
            return
        
        robot_data = self.robots[robot_id]
        robot_data.total_distance_moved += distance
        robot_data.path_optimization_savings += path_optimization_savings
        
        self.movement_distances.append(distance)
        if path_optimization_savings > 0:
            self.path_optimizations.append(path_optimization_savings)
        
        # Update total distance
        self._total_distance += distance
        self._total_path_savings += path_optimization_savings
        
        # Update movement metrics
        self.analytics.record_metric("total_distance_moved", self._total_distance, "robot_performance")
        
        if self.movement_distances:
            avg_speed = statistics.mean(self.movement_distances)
            self.analytics.record_metric("average_movement_speed", avg_speed, "robot_performance")
        
        # Update path optimization metrics
        self.analytics.record_metric("path_optimization_savings", self._total_path_savings, "robot_performance")
        
        if self.path_optimizations:
            avg_optimization = statistics.mean(self.path_optimizations)
            self.analytics.record_metric("optimization_efficiency", avg_optimization, "robot_performance")
    
    def track_item_collected(self, robot_id: str, item_id: str, collection_time: float = 0.0):
        """
        Track item collection event.
        
        Args:
            robot_id: Robot identifier
            item_id: Item identifier
            collection_time: Time taken to collect item
        """
        if robot_id not in self.robots:
            return
        
        robot_data = self.robots[robot_id]
        robot_data.total_items_collected += 1
        
        self._total_items_collected += 1
        
        # Update collection metrics
        self.analytics.record_metric("total_items_collected", self._total_items_collected, "robot_performance")
        
        # Calculate items per robot
        if self._total_robots > 0:
            items_per_robot = self._total_items_collected / self._total_robots
            self.analytics.record_metric("items_per_robot", items_per_robot, "robot_performance")
        
        # Update collection efficiency
        if collection_time > 0:
            efficiency = 1.0 / collection_time  # items per second
            self.analytics.record_metric("collection_efficiency", efficiency, "robot_performance")
    
    def track_order_completed(self, robot_id: str, order_id: str, completion_time: float = 0.0):
        """
        Track order completion by robot.
        
        Args:
            robot_id: Robot identifier
            order_id: Order identifier
            completion_time: Time taken to complete order
        """
        if robot_id not in self.robots:
            return
        
        robot_data = self.robots[robot_id]
        robot_data.total_orders_completed += 1
    
    def _update_robot_counts(self, old_state: RobotState, new_state: RobotState):
        """Update robot count metrics based on state changes."""
        # Decrement old state count
        if old_state == RobotState.IDLE:
            self._idle_robots = max(0, self._idle_robots - 1)
        elif old_state in [RobotState.MOVING, RobotState.PICKING, RobotState.COLLECTING, RobotState.RETURNING]:
            self._active_robots = max(0, self._active_robots - 1)
        
        # Increment new state count
        if new_state == RobotState.IDLE:
            self._idle_robots += 1
        elif new_state in [RobotState.MOVING, RobotState.PICKING, RobotState.COLLECTING, RobotState.RETURNING]:
            self._active_robots += 1
        
        # Update metrics
        self.analytics.record_metric("active_robots", self._active_robots, "robot_performance")
        self.analytics.record_metric("idle_robots", self._idle_robots, "robot_performance")
    
    def _update_robot_utilization(self):
        """Update robot utilization rate."""
        if self._total_robots > 0:
            utilization_rate = (self._active_robots / self._total_robots) * 100.0
            self.analytics.record_metric("robot_utilization", utilization_rate, "robot_performance")
    
    def _update_average_times(self):
        """Update average time metrics."""
        idle_times = []
        working_times = []
        
        for robot_data in self.robots.values():
            idle_times.append(robot_data.idle_time)
            working_times.append(robot_data.moving_time + robot_data.picking_time + robot_data.collecting_time)
        
        if idle_times:
            avg_idle_time = statistics.mean(idle_times)
            self.analytics.record_metric("average_idle_time", avg_idle_time, "robot_performance")
        
        if working_times:
            avg_working_time = statistics.mean(working_times)
            self.analytics.record_metric("average_working_time", avg_working_time, "robot_performance")
    
    def get_robot_performance_summary(self) -> Dict:
        """
        Get comprehensive robot performance summary.
        
        Returns:
            Dictionary with all robot performance analytics data
        """
        # Calculate movement efficiency
        movement_efficiency = 0.0
        if self.movement_distances and self._total_distance > 0:
            # Efficiency based on average movement vs total distance
            avg_movement = statistics.mean(self.movement_distances)
            movement_efficiency = (avg_movement / self._total_distance) * 100.0
        
        # Calculate path optimization efficiency
        optimization_efficiency = 0.0
        if self.path_optimizations:
            optimization_efficiency = statistics.mean(self.path_optimizations)
        
        # Calculate collection efficiency
        collection_efficiency = 0.0
        if self._total_items_collected > 0 and self._total_robots > 0:
            collection_efficiency = self._total_items_collected / self._total_robots
        
        return {
            "total_robots": self._total_robots,
            "active_robots": self._active_robots,
            "idle_robots": self._idle_robots,
            "total_distance_moved": self._total_distance,
            "total_items_collected": self._total_items_collected,
            "total_path_savings": self._total_path_savings,
            "movement_efficiency": movement_efficiency,
            "optimization_efficiency": optimization_efficiency,
            "collection_efficiency": collection_efficiency,
            "robot_utilization": self.analytics.get_kpi("robot_performance.robot_utilization").value if self.analytics.get_kpi("robot_performance.robot_utilization") else 0.0,
            "average_movement_speed": self.analytics.get_kpi("robot_performance.average_movement_speed").value if self.analytics.get_kpi("robot_performance.average_movement_speed") else 0.0,
            "items_per_robot": self.analytics.get_kpi("robot_performance.items_per_robot").value if self.analytics.get_kpi("robot_performance.items_per_robot") else 0.0
        }
    
    def get_robot_state_distribution(self) -> Dict[str, int]:
        """
        Get current robot state distribution.
        
        Returns:
            Dictionary mapping state names to counts
        """
        state_counts = defaultdict(int)
        for robot_data in self.robots.values():
            state_counts[robot_data.current_state.value] += 1
        return dict(state_counts)
    
    def get_robot_analytics(self, robot_id: str) -> Optional[Dict]:
        """
        Get analytics for a specific robot.
        
        Args:
            robot_id: Robot identifier
            
        Returns:
            Dictionary with robot-specific analytics or None if robot not found
        """
        if robot_id not in self.robots:
            return None
        
        robot_data = self.robots[robot_id]
        current_time = time.time()
        total_time = current_time - robot_data.start_time
        
        # Calculate time spent in current state
        time_in_current_state = current_time - robot_data.last_state_change
        current_moving_time = robot_data.moving_time
        current_picking_time = robot_data.picking_time
        current_collecting_time = robot_data.collecting_time
        
        # Add current state time to the appropriate counter
        if robot_data.current_state == RobotState.MOVING:
            current_moving_time += time_in_current_state
        elif robot_data.current_state == RobotState.PICKING:
            current_picking_time += time_in_current_state
        elif robot_data.current_state == RobotState.COLLECTING:
            current_collecting_time += time_in_current_state
        
        return {
            "robot_id": robot_id,
            "current_state": robot_data.current_state.value,
            "current_position": robot_data.current_position,
            "total_distance_moved": robot_data.total_distance_moved,
            "total_items_collected": robot_data.total_items_collected,
            "total_orders_completed": robot_data.total_orders_completed,
            "path_optimization_savings": robot_data.path_optimization_savings,
            "idle_time": robot_data.idle_time,
            "moving_time": current_moving_time,
            "picking_time": current_picking_time,
            "collecting_time": current_collecting_time,
            "charging_time": robot_data.charging_time,
            "error_time": robot_data.error_time,
            "total_time": total_time,
            "utilization_rate": ((current_moving_time + current_picking_time + current_collecting_time) / total_time) * 100.0 if total_time > 0 else 0.0
        }
    
    def get_movement_analytics(self) -> Dict[str, float]:
        """
        Get movement analytics.
        
        Returns:
            Dictionary with movement metrics
        """
        return {
            "total_distance": self._total_distance,
            "average_movement": statistics.mean(self.movement_distances) if self.movement_distances else 0.0,
            "max_movement": max(self.movement_distances) if self.movement_distances else 0.0,
            "min_movement": min(self.movement_distances) if self.movement_distances else 0.0,
            "total_movements": len(self.movement_distances)
        }
    
    def get_path_optimization_analytics(self) -> Dict[str, float]:
        """
        Get path optimization analytics.
        
        Returns:
            Dictionary with path optimization metrics
        """
        return {
            "total_savings": self._total_path_savings,
            "average_savings": statistics.mean(self.path_optimizations) if self.path_optimizations else 0.0,
            "max_savings": max(self.path_optimizations) if self.path_optimizations else 0.0,
            "total_optimizations": len(self.path_optimizations)
        }
    
    def clear_analytics_data(self):
        """Clear all robot analytics data."""
        self.robots.clear()
        self.state_transitions.clear()
        self.movement_distances.clear()
        self.path_optimizations.clear()
        self.last_calculation_time = time.time()
        
        # Reset internal counters
        self._total_robots = 0
        self._active_robots = 0
        self._idle_robots = 0
        self._total_distance = 0.0
        self._total_items_collected = 0
        self._total_path_savings = 0.0
        
        # Reinitialize metrics
        self._initialize_metrics() 