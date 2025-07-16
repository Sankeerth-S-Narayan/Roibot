from typing import Dict, Any, Optional
import time
from datetime import datetime
from .order_analytics import OrderAnalytics

class AnalyticsDashboard:
    """
    Simple real-time dashboard for displaying warehouse analytics.
    
    Provides an easy-to-understand UI for viewing real-time metrics
    and system performance data.
    """
    
    def __init__(self, analytics: OrderAnalytics):
        """
        Initialize the analytics dashboard.
        
        Args:
            analytics: OrderAnalytics instance for data
        """
        self.analytics = analytics
        self.last_refresh_time = time.time()
        self.refresh_interval = 1.0  # 1 second refresh interval
        
        print(f"📊 AnalyticsDashboard initialized")
    
    def display_dashboard(self) -> str:
        """
        Generate dashboard display string.
        
        Returns:
            Formatted dashboard string
        """
        try:
            # Get real-time metrics
            metrics = self.analytics.get_real_time_metrics()
            dashboard_data = self.analytics.get_dashboard_data()
            
            # Create dashboard display
            dashboard = self._create_dashboard_header()
            dashboard += self._create_system_overview(metrics)
            dashboard += self._create_order_summary(dashboard_data)
            dashboard += self._create_robot_status(dashboard_data)
            dashboard += self._create_recent_orders(dashboard_data)
            dashboard += self._create_export_options()
            
            self.last_refresh_time = time.time()
            return dashboard
            
        except Exception as e:
            return f"❌ Error displaying dashboard: {e}"
    
    def _create_dashboard_header(self) -> str:
        """Create dashboard header."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           📊 WAREHOUSE ANALYTICS DASHBOARD                   ║
║                              {current_time}                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def _create_system_overview(self, metrics: Dict[str, Any]) -> str:
        """Create system overview section."""
        return f"""
📈 SYSTEM OVERVIEW
─────────────────────────────────────────────────────────────────────────────────
• System Throughput: {metrics.get('system_throughput', '0.00 orders/min')}
• Total Completed: {metrics.get('total_completed', 0)} orders
• Total Failed: {metrics.get('total_failed', 0)} orders
• Average Completion Time: {metrics.get('average_completion_time', '0.00s')}
• Average Efficiency: {metrics.get('average_efficiency', '0.00%')}
• Queue Size: {metrics.get('queue_size', 0)} orders
• Active Robots: {metrics.get('active_robots', 0)} robots
• Total Distance: {metrics.get('total_distance', '0.0 units')}
• Path Optimization Savings: {metrics.get('total_savings', '0.0 units')}
"""
    
    def _create_order_summary(self, dashboard_data: Dict[str, Any]) -> str:
        """Create order summary section."""
        active_orders = dashboard_data.get('active_orders', [])
        completed_orders = dashboard_data.get('completed_orders', [])
        
        order_str = f"""
📋 ORDER SUMMARY
─────────────────────────────────────────────────────────────────────────────────
• Active Orders: {len(active_orders)} orders
• Recent Completions: {len(completed_orders)} orders

ACTIVE ORDERS:
"""
        
        if active_orders:
            for order in active_orders[:5]:  # Show first 5 active orders
                order_str += f"  • {order['order_id']} ({order['status']}) - {len(order['item_ids'])} items"
                if order.get('assigned_robot_id'):
                    order_str += f" → {order['assigned_robot_id']}"
                order_str += "\n"
        else:
            order_str += "  • No active orders\n"
        
        return order_str
    
    def _create_robot_status(self, dashboard_data: Dict[str, Any]) -> str:
        """Create robot status section."""
        robot_metrics = dashboard_data.get('robot_metrics', {})
        
        robot_str = f"""
🤖 ROBOT STATUS
─────────────────────────────────────────────────────────────────────────────────
• Total Robots: {len(robot_metrics)} robots

"""
        
        if robot_metrics:
            for robot_id, robot_data in robot_metrics.items():
                robot_str += f"  • {robot_id}: {robot_data['status']} "
                robot_str += f"({robot_data['utilization_rate']:.1%} utilization)\n"
                robot_str += f"    Position: A{robot_data['current_position']['aisle']}R{robot_data['current_position']['rack']} "
                robot_str += f"→ A{robot_data['target_location']['aisle']}R{robot_data['target_location']['rack']}\n"
                robot_str += f"    Items: {len(robot_data['items_held'])} held, {len(robot_data['target_items'])} target\n"
        else:
            robot_str += "  • No robots active\n"
        
        return robot_str
    
    def _create_recent_orders(self, dashboard_data: Dict[str, Any]) -> str:
        """Create recent orders section."""
        completed_orders = dashboard_data.get('completed_orders', [])
        
        recent_str = f"""
✅ RECENT COMPLETIONS
─────────────────────────────────────────────────────────────────────────────────
"""
        
        if completed_orders:
            for order in completed_orders[-5:]:  # Show last 5 completed orders
                recent_str += f"  • {order['order_id']}: {order['total_time_taken']:.1f}s, "
                recent_str += f"{order['efficiency_score']:.1%} efficiency, "
                recent_str += f"{order['total_distance_traveled']:.1f} units\n"
        else:
            recent_str += "  • No completed orders yet\n"
        
        return recent_str
    
    def _create_export_options(self) -> str:
        """Create export options section."""
        return f"""
