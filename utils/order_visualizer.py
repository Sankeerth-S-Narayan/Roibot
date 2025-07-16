"""
Order Visualization Utilities

This module provides console-based visualization tools for order queue,
status display, and real-time monitoring of the warehouse simulation.
"""

import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import threading
from collections import deque

from entities.order_generator import OrderGenerator
from entities.order_queue_manager import OrderQueueManager
from entities.robot_order_assigner import RobotOrderAssigner
from entities.order_status_tracker import OrderStatusTracker
from entities.order_analytics import OrderAnalytics
from entities.analytics_dashboard import AnalyticsDashboard
from entities.order_management_integration import OrderManagementIntegration


class VisualizationType(Enum):
    """Types of visualizations available."""
    QUEUE_STATUS = "queue_status"
    ORDER_PROGRESS = "order_progress"
    PERFORMANCE_METRICS = "performance_metrics"
    ROBOT_STATUS = "robot_status"
    SYSTEM_OVERVIEW = "system_overview"
    REAL_TIME_MONITOR = "real_time_monitor"


@dataclass
class QueueVisualization:
    """Queue visualization data."""
    total_orders: int
    pending_orders: int
    in_progress_orders: int
    completed_orders: int
    failed_orders: int
    queue_capacity: int
    recent_orders: List[Dict[str, Any]]


@dataclass
class OrderProgressVisualization:
    """Order progress visualization data."""
    order_id: str
    status: str
    progress_percentage: float
    items_collected: int
    total_items: int
    time_elapsed: float
    estimated_completion: Optional[float]
    robot_position: Tuple[int, int]
    target_position: Tuple[int, int]


@dataclass
class PerformanceVisualization:
    """Performance metrics visualization data."""
    success_rate: float
    average_completion_time: float
    throughput_per_hour: float
    efficiency_score: float
    error_rate: float
    queue_efficiency: float


