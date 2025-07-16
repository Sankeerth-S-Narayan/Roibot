"""
Data Export Module

This module provides comprehensive data export capabilities for analytics data,
including JSON, CSV, and structured data export for reporting and analysis.
"""

import json
import csv
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import asdict, is_dataclass
from datetime import datetime

from .analytics_engine import AnalyticsEngine, MetricData, KPICalculation


class DataExport:
    """
    Comprehensive data export functionality for analytics and reporting.
    
    Provides JSON, CSV, and structured data export capabilities
    for all analytics data and performance metrics.
    """
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        """
        Initialize DataExport with analytics engine.
        
        Args:
            analytics_engine: Core analytics engine for data access
        """
        self.analytics = analytics_engine
        self.export_timestamp = time.time()
        self.export_formats = ['json', 'csv']
    
    def export_analytics_data(self, export_path: str, format_type: str = 'json', 
                            include_metadata: bool = True) -> Dict[str, Any]:
        """
        Export comprehensive analytics data.
        
        Args:
            export_path: Path where to save the exported data
            format_type: Export format ('json' or 'csv')
            include_metadata: Whether to include metadata in export
            
        Returns:
            Dictionary with export summary information
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect all analytics data
        export_data = self._collect_analytics_data(include_metadata)
        
        # Export based on format
        if format_type.lower() == 'json':
            return self._export_json(export_data, export_path)
        elif format_type.lower() == 'csv':
            return self._export_csv(export_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _collect_analytics_data(self, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Collect all analytics data for export.
        
        Args:
            include_metadata: Whether to include metadata
            
        Returns:
            Dictionary with all analytics data
        """
        export_data = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "analytics_version": "1.0",
            "data_sources": {}
        }
        
        # Collect metrics data
        metrics_data = {}
        for category, metrics in self.analytics.metrics.items():
            category_data = {
                "metrics": {},
                "kpis": {}
            }
            
            # Collect metrics
            for metric_name, metric_data in metrics.items():
                metric_export = {
                    "value": metric_data.value,
                    "timestamp": metric_data.timestamp,
                    "unit": metric_data.unit
                }
                
                if include_metadata and metric_data.metadata:
                    metric_export["metadata"] = metric_data.metadata
                
                category_data["metrics"][metric_name] = metric_export
            
            # Collect KPIs
            for kpi_name, kpi_data in self.analytics.kpis.items():
                if kpi_name.startswith(f"{category}."):
                    kpi_export = {
                        "value": kpi_data.value,
                        "calculation_type": kpi_data.calculation_type,
                        "rolling_window": kpi_data.rolling_window,
                        "last_updated": kpi_data.last_updated
                    }
                    category_data["kpis"][kpi_name] = kpi_export
            
            export_data["data_sources"][category] = category_data
        
        return export_data
    
    def _export_json(self, data: Dict[str, Any], export_path: Path) -> Dict[str, Any]:
        """
        Export data as JSON.
        
        Args:
            data: Data to export
            export_path: Path for export file
            
        Returns:
            Export summary
        """
        json_path = export_path.with_suffix('.json')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
        
        return {
            "format": "json",
            "file_path": str(json_path),
            "file_size": json_path.stat().st_size,
            "export_timestamp": self.export_timestamp,
            "data_points": self._count_data_points(data),
            "status": "success"
        }
    
    def _export_csv(self, data: Dict[str, Any], export_path: Path) -> Dict[str, Any]:
        """
        Export data as CSV.
        
        Args:
            data: Data to export
            export_path: Path for export file
            
        Returns:
            Export summary
        """
        csv_path = export_path.with_suffix('.csv')
        
        # Flatten data for CSV export
        csv_data = self._flatten_data_for_csv(data)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
        
        return {
            "format": "csv",
            "file_path": str(csv_path),
            "file_size": csv_path.stat().st_size,
            "export_timestamp": self.export_timestamp,
            "data_points": len(csv_data),
            "status": "success"
        }
    
    def _flatten_data_for_csv(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Flatten nested data structure for CSV export.
        
        Args:
            data: Nested data structure
            
        Returns:
            List of flattened dictionaries
        """
        flattened_data = []
        
        # Add export metadata
        flattened_data.append({
            "data_type": "export_metadata",
            "export_timestamp": data.get("export_timestamp", ""),
            "export_datetime": data.get("export_datetime", ""),
            "analytics_version": data.get("analytics_version", ""),
            "value": "",
            "unit": "",
            "category": "",
            "metric_name": ""
        })
        
        # Flatten metrics data
        for category, category_data in data.get("data_sources", {}).items():
            # Metrics
            for metric_name, metric_data in category_data.get("metrics", {}).items():
                flattened_data.append({
                    "data_type": "metric",
                    "category": category,
                    "metric_name": metric_name,
                    "value": metric_data.get("value", ""),
                    "unit": metric_data.get("unit", ""),
                    "timestamp": metric_data.get("timestamp", ""),
                    "metadata": json.dumps(metric_data.get("metadata", {}))
                })
            
            # KPIs
            for kpi_name, kpi_data in category_data.get("kpis", {}).items():
                flattened_data.append({
                    "data_type": "kpi",
                    "category": category,
                    "metric_name": kpi_name,
                    "value": kpi_data.get("value", ""),
                    "unit": "",
                    "timestamp": kpi_data.get("last_updated", ""),
                    "metadata": json.dumps({
                        "calculation_type": kpi_data.get("calculation_type", ""),
                        "rolling_window": kpi_data.get("rolling_window", "")
                    })
                })
        
        return flattened_data
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-serializable objects."""
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return str(obj)
    
    def _count_data_points(self, data: Dict[str, Any]) -> int:
        """
        Count total data points in export data.
        
        Args:
            data: Export data
            
        Returns:
            Total number of data points
        """
        count = 0
        for category_data in data.get("data_sources", {}).values():
            count += len(category_data.get("metrics", {}))
            count += len(category_data.get("kpis", {}))
        return count
    
    def export_performance_data(self, performance_data: List[Any], export_path: str, 
                              format_type: str = 'json') -> Dict[str, Any]:
        """
        Export performance monitoring data.
        
        Args:
            performance_data: List of performance data objects
            export_path: Path where to save the exported data
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Dictionary with export summary information
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert performance data to exportable format
        export_data = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "data_type": "performance_data",
            "performance_metrics": []
        }
        
        for data_point in performance_data:
            if is_dataclass(data_point):
                export_data["performance_metrics"].append(asdict(data_point))
            else:
                export_data["performance_metrics"].append(data_point)
        
        # Export based on format
        if format_type.lower() == 'json':
            return self._export_json(export_data, export_path)
        elif format_type.lower() == 'csv':
            return self._export_csv(export_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def export_robot_analytics(self, robot_analytics: Any, export_path: str, 
                             format_type: str = 'json') -> Dict[str, Any]:
        """
        Export robot analytics data.
        
        Args:
            robot_analytics: RobotAnalytics object or data
            export_path: Path where to save the exported data
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Dictionary with export summary information
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect robot analytics data
        export_data = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "data_type": "robot_analytics",
            "robot_performance": {},
            "robot_summary": {},
            "movement_analytics": {},
            "path_optimization": {}
        }
        
        # Get robot performance summary
        if hasattr(robot_analytics, 'get_robot_performance_summary'):
            export_data["robot_summary"] = robot_analytics.get_robot_performance_summary()
        
        # Get movement analytics
        if hasattr(robot_analytics, 'get_movement_analytics'):
            export_data["movement_analytics"] = robot_analytics.get_movement_analytics()
        
        # Get path optimization analytics
        if hasattr(robot_analytics, 'get_path_optimization_analytics'):
            export_data["path_optimization"] = robot_analytics.get_path_optimization_analytics()
        
        # Get individual robot analytics
        if hasattr(robot_analytics, 'robots'):
            for robot_id, robot_data in robot_analytics.robots.items():
                if hasattr(robot_analytics, 'get_robot_analytics'):
                    robot_analytics_data = robot_analytics.get_robot_analytics(robot_id)
                    if robot_analytics_data:
                        export_data["robot_performance"][robot_id] = robot_analytics_data
        
        # Export based on format
        if format_type.lower() == 'json':
            return self._export_json(export_data, export_path)
        elif format_type.lower() == 'csv':
            return self._export_csv(export_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def export_order_analytics(self, order_analytics: Any, export_path: str, 
                             format_type: str = 'json') -> Dict[str, Any]:
        """
        Export order analytics data.
        
        Args:
            order_analytics: OrderAnalytics object or data
            export_path: Path where to save the exported data
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Dictionary with export summary information
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect order analytics data
        export_data = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "data_type": "order_analytics",
            "order_summary": {},
            "order_history": {},
            "queue_analytics": {}
        }
        
        # Get order summary
        if hasattr(order_analytics, 'get_order_summary'):
            export_data["order_summary"] = order_analytics.get_order_summary()
        
        # Get order history
        if hasattr(order_analytics, 'get_order_history'):
            export_data["order_history"] = order_analytics.get_order_history()
        
        # Get queue analytics
        if hasattr(order_analytics, 'get_queue_analytics'):
            export_data["queue_analytics"] = order_analytics.get_queue_analytics()
        
        # Export based on format
        if format_type.lower() == 'json':
            return self._export_json(export_data, export_path)
        elif format_type.lower() == 'csv':
            return self._export_csv(export_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def export_system_performance(self, performance_monitor: Any, export_path: str, 
                                format_type: str = 'json') -> Dict[str, Any]:
        """
        Export system performance data.
        
        Args:
            performance_monitor: PerformanceMonitor object or data
            export_path: Path where to save the exported data
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Dictionary with export summary information
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect system performance data
        export_data = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "data_type": "system_performance",
            "performance_summary": {},
            "health_history": {},
            "performance_alerts": {}
        }
        
        # Get performance summary
        if hasattr(performance_monitor, 'get_system_performance_summary'):
            export_data["performance_summary"] = performance_monitor.get_system_performance_summary()
        
        # Get health history
        if hasattr(performance_monitor, 'get_system_health_history'):
            health_history = performance_monitor.get_system_health_history()
            export_data["health_history"] = [asdict(health) for health in health_history]
        
        # Get performance alerts
        if hasattr(performance_monitor, 'get_performance_alerts'):
            export_data["performance_alerts"] = performance_monitor.get_performance_alerts()
        
        # Export based on format
        if format_type.lower() == 'json':
            return self._export_json(export_data, export_path)
        elif format_type.lower() == 'csv':
            return self._export_csv(export_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def export_all_data(self, export_directory: str, include_performance: bool = True,
                       include_robots: bool = True, include_orders: bool = True,
                       include_system: bool = True) -> Dict[str, Any]:
        """
        Export all available analytics data.
        
        Args:
            export_directory: Directory to save all export files
            include_performance: Whether to include performance data
            include_robots: Whether to include robot analytics
            include_orders: Whether to include order analytics
            include_system: Whether to include system performance
            
        Returns:
            Dictionary with export summary information
        """
        export_dir = Path(export_directory)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        export_summary = {
            "export_timestamp": self.export_timestamp,
            "export_datetime": datetime.fromtimestamp(self.export_timestamp).isoformat(),
            "export_directory": str(export_dir),
            "files_exported": [],
            "total_files": 0,
            "status": "success"
        }
        
        # Export main analytics data
        main_export = self.export_analytics_data(
            str(export_dir / "analytics_data.json"), 
            'json', 
            include_metadata=True
        )
        export_summary["files_exported"].append(main_export)
        export_summary["total_files"] += 1
        
        # Export CSV version
        csv_export = self.export_analytics_data(
            str(export_dir / "analytics_data.csv"), 
            'csv', 
            include_metadata=True
        )
        export_summary["files_exported"].append(csv_export)
        export_summary["total_files"] += 1
        
        return export_summary
    
    def get_export_formats(self) -> List[str]:
        """
        Get available export formats.
        
        Returns:
            List of supported export formats
        """
        return self.export_formats.copy()
    
    def validate_export_path(self, export_path: str) -> bool:
        """
        Validate export path for write access.
        
        Args:
            export_path: Path to validate
            
        Returns:
            True if path is valid and writable
        """
        try:
            path = Path(export_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False 