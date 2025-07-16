from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import time
import json
import csv
from datetime import datetime
from enum import Enum
from .robot_orders import Order, OrderStatus
from .order_status_tracker import OrderStatusTracker
from .robot_order_assigner import RobotOrderAssigner
from .order_queue_manager import OrderQueueManager

class MetricType(Enum):
    """Enumeration for metric types."""
    COMPLETION_TIME = "completion_time"
    TOTAL_DISTANCE = "total_distance"
    EFFICIENCY_SCORE = "efficiency_score"
    DIRECTION_CHANGES = "direction_changes"
    PATH_OPTIMIZATION_SAVINGS = "path_optimization_savings"
    QUEUE_WAIT_TIME = "queue_wait_time"
    ROBOT_UTILIZATION = "robot_utilization"

@dataclass
class OrderMetrics:
    """Metrics for a completed order."""
    order_id: str
    timestamp_completed: str
    total_distance_traveled: float
    efficiency_score: float
    direction_changes: int
    path_optimization_savings: float
    total_time_taken: float
    items_collected: int
    total_items: int

@dataclass
class RobotMetrics:
    """Metrics for robot performance."""
    robot_id: str
    current_position: Dict[str, int]
    target_location: Dict[str, int]
    movement_direction: str
    status: str
    items_held: List[str]
    target_items: List[str]
    snake_path_segment: str
    utilization_rate: float
    orders_completed: int
    total_distance_traveled: float

@dataclass
class SystemMetrics:
    """Overall system performance metrics."""
    total_orders_completed: int
    total_orders_failed: int
    average_completion_time: float
    average_efficiency_score: float
    total_distance_traveled: float
    total_path_optimization_savings: float
    queue_size: int
    active_robots: int
    system_throughput: float