📤 EXPORT OPTIONS
─────────────────────────────────────────────────────────────────────────────────
• JSON Export: analytics.export_to_json()
• CSV Export: analytics.export_to_csv()
• Real-time Data: analytics.get_real_time_metrics()
• Dashboard Data: analytics.get_dashboard_data()

Last Refresh: {datetime.fromtimestamp(self.last_refresh_time).strftime('%H:%M:%S')}
"""
    
    def display_simple_metrics(self) -> str:
        """
        Display simple, key metrics only.
        
        Returns:
            Simple metrics display string
        """
        try:
            metrics = self.analytics.get_real_time_metrics()
            
            return f"""
📊 QUICK METRICS
─────────────────────────────────────────────────────────────────────────────────
Throughput: {metrics.get('system_throughput', '0.00 orders/min')}
Completed: {metrics.get('total_completed', 0)} | Failed: {metrics.get('total_failed', 0)}
Avg Time: {metrics.get('average_completion_time', '0.00s')} | Avg Efficiency: {metrics.get('average_efficiency', '0.00%')}
Queue: {metrics.get('queue_size', 0)} orders | Robots: {metrics.get('active_robots', 0)} active
Distance: {metrics.get('total_distance', '0.0 units')} | Savings: {metrics.get('total_savings', '0.0 units')}
"""
            
        except Exception as e:
            return f"❌ Error displaying simple metrics: {e}"
    
    def display_order_details(self, order_id: str) -> str:
        """
        Display detailed information for a specific order.
        
        Args:
            order_id: ID of the order to display
            
        Returns:
            Order details display string
        """
        try:
            dashboard_data = self.analytics.get_dashboard_data()
            
            # Find order in completed orders
            completed_orders = dashboard_data.get('completed_orders', [])
            order_details = None
            
            for order in completed_orders:
                if order['order_id'] == order_id:
                    order_details = order
                    break
            
            if not order_details:
                return f"❌ Order {order_id} not found in completed orders"
            
            return f"""
📋 ORDER DETAILS: {order_id}
─────────────────────────────────────────────────────────────────────────────────
• Completion Time: {order_details['total_time_taken']:.2f} seconds
• Total Distance: {order_details['total_distance_traveled']:.1f} units
• Efficiency Score: {order_details['efficiency_score']:.1%}
• Direction Changes: {order_details['direction_changes']} changes
• Path Optimization Savings: {order_details['path_optimization_savings']:.1f} units
• Items Collected: {order_details['items_collected']}/{order_details['total_items']} items
• Completed At: {order_details['timestamp_completed']}
"""
            
        except Exception as e:
            return f"❌ Error displaying order details: {e}"
    
    def display_robot_details(self, robot_id: str) -> str:
        """
        Display detailed information for a specific robot.
        
        Args:
            robot_id: ID of the robot to display
            
        Returns:
            Robot details display string
        """
        try:
            dashboard_data = self.analytics.get_dashboard_data()
            robot_metrics = dashboard_data.get('robot_metrics', {})
            
            if robot_id not in robot_metrics:
                return f"❌ Robot {robot_id} not found in active robots"
            
            robot_data = robot_metrics[robot_id]
            
            return f"""
🤖 ROBOT DETAILS: {robot_id}
─────────────────────────────────────────────────────────────────────────────────
• Status: {robot_data['status']}
• Utilization Rate: {robot_data['utilization_rate']:.1%}
• Current Position: Aisle {robot_data['current_position']['aisle']}, Rack {robot_data['current_position']['rack']}
• Target Location: Aisle {robot_data['target_location']['aisle']}, Rack {robot_data['target_location']['rack']}
• Movement Direction: {robot_data['movement_direction']}
• Snake Path Segment: {robot_data['snake_path_segment']}
• Items Held: {len(robot_data['items_held'])} items
• Target Items: {len(robot_data['target_items'])} items
• Orders Completed: {robot_data['orders_completed']} orders
• Total Distance Traveled: {robot_data['total_distance_traveled']:.1f} units
"""
            
        except Exception as e:
            return f"❌ Error displaying robot details: {e}"
    
    def auto_refresh(self) -> bool:
        """
        Check if dashboard should auto-refresh.
        
        Returns:
            True if refresh is needed, False otherwise
        """
        return (time.time() - self.last_refresh_time) >= self.refresh_interval
    
    def set_refresh_interval(self, interval: float):
        """
        Set the refresh interval for the dashboard.
        
        Args:
            interval: Refresh interval in seconds
        """
        self.refresh_interval = max(0.1, interval)  # Minimum 0.1 seconds
        print(f"🔄 Dashboard refresh interval set to {self.refresh_interval:.1f}s")
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get dashboard summary information.
        
        Returns:
            Dictionary with dashboard summary
        """
        try:
            return {
                'last_refresh_time': self.last_refresh_time,
                'refresh_interval': self.refresh_interval,
                'auto_refresh_needed': self.auto_refresh(),
                'dashboard_ready': True
            }
            
        except Exception as e:
            print(f"❌ Error getting dashboard summary: {e}")
            return {'dashboard_ready': False} 