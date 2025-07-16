"""
Performance monitoring for path calculation and bidirectional navigation.

Tracks performance metrics for path calculation, direction changes,
movement efficiency, and provides performance warnings and optimization
suggestions.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import statistics


@dataclass
class PathCalculationMetrics:
    """Metrics for path calculation performance."""
    calculation_time: float
    path_length: int
    direction_changes: int
    optimization_level: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class DirectionChangeMetrics:
    """Metrics for direction change performance."""
    change_time: float
    old_direction: str
    new_direction: str
    cooldown_respected: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class MovementEfficiencyMetrics:
    """Metrics for movement efficiency."""
    distance_traveled: float
    optimal_distance: float
    efficiency_ratio: float
    movement_time: float
    timestamp: float = field(default_factory=time.time)


class PathPerformanceMonitor:
    """
    Monitors performance of path calculation and bidirectional navigation.
    
    Tracks various performance metrics including path calculation time,
    direction changes, movement efficiency, and provides performance
    warnings and optimization suggestions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the path performance monitor.
        
        Args:
            config: Configuration dictionary for performance monitoring
        """
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_path_calculation_timing = config.get("enable_path_calculation_timing", True) if config else True
        self.enable_direction_change_tracking = config.get("enable_direction_change_tracking", True) if config else True
        self.enable_movement_efficiency_tracking = config.get("enable_movement_efficiency_tracking", True) if config else True
        self.performance_warning_threshold = config.get("performance_warning_threshold", 0.05) if config else 0.05
        
        # Performance metrics storage
        self.path_calculation_metrics: deque = deque(maxlen=100)
        self.direction_change_metrics: deque = deque(maxlen=100)
        self.movement_efficiency_metrics: deque = deque(maxlen=100)
        
        # Performance statistics
        self.total_path_calculations = 0
        self.total_direction_changes = 0
        self.total_movements = 0
        
        # Performance warnings
        self.performance_warnings: List[str] = []
        
        self.logger.info("Path performance monitor initialized")
    
    def start_path_calculation_timing(self) -> float:
        """
        Start timing a path calculation.
        
        Returns:
            Start timestamp
        """
        if not self.enable_path_calculation_timing:
            return 0.0
        return time.time()
    
    def end_path_calculation_timing(self, start_time: float, path_length: int, 
                                   direction_changes: int, optimization_level: str = "standard") -> None:
        """
        End timing a path calculation and record metrics.
        
        Args:
            start_time: Start timestamp from start_path_calculation_timing
            path_length: Number of coordinates in the calculated path
            direction_changes: Number of direction changes in the path
            optimization_level: Level of optimization applied
        """
        if not self.enable_path_calculation_timing or start_time == 0.0:
            return
        
        calculation_time = time.time() - start_time
        metrics = PathCalculationMetrics(
            calculation_time=calculation_time,
            path_length=path_length,
            direction_changes=direction_changes,
            optimization_level=optimization_level
        )
        
        self.path_calculation_metrics.append(metrics)
        self.total_path_calculations += 1
        
        # Check for performance warnings
        if calculation_time > self.performance_warning_threshold:
            warning = f"Path calculation took {calculation_time:.3f}s (threshold: {self.performance_warning_threshold:.3f}s)"
            self.performance_warnings.append(warning)
            self.logger.warning(warning)
    
    def record_direction_change(self, old_direction: str, new_direction: str, 
                              cooldown_respected: bool) -> None:
        """
        Record a direction change event.
        
        Args:
            old_direction: Previous direction
            new_direction: New direction
            cooldown_respected: Whether cooldown was respected
        """
        if not self.enable_direction_change_tracking:
            return
        
        metrics = DirectionChangeMetrics(
            change_time=time.time(),
            old_direction=old_direction,
            new_direction=new_direction,
            cooldown_respected=cooldown_respected
        )
        
        self.direction_change_metrics.append(metrics)
        self.total_direction_changes += 1
        
        if not cooldown_respected:
            warning = f"Direction change cooldown violated: {old_direction} -> {new_direction}"
            self.performance_warnings.append(warning)
            self.logger.warning(warning)
    
    def record_movement_efficiency(self, distance_traveled: float, optimal_distance: float,
                                 movement_time: float) -> None:
        """
        Record movement efficiency metrics.
        
        Args:
            distance_traveled: Actual distance traveled
            optimal_distance: Optimal distance for the movement
            movement_time: Time taken for the movement
        """
        if not self.enable_movement_efficiency_tracking:
            return
        
        efficiency_ratio = optimal_distance / distance_traveled if distance_traveled > 0 else 1.0
        metrics = MovementEfficiencyMetrics(
            distance_traveled=distance_traveled,
            optimal_distance=optimal_distance,
            efficiency_ratio=efficiency_ratio,
            movement_time=movement_time
        )
        
        self.movement_efficiency_metrics.append(metrics)
        self.total_movements += 1
        
        # Check for efficiency warnings
        if efficiency_ratio < 0.8:  # Less than 80% efficient
            warning = f"Low movement efficiency: {efficiency_ratio:.2f} (traveled: {distance_traveled:.2f}, optimal: {optimal_distance:.2f})"
            self.performance_warnings.append(warning)
            self.logger.warning(warning)
    
    def get_path_calculation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for path calculation performance.
        
        Returns:
            Dictionary containing path calculation statistics
        """
        if not self.path_calculation_metrics:
            return {
                "total_calculations": 0,
                "avg_calculation_time": 0.0,
                "max_calculation_time": 0.0,
                "min_calculation_time": 0.0,
                "avg_path_length": 0,
                "avg_direction_changes": 0
            }
        
        calculation_times = [m.calculation_time for m in self.path_calculation_metrics]
        path_lengths = [m.path_length for m in self.path_calculation_metrics]
        direction_changes = [m.direction_changes for m in self.path_calculation_metrics]
        
        return {
            "total_calculations": len(self.path_calculation_metrics),
            "avg_calculation_time": statistics.mean(calculation_times),
            "max_calculation_time": max(calculation_times),
            "min_calculation_time": min(calculation_times),
            "avg_path_length": statistics.mean(path_lengths),
            "avg_direction_changes": statistics.mean(direction_changes),
            "recent_calculations": len(self.path_calculation_metrics)
        }
    
    def get_direction_change_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for direction change performance.
        
        Returns:
            Dictionary containing direction change statistics
        """
        if not self.direction_change_metrics:
            return {
                "total_changes": 0,
                "cooldown_violations": 0,
                "direction_frequency": {}
            }
        
        cooldown_violations = sum(1 for m in self.direction_change_metrics if not m.cooldown_respected)
        direction_frequency = {}
        
        for metrics in self.direction_change_metrics:
            change_key = f"{metrics.old_direction}->{metrics.new_direction}"
            direction_frequency[change_key] = direction_frequency.get(change_key, 0) + 1
        
        return {
            "total_changes": len(self.direction_change_metrics),
            "cooldown_violations": cooldown_violations,
            "cooldown_compliance_rate": (len(self.direction_change_metrics) - cooldown_violations) / len(self.direction_change_metrics),
            "direction_frequency": direction_frequency,
            "recent_changes": len(self.direction_change_metrics)
        }
    
    def get_movement_efficiency_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for movement efficiency.
        
        Returns:
            Dictionary containing movement efficiency statistics
        """
        if not self.movement_efficiency_metrics:
            return {
                "total_movements": 0,
                "avg_efficiency": 0.0,
                "avg_distance_traveled": 0.0,
                "avg_movement_time": 0.0
            }
        
        efficiency_ratios = [m.efficiency_ratio for m in self.movement_efficiency_metrics]
        distances = [m.distance_traveled for m in self.movement_efficiency_metrics]
        movement_times = [m.movement_time for m in self.movement_efficiency_metrics]
        
        return {
            "total_movements": len(self.movement_efficiency_metrics),
            "avg_efficiency": statistics.mean(efficiency_ratios),
            "min_efficiency": min(efficiency_ratios),
            "max_efficiency": max(efficiency_ratios),
            "avg_distance_traveled": statistics.mean(distances),
            "avg_movement_time": statistics.mean(movement_times),
            "recent_movements": len(self.movement_efficiency_metrics)
        }
    
    def get_performance_warnings(self) -> List[str]:
        """
        Get current performance warnings.
        
        Returns:
            List of performance warning messages
        """
        return self.performance_warnings.copy()
    
    def clear_performance_warnings(self) -> None:
        """Clear all performance warnings."""
        self.performance_warnings.clear()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance summary.
        
        Returns:
            Dictionary containing comprehensive performance summary
        """
        return {
            "path_calculation": self.get_path_calculation_statistics(),
            "direction_changes": self.get_direction_change_statistics(),
            "movement_efficiency": self.get_movement_efficiency_statistics(),
            "performance_warnings": self.get_performance_warnings(),
            "total_metrics": {
                "path_calculations": self.total_path_calculations,
                "direction_changes": self.total_direction_changes,
                "movements": self.total_movements
            }
        }
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.path_calculation_metrics.clear()
        self.direction_change_metrics.clear()
        self.movement_efficiency_metrics.clear()
        self.performance_warnings.clear()
        self.total_path_calculations = 0
        self.total_direction_changes = 0
        self.total_movements = 0
        self.logger.info("Path performance metrics reset")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the performance monitor with new settings.
        
        Args:
            config: Configuration dictionary
        """
        self.enable_path_calculation_timing = config.get("enable_path_calculation_timing", True)
        self.enable_direction_change_tracking = config.get("enable_direction_change_tracking", True)
        self.enable_movement_efficiency_tracking = config.get("enable_movement_efficiency_tracking", True)
        self.performance_warning_threshold = config.get("performance_warning_threshold", 0.05)
        
        self.logger.info("Path performance monitor reconfigured")
    
    def print_performance_report(self) -> None:
        """Print a comprehensive performance report."""
        summary = self.get_performance_summary()
        
        print("\n📊 Path Performance Report")
        print("=" * 50)
        
        # Path calculation statistics
        path_stats = summary["path_calculation"]
        print(f"Path Calculations: {path_stats['total_calculations']}")
        print(f"  Avg Time: {path_stats['avg_calculation_time']:.3f}s")
        print(f"  Max Time: {path_stats['max_calculation_time']:.3f}s")
        print(f"  Avg Path Length: {path_stats['avg_path_length']:.1f}")
        print(f"  Avg Direction Changes: {path_stats['avg_direction_changes']:.1f}")
        
        # Direction change statistics
        dir_stats = summary["direction_changes"]
        print(f"\nDirection Changes: {dir_stats['total_changes']}")
        print(f"  Cooldown Violations: {dir_stats['cooldown_violations']}")
        print(f"  Compliance Rate: {dir_stats['cooldown_compliance_rate']:.1%}")
        
        # Movement efficiency statistics
        move_stats = summary["movement_efficiency"]
        print(f"\nMovement Efficiency: {move_stats['total_movements']} movements")
        print(f"  Avg Efficiency: {move_stats['avg_efficiency']:.1%}")
        print(f"  Min Efficiency: {move_stats['min_efficiency']:.1%}")
        print(f"  Avg Distance: {move_stats['avg_distance_traveled']:.2f}")
        
        # Performance warnings
        warnings = summary["performance_warnings"]
        if warnings:
            print(f"\n⚠️  Performance Warnings ({len(warnings)}):")
            for warning in warnings[-5:]:  # Show last 5 warnings
                print(f"  - {warning}")
        
        print("=" * 50) 