class OrderAnalytics:
    """
    Handles real-time performance metrics tracking and analytics.
    
    Provides real-time metrics collection, simple dashboard display,
    and CSV/JSON export functionality for warehouse simulation.
    """
    
    def __init__(self, status_tracker: OrderStatusTracker, 
                 robot_assigner: RobotOrderAssigner, 
                 queue_manager: OrderQueueManager):
        """
        Initialize the order analytics system.
        
        Args:
            status_tracker: OrderStatusTracker for order status data
            robot_assigner: RobotOrderAssigner for robot performance data
            queue_manager: OrderQueueManager for queue metrics
        """
        self.status_tracker = status_tracker
        self.robot_assigner = robot_assigner
        self.queue_manager = queue_manager
        
        # Metrics storage
        self.completed_orders_metrics: List[OrderMetrics] = []
        self.robot_metrics: Dict[str, RobotMetrics] = {}
        self.system_metrics = SystemMetrics(
            total_orders_completed=0,
            total_orders_failed=0,
            average_completion_time=0.0,
            average_efficiency_score=0.0,
            total_distance_traveled=0.0,
            total_path_optimization_savings=0.0,
            queue_size=0,
            active_robots=0,
            system_throughput=0.0
        )
        
        # Real-time tracking
        self.start_time = time.time()
        self.last_update_time = time.time()
        
        # Export settings
        self.export_directory = "exports"
        self.auto_export_interval = 300  # 5 minutes
        
        print(f"📊 OrderAnalytics initialized")
    
    def update_order_metrics(self, order: Order):
        """
        Update metrics when an order is completed.
        
        Args:
            order: Completed order object
        """
        try:
            # Calculate order metrics
            completion_time = 0.0
            if order.timestamp_assigned and order.timestamp_completed:
                completion_time = order.timestamp_completed - order.timestamp_assigned
            
            # Create order metrics
            order_metrics = OrderMetrics(
                order_id=order.order_id,
                timestamp_completed=datetime.fromtimestamp(order.timestamp_completed).isoformat() if order.timestamp_completed else "",
                total_distance_traveled=order.total_distance,
                efficiency_score=order.efficiency_score,
                direction_changes=self._calculate_direction_changes(order),
                path_optimization_savings=self._calculate_path_optimization_savings(order),
                total_time_taken=completion_time,
                items_collected=len(order.items_collected),
                total_items=len(order.item_ids)
            )
            
            # Add to completed orders metrics
            self.completed_orders_metrics.append(order_metrics)
            
            # Update system metrics
            self._update_system_metrics()
            
            print(f"📈 Updated metrics for order {order.order_id}")
            
        except Exception as e:
            print(f"❌ Error updating order metrics: {e}")
    
    def update_robot_metrics(self, robot_id: str, robot_data: Dict[str, Any]):
        """
        Update robot performance metrics.
        
        Args:
            robot_id: ID of the robot
            robot_data: Robot performance data
        """
        try:
            # Calculate robot utilization
            utilization_rate = self._calculate_robot_utilization(robot_id)
            
            # Create or update robot metrics
            robot_metrics = RobotMetrics(
                robot_id=robot_id,
                current_position=robot_data.get('current_position', {'aisle': 0, 'rack': 0}),
                target_location=robot_data.get('target_location', {'aisle': 0, 'rack': 0}),
                movement_direction=robot_data.get('movement_direction', 'FORWARD'),
                status=robot_data.get('status', 'IDLE'),
                items_held=robot_data.get('items_held', []),
                target_items=robot_data.get('target_items', []),
                snake_path_segment=robot_data.get('snake_path_segment', ''),
                utilization_rate=utilization_rate,
                orders_completed=robot_data.get('orders_completed', 0),
                total_distance_traveled=robot_data.get('total_distance_traveled', 0.0)
            )
            
            self.robot_metrics[robot_id] = robot_metrics
            
        except Exception as e:
            print(f"❌ Error updating robot metrics: {e}")
    
    def _calculate_direction_changes(self, order: Order) -> int:
        """
        Calculate direction changes for an order.
        
        Args:
            order: Order object
            
        Returns:
            Number of direction changes
        """
        try:
            # Simplified calculation - in real system would track actual direction changes
            # For now, estimate based on number of items and positions
            if len(order.item_positions) <= 1:
                return 0
            
            # Estimate direction changes based on item count and positions
            estimated_changes = max(0, len(order.item_positions) - 1)
            return estimated_changes
            
        except Exception as e:
            print(f"❌ Error calculating direction changes: {e}")
            return 0
    
    def _calculate_path_optimization_savings(self, order: Order) -> float:
        """
        Calculate path optimization savings for an order.
        
        Args:
            order: Order object
            
        Returns:
            Path optimization savings in distance units
        """
        try:
            # Simplified calculation - in real system would compare optimized vs non-optimized paths
            # For now, estimate based on efficiency score
            if order.efficiency_score > 0:
                # Estimate savings based on efficiency
                base_distance = order.total_distance
                optimized_distance = base_distance * order.efficiency_score
                savings = base_distance - optimized_distance
                return max(0.0, savings)
            return 0.0
            
        except Exception as e:
            print(f"❌ Error calculating path optimization savings: {e}")
            return 0.0
    
    def _calculate_robot_utilization(self, robot_id: str) -> float:
        """
        Calculate robot utilization rate.
        
        Args:
            robot_id: ID of the robot
            
        Returns:
            Utilization rate (0.0 to 1.0)
        """
        try:
            # Get robot assignment statistics
            assignment_stats = self.robot_assigner.get_assignment_statistics()
            
            if assignment_stats and assignment_stats.get('robot_id') == robot_id:
                utilization = assignment_stats.get('statistics', {}).get('robot_utilization_rate', 0.0)
                return min(1.0, max(0.0, utilization / 100.0))  # Convert percentage to decimal
            return 0.0
            
        except Exception as e:
            print(f"❌ Error calculating robot utilization: {e}")
            return 0.0
    
    def _update_system_metrics(self):
        """Update overall system metrics."""
        try:
            # Get tracking statistics
            tracking_stats = self.status_tracker.get_tracking_statistics()
            
            # Update system metrics
            self.system_metrics.total_orders_completed = tracking_stats.get('total_completions', 0)
            self.system_metrics.total_orders_failed = tracking_stats.get('total_failures', 0)
            self.system_metrics.average_completion_time = tracking_stats.get('average_completion_time', 0.0)
            self.system_metrics.average_efficiency_score = tracking_stats.get('average_efficiency_score', 0.0)
            
            # Calculate total distance and savings
            total_distance = sum(metrics.total_distance_traveled for metrics in self.completed_orders_metrics)
            total_savings = sum(metrics.path_optimization_savings for metrics in self.completed_orders_metrics)
            
            self.system_metrics.total_distance_traveled = total_distance
            self.system_metrics.total_path_optimization_savings = total_savings
            
            # Update queue and robot metrics
            self.system_metrics.queue_size = self.queue_manager.get_queue_size()
            self.system_metrics.active_robots = len(self.robot_metrics)
            
            # Calculate system throughput
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                self.system_metrics.system_throughput = self.system_metrics.total_orders_completed / elapsed_time
            
            self.last_update_time = time.time()
            
        except Exception as e:
            print(f"❌ Error updating system metrics: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the real-time dashboard.
        
        Returns:
            Dictionary with dashboard data
        """
        try:
            # Update system metrics
            self._update_system_metrics()
            
            # Get active orders
            active_orders = self.status_tracker.get_active_orders()
            
            # Get queue status
            queue_status = self.queue_manager.get_queue_status()
            
            return {
                'system_metrics': asdict(self.system_metrics),
                'active_orders': [
                    {
                        'order_id': order.order_id,
                        'item_ids': order.item_ids,
                        'timestamp_received': datetime.fromtimestamp(order.timestamp_assigned).isoformat() if order.timestamp_assigned else "",
                        'status': order.status.value,
                        'assigned_robot_id': order.assigned_robot_id
                    }
                    for order in active_orders
                ],
                'completed_orders': [
                    asdict(metrics) for metrics in self.completed_orders_metrics[-10:]  # Last 10 completed orders
                ],
                'robot_metrics': {
                    robot_id: asdict(metrics) for robot_id, metrics in self.robot_metrics.items()
                },
                'queue_status': queue_status.value if hasattr(queue_status, 'value') else str(queue_status),
                'last_update': datetime.fromtimestamp(self.last_update_time).isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting dashboard data: {e}")
            return {}
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Export metrics to JSON file.
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"order_analytics_{timestamp}.json"
            
            filepath = f"{self.export_directory}/{filename}"
            
            # Prepare export data
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'system_metrics': asdict(self.system_metrics),
                'completed_orders': [asdict(metrics) for metrics in self.completed_orders_metrics],
                'robot_metrics': {
                    robot_id: asdict(metrics) for robot_id, metrics in self.robot_metrics.items()
                },
                'analytics_summary': {
                    'total_orders_tracked': len(self.completed_orders_metrics),
                    'average_completion_time': self.system_metrics.average_completion_time,
                    'average_efficiency_score': self.system_metrics.average_efficiency_score,
                    'total_distance_traveled': self.system_metrics.total_distance_traveled,
                    'total_path_optimization_savings': self.system_metrics.total_path_optimization_savings
                }
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"📊 Exported analytics to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return ""
    
    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Export metrics to CSV file.
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to exported file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"order_analytics_{timestamp}.csv"
            
            filepath = f"{self.export_directory}/{filename}"
            
            # Write completed orders to CSV
            with open(filepath, 'w', newline='') as f:
                if self.completed_orders_metrics:
                    # Get field names from first order metrics
                    fieldnames = asdict(self.completed_orders_metrics[0]).keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for metrics in self.completed_orders_metrics:
                        writer.writerow(asdict(metrics))
            
            print(f"📊 Exported analytics to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics for display.
        
        Returns:
            Dictionary with real-time metrics
        """
        try:
            self._update_system_metrics()
            
            return {
                'current_time': datetime.now().isoformat(),
                'system_throughput': f"{self.system_metrics.system_throughput:.2f} orders/min",
                'total_completed': self.system_metrics.total_orders_completed,
                'total_failed': self.system_metrics.total_orders_failed,
                'average_completion_time': f"{self.system_metrics.average_completion_time:.2f}s",
                'average_efficiency': f"{self.system_metrics.average_efficiency_score:.2%}",
                'queue_size': self.system_metrics.queue_size,
                'active_robots': self.system_metrics.active_robots,
                'total_distance': f"{self.system_metrics.total_distance_traveled:.1f} units",
                'total_savings': f"{self.system_metrics.total_path_optimization_savings:.1f} units"
            }
            
        except Exception as e:
            print(f"❌ Error getting real-time metrics: {e}")
            return {}
    
    def reset_analytics(self):
        """Reset all analytics data."""
        try:
            self.completed_orders_metrics.clear()
            self.robot_metrics.clear()
            self.system_metrics = SystemMetrics(
                total_orders_completed=0,
                total_orders_failed=0,
                average_completion_time=0.0,
                average_efficiency_score=0.0,
                total_distance_traveled=0.0,
                total_path_optimization_savings=0.0,
                queue_size=0,
                active_robots=0,
                system_throughput=0.0
            )
            self.start_time = time.time()
            self.last_update_time = time.time()
            
            print("📊 Analytics data reset")
            
        except Exception as e:
            print(f"❌ Error resetting analytics: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get analytics summary.
        
        Returns:
            Dictionary with analytics summary
        """
        try:
            return {
                'total_orders_tracked': len(self.completed_orders_metrics),
                'total_robots_tracked': len(self.robot_metrics),
                'system_uptime': time.time() - self.start_time,
                'last_update': self.last_update_time,
                'export_directory': self.export_directory,
                'auto_export_interval': self.auto_export_interval
            }
            
        except Exception as e:
            print(f"❌ Error getting analytics summary: {e}")
            return {} 