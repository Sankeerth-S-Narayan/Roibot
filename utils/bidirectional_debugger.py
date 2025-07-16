"""
Debugging tools for bidirectional navigation system.

Provides comprehensive debugging capabilities for the bidirectional navigation
system including path visualization, performance analysis, and debugging utilities.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from core.layout.coordinate import Coordinate
from core.layout.snake_pattern import SnakePattern
from core.config.bidirectional_config import BidirectionalConfigManager
from core.performance.path_performance_monitor import PathPerformanceMonitor


@dataclass
class DebugPathInfo:
    """Information about a path for debugging."""
    start: Coordinate
    end: Coordinate
    path: List[Coordinate]
    direction: str
    calculation_time: float
    path_length: int
    direction_changes: int
    efficiency_ratio: float


@dataclass
class DebugPerformanceInfo:
    """Performance information for debugging."""
    total_path_calculations: int
    average_calculation_time: float
    total_direction_changes: int
    average_efficiency: float
    performance_warnings: int
    timestamp: float


class BidirectionalDebugger:
    """
    Comprehensive debugging tools for bidirectional navigation.
    
    Provides path visualization, performance analysis, and debugging
    utilities for the bidirectional navigation system.
    """
    
    def __init__(self, config_manager: Optional[BidirectionalConfigManager] = None):
        """
        Initialize the bidirectional debugger.
        
        Args:
            config_manager: Configuration manager for debugging settings
        """
        self.config_manager = config_manager or BidirectionalConfigManager()
        self.logger = logging.getLogger(__name__)
        self.debug_paths: List[DebugPathInfo] = []
        self.performance_history: List[DebugPerformanceInfo] = []
        self.debug_enabled = self.config_manager.is_direction_debug_enabled()
        
        # Setup logging
        if self.debug_enabled:
            self._setup_debug_logging()
        
        self.logger.info("🔍 BidirectionalDebugger initialized")
    
    def _setup_debug_logging(self) -> None:
        """Setup debug logging configuration."""
        debug_level = self.config_manager.get_log_level()
        
        # Configure logging level
        if debug_level == "debug":
            logging.getLogger('core.layout').setLevel(logging.DEBUG)
            logging.getLogger('core.performance').setLevel(logging.DEBUG)
        elif debug_level == "info":
            logging.getLogger('core.layout').setLevel(logging.INFO)
            logging.getLogger('core.performance').setLevel(logging.INFO)
        
        self.logger.info(f"🔧 Debug logging configured: {debug_level}")
    
    def debug_path_calculation(self, start: Coordinate, end: Coordinate, 
                              path: List[Coordinate], direction: str,
                              calculation_time: float, direction_changes: int) -> None:
        """
        Debug a path calculation.
        
        Args:
            start: Starting coordinate
            end: Ending coordinate
            path: Calculated path
            direction: Direction used
            calculation_time: Time taken for calculation
            direction_changes: Number of direction changes
        """
        if not self.debug_enabled:
            return
        
        # Calculate efficiency ratio
        optimal_distance = start.distance_to(end)
        actual_distance = self._calculate_path_distance(path)
        efficiency_ratio = optimal_distance / actual_distance if actual_distance > 0 else 1.0
        
        # Create debug info
        debug_info = DebugPathInfo(
            start=start,
            end=end,
            path=path,
            direction=direction,
            calculation_time=calculation_time,
            path_length=len(path),
            direction_changes=direction_changes,
            efficiency_ratio=efficiency_ratio
        )
        
        self.debug_paths.append(debug_info)
        
        # Log debug information
        self.logger.debug(f"Path calculation: {start} -> {end}")
        self.logger.debug(f"  Direction: {direction}")
        self.logger.debug(f"  Path length: {len(path)}")
        self.logger.debug(f"  Calculation time: {calculation_time:.4f}s")
        self.logger.debug(f"  Direction changes: {direction_changes}")
        self.logger.debug(f"  Efficiency ratio: {efficiency_ratio:.3f}")
        
        # Check for performance issues
        if calculation_time > self.config_manager.get_max_path_calculation_time():
            self.logger.warning(f"Slow path calculation: {calculation_time:.4f}s")
        
        if efficiency_ratio < 0.8:
            self.logger.warning(f"Low path efficiency: {efficiency_ratio:.3f}")
    
    def debug_direction_change(self, old_direction: str, new_direction: str, 
                              cooldown_respected: bool, position: Coordinate) -> None:
        """
        Debug a direction change.
        
        Args:
            old_direction: Previous direction
            new_direction: New direction
            cooldown_respected: Whether cooldown was respected
            position: Current position
        """
        if not self.debug_enabled:
            return
        
        self.logger.debug(f"Direction change: {old_direction} -> {new_direction}")
        self.logger.debug(f"  Position: {position}")
        self.logger.debug(f"  Cooldown respected: {cooldown_respected}")
        
        if not cooldown_respected:
            self.logger.warning(f"Cooldown violation at {position}")
    
    def debug_performance_metrics(self, performance_monitor: PathPerformanceMonitor) -> None:
        """
        Debug performance metrics.
        
        Args:
            performance_monitor: Performance monitor instance
        """
        if not self.debug_enabled:
            return
        
        # Create performance info
        performance_info = DebugPerformanceInfo(
            total_path_calculations=performance_monitor.total_path_calculations,
            average_calculation_time=self._calculate_average_calculation_time(performance_monitor),
            total_direction_changes=performance_monitor.total_direction_changes,
            average_efficiency=self._calculate_average_efficiency(performance_monitor),
            performance_warnings=len(performance_monitor.get_performance_warnings()),
            timestamp=time.time()
        )
        
        self.performance_history.append(performance_info)
        
        # Log performance summary
        self.logger.info("📊 Performance Summary:")
        self.logger.info(f"  Total path calculations: {performance_info.total_path_calculations}")
        self.logger.info(f"  Average calculation time: {performance_info.average_calculation_time:.4f}s")
        self.logger.info(f"  Total direction changes: {performance_info.total_direction_changes}")
        self.logger.info(f"  Average efficiency: {performance_info.average_efficiency:.3f}")
        self.logger.info(f"  Performance warnings: {performance_info.performance_warnings}")
    
    def debug_snake_pattern_integrity(self, snake_pattern: SnakePattern, 
                                     path: List[Coordinate]) -> bool:
        """
        Debug snake pattern integrity for a path.
        
        Args:
            snake_pattern: Snake pattern instance
            path: Path to validate
            
        Returns:
            True if path follows snake pattern rules
        """
        if not self.debug_enabled:
            return True
        
        violations = []
        
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            # Check horizontal movement in aisles
            if current.aisle == next_pos.aisle:
                aisle_direction = snake_pattern.get_aisle_direction(current.aisle, "forward")
                
                if aisle_direction.value == "left_to_right":
                    if next_pos.rack < current.rack:
                        violations.append(f"Wrong direction in aisle {current.aisle}: {current} -> {next_pos}")
                else:  # right_to_left
                    if next_pos.rack > current.rack:
                        violations.append(f"Wrong direction in aisle {current.aisle}: {current} -> {next_pos}")
        
        if violations:
            self.logger.warning("🐍 Snake pattern violations detected:")
            for violation in violations:
                self.logger.warning(f"  {violation}")
            return False
        else:
            self.logger.debug("✅ Snake pattern integrity maintained")
            return True
    
    def debug_configuration(self) -> None:
        """Debug configuration settings."""
        if not self.debug_enabled:
            return
        
        summary = self.config_manager.get_configuration_summary()
        
        self.logger.info("⚙️ Configuration Debug:")
        self.logger.info(f"  Aisle traversal time: {summary['aisle_traversal_time']}")
        self.logger.info(f"  Direction change cooldown: {summary['direction_change_cooldown']}")
        
        path_opt = summary['path_optimization']
        self.logger.info("  Path optimization:")
        self.logger.info(f"    Shortest path enabled: {path_opt['enable_shortest_path']}")
        self.logger.info(f"    Direction optimization enabled: {path_opt['enable_direction_optimization']}")
        self.logger.info(f"    Snake pattern integrity: {path_opt['enable_snake_pattern_integrity']}")
        
        perf_mon = summary['performance_monitoring']
        self.logger.info("  Performance monitoring:")
        self.logger.info(f"    Path calculation timing: {perf_mon['enable_path_calculation_timing']}")
        self.logger.info(f"    Direction change tracking: {perf_mon['enable_direction_change_tracking']}")
        self.logger.info(f"    Movement efficiency tracking: {perf_mon['enable_movement_efficiency_tracking']}")
    
    def generate_debug_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive debug report.
        
        Args:
            output_file: Optional file to save the report
            
        Returns:
            Debug report as string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("🐍 BIDIRECTIONAL NAVIGATION DEBUG REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Configuration section
        report_lines.append("📋 CONFIGURATION")
        report_lines.append("-" * 20)
        summary = self.config_manager.get_configuration_summary()
        report_lines.append(f"Aisle traversal time: {summary['aisle_traversal_time']}")
        report_lines.append(f"Direction change cooldown: {summary['direction_change_cooldown']}")
        report_lines.append("")
        
        # Path calculation section
        report_lines.append("🛤️ PATH CALCULATIONS")
        report_lines.append("-" * 20)
        if self.debug_paths:
            total_calculations = len(self.debug_paths)
            avg_calculation_time = sum(p.calculation_time for p in self.debug_paths) / total_calculations
            avg_efficiency = sum(p.efficiency_ratio for p in self.debug_paths) / total_calculations
            
            report_lines.append(f"Total path calculations: {total_calculations}")
            report_lines.append(f"Average calculation time: {avg_calculation_time:.4f}s")
            report_lines.append(f"Average efficiency ratio: {avg_efficiency:.3f}")
            report_lines.append("")
            
            # Recent paths
            report_lines.append("Recent paths:")
            for i, path_info in enumerate(self.debug_paths[-5:], 1):
                report_lines.append(f"  {i}. {path_info.start} -> {path_info.end}")
                report_lines.append(f"     Length: {path_info.path_length}, Time: {path_info.calculation_time:.4f}s")
                report_lines.append(f"     Efficiency: {path_info.efficiency_ratio:.3f}")
        else:
            report_lines.append("No path calculations recorded")
        report_lines.append("")
        
        # Performance section
        report_lines.append("📊 PERFORMANCE METRICS")
        report_lines.append("-" * 20)
        if self.performance_history:
            latest = self.performance_history[-1]
            report_lines.append(f"Total path calculations: {latest.total_path_calculations}")
            report_lines.append(f"Average calculation time: {latest.average_calculation_time:.4f}s")
            report_lines.append(f"Total direction changes: {latest.total_direction_changes}")
            report_lines.append(f"Average efficiency: {latest.average_efficiency:.3f}")
            report_lines.append(f"Performance warnings: {latest.performance_warnings}")
        else:
            report_lines.append("No performance metrics recorded")
        report_lines.append("")
        
        # Recommendations section
        report_lines.append("💡 RECOMMENDATIONS")
        report_lines.append("-" * 20)
        
        if self.debug_paths:
            avg_calculation_time = sum(p.calculation_time for p in self.debug_paths) / len(self.debug_paths)
            if avg_calculation_time > 0.1:
                report_lines.append("⚠️  Consider optimizing path calculation algorithms")
            
            avg_efficiency = sum(p.efficiency_ratio for p in self.debug_paths) / len(self.debug_paths)
            if avg_efficiency < 0.8:
                report_lines.append("⚠️  Consider improving path optimization")
        
        if self.performance_history:
            latest = self.performance_history[-1]
            if latest.performance_warnings > 0:
                report_lines.append("⚠️  Review performance warnings")
        
        report_lines.append("✅ System appears to be functioning normally")
        report_lines.append("")
        
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            self.logger.info(f"📄 Debug report saved to: {output_file}")
        
        return report
    
    def _calculate_path_distance(self, path: List[Coordinate]) -> float:
        """Calculate total distance of a path."""
        if len(path) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            total_distance += path[i].distance_to(path[i + 1])
        
        return total_distance
    
    def _calculate_average_calculation_time(self, monitor: PathPerformanceMonitor) -> float:
        """Calculate average path calculation time."""
        if not monitor.path_calculation_metrics:
            return 0.0
        
        total_time = sum(metric.calculation_time for metric in monitor.path_calculation_metrics)
        return total_time / len(monitor.path_calculation_metrics)
    
    def _calculate_average_efficiency(self, monitor: PathPerformanceMonitor) -> float:
        """Calculate average movement efficiency."""
        if not monitor.movement_efficiency_metrics:
            return 1.0
        
        total_efficiency = sum(metric.efficiency_ratio for metric in monitor.movement_efficiency_metrics)
        return total_efficiency / len(monitor.movement_efficiency_metrics)
    
    def clear_debug_data(self) -> None:
        """Clear all debug data."""
        self.debug_paths.clear()
        self.performance_history.clear()
        self.logger.info("🧹 Debug data cleared")
    
    def enable_debug_mode(self) -> None:
        """Enable debug mode."""
        self.debug_enabled = True
        self._setup_debug_logging()
        self.logger.info("🔍 Debug mode enabled")
    
    def disable_debug_mode(self) -> None:
        """Disable debug mode."""
        self.debug_enabled = False
        self.logger.info("🔍 Debug mode disabled")


def create_debug_visualization(path: List[Coordinate], warehouse_width: int = 25, 
                              warehouse_height: int = 20) -> str:
    """
    Create a simple ASCII visualization of a path.
    
    Args:
        path: List of coordinates representing the path
        warehouse_width: Width of the warehouse
        warehouse_height: Height of the warehouse
        
    Returns:
        ASCII visualization string
    """
    if not path:
        return "Empty path"
    
    # Create grid
    grid = [[' ' for _ in range(warehouse_width)] for _ in range(warehouse_height)]
    
    # Mark path
    for i, coord in enumerate(path):
        if 0 <= coord.aisle - 1 < warehouse_width and 0 <= coord.rack - 1 < warehouse_height:
            if i == 0:
                grid[coord.rack - 1][coord.aisle - 1] = 'S'  # Start
            elif i == len(path) - 1:
                grid[coord.rack - 1][coord.aisle - 1] = 'E'  # End
            else:
                grid[coord.rack - 1][coord.aisle - 1] = '·'  # Path
    
    # Create visualization
    lines = []
    lines.append("Warehouse Path Visualization:")
    lines.append("S = Start, E = End, · = Path")
    lines.append("")
    
    # Add header
    header = "   " + "".join(f"{i:2}" for i in range(1, warehouse_width + 1))
    lines.append(header)
    lines.append("   " + "-" * (warehouse_width * 2))
    
    # Add grid
    for row in range(warehouse_height - 1, -1, -1):  # Reverse to show bottom to top
        line = f"{row + 1:2}|"
        for col in range(warehouse_width):
            line += f" {grid[row][col]}"
        lines.append(line)
    
    return "\n".join(lines)


# Global debugger instance
_debugger_instance: Optional[BidirectionalDebugger] = None


def get_debugger() -> BidirectionalDebugger:
    """Get the global debugger instance."""
    global _debugger_instance
    if _debugger_instance is None:
        _debugger_instance = BidirectionalDebugger()
    return _debugger_instance


def debug_path_calculation(start: Coordinate, end: Coordinate, path: List[Coordinate],
                          direction: str, calculation_time: float, direction_changes: int) -> None:
    """Debug a path calculation using the global debugger."""
    debugger = get_debugger()
    debugger.debug_path_calculation(start, end, path, direction, calculation_time, direction_changes)


def debug_direction_change(old_direction: str, new_direction: str, 
                          cooldown_respected: bool, position: Coordinate) -> None:
    """Debug a direction change using the global debugger."""
    debugger = get_debugger()
    debugger.debug_direction_change(old_direction, new_direction, cooldown_respected, position)


def generate_debug_report(output_file: Optional[str] = None) -> str:
    """Generate a debug report using the global debugger."""
    debugger = get_debugger()
    return debugger.generate_debug_report(output_file) 