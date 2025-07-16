"""
System Performance Monitoring Module

This module provides comprehensive system-wide performance monitoring capabilities,
including throughput analytics, system health dashboard, and performance threshold monitoring.
"""

import time
import psutil
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import json

from .analytics_engine import AnalyticsEngine, MetricData, KPICalculation


class SystemMetric(Enum):
    """System performance metric enumeration."""
    THROUGHPUT = "throughput"
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_UTILIZATION = "cpu_utilization"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ERROR_RATE = "error_rate"
    SYSTEM_LOAD = "system_load"
    PROCESS_COUNT = "process_count"
    THREAD_COUNT = "thread_count"


@dataclass
class SystemPerformanceData:
    """Data structure for system performance information."""
    timestamp: float
    metric_type: SystemMetric
    value: float
    unit: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class SystemHealthSnapshot:
    """Data structure for system health snapshot."""
    timestamp: float
    throughput_ops_per_sec: float
    average_response_time: float
    memory_usage_percent: float
    cpu_utilization_percent: float
    disk_io_mbps: float
    network_io_mbps: float
    error_rate_percent: float
    system_load: float
    process_count: int
    thread_count: int
    health_score: float
    alerts: List[str] = field(default_factory=list)
    is_healthy: bool = True


@dataclass
class PerformanceThreshold:
    """Data structure for performance thresholds."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


class SystemPerformanceMonitor:
    """
    Comprehensive system performance monitoring with throughput analytics and health dashboard.
    
    Provides real-time system performance monitoring, throughput analysis,
    performance threshold monitoring, and system health dashboard capabilities.
    """
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        """
        Initialize SystemPerformanceMonitor with analytics engine.
        
        Args:
            analytics_engine: Core analytics engine for data collection
        """
        self.analytics = analytics_engine
        self.performance_data: List[SystemPerformanceData] = []
        self.health_snapshots: List[SystemHealthSnapshot] = []
        self.throughput_history: List[float] = []
        self.response_time_history: List[float] = []
        self.error_count_history: List[int] = []
        
        # Performance tracking
        self.last_monitoring_time = time.time()
        self.monitoring_interval = 5.0  # seconds
        self.max_history_size = 1000
        
        # Performance thresholds
        self.thresholds = self._initialize_thresholds()
        
        # System metrics
        self._total_operations = 0
        self._total_response_time = 0.0
        self._total_errors = 0
        self._last_throughput_calculation = time.time()
        self._start_time = time.time()  # Track when monitoring started
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize metrics
        self._initialize_system_metrics()
    
    def _initialize_thresholds(self) -> Dict[str, PerformanceThreshold]:
        """Initialize performance thresholds."""
        return {
            "throughput": PerformanceThreshold(
                "throughput", 100.0, 50.0, "ops/sec", "Operations per second"
            ),
            "response_time": PerformanceThreshold(
                "response_time", 1000.0, 2000.0, "ms", "Average response time"
            ),
            "memory_usage": PerformanceThreshold(
                "memory_usage", 80.0, 90.0, "%", "Memory usage percentage"
            ),
            "cpu_utilization": PerformanceThreshold(
                "cpu_utilization", 80.0, 95.0, "%", "CPU utilization percentage"
            ),
            "error_rate": PerformanceThreshold(
                "error_rate", 5.0, 10.0, "%", "Error rate percentage"
            ),
            "system_load": PerformanceThreshold(
                "system_load", 2.0, 5.0, "load", "System load average"
            )
        }
    
    def _initialize_system_metrics(self):
        """Initialize system-specific metrics in the analytics engine."""
        # System performance metrics
        self.analytics.record_metric("system_throughput", 0.0, "system_performance")
        self.analytics.record_metric("system_response_time", 0.0, "system_performance")
        self.analytics.record_metric("system_error_rate", 0.0, "system_performance")
        self.analytics.record_metric("system_health_score", 100.0, "system_performance")
        
        # Resource utilization metrics
        self.analytics.record_metric("system_memory_usage", 0.0, "system_performance")
        self.analytics.record_metric("system_cpu_utilization", 0.0, "system_performance")
        self.analytics.record_metric("system_disk_io", 0.0, "system_performance")
        self.analytics.record_metric("system_network_io", 0.0, "system_performance")
        
        # System load metrics
        self.analytics.record_metric("system_load_average", 0.0, "system_performance")
        self.analytics.record_metric("system_process_count", 0, "system_performance")
        self.analytics.record_metric("system_thread_count", 0, "system_performance")
    
    def start_system_monitoring(self):
        """Start system performance monitoring."""
        with self._lock:
            self.last_monitoring_time = time.time()
            self._collect_system_performance_metrics()
    
    def track_operation(self, operation_name: str, response_time_ms: float, 
                       success: bool = True, metadata: Dict = None):
        """
        Track a system operation for performance monitoring.
        
        Args:
            operation_name: Name of the operation being tracked
            response_time_ms: Response time in milliseconds
            success: Whether the operation was successful
            metadata: Additional operation metadata
        """
        with self._lock:
            current_time = time.time()
            
            # Record performance data
            performance_data = SystemPerformanceData(
                timestamp=current_time,
                metric_type=SystemMetric.RESPONSE_TIME,
                value=response_time_ms,
                unit="ms",
                metadata={
                    "operation": operation_name,
                    "success": success,
                    **(metadata or {})
                }
            )
            
            self.performance_data.append(performance_data)
            self.response_time_history.append(response_time_ms)
            
            # Update counters
            self._total_operations += 1
            self._total_response_time += response_time_ms
            
            if not success:
                self._total_errors += 1
                self.error_count_history.append(1)
            else:
                self.error_count_history.append(0)
            
            # Update metrics
            if self.response_time_history:
                avg_response_time = statistics.mean(self.response_time_history)
                self.analytics.record_metric("system_response_time", avg_response_time, "system_performance")
            
            # Calculate throughput (simplified to avoid hanging)
            self._update_throughput_metrics_simple()
            
            # Cleanup old data
            self._cleanup_old_data()
    
    def _update_throughput_metrics_simple(self):
        """Update throughput metrics with simplified calculation."""
        # Simple throughput calculation based on total operations
        if self._total_operations > 0:
            # Calculate overall throughput (operations per second since start)
            total_time = time.time() - self._start_time
            if total_time > 0:
                throughput = self._total_operations / total_time
            else:
                throughput = 0.0
            
            self.throughput_history.append(throughput)
            self.analytics.record_metric("system_throughput", throughput, "system_performance")
            
            # Calculate error rate
            if self._total_operations > 0:
                error_rate = (self._total_errors / self._total_operations * 100)
                self.analytics.record_metric("system_error_rate", error_rate, "system_performance")
    
    def _update_throughput_metrics(self):
        """Update throughput metrics."""
        current_time = time.time()
        time_window = current_time - self._last_throughput_calculation
        
        if time_window >= 1.0:  # Update every second
            # Calculate operations per second
            recent_operations = len([op for op in self.performance_data 
                                   if op.timestamp >= self._last_throughput_calculation])
            throughput = recent_operations / time_window if time_window > 0 else 0.0
            
            self.throughput_history.append(throughput)
            self.analytics.record_metric("system_throughput", throughput, "system_performance")
            
            # Calculate error rate
            if self.error_count_history:
                # Use a simpler approach to avoid hanging
                recent_errors = sum(self.error_count_history[-min(100, len(self.error_count_history)):])
                total_recent_ops = min(100, len(self.error_count_history))
                error_rate = (recent_errors / total_recent_ops * 100) if total_recent_ops > 0 else 0.0
                self.analytics.record_metric("system_error_rate", error_rate, "system_performance")
            
            self._last_throughput_calculation = current_time
    
    def _collect_system_performance_metrics(self):
        """Collect comprehensive system performance metrics."""
        try:
            current_time = time.time()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # CPU usage (with timeout to prevent hanging)
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
            except Exception:
                # Fallback if psutil hangs
                cpu_percent = 0.0
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_io_mbps = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_io_mbps = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)
            
            # Process and thread counts
            process_count = len(psutil.pids())
            thread_count = psutil.cpu_count(logical=True)
            
            # System load
            try:
                system_load = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            except AttributeError:
                system_load = 0.0
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(self.response_time_history) if self.response_time_history else 0.0
            current_throughput = self.throughput_history[-1] if self.throughput_history else 0.0
            error_rate = (self._total_errors / self._total_operations * 100) if self._total_operations > 0 else 0.0
            
            # Record metrics
            self.analytics.record_metric("system_memory_usage", memory_percent, "system_performance")
            self.analytics.record_metric("system_cpu_utilization", cpu_percent, "system_performance")
            self.analytics.record_metric("system_disk_io", disk_io_mbps, "system_performance")
            self.analytics.record_metric("system_network_io", network_io_mbps, "system_performance")
            self.analytics.record_metric("system_load_average", system_load, "system_performance")
            self.analytics.record_metric("system_process_count", process_count, "system_performance")
            self.analytics.record_metric("system_thread_count", thread_count, "system_performance")
            
            # Generate health snapshot
            health_snapshot = self._generate_health_snapshot(
                current_time, current_throughput, avg_response_time, memory_percent,
                cpu_percent, disk_io_mbps, network_io_mbps, error_rate,
                system_load, process_count, thread_count
            )
            
            self.health_snapshots.append(health_snapshot)
            
            # Update health score
            self.analytics.record_metric("system_health_score", health_snapshot.health_score, "system_performance")
            
        except Exception as e:
            print(f"Warning: Could not collect system performance metrics: {e}")
    
    def _generate_health_snapshot(self, timestamp: float, throughput: float, 
                                 response_time: float, memory_percent: float,
                                 cpu_percent: float, disk_io: float, 
                                 network_io: float, error_rate: float,
                                 system_load: float, process_count: int, 
                                 thread_count: int) -> SystemHealthSnapshot:
        """
        Generate system health snapshot with scoring and alerts.
        
        Args:
            timestamp: Current timestamp
            throughput: Current throughput (ops/sec)
            response_time: Average response time (ms)
            memory_percent: Memory usage percentage
            cpu_percent: CPU usage percentage
            disk_io: Disk I/O in MB/s
            network_io: Network I/O in MB/s
            error_rate: Error rate percentage
            system_load: System load average
            process_count: Number of processes
            thread_count: Number of threads
            
        Returns:
            SystemHealthSnapshot with health score and alerts
        """
        alerts = []
        health_score = 100.0
        
        # Check throughput
        if throughput < self.thresholds["throughput"].critical_threshold:
            alerts.append(f"Critical: Low throughput ({throughput:.1f} ops/sec)")
            health_score -= 25.0
        elif throughput < self.thresholds["throughput"].warning_threshold:
            alerts.append(f"Warning: Low throughput ({throughput:.1f} ops/sec)")
            health_score -= 10.0
        
        # Check response time
        if response_time > self.thresholds["response_time"].critical_threshold:
            alerts.append(f"Critical: High response time ({response_time:.1f} ms)")
            health_score -= 25.0
        elif response_time > self.thresholds["response_time"].warning_threshold:
            alerts.append(f"Warning: High response time ({response_time:.1f} ms)")
            health_score -= 10.0
        
        # Check memory usage
        if memory_percent > self.thresholds["memory_usage"].critical_threshold:
            alerts.append(f"Critical: High memory usage ({memory_percent:.1f}%)")
            health_score -= 20.0
        elif memory_percent > self.thresholds["memory_usage"].warning_threshold:
            alerts.append(f"Warning: High memory usage ({memory_percent:.1f}%)")
            health_score -= 10.0
        
        # Check CPU utilization
        if cpu_percent > self.thresholds["cpu_utilization"].critical_threshold:
            alerts.append(f"Critical: High CPU usage ({cpu_percent:.1f}%)")
            health_score -= 20.0
        elif cpu_percent > self.thresholds["cpu_utilization"].warning_threshold:
            alerts.append(f"Warning: High CPU usage ({cpu_percent:.1f}%)")
            health_score -= 10.0
        
        # Check error rate
        if error_rate > self.thresholds["error_rate"].critical_threshold:
            alerts.append(f"Critical: High error rate ({error_rate:.1f}%)")
            health_score -= 30.0
        elif error_rate > self.thresholds["error_rate"].warning_threshold:
            alerts.append(f"Warning: High error rate ({error_rate:.1f}%)")
            health_score -= 15.0
        
        # Check system load
        if system_load > self.thresholds["system_load"].critical_threshold:
            alerts.append(f"Critical: High system load ({system_load:.1f})")
            health_score -= 15.0
        elif system_load > self.thresholds["system_load"].warning_threshold:
            alerts.append(f"Warning: High system load ({system_load:.1f})")
            health_score -= 5.0
        
        # Ensure health score doesn't go below 0
        health_score = max(0.0, health_score)
        
        # Determine if system is healthy
        is_healthy = health_score >= 70.0 and len(alerts) == 0
        
        return SystemHealthSnapshot(
            timestamp=timestamp,
            throughput_ops_per_sec=throughput,
            average_response_time=response_time,
            memory_usage_percent=memory_percent,
            cpu_utilization_percent=cpu_percent,
            disk_io_mbps=disk_io,
            network_io_mbps=network_io,
            error_rate_percent=error_rate,
            system_load=system_load,
            process_count=process_count,
            thread_count=thread_count,
            health_score=health_score,
            alerts=alerts,
            is_healthy=is_healthy
        )
    
    def get_system_performance_summary(self) -> Dict:
        """
        Get comprehensive system performance summary.
        
        Returns:
            Dictionary with all system performance analytics data
        """
        with self._lock:
            # Calculate performance statistics
            throughput_stats = {
                "current_throughput": self.throughput_history[-1] if self.throughput_history else 0.0,
                "average_throughput": statistics.mean(self.throughput_history) if self.throughput_history else 0.0,
                "max_throughput": max(self.throughput_history) if self.throughput_history else 0.0,
                "min_throughput": min(self.throughput_history) if self.throughput_history else 0.0
            }
            
            response_time_stats = {
                "current_response_time": self.response_time_history[-1] if self.response_time_history else 0.0,
                "average_response_time": statistics.mean(self.response_time_history) if self.response_time_history else 0.0,
                "max_response_time": max(self.response_time_history) if self.response_time_history else 0.0,
                "min_response_time": min(self.response_time_history) if self.response_time_history else 0.0
            }
            
            # Get current system health
            current_health = self.health_snapshots[-1] if self.health_snapshots else None
            
            return {
                "throughput_stats": throughput_stats,
                "response_time_stats": response_time_stats,
                "system_health": {
                    "current_score": current_health.health_score if current_health else 100.0,
                    "is_healthy": current_health.is_healthy if current_health else True,
                    "alerts": current_health.alerts if current_health else [],
                    "alert_count": len(current_health.alerts) if current_health else 0
                },
                "system_resources": {
                    "memory_usage": self.analytics.get_kpi("system_performance.system_memory_usage").value if self.analytics.get_kpi("system_performance.system_memory_usage") else 0.0,
                    "cpu_utilization": self.analytics.get_kpi("system_performance.system_cpu_utilization").value if self.analytics.get_kpi("system_performance.system_cpu_utilization") else 0.0,
                    "disk_io": self.analytics.get_kpi("system_performance.system_disk_io").value if self.analytics.get_kpi("system_performance.system_disk_io") else 0.0,
                    "network_io": self.analytics.get_kpi("system_performance.system_network_io").value if self.analytics.get_kpi("system_performance.system_network_io") else 0.0,
                    "system_load": self.analytics.get_kpi("system_performance.system_load_average").value if self.analytics.get_kpi("system_performance.system_load_average") else 0.0,
                    "process_count": self.analytics.get_kpi("system_performance.system_process_count").value if self.analytics.get_kpi("system_performance.system_process_count") else 0,
                    "thread_count": self.analytics.get_kpi("system_performance.system_thread_count").value if self.analytics.get_kpi("system_performance.system_thread_count") else 0
                },
                "performance_metrics": {
                    "total_operations": self._total_operations,
                    "total_errors": self._total_errors,
                    "error_rate": (self._total_errors / self._total_operations * 100) if self._total_operations > 0 else 0.0,
                    "throughput": self.analytics.get_kpi("system_performance.system_throughput").value if self.analytics.get_kpi("system_performance.system_throughput") else 0.0,
                    "response_time": self.analytics.get_kpi("system_performance.system_response_time").value if self.analytics.get_kpi("system_performance.system_response_time") else 0.0
                }
            }
    
    def get_performance_history(self, metric_type: SystemMetric = None, 
                              limit: int = 100) -> List[SystemPerformanceData]:
        """
        Get performance history for specific metric type.
        
        Args:
            metric_type: Type of performance metric to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of performance data records
        """
        with self._lock:
            if metric_type:
                filtered_data = [data for data in self.performance_data if data.metric_type == metric_type]
            else:
                filtered_data = self.performance_data
            
            return filtered_data[-limit:] if limit else filtered_data
    
    def get_health_history(self, limit: int = 100) -> List[SystemHealthSnapshot]:
        """
        Get system health history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of system health snapshot records
        """
        with self._lock:
            return self.health_snapshots[-limit:] if limit else self.health_snapshots
    
    def get_performance_alerts(self) -> List[str]:
        """
        Get current performance alerts.
        
        Returns:
            List of active performance alerts
        """
        with self._lock:
            current_health = self.health_snapshots[-1] if self.health_snapshots else None
            return current_health.alerts if current_health else []
    
    def is_system_healthy(self) -> bool:
        """
        Check if system is currently healthy.
        
        Returns:
            True if system is healthy, False otherwise
        """
        with self._lock:
            current_health = self.health_snapshots[-1] if self.health_snapshots else None
            return current_health.is_healthy if current_health else True
    
    def get_health_score(self) -> float:
        """
        Get current system health score.
        
        Returns:
            Health score (0-100)
        """
        with self._lock:
            current_health = self.health_snapshots[-1] if self.health_snapshots else None
            return current_health.health_score if current_health else 100.0
    
    def update_thresholds(self, **thresholds):
        """
        Update performance thresholds.
        
        Args:
            **thresholds: Keyword arguments with threshold name and new values
        """
        with self._lock:
            for threshold_name, new_value in thresholds.items():
                if threshold_name in self.thresholds:
                    if isinstance(new_value, (list, tuple)) and len(new_value) >= 2:
                        self.thresholds[threshold_name].warning_threshold = new_value[0]
                        self.thresholds[threshold_name].critical_threshold = new_value[1]
                    else:
                        # Assume it's a critical threshold
                        self.thresholds[threshold_name].critical_threshold = new_value
    
    def get_thresholds(self) -> Dict[str, PerformanceThreshold]:
        """
        Get current performance thresholds.
        
        Returns:
            Dictionary of current performance thresholds
        """
        with self._lock:
            return self.thresholds.copy()
    
    def _cleanup_old_data(self):
        """Clean up old performance data to manage memory usage."""
        # Don't acquire lock if already held (prevents deadlock)
        if len(self.performance_data) > self.max_history_size:
            # Keep only the most recent data
            self.performance_data = self.performance_data[-self.max_history_size:]
        
        if len(self.health_snapshots) > self.max_history_size:
            self.health_snapshots = self.health_snapshots[-self.max_history_size:]
        
        if len(self.throughput_history) > self.max_history_size:
            self.throughput_history = self.throughput_history[-self.max_history_size:]
        
        if len(self.response_time_history) > self.max_history_size:
            self.response_time_history = self.response_time_history[-self.max_history_size:]
        
        if len(self.error_count_history) > self.max_history_size:
            self.error_count_history = self.error_count_history[-self.max_history_size:]
    
    def clear_performance_data(self):
        """Clear all performance data."""
        with self._lock:
            self.performance_data.clear()
            self.health_snapshots.clear()
            self.throughput_history.clear()
            self.response_time_history.clear()
            self.error_count_history.clear()
            
            # Reset counters
            self._total_operations = 0
            self._total_response_time = 0.0
            self._total_errors = 0
            self._last_throughput_calculation = time.time()
            
            # Reset metrics
            self._initialize_system_metrics()
    
    def export_performance_data(self, format_type: str = "json") -> str:
        """
        Export performance data in specified format.
        
        Args:
            format_type: Export format ("json" or "csv")
            
        Returns:
            Exported data as string
        """
        with self._lock:
            if format_type.lower() == "json":
                return self._export_to_json()
            elif format_type.lower() == "csv":
                return self._export_to_csv()
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_to_json(self) -> str:
        """Export performance data to JSON format."""
        export_data = {
            "export_timestamp": time.time(),
            "performance_data": [
                {
                    "timestamp": data.timestamp,
                    "metric_type": data.metric_type.value,
                    "value": data.value,
                    "unit": data.unit,
                    "metadata": data.metadata
                }
                for data in self.performance_data
            ],
            "health_snapshots": [
                {
                    "timestamp": snapshot.timestamp,
                    "throughput_ops_per_sec": snapshot.throughput_ops_per_sec,
                    "average_response_time": snapshot.average_response_time,
                    "memory_usage_percent": snapshot.memory_usage_percent,
                    "cpu_utilization_percent": snapshot.cpu_utilization_percent,
                    "disk_io_mbps": snapshot.disk_io_mbps,
                    "network_io_mbps": snapshot.network_io_mbps,
                    "error_rate_percent": snapshot.error_rate_percent,
                    "system_load": snapshot.system_load,
                    "process_count": snapshot.process_count,
                    "thread_count": snapshot.thread_count,
                    "health_score": snapshot.health_score,
                    "alerts": snapshot.alerts,
                    "is_healthy": snapshot.is_healthy
                }
                for snapshot in self.health_snapshots
            ],
            "summary": self.get_system_performance_summary()
        }
        
        return json.dumps(export_data, indent=2)
    
    def _export_to_csv(self) -> str:
        """Export performance data to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "timestamp", "metric_type", "value", "unit", "metadata"
        ])
        
        # Write performance data
        for data in self.performance_data:
            writer.writerow([
                data.timestamp,
                data.metric_type.value,
                data.value,
                data.unit,
                json.dumps(data.metadata)
            ])
        
        return output.getvalue() 