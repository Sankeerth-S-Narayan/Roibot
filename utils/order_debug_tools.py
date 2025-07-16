"""
Order Management Debug Tools

This module provides comprehensive debugging tools for order tracking,
status monitoring, and system diagnostics for the warehouse simulation.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import threading
from collections import defaultdict, deque

from entities.order_generator import OrderGenerator
from entities.order_queue_manager import OrderQueueManager
from entities.robot_order_assigner import RobotOrderAssigner
from entities.order_status_tracker import OrderStatusTracker
from entities.order_analytics import OrderAnalytics
from entities.analytics_dashboard import AnalyticsDashboard
from entities.configuration_manager import ConfigurationManager
from entities.order_management_integration import OrderManagementIntegration


class DebugLevel(Enum):
    """Debug logging levels."""
    BASIC = "basic"
    DETAILED = "detailed"
    VERBOSE = "verbose"
    TRACE = "trace"


@dataclass
class OrderDebugInfo:
    """Debug information for a single order."""
    order_id: str
    status: str
    creation_time: float
    assignment_time: Optional[float] = None
    completion_time: Optional[float] = None
    items_collected: int = 0
    total_items: int = 0
    robot_id: Optional[str] = None
    current_position: Optional[Tuple[int, int]] = None
    target_position: Optional[Tuple[int, int]] = None
    error_messages: List[str] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.error_messages is None:
            self.error_messages = []
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class SystemDebugInfo:
    """System-wide debug information."""
    timestamp: float
    total_orders: int
    active_orders: int
    completed_orders: int
    failed_orders: int
    queue_size: int
    robot_status: str
    robot_position: Tuple[int, int]
    system_errors: List[str]
    performance_metrics: Dict[str, Any]
    component_status: Dict[str, str]


class OrderDebugTracker:
    """Tracks and monitors order lifecycle for debugging purposes."""
    
    def __init__(self, debug_level: DebugLevel = DebugLevel.DETAILED):
        self.debug_level = debug_level
        self.order_history: Dict[str, OrderDebugInfo] = {}
        self.system_history: deque = deque(maxlen=1000)
        self.error_log: List[str] = []
        self.performance_log: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
        
        # Setup logging
        self.logger = logging.getLogger("OrderDebugTracker")
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def track_order_created(self, order_id: str, order_data: Dict[str, Any]) -> None:
        """Track order creation event."""
        with self.lock:
            debug_info = OrderDebugInfo(
                order_id=order_id,
                status="CREATED",
                creation_time=time.time(),
                total_items=len(order_data.get('items', [])),
                performance_metrics={
                    'creation_timestamp': time.time(),
                    'items_count': len(order_data.get('items', []))
                }
            )
            self.order_history[order_id] = debug_info
            
            if self.debug_level in [DebugLevel.DETAILED, DebugLevel.VERBOSE, DebugLevel.TRACE]:
                self.logger.info(f"Order created: {order_id} with {debug_info.total_items} items")
    
    def track_order_assigned(self, order_id: str, robot_id: str) -> None:
        """Track order assignment event."""
        with self.lock:
            if order_id in self.order_history:
                debug_info = self.order_history[order_id]
                debug_info.status = "ASSIGNED"
                debug_info.assignment_time = time.time()
                debug_info.robot_id = robot_id
                debug_info.performance_metrics['assignment_timestamp'] = time.time()
                
                if self.debug_level in [DebugLevel.DETAILED, DebugLevel.VERBOSE, DebugLevel.TRACE]:
                    self.logger.info(f"Order assigned: {order_id} to robot {robot_id}")
    
    def track_order_completed(self, order_id: str, completion_data: Dict[str, Any]) -> None:
        """Track order completion event."""
        with self.lock:
            if order_id in self.order_history:
                debug_info = self.order_history[order_id]
                debug_info.status = "COMPLETED"
                debug_info.completion_time = time.time()
                debug_info.items_collected = completion_data.get('items_collected', 0)
                debug_info.performance_metrics.update({
                    'completion_timestamp': time.time(),
                    'completion_time': debug_info.completion_time - debug_info.creation_time,
                    'efficiency_score': completion_data.get('efficiency_score', 0.0)
                })
                
                if self.debug_level in [DebugLevel.DETAILED, DebugLevel.VERBOSE, DebugLevel.TRACE]:
                    self.logger.info(f"Order completed: {order_id} in {debug_info.performance_metrics['completion_time']:.2f}s")
    
    def track_order_failed(self, order_id: str, error_message: str) -> None:
        """Track order failure event."""
        with self.lock:
            if order_id in self.order_history:
                debug_info = self.order_history[order_id]
                debug_info.status = "FAILED"
                debug_info.error_messages.append(error_message)
                
                if self.debug_level in [DebugLevel.DETAILED, DebugLevel.VERBOSE, DebugLevel.TRACE]:
                    self.logger.error(f"Order failed: {order_id} - {error_message}")
    
    def track_item_collected(self, order_id: str, item_id: str, robot_id: str) -> None:
        """Track item collection event."""
        with self.lock:
            if order_id in self.order_history:
                debug_info = self.order_history[order_id]
                debug_info.items_collected += 1
                
                if self.debug_level == DebugLevel.TRACE:
                    self.logger.debug(f"Item collected: {item_id} for order {order_id} by robot {robot_id}")
    
    def track_robot_movement(self, order_id: str, current_position: Tuple[int, int], target_position: Tuple[int, int]) -> None:
        """Track robot movement for an order."""
        with self.lock:
            if order_id in self.order_history:
                debug_info = self.order_history[order_id]
                debug_info.current_position = current_position
                debug_info.target_position = target_position
                
                if self.debug_level == DebugLevel.TRACE:
                    self.logger.debug(f"Robot movement: {order_id} from {current_position} to {target_position}")
    
    def update_system_status(self, system_info: SystemDebugInfo) -> None:
        """Update system-wide debug information."""
        with self.lock:
            self.system_history.append(system_info)
            
            # Track performance metrics
            self.performance_log['queue_size'].append(system_info.queue_size)
            self.performance_log['active_orders'].append(system_info.active_orders)
            
            if system_info.system_errors:
                self.error_log.extend(system_info.system_errors)
    
    def get_order_debug_info(self, order_id: str) -> Optional[OrderDebugInfo]:
        """Get debug information for a specific order."""
        with self.lock:
            return self.order_history.get(order_id)
    
    def get_system_debug_info(self) -> SystemDebugInfo:
        """Get current system debug information."""
        with self.lock:
            if not self.system_history:
                return SystemDebugInfo(
                    timestamp=time.time(),
                    total_orders=0,
                    active_orders=0,
                    completed_orders=0,
                    failed_orders=0,
                    queue_size=0,
                    robot_status="UNKNOWN",
                    robot_position=(0, 0),
                    system_errors=[],
                    performance_metrics={},
                    component_status={}
                )
            return self.system_history[-1]
    
    def get_debug_summary(self) -> Dict[str, Any]:
        """Get comprehensive debug summary."""
        with self.lock:
            total_orders = len(self.order_history)
            completed_orders = sum(1 for info in self.order_history.values() if info.status == "COMPLETED")
            failed_orders = sum(1 for info in self.order_history.values() if info.status == "FAILED")
            active_orders = sum(1 for info in self.order_history.values() if info.status in ["CREATED", "ASSIGNED"])
            
            # Calculate performance metrics
            completion_times = [
                info.performance_metrics.get('completion_time', 0)
                for info in self.order_history.values()
                if info.status == "COMPLETED"
            ]
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            return {
                'timestamp': time.time(),
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'failed_orders': failed_orders,
                'active_orders': active_orders,
                'average_completion_time': avg_completion_time,
                'recent_errors': self.error_log[-10:] if self.error_log else [],
                'performance_trends': {
                    'queue_size': self.performance_log.get('queue_size', []),
                    'active_orders': self.performance_log.get('active_orders', [])
                }
            }
    
    def export_debug_data(self, filename: str) -> bool:
        """Export debug data to JSON file."""
        try:
            with self.lock:
                export_data = {
                    'timestamp': time.time(),
                    'debug_level': self.debug_level.value,
                    'order_history': {order_id: asdict(info) for order_id, info in self.order_history.items()},
                    'system_history': [asdict(info) for info in self.system_history],
                    'error_log': self.error_log,
                    'performance_log': dict(self.performance_log),
                    'summary': self.get_debug_summary()
                }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Debug data exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export debug data: {e}")
            return False


class OrderStatusMonitor:
    """Real-time order status monitoring and visualization."""
    
    def __init__(self, debug_tracker: OrderDebugTracker):
        self.debug_tracker = debug_tracker
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 1.0  # seconds
        
    def start_monitoring(self) -> None:
        """Start real-time monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🔍 Order status monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("⏹️ Order status monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._display_status()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _display_status(self) -> None:
        """Display current system status."""
        system_info = self.debug_tracker.get_system_debug_info()
        summary = self.debug_tracker.get_debug_summary()
        
        # Clear console (simple approach)
        print("\n" * 50)
        
        # Display header
        print("=" * 80)
        print("🔄 ORDER MANAGEMENT SYSTEM - REAL-TIME MONITOR")
        print("=" * 80)
        print(f"📅 Time: {datetime.fromtimestamp(system_info.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Debug Level: {self.debug_tracker.debug_level.value.upper()}")
        print()
        
        # System overview
        print("📊 SYSTEM OVERVIEW")
        print("-" * 40)
        print(f"📦 Total Orders: {summary['total_orders']}")
        print(f"✅ Completed: {summary['completed_orders']}")
        print(f"❌ Failed: {summary['failed_orders']}")
        print(f"🔄 Active: {summary['active_orders']}")
        print(f"📋 Queue Size: {system_info.queue_size}")
        print(f"🤖 Robot Status: {system_info.robot_status}")
        print(f"📍 Robot Position: {system_info.robot_position}")
        print()
        
        # Performance metrics
        print("📈 PERFORMANCE METRICS")
        print("-" * 40)
        print(f"⏱️ Avg Completion Time: {summary['average_completion_time']:.2f}s")
        print(f"📊 Success Rate: {(summary['completed_orders'] / max(summary['total_orders'], 1) * 100):.1f}%")
        print()
        
        # Recent activity
        print("🕒 RECENT ACTIVITY")
        print("-" * 40)
        recent_orders = list(self.debug_tracker.order_history.items())[-5:]
        for order_id, info in recent_orders:
            status_emoji = {
                "CREATED": "🆕",
                "ASSIGNED": "📋",
                "COMPLETED": "✅",
                "FAILED": "❌"
            }.get(info.status, "❓")
            
            print(f"{status_emoji} {order_id}: {info.status} ({info.items_collected}/{info.total_items} items)")
        
        print()
        
        # Recent errors
        if summary['recent_errors']:
            print("⚠️ RECENT ERRORS")
            print("-" * 40)
            for error in summary['recent_errors'][-3:]:
                print(f"❌ {error}")
            print()
        
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring")
        print("=" * 80)


class OrderDebugger:
    """Main debugging interface for order management system."""
    
    def __init__(self, integration: OrderManagementIntegration):
        self.integration = integration
        self.debug_tracker = OrderDebugTracker()
        self.status_monitor = OrderStatusMonitor(self.debug_tracker)
        
        # Connect to integration components
        self._connect_to_components()
    
    def _connect_to_components(self) -> None:
        """Connect debug tracker to order management components."""
        # This would require adding debug callbacks to the components
        # For now, we'll provide manual tracking methods
        pass
    
    def start_debugging(self, debug_level: DebugLevel = DebugLevel.DETAILED) -> None:
        """Start comprehensive debugging."""
        self.debug_tracker.debug_level = debug_level
        self.status_monitor.start_monitoring()
        print(f"🐛 Debugging started with level: {debug_level.value}")
    
    def stop_debugging(self) -> None:
        """Stop debugging."""
        self.status_monitor.stop_monitoring()
        print("🛑 Debugging stopped")
    
    def get_debug_report(self) -> Dict[str, Any]:
        """Generate comprehensive debug report."""
        return {
            'system_summary': self.debug_tracker.get_debug_summary(),
            'integration_status': self.integration.get_integration_status(),
            'component_status': self._get_component_status(),
            'performance_analysis': self._analyze_performance()
        }
    
    def _get_component_status(self) -> Dict[str, str]:
        """Get status of all components."""
        return {
            'order_generator': 'ACTIVE' if self.integration.order_generator.is_generating else 'INACTIVE',
            'queue_manager': 'ACTIVE',
            'robot_assigner': 'ACTIVE' if self.integration.robot_assigner.is_active else 'INACTIVE',
            'status_tracker': 'ACTIVE',
            'analytics': 'ACTIVE',
            'integration': 'ACTIVE' if self.integration.is_integrated else 'INACTIVE'
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance."""
        summary = self.debug_tracker.get_debug_summary()
        
        # Calculate performance metrics
        total_orders = summary['total_orders']
        completed_orders = summary['completed_orders']
        failed_orders = summary['failed_orders']
        
        success_rate = (completed_orders / max(total_orders, 1)) * 100
        failure_rate = (failed_orders / max(total_orders, 1)) * 100
        avg_completion_time = summary['average_completion_time']
        
        return {
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'average_completion_time': avg_completion_time,
            'total_orders_processed': total_orders,
            'performance_grade': self._calculate_performance_grade(success_rate, avg_completion_time)
        }
    
    def _calculate_performance_grade(self, success_rate: float, avg_completion_time: float) -> str:
        """Calculate performance grade based on metrics."""
        if success_rate >= 95 and avg_completion_time <= 60:
            return "A+"
        elif success_rate >= 90 and avg_completion_time <= 90:
            return "A"
        elif success_rate >= 85 and avg_completion_time <= 120:
            return "B"
        elif success_rate >= 80 and avg_completion_time <= 180:
            return "C"
        else:
            return "D"
    
    def export_debug_report(self, filename: str) -> bool:
        """Export comprehensive debug report."""
        try:
            report = self.get_debug_report()
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Debug report exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export debug report: {e}")
            return False
    
    def diagnose_issues(self) -> List[str]:
        """Diagnose potential issues in the system."""
        issues = []
        report = self.get_debug_report()
        
        # Check for common issues
        if report['performance_analysis']['failure_rate'] > 10:
            issues.append("High failure rate detected (>10%)")
        
        if report['performance_analysis']['average_completion_time'] > 300:
            issues.append("Slow order completion (>5 minutes average)")
        
        if report['system_summary']['active_orders'] > 20:
            issues.append("High number of active orders (>20)")
        
        if report['system_summary']['queue_size'] > 50:
            issues.append("Large order queue (>50 orders)")
        
        if report['system_summary']['recent_errors']:
            issues.append(f"Recent errors detected: {len(report['system_summary']['recent_errors'])} errors")
        
        return issues


class OrderVisualizer:
    """Console-based order visualization tools."""
    
    def __init__(self, debug_tracker: OrderDebugTracker):
        self.debug_tracker = debug_tracker
    
    def display_order_queue(self) -> None:
        """Display current order queue status."""
        system_info = self.debug_tracker.get_system_debug_info()
        
        print("\n📋 ORDER QUEUE STATUS")
        print("=" * 50)
        print(f"Queue Size: {system_info.queue_size}")
        print(f"Active Orders: {system_info.active_orders}")
        print(f"Completed Orders: {system_info.completed_orders}")
        print(f"Failed Orders: {system_info.failed_orders}")
        print()
        
        # Display recent orders
        recent_orders = list(self.debug_tracker.order_history.items())[-10:]
        if recent_orders:
            print("Recent Orders:")
            for order_id, info in recent_orders:
                status_emoji = {
                    "CREATED": "🆕",
                    "ASSIGNED": "📋",
                    "COMPLETED": "✅",
                    "FAILED": "❌"
                }.get(info.status, "❓")
                
                print(f"  {status_emoji} {order_id}: {info.status} ({info.items_collected}/{info.total_items})")
    
    def display_performance_chart(self) -> None:
        """Display simple performance chart."""
        summary = self.debug_tracker.get_debug_summary()
        
        print("\n📊 PERFORMANCE CHART")
        print("=" * 50)
        
        # Success rate bar
        success_rate = (summary['completed_orders'] / max(summary['total_orders'], 1)) * 100
        success_bars = int(success_rate / 5)
        print(f"Success Rate: {'█' * success_bars}{'░' * (20 - success_bars)} {success_rate:.1f}%")
        
        # Completion time indicator
        avg_time = summary['average_completion_time']
        if avg_time <= 60:
            time_indicator = "🟢 Fast"
        elif avg_time <= 180:
            time_indicator = "🟡 Normal"
        else:
            time_indicator = "🔴 Slow"
        print(f"Avg Completion: {time_indicator} ({avg_time:.1f}s)")
        
        # Performance grade
        grade = self._calculate_grade(success_rate, avg_time)
        print(f"Performance Grade: {grade}")
    
    def _calculate_grade(self, success_rate: float, avg_time: float) -> str:
        """Calculate simple performance grade."""
        if success_rate >= 95 and avg_time <= 60:
            return "🟢 A+"
        elif success_rate >= 90 and avg_time <= 90:
            return "🟢 A"
        elif success_rate >= 85 and avg_time <= 120:
            return "🟡 B"
        elif success_rate >= 80 and avg_time <= 180:
            return "🟡 C"
        else:
            return "🔴 D"


# Utility functions for easy debugging

def create_debug_tools(integration: OrderManagementIntegration) -> OrderDebugger:
    """Create debug tools for order management integration."""
    return OrderDebugger(integration)


def start_debug_monitoring(integration: OrderManagementIntegration, debug_level: DebugLevel = DebugLevel.DETAILED) -> OrderDebugger:
    """Start debug monitoring for order management system."""
    debugger = create_debug_tools(integration)
    debugger.start_debugging(debug_level)
    return debugger


def generate_debug_report(integration: OrderManagementIntegration, filename: str = "debug_report.json") -> bool:
    """Generate and export debug report."""
    debugger = create_debug_tools(integration)
    return debugger.export_debug_report(filename)


def diagnose_system_issues(integration: OrderManagementIntegration) -> List[str]:
    """Diagnose potential issues in the order management system."""
    debugger = create_debug_tools(integration)
    return debugger.diagnose_issues() 