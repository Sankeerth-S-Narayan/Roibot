"""
Performance Monitoring Tools

This module provides comprehensive performance monitoring tools with real-time
metrics display, alerting, and performance analysis for the warehouse simulation.
"""

import time
import json
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

from entities.order_analytics import OrderAnalytics
from entities.order_management_integration import OrderManagementIntegration


class AlertLevel(Enum):
    """Performance alert levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: float
    threshold: Optional[float] = None
    alert_level: AlertLevel = AlertLevel.INFO


@dataclass
class PerformanceAlert:
    """Performance alert information."""
    metric_name: str
    current_value: float
    threshold_value: float
    alert_level: AlertLevel
    message: str
    timestamp: float
    is_active: bool = True


@dataclass
class PerformanceSnapshot:
    """Snapshot of performance metrics at a point in time."""
    timestamp: float
    metrics: Dict[str, PerformanceMetric]
    alerts: List[PerformanceAlert]
    summary: Dict[str, Any]


class PerformanceThresholds:
    """Configurable performance thresholds."""
    
    def __init__(self):
        # Order completion metrics
        self.max_completion_time = 300.0  # 5 minutes
        self.min_success_rate = 85.0  # 85%
        self.max_error_rate = 10.0  # 10%
        
        # Queue metrics
        self.max_queue_size = 50
        self.max_queue_wait_time = 600.0  # 10 minutes
        
        # Robot metrics
        self.min_robot_utilization = 60.0  # 60%
        self.max_robot_idle_time = 300.0  # 5 minutes
        
        # System metrics
        self.max_system_latency = 1000.0  # 1 second
        self.min_throughput = 5.0  # 5 orders/hour
        
        # Alert thresholds
        self.warning_threshold_multiplier = 0.8  # 80% of critical
        self.critical_threshold_multiplier = 1.0  # 100% of critical


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, integration: OrderManagementIntegration, thresholds: Optional[PerformanceThresholds] = None):
        self.integration = integration
        self.thresholds = thresholds or PerformanceThresholds()
        
        # Performance tracking
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts_history: deque = deque(maxlen=500)
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 1.0  # seconds
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Performance tracking
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        self.performance_stats: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def start_monitoring(self) -> None:
        """Start real-time performance monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("📊 Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("⏹️ Performance monitoring stopped")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add alert callback function."""
        self.alert_callbacks.append(callback)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._check_thresholds()
                self._update_trends()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Performance monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_metrics(self) -> None:
        """Collect current performance metrics."""
        timestamp = time.time()
        metrics = {}
        
        # Get analytics data
        analytics_data = self.integration.analytics.get_real_time_metrics()
        integration_status = self.integration.get_integration_status()
        
        # Order completion metrics
        metrics['success_rate'] = PerformanceMetric(
            name='success_rate',
            value=analytics_data.get('success_rate', 0.0),
            unit='%',
            timestamp=timestamp,
            threshold=self.thresholds.min_success_rate,
            alert_level=AlertLevel.WARNING if analytics_data.get('success_rate', 0.0) < self.thresholds.min_success_rate else AlertLevel.INFO
        )
        
        metrics['average_completion_time'] = PerformanceMetric(
            name='average_completion_time',
            value=analytics_data.get('average_completion_time', 0.0),
            unit='seconds',
            timestamp=timestamp,
            threshold=self.thresholds.max_completion_time,
            alert_level=AlertLevel.WARNING if analytics_data.get('average_completion_time', 0.0) > self.thresholds.max_completion_time else AlertLevel.INFO
        )
        
        metrics['error_rate'] = PerformanceMetric(
            name='error_rate',
            value=analytics_data.get('error_rate', 0.0),
            unit='%',
            timestamp=timestamp,
            threshold=self.thresholds.max_error_rate,
            alert_level=AlertLevel.WARNING if analytics_data.get('error_rate', 0.0) > self.thresholds.max_error_rate else AlertLevel.INFO
        )
        
        # Queue metrics
        queue_status = self.integration.queue_manager.get_queue_status()
        metrics['queue_size'] = PerformanceMetric(
            name='queue_size',
            value=queue_status.get('queue_size', 0),
            unit='orders',
            timestamp=timestamp,
            threshold=self.thresholds.max_queue_size,
            alert_level=AlertLevel.WARNING if queue_status.get('queue_size', 0) > self.thresholds.max_queue_size else AlertLevel.INFO
        )
        
        # Throughput metrics
        metrics['throughput_per_hour'] = PerformanceMetric(
            name='throughput_per_hour',
            value=analytics_data.get('throughput_per_hour', 0.0),
            unit='orders/hour',
            timestamp=timestamp,
            threshold=self.thresholds.min_throughput,
            alert_level=AlertLevel.WARNING if analytics_data.get('throughput_per_hour', 0.0) < self.thresholds.min_throughput else AlertLevel.INFO
        )
        
        # System metrics
        metrics['total_orders_processed'] = PerformanceMetric(
            name='total_orders_processed',
            value=integration_status.get('integration_metrics', {}).get('total_orders_processed', 0),
            unit='orders',
            timestamp=timestamp
        )
        
        # Create snapshot
        snapshot = PerformanceSnapshot(
            timestamp=timestamp,
            metrics=metrics,
            alerts=list(self.active_alerts.values()),
            summary=self._calculate_summary(metrics)
        )
        
        self.metrics_history.append(snapshot)
    
    def _check_thresholds(self) -> None:
        """Check metrics against thresholds and generate alerts."""
        if not self.metrics_history:
            return
        
        current_snapshot = self.metrics_history[-1]
        
        for metric_name, metric in current_snapshot.metrics.items():
            if metric.threshold is None:
                continue
            
            # Check if threshold is exceeded
            threshold_exceeded = False
            alert_level = AlertLevel.INFO
            
            if metric_name in ['success_rate', 'throughput_per_hour', 'robot_utilization']:
                # Higher is better
                threshold_exceeded = metric.value < metric.threshold
            else:
                # Lower is better
                threshold_exceeded = metric.value > metric.threshold
            
            if threshold_exceeded:
                # Determine alert level
                if metric.value >= metric.threshold * self.thresholds.critical_threshold_multiplier:
                    alert_level = AlertLevel.CRITICAL
                elif metric.value >= metric.threshold * self.thresholds.warning_threshold_multiplier:
                    alert_level = AlertLevel.WARNING
                else:
                    alert_level = AlertLevel.ERROR
                
                # Create or update alert
                alert = PerformanceAlert(
                    metric_name=metric_name,
                    current_value=metric.value,
                    threshold_value=metric.threshold,
                    alert_level=alert_level,
                    message=f"{metric_name} threshold exceeded: {metric.value:.2f} {metric.unit} (threshold: {metric.threshold:.2f})",
                    timestamp=time.time()
                )
                
                self.active_alerts[metric_name] = alert
                
                # Trigger alert callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        print(f"❌ Alert callback error: {e}")
            else:
                # Clear alert if threshold is no longer exceeded
                if metric_name in self.active_alerts:
                    del self.active_alerts[metric_name]
    
    def _update_trends(self) -> None:
        """Update performance trends and statistics."""
        if len(self.metrics_history) < 2:
            return
        
        # Get recent metrics (last 10 snapshots)
        recent_snapshots = list(self.metrics_history)[-10:]
        
        for snapshot in recent_snapshots:
            for metric_name, metric in snapshot.metrics.items():
                self.performance_trends[metric_name].append(metric.value)
                
                # Keep only last 100 values
                if len(self.performance_trends[metric_name]) > 100:
                    self.performance_trends[metric_name] = self.performance_trends[metric_name][-100:]
        
        # Calculate statistics for each metric
        for metric_name, values in self.performance_trends.items():
            if values:
                self.performance_stats[metric_name] = {
                    'current': values[-1] if values else 0.0,
                    'average': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'trend': self._calculate_trend(values)
                }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a metric."""
        if len(values) < 2:
            return "stable"
        
        recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
        older_avg = statistics.mean(values[-10:-5]) if len(values) >= 10 else values[0]
        
        change_percent = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_summary(self, metrics: Dict[str, PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance summary."""
        summary = {
            'total_metrics': len(metrics),
            'metrics_with_alerts': sum(1 for m in metrics.values() if m.alert_level != AlertLevel.INFO),
            'critical_alerts': sum(1 for m in metrics.values() if m.alert_level == AlertLevel.CRITICAL),
            'warning_alerts': sum(1 for m in metrics.values() if m.alert_level == AlertLevel.WARNING),
            'error_alerts': sum(1 for m in metrics.values() if m.alert_level == AlertLevel.ERROR),
            'overall_health': self._calculate_overall_health(metrics)
        }
        return summary
    
    def _calculate_overall_health(self, metrics: Dict[str, PerformanceMetric]) -> str:
        """Calculate overall system health."""
        critical_count = sum(1 for m in metrics.values() if m.alert_level == AlertLevel.CRITICAL)
        warning_count = sum(1 for m in metrics.values() if m.alert_level == AlertLevel.WARNING)
        error_count = sum(1 for m in metrics.values() if m.alert_level == AlertLevel.ERROR)
        
        if critical_count > 0 or error_count > 0:
            return "critical"
        elif warning_count > 0:
            return "warning"
        else:
            return "healthy"
    
    def get_current_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get current performance metrics."""
        if not self.metrics_history:
            return {}
        
        return self.metrics_history[-1].metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.metrics_history:
            return {}
        
        current_snapshot = self.metrics_history[-1]
        
        return {
            'timestamp': current_snapshot.timestamp,
            'metrics': {name: asdict(metric) for name, metric in current_snapshot.metrics.items()},
            'alerts': [asdict(alert) for alert in current_snapshot.alerts],
            'summary': current_snapshot.summary,
            'trends': self.performance_stats,
            'active_alerts_count': len(self.active_alerts)
        }
    
    def get_performance_trends(self, metric_name: str, duration_minutes: int = 60) -> List[float]:
        """Get performance trends for a specific metric."""
        if metric_name not in self.performance_trends:
            return []
        
        values = self.performance_trends[metric_name]
        cutoff_time = time.time() - (duration_minutes * 60)
        
        # Filter values by time (approximate)
        recent_values = values[-min(len(values), duration_minutes * 60):]
        return recent_values
    
    def export_performance_data(self, filename: str) -> bool:
        """Export performance data to JSON file."""
        try:
            export_data = {
                'timestamp': time.time(),
                'thresholds': asdict(self.thresholds),
                'metrics_history': [asdict(snapshot) for snapshot in self.metrics_history],
                'alerts_history': [asdict(alert) for alert in self.alerts_history],
                'performance_stats': self.performance_stats,
                'active_alerts': [asdict(alert) for alert in self.active_alerts.values()]
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"📊 Performance data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export performance data: {e}")
            return False


class PerformanceDisplay:
    """Console-based performance display."""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.display_active = False
        self.display_thread = None
        self.update_interval = 2.0
    
    def start_display(self) -> None:
        """Start real-time performance display."""
        if not self.display_active:
            self.display_active = True
            self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self.display_thread.start()
            print("📈 Performance display started")
    
    def stop_display(self) -> None:
        """Stop performance display."""
        self.display_active = False
        if self.display_thread:
            self.display_thread.join(timeout=2.0)
        print("⏹️ Performance display stopped")
    
    def _display_loop(self) -> None:
        """Main display loop."""
        while self.display_active:
            try:
                self._display_performance()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Display error: {e}")
                time.sleep(self.update_interval)
    
    def _display_performance(self) -> None:
        """Display current performance metrics."""
        summary = self.monitor.get_performance_summary()
        
        # Clear console
        print("\n" * 40)
        
        # Header
        print("=" * 80)
        print("📊 PERFORMANCE MONITOR")
        print("=" * 80)
        print(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Overall health
        health = summary.get('summary', {}).get('overall_health', 'unknown')
        health_emoji = {
            'healthy': '🟢',
            'warning': '🟡',
            'critical': '🔴'
        }.get(health, '❓')
        
        print(f"🏥 Overall Health: {health_emoji} {health.upper()}")
        print()
        
        # Current metrics
        print("📈 CURRENT METRICS")
        print("-" * 40)
        
        metrics = summary.get('metrics', {})
        for metric_name, metric_data in metrics.items():
            value = metric_data.get('value', 0.0)
            unit = metric_data.get('unit', '')
            alert_level = metric_data.get('alert_level', 'info')
            
            alert_emoji = {
                'info': '🟢',
                'warning': '🟡',
                'critical': '🔴',
                'error': '❌'
            }.get(alert_level, '❓')
            
            print(f"{alert_emoji} {metric_name}: {value:.2f} {unit}")
        
        print()
        
        # Active alerts
        active_alerts = summary.get('active_alerts_count', 0)
        if active_alerts > 0:
            print("⚠️ ACTIVE ALERTS")
            print("-" * 40)
            print(f"Total active alerts: {active_alerts}")
            
            alerts = summary.get('alerts', [])
            for alert in alerts[:3]:  # Show first 3 alerts
                alert_level = alert.get('alert_level', 'info')
                alert_emoji = {
                    'info': '🟢',
                    'warning': '🟡',
                    'critical': '🔴',
                    'error': '❌'
                }.get(alert_level, '❓')
                
                print(f"{alert_emoji} {alert.get('metric_name', 'unknown')}: {alert.get('message', 'No message')}")
        else:
            print("✅ No active alerts")
        
        print()
        
        # Performance trends
        print("📊 PERFORMANCE TRENDS")
        print("-" * 40)
        
        trends = summary.get('trends', {})
        for metric_name, trend_data in list(trends.items())[:5]:  # Show first 5 trends
            current = trend_data.get('current', 0.0)
            average = trend_data.get('average', 0.0)
            trend = trend_data.get('trend', 'stable')
            
            trend_emoji = {
                'increasing': '📈',
                'decreasing': '📉',
                'stable': '➡️'
            }.get(trend, '❓')
            
            print(f"{trend_emoji} {metric_name}: {current:.2f} (avg: {average:.2f})")
        
        print()
        print("=" * 80)


class PerformanceAlertHandler:
    """Handles performance alerts and notifications."""
    
    def __init__(self):
        self.alert_history: List[PerformanceAlert] = []
        self.alert_callbacks: Dict[AlertLevel, List[Callable]] = defaultdict(list)
    
    def add_alert_callback(self, alert_level: AlertLevel, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback for specific alert level."""
        self.alert_callbacks[alert_level].append(callback)
    
    def handle_alert(self, alert: PerformanceAlert) -> None:
        """Handle a performance alert."""
        self.alert_history.append(alert)
        
        # Call level-specific callbacks
        for callback in self.alert_callbacks[alert.alert_level]:
            try:
                callback(alert)
            except Exception as e:
                print(f"❌ Alert callback error: {e}")
        
        # Call general callbacks
        for callback in self.alert_callbacks[None]:
            try:
                callback(alert)
            except Exception as e:
                print(f"❌ General alert callback error: {e}")
        
        # Console notification
        alert_emoji = {
            AlertLevel.INFO: 'ℹ️',
            AlertLevel.WARNING: '⚠️',
            AlertLevel.CRITICAL: '🚨',
            AlertLevel.ERROR: '❌'
        }.get(alert.alert_level, '❓')
        
        print(f"{alert_emoji} PERFORMANCE ALERT: {alert.message}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        alert_counts = defaultdict(int)
        for alert in self.alert_history:
            alert_counts[alert.alert_level.value] += 1
        
        return {
            'total_alerts': len(self.alert_history),
            'alert_counts': dict(alert_counts),
            'recent_alerts': [asdict(alert) for alert in self.alert_history[-10:]]
        }


# Utility functions

def create_performance_monitor(integration: OrderManagementIntegration, thresholds: Optional[PerformanceThresholds] = None) -> PerformanceMonitor:
    """Create performance monitor."""
    return PerformanceMonitor(integration, thresholds)


def create_performance_display(monitor: PerformanceMonitor) -> PerformanceDisplay:
    """Create performance display."""
    return PerformanceDisplay(monitor)


def create_alert_handler() -> PerformanceAlertHandler:
    """Create alert handler."""
    return PerformanceAlertHandler()


def start_performance_monitoring(integration: OrderManagementIntegration, display: bool = True) -> PerformanceMonitor:
    """Start comprehensive performance monitoring."""
    monitor = create_performance_monitor(integration)
    monitor.start_monitoring()
    
    if display:
        display_obj = create_performance_display(monitor)
        display_obj.start_display()
    
    return monitor


def export_performance_report(integration: OrderManagementIntegration, filename: str = "performance_report.json") -> bool:
    """Export comprehensive performance report."""
    monitor = create_performance_monitor(integration)
    return monitor.export_performance_data(filename) 