class OrderQueueVisualizer:
    """Visualizes order queue status and statistics."""
    
    def __init__(self, queue_manager: OrderQueueManager):
        self.queue_manager = queue_manager
        self.update_interval = 2.0  # seconds
        self.visualization_active = False
        self.visualization_thread = None
    
    def start_queue_visualization(self) -> None:
        """Start real-time queue visualization."""
        if not self.visualization_active:
            self.visualization_active = True
            self.visualization_thread = threading.Thread(target=self._visualization_loop, daemon=True)
            self.visualization_thread.start()
            print("📊 Queue visualization started")
    
    def stop_queue_visualization(self) -> None:
        """Stop queue visualization."""
        self.visualization_active = False
        if self.visualization_thread:
            self.visualization_thread.join(timeout=2.0)
        print("⏹️ Queue visualization stopped")
    
    def _visualization_loop(self) -> None:
        """Main visualization loop."""
        while self.visualization_active:
            try:
                self._display_queue_status()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Visualization error: {e}")
                time.sleep(self.update_interval)
    
    def _display_queue_status(self) -> None:
        """Display current queue status."""
        queue_status = self.queue_manager.get_queue_status()
        
        # Clear console
        print("\n" * 30)
        
        # Header
        print("=" * 80)
        print("📋 ORDER QUEUE VISUALIZATION")
        print("=" * 80)
        print(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Queue statistics
        print("📊 QUEUE STATISTICS")
        print("-" * 40)
        print(f"📦 Total Orders: {queue_status['total_orders']}")
        print(f"⏳ Pending: {queue_status['pending_orders']}")
        print(f"🔄 In Progress: {queue_status['in_progress_orders']}")
        print(f"✅ Completed: {queue_status['completed_orders']}")
        print(f"❌ Failed: {queue_status['failed_orders']}")
        print(f"📋 Queue Size: {queue_status['queue_size']}/{queue_status['max_size']}")
        print()
        
        # Queue capacity bar
        capacity_percentage = (queue_status['queue_size'] / queue_status['max_size']) * 100
        capacity_bars = int(capacity_percentage / 5)
        print(f"Queue Capacity: {'█' * capacity_bars}{'░' * (20 - capacity_bars)} {capacity_percentage:.1f}%")
        print()
        
        # Recent orders
        print("🕒 RECENT ORDERS")
        print("-" * 40)
        recent_orders = queue_status.get('recent_orders', [])[-5:]
        
        if recent_orders:
            for order in recent_orders:
                status_emoji = {
                    "PENDING": "⏳",
                    "IN_PROGRESS": "🔄",
                    "COMPLETED": "✅",
                    "FAILED": "❌"
                }.get(order['status'], "❓")
                
                print(f"{status_emoji} {order['order_id']}: {order['status']} ({order['items_collected']}/{order['total_items']})")
        else:
            print("No recent orders")
        
        print()
        print("=" * 80)
    
    def get_queue_visualization_data(self) -> QueueVisualization:
        """Get queue visualization data."""
        queue_status = self.queue_manager.get_queue_status()
        
        return QueueVisualization(
            total_orders=queue_status['total_orders'],
            pending_orders=queue_status['pending_orders'],
            in_progress_orders=queue_status['in_progress_orders'],
            completed_orders=queue_status['completed_orders'],
            failed_orders=queue_status['failed_orders'],
            queue_capacity=queue_status['max_size'],
            recent_orders=queue_status.get('recent_orders', [])
        )


class OrderProgressVisualizer:
    """Visualizes individual order progress and status."""
    
    def __init__(self, status_tracker: OrderStatusTracker):
        self.status_tracker = status_tracker
        self.active_orders: Dict[str, OrderProgressVisualization] = {}
    
    def update_order_progress(self, order_id: str, progress_data: Dict[str, Any]) -> None:
        """Update order progress visualization."""
        progress_viz = OrderProgressVisualization(
            order_id=order_id,
            status=progress_data.get('status', 'UNKNOWN'),
            progress_percentage=progress_data.get('progress_percentage', 0.0),
            items_collected=progress_data.get('items_collected', 0),
            total_items=progress_data.get('total_items', 0),
            time_elapsed=progress_data.get('time_elapsed', 0.0),
            estimated_completion=progress_data.get('estimated_completion'),
            robot_position=progress_data.get('robot_position', (0, 0)),
            target_position=progress_data.get('target_position', (0, 0))
        )
        
        self.active_orders[order_id] = progress_viz
    
    def remove_completed_order(self, order_id: str) -> None:
        """Remove completed order from visualization."""
        if order_id in self.active_orders:
            del self.active_orders[order_id]
    
    def display_order_progress(self, order_id: str) -> None:
        """Display progress for a specific order."""
        if order_id not in self.active_orders:
            print(f"❌ Order {order_id} not found in active orders")
            return
        
        progress = self.active_orders[order_id]
        
        print(f"\n📦 ORDER PROGRESS: {order_id}")
        print("=" * 50)
        print(f"Status: {progress.status}")
        print(f"Progress: {progress.progress_percentage:.1f}%")
        print(f"Items: {progress.items_collected}/{progress.total_items}")
        print(f"Time Elapsed: {progress.time_elapsed:.1f}s")
        
        if progress.estimated_completion:
            print(f"Estimated Completion: {progress.estimated_completion:.1f}s")
        
        print(f"Robot Position: {progress.robot_position}")
        print(f"Target Position: {progress.target_position}")
        
        # Progress bar
        progress_bars = int(progress.progress_percentage / 5)
        print(f"Progress: {'█' * progress_bars}{'░' * (20 - progress_bars)} {progress.progress_percentage:.1f}%")
    
    def display_all_active_orders(self) -> None:
        """Display progress for all active orders."""
        if not self.active_orders:
            print("📭 No active orders")
            return
        
        print("\n🔄 ACTIVE ORDERS")
        print("=" * 50)
        
        for order_id, progress in self.active_orders.items():
            status_emoji = {
                "PENDING": "⏳",
                "IN_PROGRESS": "🔄",
                "COMPLETED": "✅",
                "FAILED": "❌"
            }.get(progress.status, "❓")
            
            progress_bars = int(progress.progress_percentage / 5)
            progress_bar = f"{'█' * progress_bars}{'░' * (20 - progress_bars)}"
            
            print(f"{status_emoji} {order_id}: {progress_bar} {progress.progress_percentage:.1f}% ({progress.items_collected}/{progress.total_items})")


class PerformanceVisualizer:
    """Visualizes performance metrics and analytics."""
    
    def __init__(self, analytics: OrderAnalytics):
        self.analytics = analytics
    
    def display_performance_metrics(self) -> None:
        """Display comprehensive performance metrics."""
        metrics = self.analytics.get_real_time_metrics()
        
        print("\n📈 PERFORMANCE METRICS")
        print("=" * 50)
        
        # Success rate
        success_rate = metrics.get('success_rate', 0.0)
        success_bars = int(success_rate / 5)
        print(f"Success Rate: {'█' * success_bars}{'░' * (20 - success_bars)} {success_rate:.1f}%")
        
        # Average completion time
        avg_time = metrics.get('average_completion_time', 0.0)
        time_indicator = "🟢" if avg_time <= 60 else "🟡" if avg_time <= 180 else "🔴"
        print(f"Avg Completion Time: {time_indicator} {avg_time:.1f}s")
        
        # Throughput
        throughput = metrics.get('throughput_per_hour', 0.0)
        print(f"Throughput: {throughput:.1f} orders/hour")
        
        # Efficiency score
        efficiency = metrics.get('efficiency_score', 0.0)
        efficiency_bars = int(efficiency / 5)
        print(f"Efficiency Score: {'█' * efficiency_bars}{'░' * (20 - efficiency_bars)} {efficiency:.1f}%")
        
        # Error rate
        error_rate = metrics.get('error_rate', 0.0)
        error_bars = int(error_rate / 5)
        print(f"Error Rate: {'█' * error_bars}{'░' * (20 - error_bars)} {error_rate:.1f}%")
        
        # Queue efficiency
        queue_efficiency = metrics.get('queue_efficiency', 0.0)
        queue_bars = int(queue_efficiency / 5)
        print(f"Queue Efficiency: {'█' * queue_bars}{'░' * (20 - queue_bars)} {queue_efficiency:.1f}%")
    
    def display_performance_trends(self) -> None:
        """Display performance trends over time."""
        analytics_summary = self.analytics.get_analytics_summary()
        
        print("\n📊 PERFORMANCE TRENDS")
        print("=" * 50)
        
        # Recent performance data
        recent_metrics = analytics_summary.get('recent_metrics', [])
        
        if recent_metrics:
            print("Recent Performance:")
            for i, metric in enumerate(recent_metrics[-5:], 1):
                success_rate = metric.get('success_rate', 0.0)
                avg_time = metric.get('average_completion_time', 0.0)
                print(f"  {i}. Success: {success_rate:.1f}%, Time: {avg_time:.1f}s")
        else:
            print("No recent performance data available")
    
    def get_performance_visualization_data(self) -> PerformanceVisualization:
        """Get performance visualization data."""
        metrics = self.analytics.get_real_time_metrics()
        
        return PerformanceVisualization(
            success_rate=metrics.get('success_rate', 0.0),
            average_completion_time=metrics.get('average_completion_time', 0.0),
            throughput_per_hour=metrics.get('throughput_per_hour', 0.0),
            efficiency_score=metrics.get('efficiency_score', 0.0),
            error_rate=metrics.get('error_rate', 0.0),
            queue_efficiency=metrics.get('queue_efficiency', 0.0)
        )


class RobotStatusVisualizer:
    """Visualizes robot status and movement."""
    
    def __init__(self, robot_assigner: RobotOrderAssigner):
        self.robot_assigner = robot_assigner
    
    def display_robot_status(self) -> None:
        """Display current robot status."""
        assignment_status = self.robot_assigner.get_assignment_status()
        
        print("\n🤖 ROBOT STATUS")
        print("=" * 50)
        
        robot_id = assignment_status.get('robot_id', 'UNKNOWN')
        current_order = assignment_status.get('current_order')
        is_available = assignment_status.get('is_available', False)
        total_orders_assigned = assignment_status.get('total_orders_assigned', 0)
        
        print(f"Robot ID: {robot_id}")
        print(f"Status: {'🟢 Available' if is_available else '🔴 Busy'}")
        print(f"Total Orders Assigned: {total_orders_assigned}")
        
        if current_order:
            print(f"Current Order: {current_order.order_id}")
            print(f"Order Status: {current_order.status}")
            print(f"Items: {current_order.items_collected}/{current_order.total_items}")
        else:
            print("Current Order: None")
    
    def display_robot_movement(self, robot_position: Tuple[int, int], target_position: Tuple[int, int]) -> None:
        """Display robot movement visualization."""
        print(f"\n📍 ROBOT MOVEMENT")
        print("=" * 50)
        print(f"Current Position: {robot_position}")
        print(f"Target Position: {target_position}")
        
        # Calculate distance
        distance = math.sqrt((target_position[0] - robot_position[0])**2 + 
                           (target_position[1] - robot_position[1])**2)
        print(f"Distance to Target: {distance:.2f} units")
        
        # Movement direction
        dx = target_position[0] - robot_position[0]
        dy = target_position[1] - robot_position[1]
        
        if dx > 0:
            direction_x = "→"
        elif dx < 0:
            direction_x = "←"
        else:
            direction_x = "·"
        
        if dy > 0:
            direction_y = "↓"
        elif dy < 0:
            direction_y = "↑"
        else:
            direction_y = "·"
        
        print(f"Movement Direction: {direction_x} {direction_y}")


class SystemOverviewVisualizer:
    """Provides comprehensive system overview visualization."""
    
    def __init__(self, integration: OrderManagementIntegration):
        self.integration = integration
        self.update_interval = 3.0  # seconds
        self.visualization_active = False
        self.visualization_thread = None
    
    def start_system_overview(self) -> None:
        """Start real-time system overview visualization."""
        if not self.visualization_active:
            self.visualization_active = True
            self.visualization_thread = threading.Thread(target=self._overview_loop, daemon=True)
            self.visualization_thread.start()
            print("🌐 System overview visualization started")
    
    def stop_system_overview(self) -> None:
        """Stop system overview visualization."""
        self.visualization_active = False
        if self.visualization_thread:
            self.visualization_thread.join(timeout=2.0)
        print("⏹️ System overview visualization stopped")
    
    def _overview_loop(self) -> None:
        """Main overview loop."""
        while self.visualization_active:
            try:
                self._display_system_overview()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Overview error: {e}")
                time.sleep(self.update_interval)
    
    def _display_system_overview(self) -> None:
        """Display comprehensive system overview."""
        integration_status = self.integration.get_integration_status()
        dashboard_data = self.integration.get_dashboard_data()
        
        # Clear console
        print("\n" * 40)
        
        # Header
        print("=" * 80)
        print("🌐 WAREHOUSE SIMULATION - SYSTEM OVERVIEW")
        print("=" * 80)
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Integration status
        print("🔗 INTEGRATION STATUS")
        print("-" * 40)
        is_integrated = integration_status.get('is_integrated', False)
        print(f"Integration: {'🟢 Active' if is_integrated else '🔴 Inactive'}")
        
        metrics = integration_status.get('integration_metrics', {})
        print(f"Total Orders Processed: {metrics.get('total_orders_processed', 0)}")
        print(f"Successful Integrations: {metrics.get('successful_integrations', 0)}")
        print(f"Failed Integrations: {metrics.get('failed_integrations', 0)}")
        print()
        
        # Component status
        print("⚙️ COMPONENT STATUS")
        print("-" * 40)
        component_status = integration_status.get('component_status', {})
        
        for component, status in component_status.items():
            status_emoji = "🟢" if status == "ACTIVE" else "🔴"
            print(f"{status_emoji} {component}: {status}")
        print()
        
        # Performance overview
        print("📈 PERFORMANCE OVERVIEW")
        print("-" * 40)
        performance = dashboard_data.get('performance', {})
        
        success_rate = performance.get('success_rate', 0.0)
        avg_time = performance.get('average_completion_time', 0.0)
        throughput = performance.get('throughput_per_hour', 0.0)
        
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Avg Completion Time: {avg_time:.1f}s")
        print(f"Throughput: {throughput:.1f} orders/hour")
        print()
        
        # System health
        print("🏥 SYSTEM HEALTH")
        print("-" * 40)
        
        # Calculate health score
        health_score = 0
        if is_integrated:
            health_score += 25
        if success_rate >= 90:
            health_score += 25
        if avg_time <= 120:
            health_score += 25
        if throughput >= 10:
            health_score += 25
        
        health_bars = int(health_score / 5)
        health_indicator = "🟢" if health_score >= 75 else "🟡" if health_score >= 50 else "🔴"
        
        print(f"Health Score: {health_indicator} {'█' * health_bars}{'░' * (20 - health_bars)} {health_score}%")
        
        if health_score >= 75:
            print("Status: Excellent")
        elif health_score >= 50:
            print("Status: Good")
        else:
            print("Status: Needs Attention")
        
        print()
        print("=" * 80)


class RealTimeMonitor:
    """Comprehensive real-time monitoring system."""
    
    def __init__(self, integration: OrderManagementIntegration):
        self.integration = integration
        self.queue_visualizer = OrderQueueVisualizer(integration.queue_manager)
        self.progress_visualizer = OrderProgressVisualizer(integration.status_tracker)
        self.performance_visualizer = PerformanceVisualizer(integration.analytics)
        self.robot_visualizer = RobotStatusVisualizer(integration.robot_assigner)
        self.overview_visualizer = SystemOverviewVisualizer(integration)
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 2.0
    
    def start_monitoring(self) -> None:
        """Start comprehensive real-time monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("📊 Real-time monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("⏹️ Real-time monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._display_comprehensive_monitor()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _display_comprehensive_monitor(self) -> None:
        """Display comprehensive monitoring information."""
        # Clear console
        print("\n" * 50)
        
        # Header
        print("=" * 100)
        print("📊 WAREHOUSE SIMULATION - REAL-TIME MONITOR")
        print("=" * 100)
        print(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Get all data
        queue_data = self.queue_visualizer.get_queue_visualization_data()
        performance_data = self.performance_visualizer.get_performance_visualization_data()
        integration_status = self.integration.get_integration_status()
        
        # System overview
        print("🌐 SYSTEM OVERVIEW")
        print("-" * 50)
        print(f"Integration: {'🟢 Active' if integration_status.get('is_integrated', False) else '🔴 Inactive'}")
        print(f"Total Orders: {queue_data.total_orders}")
        print(f"Success Rate: {performance_data.success_rate:.1f}%")
        print(f"Throughput: {performance_data.throughput_per_hour:.1f} orders/hour")
        print()
        
        # Queue status
        print("📋 QUEUE STATUS")
        print("-" * 50)
        print(f"Pending: {queue_data.pending_orders} | In Progress: {queue_data.in_progress_orders}")
        print(f"Completed: {queue_data.completed_orders} | Failed: {queue_data.failed_orders}")
        print(f"Queue Size: {queue_data.total_orders - queue_data.completed_orders - queue_data.failed_orders}/{queue_data.queue_capacity}")
        print()
        
        # Performance metrics
        print("📈 PERFORMANCE METRICS")
        print("-" * 50)
        print(f"Avg Completion Time: {performance_data.average_completion_time:.1f}s")
        print(f"Efficiency Score: {performance_data.efficiency_score:.1f}%")
        print(f"Error Rate: {performance_data.error_rate:.1f}%")
        print(f"Queue Efficiency: {performance_data.queue_efficiency:.1f}%")
        print()
        
        # Recent activity
        print("🕒 RECENT ACTIVITY")
        print("-" * 50)
        recent_orders = queue_data.recent_orders[-3:]
        for order in recent_orders:
            status_emoji = {
                "PENDING": "⏳",
                "IN_PROGRESS": "🔄",
                "COMPLETED": "✅",
                "FAILED": "❌"
            }.get(order.get('status', 'UNKNOWN'), "❓")
            
            print(f"{status_emoji} {order.get('order_id', 'UNKNOWN')}: {order.get('status', 'UNKNOWN')}")
        
        print()
        print("=" * 100)


# Utility functions for easy visualization

def create_queue_visualizer(queue_manager: OrderQueueManager) -> OrderQueueVisualizer:
    """Create queue visualizer."""
    return OrderQueueVisualizer(queue_manager)


def create_progress_visualizer(status_tracker: OrderStatusTracker) -> OrderProgressVisualizer:
    """Create progress visualizer."""
    return OrderProgressVisualizer(status_tracker)


def create_performance_visualizer(analytics: OrderAnalytics) -> PerformanceVisualizer:
    """Create performance visualizer."""
    return PerformanceVisualizer(analytics)


def create_robot_visualizer(robot_assigner: RobotOrderAssigner) -> RobotStatusVisualizer:
    """Create robot status visualizer."""
    return RobotStatusVisualizer(robot_assigner)


def create_system_overview(integration: OrderManagementIntegration) -> SystemOverviewVisualizer:
    """Create system overview visualizer."""
    return SystemOverviewVisualizer(integration)


def create_real_time_monitor(integration: OrderManagementIntegration) -> RealTimeMonitor:
    """Create comprehensive real-time monitor."""
    return RealTimeMonitor(integration)


def start_visualization(integration: OrderManagementIntegration, viz_type: VisualizationType) -> Any:
    """Start specific type of visualization."""
    if viz_type == VisualizationType.QUEUE_STATUS:
        visualizer = create_queue_visualizer(integration.queue_manager)
        visualizer.start_queue_visualization()
        return visualizer
    elif viz_type == VisualizationType.SYSTEM_OVERVIEW:
        visualizer = create_system_overview(integration)
        visualizer.start_system_overview()
        return visualizer
    elif viz_type == VisualizationType.REAL_TIME_MONITOR:
        monitor = create_real_time_monitor(integration)
        monitor.start_monitoring()
        return monitor
    else:
        raise ValueError(f"Unsupported visualization type: {viz_type}") 