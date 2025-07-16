"""
Analytics Engine Core

This module provides the core analytics engine with real-time KPI calculations,
event-driven data collection, and session-based storage for the warehouse simulation.
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading

from core.events import EventSystem


class MetricType(Enum):
    """Types of metrics that can be tracked."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricData:
    """Data structure for metric information."""
    name: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPICalculation:
    """Data structure for KPI calculation results."""
    name: str
    value: float
    unit: str
    timestamp: float
    description: str
    category: str


class AnalyticsEngine:
    """
    Core analytics engine for real-time KPI calculations and performance monitoring.
    
    Features:
    - Real-time KPI calculations
    - Event-driven data collection
    - Session-based storage
    - Rolling average calculations
    - Memory-efficient data management
    - Thread-safe operations
    """
    
    def __init__(self, config_file: str = "config/analytics.json"):
        """Initialize the analytics engine."""
        self.config_file = config_file
        self.config = self._load_configuration()
        
        # Data storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.kpi_cache: Dict[str, KPICalculation] = {}
        self.session_start_time = time.time()
        
        # Event system integration
        self.event_system: Optional[EventSystem] = None
        self.event_handlers: Dict[str, Callable] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance tracking
        self.calculation_times: deque = deque(maxlen=100)
        self.last_calculation_time = 0.0
        
        # Rolling window configuration
        self.rolling_window_seconds = self.config.get("rolling_window_seconds", 300)  # 5 minutes
        self.update_frequency_seconds = self.config.get("update_frequency_seconds", 1.0)
        
        print(f"📊 Analytics Engine initialized with rolling window: {self.rolling_window_seconds}s")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load analytics configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            print(f"✅ Analytics configuration loaded from {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"⚠️  Analytics config file not found: {self.config_file}, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing analytics config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default analytics configuration."""
        return {
            "rolling_window_seconds": 300,  # 5 minutes
            "update_frequency_seconds": 1.0,
            "max_metrics_per_category": 1000,
            "kpi_calculation_timeout_ms": 100,
            "enable_performance_monitoring": True,
            "enable_debug_mode": False,
            "categories": {
                "order_processing": {
                    "enabled": True,
                    "metrics": ["orders_per_hour", "avg_order_time", "completion_rate"]
                },
                "robot_performance": {
                    "enabled": True,
                    "metrics": ["utilization", "efficiency", "idle_time"]
                },
                "inventory_management": {
                    "enabled": True,
                    "metrics": ["stock_levels", "availability", "turnover"]
                },
                "system_performance": {
                    "enabled": True,
                    "metrics": ["response_time", "memory_usage", "throughput"]
                }
            }
        }
    
    def set_event_system(self, event_system: EventSystem) -> bool:
        """Set the event system for analytics."""
        try:
            self.event_system = event_system
            self._register_event_handlers()
            print("✅ Event system integrated with analytics engine")
            return True
        except Exception as e:
            print(f"❌ Failed to integrate event system: {e}")
            return False
    
    def _register_event_handlers(self):
        """Register event handlers for analytics data collection."""
        if not self.event_system:
            return
        
        # Order events
        self.event_system.register_handler("order_created", self._handle_order_created)
        self.event_system.register_handler("order_assigned", self._handle_order_assigned)
        self.event_system.register_handler("order_completed", self._handle_order_completed)
        self.event_system.register_handler("order_cancelled", self._handle_order_cancelled)
        
        # Robot events
        self.event_system.register_handler("robot_movement", self._handle_robot_movement)
        self.event_system.register_handler("robot_state_change", self._handle_robot_state_change)
        self.event_system.register_handler("robot_path_update", self._handle_robot_path_update)
        
        # Inventory events
        self.event_system.register_handler("inventory_update", self._handle_inventory_update)
        self.event_system.register_handler("item_collected", self._handle_item_collected)
        
        # System events
        self.event_system.register_handler("performance_metric", self._handle_performance_metric)
        
        print("✅ Event handlers registered for analytics")
    
    def record_metric(self, name: str, value: float, category: str = "general", 
                     metadata: Dict[str, Any] = None) -> bool:
        """
        Record a metric with real-time processing.
        
        Args:
            name: Metric name
            value: Metric value
            category: Metric category
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            with self._lock:
                timestamp = time.time()
                metric_data = MetricData(
                    name=name,
                    value=value,
                    timestamp=timestamp,
                    metadata=metadata or {}
                )
                
                # Store metric
                metric_key = f"{category}.{name}"
                self.metrics[metric_key].append(metric_data)
                
                # Update KPI cache if needed
                self._update_kpi_cache(metric_key, metric_data)
                
                # Performance tracking
                self._track_calculation_performance()
                
                if self.config.get("enable_debug_mode", False):
                    print(f"📊 Recorded metric: {metric_key} = {value}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error recording metric {name}: {e}")
            return False
    
    def _update_kpi_cache(self, metric_key: str, metric_data: MetricData):
        """Update KPI cache with new metric data."""
        try:
            # Calculate rolling average
            recent_metrics = self._get_recent_metrics(metric_key)
            if recent_metrics:
                avg_value = sum(m.value for m in recent_metrics) / len(recent_metrics)
                
                kpi = KPICalculation(
                    name=metric_key,
                    value=avg_value,
                    unit=self._get_unit_for_metric(metric_key),
                    timestamp=metric_data.timestamp,
                    description=self._get_description_for_metric(metric_key),
                    category=metric_key.split('.')[0]
                )
                
                self.kpi_cache[metric_key] = kpi
                
        except Exception as e:
            print(f"❌ Error updating KPI cache for {metric_key}: {e}")
    
    def _get_recent_metrics(self, metric_key: str, window_seconds: float = None) -> List[MetricData]:
        """Get recent metrics within the specified time window."""
        if window_seconds is None:
            window_seconds = self.rolling_window_seconds
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        recent_metrics = []
        for metric in self.metrics[metric_key]:
            if metric.timestamp >= cutoff_time:
                recent_metrics.append(metric)
        
        return recent_metrics
    
    def _get_unit_for_metric(self, metric_key: str) -> str:
        """Get the appropriate unit for a metric."""
        unit_mapping = {
            "order_processing.orders_per_hour": "orders/hour",
            "order_processing.avg_order_time": "seconds",
            "order_processing.completion_rate": "percentage",
            "robot_performance.utilization": "percentage",
            "robot_performance.efficiency": "percentage",
            "robot_performance.idle_time": "seconds",
            "inventory_management.stock_levels": "items",
            "inventory_management.availability": "percentage",
            "system_performance.response_time": "milliseconds",
            "system_performance.memory_usage": "MB",
            "system_performance.throughput": "ops/second"
        }
        return unit_mapping.get(metric_key, "units")
    
    def _get_description_for_metric(self, metric_key: str) -> str:
        """Get description for a metric."""
        description_mapping = {
            "order_processing.orders_per_hour": "Orders completed per hour (rolling average)",
            "order_processing.avg_order_time": "Average time to complete an order",
            "order_processing.completion_rate": "Percentage of orders completed successfully",
            "robot_performance.utilization": "Percentage of time robots are active",
            "robot_performance.efficiency": "Path efficiency compared to optimal",
            "robot_performance.idle_time": "Time robots spend waiting for orders",
            "inventory_management.stock_levels": "Current stock levels by item",
            "inventory_management.availability": "Percentage of items available",
            "system_performance.response_time": "System operation response times",
            "system_performance.memory_usage": "System memory consumption",
            "system_performance.throughput": "Operations per second"
        }
        return description_mapping.get(metric_key, "Analytics metric")
    
    def get_kpi(self, name: str) -> Optional[KPICalculation]:
        """Get a specific KPI calculation."""
        with self._lock:
            return self.kpi_cache.get(name)
    
    def get_all_kpis(self) -> Dict[str, KPICalculation]:
        """Get all current KPI calculations."""
        with self._lock:
            return self.kpi_cache.copy()
    
    def get_kpis_by_category(self, category: str) -> Dict[str, KPICalculation]:
        """Get KPIs for a specific category."""
        with self._lock:
            return {k: v for k, v in self.kpi_cache.items() if k.startswith(f"{category}.")}

    def get_total_orders_created(self) -> int:
        """Get the total number of orders created in the session."""
        with self._lock:
            total_orders = 0
            # The metric key is "order_processing.orders_created"
            metric_key = "order_processing.orders_created"
            if metric_key in self.metrics:
                # The value of a counter is the sum of all recorded values (which are 1 for each order)
                total_orders = sum(m.value for m in self.metrics[metric_key])
            return int(total_orders)

    def calculate_orders_per_hour(self) -> float:
        """Calculate orders per hour (rolling average)."""
        try:
            recent_completions = self._get_recent_metrics("order_processing.order_completed")
            if not recent_completions:
                return 0.0
            
            # Calculate orders per hour
            time_window_hours = self.rolling_window_seconds / 3600
            orders_count = len(recent_completions)
            
            orders_per_hour = orders_count / time_window_hours
            return orders_per_hour
            
        except Exception as e:
            print(f"❌ Error calculating orders per hour: {e}")
            return 0.0
    
    def calculate_robot_utilization(self) -> float:
        """Calculate robot utilization percentage."""
        try:
            recent_activity = self._get_recent_metrics("robot_performance.active_time")
            recent_total = self._get_recent_metrics("robot_performance.total_time")
            
            if not recent_total:
                return 0.0
            
            total_active = sum(m.value for m in recent_activity)
            total_time = sum(m.value for m in recent_total)
            
            if total_time > 0:
                utilization = (total_active / total_time) * 100
                return min(utilization, 100.0)  # Cap at 100%
            
            return 0.0
            
        except Exception as e:
            print(f"❌ Error calculating robot utilization: {e}")
            return 0.0
    
    def _track_calculation_performance(self):
        """Track calculation performance for monitoring."""
        current_time = time.time()
        if self.last_calculation_time > 0:
            calculation_time = (current_time - self.last_calculation_time) * 1000  # Convert to ms
            self.calculation_times.append(calculation_time)
        
        self.last_calculation_time = current_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get analytics engine performance statistics."""
        with self._lock:
            if not self.calculation_times:
                return {"avg_calculation_time_ms": 0.0, "total_metrics": 0}
            
            avg_time = sum(self.calculation_times) / len(self.calculation_times)
            total_metrics = sum(len(metrics) for metrics in self.metrics.values())
            
            return {
                "avg_calculation_time_ms": avg_time,
                "total_metrics": total_metrics,
                "kpi_count": len(self.kpi_cache),
                "session_duration_seconds": time.time() - self.session_start_time
            }
    
    def clear_session_data(self):
        """Clear all session data (for new simulation session)."""
        with self._lock:
            self.metrics.clear()
            self.kpi_cache.clear()
            self.calculation_times.clear()
            self.session_start_time = time.time()
            print("🧹 Analytics session data cleared")
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export current analytics data for external analysis."""
        with self._lock:
            return {
                "session_info": {
                    "start_time": self.session_start_time,
                    "duration_seconds": time.time() - self.session_start_time,
                    "config": self.config
                },
                "kpis": {k: {
                    "name": v.name,
                    "value": v.value,
                    "unit": v.unit,
                    "timestamp": v.timestamp,
                    "description": v.description,
                    "category": v.category
                } for k, v in self.kpi_cache.items()},
                "performance_stats": self.get_performance_stats()
            }
    
    # Event handlers
    def _handle_order_created(self, event_data: Dict[str, Any]):
        """Handle order created event."""
        self.record_metric("order_created", 1.0, "order_processing", event_data)
    
    def _handle_order_assigned(self, event_data: Dict[str, Any]):
        """Handle order assigned event."""
        self.record_metric("order_assigned", 1.0, "order_processing", event_data)
    
    def _handle_order_completed(self, event_data: Dict[str, Any]):
        """Handle order completed event."""
        self.record_metric("order_completed", 1.0, "order_processing", event_data)
        
        # Calculate completion time if available
        if "completion_time" in event_data:
            self.record_metric("order_completion_time", event_data["completion_time"], 
                             "order_processing", event_data)
    
    def _handle_order_cancelled(self, event_data: Dict[str, Any]):
        """Handle order cancelled event."""
        self.record_metric("order_cancelled", 1.0, "order_processing", event_data)
    
    def _handle_robot_movement(self, event_data: Dict[str, Any]):
        """Handle robot movement event."""
        self.record_metric("robot_movement", 1.0, "robot_performance", event_data)
        
        # Record movement distance if available
        if "distance" in event_data:
            self.record_metric("movement_distance", event_data["distance"], 
                             "robot_performance", event_data)
    
    def _handle_robot_state_change(self, event_data: Dict[str, Any]):
        """Handle robot state change event."""
        self.record_metric("robot_state_change", 1.0, "robot_performance", event_data)
        
        # Track state-specific metrics
        new_state = event_data.get("new_state", "")
        if new_state == "IDLE":
            self.record_metric("robot_idle_time", 0.0, "robot_performance", event_data)
        elif new_state == "MOVING_TO_ITEM":
            self.record_metric("robot_active_time", 0.0, "robot_performance", event_data)
    
    def _handle_robot_path_update(self, event_data: Dict[str, Any]):
        """Handle robot path update event."""
        self.record_metric("path_update", 1.0, "robot_performance", event_data)
        
        # Record path efficiency if available
        if "efficiency" in event_data:
            self.record_metric("path_efficiency", event_data["efficiency"], 
                             "robot_performance", event_data)
    
    def _handle_inventory_update(self, event_data: Dict[str, Any]):
        """Handle inventory update event."""
        self.record_metric("inventory_update", 1.0, "inventory_management", event_data)
        
        # Record stock level if available
        if "quantity" in event_data:
            self.record_metric("stock_level", event_data["quantity"], 
                             "inventory_management", event_data)
    
    def _handle_item_collected(self, event_data: Dict[str, Any]):
        """Handle item collected event."""
        self.record_metric("item_collected", 1.0, "inventory_management", event_data)
    
    def _handle_performance_metric(self, event_data: Dict[str, Any]):
        """Handle performance metric event."""
        metric_name = event_data.get("metric_name", "unknown")
        metric_value = event_data.get("value", 0.0)
        self.record_metric(metric_name, metric_value, "system_performance", event_data)
    
    def shutdown(self):
        """Shutdown the analytics engine."""
        print("🔄 Shutting down analytics engine...")
        # Clear data
        self.clear_session_data()
        print("✅ Analytics engine shutdown complete") 