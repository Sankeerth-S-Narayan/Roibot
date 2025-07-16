"""
Performance Monitoring Module

This module provides comprehensive system performance monitoring capabilities,
including response time tracking, memory usage monitoring, CPU utilization,
and system health analytics.
"""

import time
import psutil
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from .analytics_engine import AnalyticsEngine, MetricData, KPICalculation


class PerformanceMetric(Enum):
    """Performance metric enumeration for monitoring."""
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_UTILIZATION = "cpu_utilization"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    SYSTEM_LOAD = "system_load"
    THREAD_COUNT = "thread_count"
    PROCESS_COUNT = "process_count"


@dataclass
class PerformanceData:
    """Data structure for performance monitoring information."""
    timestamp: float
    metric_type: PerformanceMetric
    value: float
    unit: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class SystemHealthData:
    """Data structure for system health information."""
    timestamp: float
    memory_percent: float
    cpu_percent: float
    disk_usage_percent: float
    network_io_bytes: int
    thread_count: int
    process_count: int
    system_load: float
    is_healthy: bool
    health_score: float
    alerts: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """
    Comprehensive system performance monitoring and health tracking.
    
    Provides real-time monitoring of system resources, response times,
    and performance metrics with health scoring and alerting.
    """
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        """
        Initialize PerformanceMonitor with analytics engine.
        
        Args:
            analytics_engine: Core analytics engine for data collection
        """
        self.analytics = analytics_engine
        self.performance_data: List[PerformanceData] = []
        self.system_health_history: List[SystemHealthData] = []
        self.response_times: List[float] = []
        self.memory_usage_history: List[float] = []
        self.cpu_usage_history: List[float] = []
        
        # Performance tracking
        self.last_monitoring_time = time.time()
        self.monitoring_interval = 5.0  # seconds
        self.max_history_size = 1000
        
        # Health thresholds
        self.memory_threshold = 80.0  # percent
        self.cpu_threshold = 90.0  # percent
        self.disk_threshold = 85.0  # percent
        self.response_time_threshold = 1000.0  # milliseconds
        
        # Initialize metrics
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize performance-specific metrics in the analytics engine."""
        # System performance metrics
        self.analytics.record_metric("system_memory_usage", 0.0, "system_performance")
        self.analytics.record_metric("system_cpu_utilization", 0.0, "system_performance")
        self.analytics.record_metric("system_disk_usage", 0.0, "system_performance")
        self.analytics.record_metric("system_network_io", 0, "system_performance")
        
        # Response time metrics
        self.analytics.record_metric("average_response_time", 0.0, "system_performance")
        self.analytics.record_metric("max_response_time", 0.0, "system_performance")
        self.analytics.record_metric("response_time_threshold_exceeded", 0, "system_performance")
        
        # System health metrics
        self.analytics.record_metric("system_health_score", 100.0, "system_performance")
        self.analytics.record_metric("system_alerts_count", 0, "system_performance")
        self.analytics.record_metric("system_thread_count", 0, "system_performance")
        self.analytics.record_metric("system_process_count", 0, "system_performance")
        
        # Initialize internal counters
        self._total_response_time = 0.0
        self._max_response_time = 0.0
        self._threshold_exceeded_count = 0
        self._total_alerts = 0
    
    def start_performance_tracking(self):
        """Start performance monitoring and data collection."""
        self.last_monitoring_time = time.time()
        self._collect_system_metrics()
    
    def track_response_time(self, operation_name: str, response_time_ms: float, metadata: Dict = None):
        """
        Track response time for a specific operation.
        
        Args:
            operation_name: Name of the operation being tracked
            response_time_ms: Response time in milliseconds
            metadata: Additional operation metadata
        """
        current_time = time.time()
        
        # Record performance data
        performance_data = PerformanceData(
            timestamp=current_time,
            metric_type=PerformanceMetric.RESPONSE_TIME,
            value=response_time_ms,
            unit="ms",
            metadata={
                "operation": operation_name,
                **(metadata or {})
            }
        )
        
        self.performance_data.append(performance_data)
        self.response_times.append(response_time_ms)
        
        # Update internal counters
        self._total_response_time += response_time_ms
        if response_time_ms > self._max_response_time:
            self._max_response_time = response_time_ms
        
        # Check threshold
        if response_time_ms > self.response_time_threshold:
            self._threshold_exceeded_count += 1
        
        # Update metrics
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times)
            self.analytics.record_metric("average_response_time", avg_response_time, "system_performance")
        
        self.analytics.record_metric("max_response_time", self._max_response_time, "system_performance")
        self.analytics.record_metric("response_time_threshold_exceeded", self._threshold_exceeded_count, "system_performance")
        
        # Cleanup old data
        self._cleanup_old_data()
    
    def _collect_system_metrics(self):
        """Collect current system performance metrics."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_bytes = network.bytes_sent + network.bytes_recv
            
            # Process and thread counts
            process_count = len(psutil.pids())
            thread_count = psutil.cpu_count(logical=True)
            
            # System load (Unix-like systems)
            try:
                system_load = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            except AttributeError:
                system_load = 0.0
            
            # Record metrics
            self.analytics.record_metric("system_memory_usage", memory_percent, "system_performance")
            self.analytics.record_metric("system_cpu_utilization", cpu_percent, "system_performance")
            self.analytics.record_metric("system_disk_usage", disk_percent, "system_performance")
            self.analytics.record_metric("system_network_io", network_bytes, "system_performance")
            self.analytics.record_metric("system_thread_count", thread_count, "system_performance")
            self.analytics.record_metric("system_process_count", process_count, "system_performance")
            
            # Store history
            self.memory_usage_history.append(memory_percent)
            self.cpu_usage_history.append(cpu_percent)
            
            # Generate system health data
            health_data = self._generate_system_health_data(
                memory_percent, cpu_percent, disk_percent, 
                network_bytes, thread_count, process_count, system_load
            )
            
            self.system_health_history.append(health_data)
            
            # Update health metrics
            self.analytics.record_metric("system_health_score", health_data.health_score, "system_performance")
            self.analytics.record_metric("system_alerts_count", len(health_data.alerts), "system_performance")
            
        except Exception as e:
            # Handle cases where psutil might not be available or fail
            print(f"Warning: Could not collect system metrics: {e}")
    
    def _generate_system_health_data(self, memory_percent: float, cpu_percent: float, 
                                   disk_percent: float, network_bytes: int, 
                                   thread_count: int, process_count: int, 
                                   system_load: float) -> SystemHealthData:
        """
        Generate system health data with scoring and alerts.
        
        Args:
            memory_percent: Current memory usage percentage
            cpu_percent: Current CPU usage percentage
            disk_percent: Current disk usage percentage
            network_bytes: Network I/O bytes
            thread_count: Number of threads
            process_count: Number of processes
            system_load: System load average
            
        Returns:
            SystemHealthData with health score and alerts
        """
        current_time = time.time()
        alerts = []
        health_score = 100.0
        
        # Check memory usage
        if memory_percent > self.memory_threshold:
            alerts.append(f"High memory usage: {memory_percent:.1f}%")
            health_score -= 20.0
        
        # Check CPU usage
        if cpu_percent > self.cpu_threshold:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            health_score -= 20.0
        
        # Check disk usage
        if disk_percent > self.disk_threshold:
            alerts.append(f"High disk usage: {disk_percent:.1f}%")
            health_score -= 15.0
        
        # Check response time threshold
        if self._threshold_exceeded_count > 0:
            alerts.append(f"Response time threshold exceeded {self._threshold_exceeded_count} times")
            health_score -= 10.0
        
        # Ensure health score doesn't go below 0
        health_score = max(0.0, health_score)
        
        # Determine if system is healthy
        is_healthy = health_score >= 70.0 and len(alerts) == 0
        
        return SystemHealthData(
            timestamp=current_time,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            disk_usage_percent=disk_percent,
            network_io_bytes=network_bytes,
            thread_count=thread_count,
            process_count=process_count,
            system_load=system_load,
            is_healthy=is_healthy,
            health_score=health_score,
            alerts=alerts
        )
    
    def get_system_performance_summary(self) -> Dict:
        """
        Get comprehensive system performance summary.
        
        Returns:
            Dictionary with all system performance analytics data
        """
        # Calculate response time statistics
        response_time_stats = {
            "average_response_time": statistics.mean(self.response_times) if self.response_times else 0.0,
            "max_response_time": max(self.response_times) if self.response_times else 0.0,
            "min_response_time": min(self.response_times) if self.response_times else 0.0,
            "total_operations": len(self.response_times),
            "threshold_exceeded_count": self._threshold_exceeded_count
        }
        
        # Calculate system resource statistics
        memory_stats = {
            "current_usage": self.memory_usage_history[-1] if self.memory_usage_history else 0.0,
            "average_usage": statistics.mean(self.memory_usage_history) if self.memory_usage_history else 0.0,
            "max_usage": max(self.memory_usage_history) if self.memory_usage_history else 0.0
        }
        
        cpu_stats = {
            "current_usage": self.cpu_usage_history[-1] if self.cpu_usage_history else 0.0,
            "average_usage": statistics.mean(self.cpu_usage_history) if self.cpu_usage_history else 0.0,
            "max_usage": max(self.cpu_usage_history) if self.cpu_usage_history else 0.0
        }
        
        # Get current system health
        current_health = self.system_health_history[-1] if self.system_health_history else None
        
        return {
            "response_time_stats": response_time_stats,
            "memory_stats": memory_stats,
            "cpu_stats": cpu_stats,
            "system_health": {
                "current_score": current_health.health_score if current_health else 100.0,
                "is_healthy": current_health.is_healthy if current_health else True,
                "alerts": current_health.alerts if current_health else [],
                "alert_count": len(current_health.alerts) if current_health else 0
            },
            "system_resources": {
                "memory_usage": self.analytics.get_kpi("system_performance.system_memory_usage").value if self.analytics.get_kpi("system_performance.system_memory_usage") else 0.0,
                "cpu_utilization": self.analytics.get_kpi("system_performance.system_cpu_utilization").value if self.analytics.get_kpi("system_performance.system_cpu_utilization") else 0.0,
                "disk_usage": self.analytics.get_kpi("system_performance.system_disk_usage").value if self.analytics.get_kpi("system_performance.system_disk_usage") else 0.0,
                "network_io": self.analytics.get_kpi("system_performance.system_network_io").value if self.analytics.get_kpi("system_performance.system_network_io") else 0,
                "thread_count": self.analytics.get_kpi("system_performance.system_thread_count").value if self.analytics.get_kpi("system_performance.system_thread_count") else 0,
                "process_count": self.analytics.get_kpi("system_performance.system_process_count").value if self.analytics.get_kpi("system_performance.system_process_count") else 0
            }
        }
    
    def get_performance_history(self, metric_type: PerformanceMetric = None, 
                              limit: int = 100) -> List[PerformanceData]:
        """
        Get performance history for specific metric type.
        
        Args:
            metric_type: Type of performance metric to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of performance data records
        """
        if metric_type:
            filtered_data = [data for data in self.performance_data if data.metric_type == metric_type]
        else:
            filtered_data = self.performance_data
        
        return filtered_data[-limit:] if limit else filtered_data
    
    def get_system_health_history(self, limit: int = 100) -> List[SystemHealthData]:
        """
        Get system health history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of system health data records
        """
        return self.system_health_history[-limit:] if limit else self.system_health_history
    
    def get_performance_alerts(self) -> List[str]:
        """
        Get current performance alerts.
        
        Returns:
            List of active performance alerts
        """
        current_health = self.system_health_history[-1] if self.system_health_history else None
        return current_health.alerts if current_health else []
    
    def is_system_healthy(self) -> bool:
        """
        Check if system is currently healthy.
        
        Returns:
            True if system is healthy, False otherwise
        """
        current_health = self.system_health_history[-1] if self.system_health_history else None
        return current_health.is_healthy if current_health else True
    
    def get_health_score(self) -> float:
        """
        Get current system health score.
        
        Returns:
            Health score (0-100)
        """
        current_health = self.system_health_history[-1] if self.system_health_history else None
        return current_health.health_score if current_health else 100.0
    
    def update_monitoring_interval(self, interval_seconds: float):
        """
        Update monitoring interval.
        
        Args:
            interval_seconds: New monitoring interval in seconds
        """
        self.monitoring_interval = interval_seconds
    
    def update_thresholds(self, memory_threshold: float = None, cpu_threshold: float = None,
                         disk_threshold: float = None, response_time_threshold: float = None):
        """
        Update performance thresholds.
        
        Args:
            memory_threshold: New memory usage threshold (percent)
            cpu_threshold: New CPU usage threshold (percent)
            disk_threshold: New disk usage threshold (percent)
            response_time_threshold: New response time threshold (milliseconds)
        """
        if memory_threshold is not None:
            self.memory_threshold = memory_threshold
        if cpu_threshold is not None:
            self.cpu_threshold = cpu_threshold
        if disk_threshold is not None:
            self.disk_threshold = disk_threshold
        if response_time_threshold is not None:
            self.response_time_threshold = response_time_threshold
    
    def _cleanup_old_data(self):
        """Clean up old performance data to prevent memory issues."""
        if len(self.performance_data) > self.max_history_size:
            self.performance_data = self.performance_data[-self.max_history_size:]
        
        if len(self.system_health_history) > self.max_history_size:
            self.system_health_history = self.system_health_history[-self.max_history_size:]
        
        if len(self.response_times) > self.max_history_size:
            self.response_times = self.response_times[-self.max_history_size:]
        
        if len(self.memory_usage_history) > self.max_history_size:
            self.memory_usage_history = self.memory_usage_history[-self.max_history_size:]
        
        if len(self.cpu_usage_history) > self.max_history_size:
            self.cpu_usage_history = self.cpu_usage_history[-self.max_history_size:]
    
    def clear_performance_data(self):
        """Clear all performance monitoring data."""
        self.performance_data.clear()
        self.system_health_history.clear()
        self.response_times.clear()
        self.memory_usage_history.clear()
        self.cpu_usage_history.clear()
        self.last_monitoring_time = time.time()
        
        # Reset internal counters
        self._total_response_time = 0.0
        self._max_response_time = 0.0
        self._threshold_exceeded_count = 0
        self._total_alerts = 0
        
        # Reinitialize metrics
        self._initialize_metrics() 