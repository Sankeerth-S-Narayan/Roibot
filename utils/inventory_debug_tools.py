"""
Inventory System Debugging Tools

This module provides comprehensive debugging utilities for the inventory system,
including diagnostic tools, troubleshooting helpers, and performance analyzers.
"""

import time
import json
import traceback
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from core.inventory.inventory_item import InventoryItem, Coordinate
from core.inventory.inventory_manager import InventoryManager
from core.inventory.inventory_sync import InventorySyncManager
from core.inventory.inventory_config import InventoryConfigManager, PerformanceMetricType
from core.inventory.inventory_integration import InventorySystemIntegration


@dataclass
class DebugReport:
    """Debug report data structure"""
    timestamp: float
    system_status: Dict
    performance_metrics: Dict
    error_log: List[str]
    warnings: List[str]
    recommendations: List[str]


class InventoryDebugger:
    """
    Comprehensive debugging tools for the inventory system.
    
    Features:
    - System health diagnostics
    - Performance analysis
    - Error tracking and reporting
    - Configuration validation
    - Integration testing
    - Troubleshooting recommendations
    """
    
    def __init__(self):
        """Initialize the inventory debugger"""
        self.error_log = []
        self.warnings = []
        self.performance_data = []
        self.debug_reports = []
    
    def diagnose_system_health(self, integration: InventorySystemIntegration) -> DebugReport:
        """
        Perform comprehensive system health diagnosis.
        
        Args:
            integration: InventorySystemIntegration instance
            
        Returns:
            DebugReport with system health information
        """
        print("🔍 Performing system health diagnosis...")
        
        # Get system status
        status = integration.get_integration_status()
        
        # Get debug information
        debug_info = integration.get_debug_info()
        
        # Analyze performance
        performance_metrics = self._analyze_performance(integration.config_manager)
        
        # Check for issues
        errors = self._check_for_errors(status, debug_info)
        warnings = self._check_for_warnings(status, debug_info)
        recommendations = self._generate_recommendations(status, debug_info, performance_metrics)
        
        # Create debug report
        report = DebugReport(
            timestamp=time.time(),
            system_status=status,
            performance_metrics=performance_metrics,
            error_log=errors,
            warnings=warnings,
            recommendations=recommendations
        )
        
        self.debug_reports.append(report)
        
        # Print summary
        self._print_diagnosis_summary(report)
        
        return report
    
    def _analyze_performance(self, config_manager: InventoryConfigManager) -> Dict:
        """Analyze performance metrics"""
        try:
            analytics = config_manager.get_performance_analytics()
            violations = config_manager.check_performance_thresholds()
            
            return {
                "analytics": analytics,
                "violations": violations,
                "thresholds": {
                    "max_operation_time_ms": config_manager.config.max_operation_time_ms,
                    "max_memory_usage_mb": config_manager.config.max_memory_usage_mb
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_for_errors(self, status: Dict, debug_info: Dict) -> List[str]:
        """Check for system errors"""
        errors = []
        
        # Check initialization
        if not status.get("initialized", False):
            errors.append("System not initialized")
        
        # Check component integration
        components = status.get("components", {})
        for component, integrated in components.items():
            if not integrated:
                errors.append(f"{component} not integrated")
        
        # Check inventory components
        inventory_components = status.get("inventory_components", {})
        for component, initialized in inventory_components.items():
            if not initialized:
                errors.append(f"{component} not initialized")
        
        # Check for performance violations
        performance_metrics = debug_info.get("config_manager", {}).get("performance_metrics", {})
        if performance_metrics.get("total_metrics", 0) == 0:
            errors.append("No performance metrics recorded")
        
        return errors
    
    def _check_for_warnings(self, status: Dict, debug_info: Dict) -> List[str]:
        """Check for system warnings"""
        warnings = []
        
        # Check integration thread
        thread_status = status.get("integration_thread", {})
        if not thread_status.get("running", False):
            warnings.append("Integration thread not running")
        
        # Check performance monitoring
        config = debug_info.get("configuration", {})
        performance_config = config.get("performance", {})
        if not performance_config.get("monitoring_enabled", False):
            warnings.append("Performance monitoring disabled")
        
        # Check debug mode
        if not performance_config.get("debug_mode", False):
            warnings.append("Debug mode disabled")
        
        return warnings
    
    def _generate_recommendations(self, status: Dict, debug_info: Dict, performance_metrics: Dict) -> List[str]:
        """Generate troubleshooting recommendations"""
        recommendations = []
        
        # Check initialization
        if not status.get("initialized", False):
            recommendations.append("Initialize the inventory system")
        
        # Check component integration
        components = status.get("components", {})
        missing_components = [comp for comp, integrated in components.items() if not integrated]
        if missing_components:
            recommendations.append(f"Integrate missing components: {', '.join(missing_components)}")
        
        # Check performance
        violations = performance_metrics.get("violations", {})
        if any(violations.values()):
            recommendations.append("Review performance thresholds and optimize operations")
        
        # Check monitoring
        if not debug_info.get("integration_config", {}).get("enable_performance_monitoring", False):
            recommendations.append("Enable performance monitoring for better diagnostics")
        
        return recommendations
    
    def _print_diagnosis_summary(self, report: DebugReport):
        """Print diagnosis summary"""
        print(f"\n📊 System Health Diagnosis Summary")
        print(f"  Timestamp: {datetime.fromtimestamp(report.timestamp)}")
        print(f"  Errors: {len(report.error_log)}")
        print(f"  Warnings: {len(report.warnings)}")
        print(f"  Recommendations: {len(report.recommendations)}")
        
        if report.error_log:
            print(f"\n❌ Errors:")
            for error in report.error_log:
                print(f"  - {error}")
        
        if report.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in report.warnings:
                print(f"  - {warning}")
        
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")


class InventoryTroubleshooter:
    """
    Troubleshooting tools for common inventory system issues.
    """
    
    def __init__(self):
        """Initialize the troubleshooter"""
        self.common_issues = {
            "initialization_failure": self._troubleshoot_initialization,
            "integration_failure": self._troubleshoot_integration,
            "performance_issues": self._troubleshoot_performance,
            "configuration_errors": self._troubleshoot_configuration,
            "event_handling_issues": self._troubleshoot_events
        }
    
    def troubleshoot_issue(self, issue_type: str, context: Dict) -> Dict:
        """
        Troubleshoot a specific issue type.
        
        Args:
            issue_type: Type of issue to troubleshoot
            context: Context information for troubleshooting
            
        Returns:
            Dictionary with troubleshooting results
        """
        if issue_type in self.common_issues:
            return self.common_issues[issue_type](context)
        else:
            return {"error": f"Unknown issue type: {issue_type}"}
    
    def _troubleshoot_initialization(self, context: Dict) -> Dict:
        """Troubleshoot initialization issues"""
        print("🔧 Troubleshooting initialization issues...")
        
        results = {
            "issue": "Initialization Failure",
            "checks": [],
            "solutions": []
        }
        
        # Check configuration
        config_manager = context.get("config_manager")
        if config_manager:
            validation = config_manager.validate_configuration()
            results["checks"].append(f"Configuration validation: {'PASS' if validation['valid'] else 'FAIL'}")
            
            if not validation["valid"]:
                results["solutions"].append("Fix configuration errors")
                for error in validation["errors"]:
                    results["solutions"].append(f"  - {error}")
        
        # Check warehouse dimensions
        if config_manager:
            config = config_manager.config
            if config.warehouse_width <= 0 or config.warehouse_height <= 0:
                results["solutions"].append("Set valid warehouse dimensions")
        
        # Check item generation
        if config_manager:
            config = config_manager.config
            available_space = (config.warehouse_width * config.warehouse_height - 
                             config.packout_zone_width * config.packout_zone_height)
            if config.total_items > available_space:
                results["solutions"].append(f"Reduce total_items from {config.total_items} to {available_space}")
        
        return results
    
    def _troubleshoot_integration(self, context: Dict) -> Dict:
        """Troubleshoot integration issues"""
        print("🔧 Troubleshooting integration issues...")
        
        results = {
            "issue": "Integration Failure",
            "checks": [],
            "solutions": []
        }
        
        # Check component availability
        integration = context.get("integration")
        if integration:
            status = integration.get_integration_status()
            components = status.get("components", {})
            
            for component, integrated in components.items():
                results["checks"].append(f"{component}: {'INTEGRATED' if integrated else 'NOT INTEGRATED'}")
                if not integrated:
                    results["solutions"].append(f"Integrate with {component}")
        
        return results
    
    def _troubleshoot_performance(self, context: Dict) -> Dict:
        """Troubleshoot performance issues"""
        print("🔧 Troubleshooting performance issues...")
        
        results = {
            "issue": "Performance Issues",
            "checks": [],
            "solutions": []
        }
        
        # Check performance metrics
        config_manager = context.get("config_manager")
        if config_manager:
            violations = config_manager.check_performance_thresholds()
            
            for violation_type, violations_list in violations.items():
                if violations_list:
                    results["checks"].append(f"{violation_type}: {len(violations_list)} violations")
                    results["solutions"].append(f"Review {violation_type} thresholds")
        
        # Check monitoring
        if config_manager:
            if not config_manager.config.performance_monitoring_enabled:
                results["solutions"].append("Enable performance monitoring")
        
        return results
    
    def _troubleshoot_configuration(self, context: Dict) -> Dict:
        """Troubleshoot configuration issues"""
        print("🔧 Troubleshooting configuration issues...")
        
        results = {
            "issue": "Configuration Errors",
            "checks": [],
            "solutions": []
        }
        
        # Check configuration file
        config_manager = context.get("config_manager")
        if config_manager:
            try:
                success = config_manager.load_configuration()
                results["checks"].append(f"Configuration loading: {'SUCCESS' if success else 'FAIL'}")
                
                if not success:
                    results["solutions"].append("Check configuration file path and format")
            except Exception as e:
                results["checks"].append(f"Configuration error: {e}")
                results["solutions"].append("Fix configuration file syntax")
        
        return results
    
    def _troubleshoot_events(self, context: Dict) -> Dict:
        """Troubleshoot event handling issues"""
        print("🔧 Troubleshooting event handling issues...")
        
        results = {
            "issue": "Event Handling Issues",
            "checks": [],
            "solutions": []
        }
        
        # Check event system integration
        integration = context.get("integration")
        if integration:
            status = integration.get_integration_status()
            event_system_integrated = status.get("components", {}).get("event_system", False)
            
            results["checks"].append(f"Event system: {'INTEGRATED' if event_system_integrated else 'NOT INTEGRATED'}")
            
            if not event_system_integrated:
                results["solutions"].append("Integrate with event system")
        
        return results


class InventoryPerformanceAnalyzer:
    """
    Performance analysis tools for the inventory system.
    """
    
    def __init__(self):
        """Initialize the performance analyzer"""
        self.performance_history = []
    
    def analyze_performance(self, config_manager: InventoryConfigManager) -> Dict:
        """
        Analyze system performance.
        
        Args:
            config_manager: InventoryConfigManager instance
            
        Returns:
            Dictionary with performance analysis
        """
        print("📈 Analyzing system performance...")
        
        try:
            # Get performance analytics
            analytics = config_manager.get_performance_analytics()
            
            # Get threshold violations
            violations = config_manager.check_performance_thresholds()
            
            # Analyze trends
            trends = self._analyze_trends(analytics)
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(analytics, violations)
            
            analysis = {
                "analytics": analytics,
                "violations": violations,
                "trends": trends,
                "recommendations": recommendations,
                "timestamp": time.time()
            }
            
            self.performance_history.append(analysis)
            
            # Print summary
            self._print_performance_summary(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_trends(self, analytics: Dict) -> Dict:
        """Analyze performance trends"""
        trends = {}
        
        performance_summary = analytics.get("performance_summary", {})
        
        for metric_type, stats in performance_summary.items():
            if stats.get("count", 0) > 1:
                # Calculate trend (simplified)
                if "values" in analytics.get("metric_types", {}).get(metric_type, []):
                    values = analytics["metric_types"][metric_type]
                    if len(values) >= 2:
                        trend = "increasing" if values[-1] > values[0] else "decreasing"
                        trends[metric_type] = trend
        
        return trends
    
    def _generate_performance_recommendations(self, analytics: Dict, violations: Dict) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check for violations
        for violation_type, violations_list in violations.items():
            if violations_list:
                recommendations.append(f"Address {violation_type} violations")
        
        # Check for low metric counts
        total_metrics = analytics.get("total_metrics", 0)
        if total_metrics < 10:
            recommendations.append("Increase performance monitoring frequency")
        
        # Check for high operation times
        op_time_stats = analytics.get("performance_summary", {}).get("operation_time", {})
        if op_time_stats.get("average", 0) > 5.0:
            recommendations.append("Optimize operation performance")
        
        return recommendations
    
    def _print_performance_summary(self, analysis: Dict):
        """Print performance analysis summary"""
        print(f"\n📊 Performance Analysis Summary")
        
        analytics = analysis.get("analytics", {})
        violations = analysis.get("violations", {})
        trends = analysis.get("trends", {})
        recommendations = analysis.get("recommendations", [])
        
        print(f"  Total metrics: {analytics.get('total_metrics', 0)}")
        print(f"  Violations: {sum(len(v) for v in violations.values())}")
        print(f"  Trends: {len(trends)}")
        print(f"  Recommendations: {len(recommendations)}")
        
        if recommendations:
            print(f"\n💡 Performance Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")


class InventoryLogAnalyzer:
    """
    Log analysis tools for the inventory system.
    """
    
    def __init__(self):
        """Initialize the log analyzer"""
        self.log_patterns = {
            "error": r"ERROR|Exception|Traceback",
            "warning": r"WARNING|Warning",
            "performance": r"performance|metric|threshold",
            "integration": r"integration|connect|register"
        }
    
    def analyze_logs(self, log_file: str) -> Dict:
        """
        Analyze inventory system logs.
        
        Args:
            log_file: Path to log file
            
        Returns:
            Dictionary with log analysis
        """
        print(f"📋 Analyzing logs from {log_file}...")
        
        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
            
            analysis = {
                "total_lines": len(log_lines),
                "error_count": 0,
                "warning_count": 0,
                "performance_entries": 0,
                "integration_entries": 0,
                "recent_errors": [],
                "recent_warnings": []
            }
            
            for line in log_lines:
                if "ERROR" in line or "Exception" in line:
                    analysis["error_count"] += 1
                    if len(analysis["recent_errors"]) < 10:
                        analysis["recent_errors"].append(line.strip())
                
                elif "WARNING" in line:
                    analysis["warning_count"] += 1
                    if len(analysis["recent_warnings"]) < 10:
                        analysis["recent_warnings"].append(line.strip())
                
                elif "performance" in line.lower() or "metric" in line.lower():
                    analysis["performance_entries"] += 1
                
                elif "integration" in line.lower() or "connect" in line.lower():
                    analysis["integration_entries"] += 1
            
            # Print summary
            self._print_log_summary(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze logs: {e}"}
    
    def _print_log_summary(self, analysis: Dict):
        """Print log analysis summary"""
        print(f"\n📋 Log Analysis Summary")
        print(f"  Total lines: {analysis['total_lines']}")
        print(f"  Errors: {analysis['error_count']}")
        print(f"  Warnings: {analysis['warning_count']}")
        print(f"  Performance entries: {analysis['performance_entries']}")
        print(f"  Integration entries: {analysis['integration_entries']}")
        
        if analysis["recent_errors"]:
            print(f"\n❌ Recent Errors:")
            for error in analysis["recent_errors"][:5]:
                print(f"  - {error}")
        
        if analysis["recent_warnings"]:
            print(f"\n⚠️  Recent Warnings:")
            for warning in analysis["recent_warnings"][:5]:
                print(f"  - {warning}")


def create_debug_report(integration: InventorySystemIntegration, 
                       config_manager: InventoryConfigManager,
                       log_file: str = None) -> Dict:
    """
    Create a comprehensive debug report.
    
    Args:
        integration: InventorySystemIntegration instance
        config_manager: InventoryConfigManager instance
        log_file: Optional log file path
        
    Returns:
        Dictionary with comprehensive debug report
    """
    print("📋 Creating comprehensive debug report...")
    
    # Initialize debug tools
    debugger = InventoryDebugger()
    troubleshooter = InventoryTroubleshooter()
    performance_analyzer = InventoryPerformanceAnalyzer()
    log_analyzer = InventoryLogAnalyzer()
    
    # Perform diagnostics
    diagnosis = debugger.diagnose_system_health(integration)
    
    # Analyze performance
    performance_analysis = performance_analyzer.analyze_performance(config_manager)
    
    # Analyze logs if available
    log_analysis = {}
    if log_file:
        log_analysis = log_analyzer.analyze_logs(log_file)
    
    # Create comprehensive report
    report = {
        "timestamp": time.time(),
        "diagnosis": diagnosis,
        "performance_analysis": performance_analysis,
        "log_analysis": log_analysis,
        "system_info": {
            "integration_status": integration.get_integration_status(),
            "debug_info": integration.get_debug_info(),
            "configuration": config_manager.export_configuration()
        }
    }
    
    # Save report to file
    report_file = f"debug_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Debug report saved to: {report_file}")
    
    return report


def quick_diagnosis(integration: InventorySystemIntegration) -> Dict:
    """
    Perform a quick system diagnosis.
    
    Args:
        integration: InventorySystemIntegration instance
        
    Returns:
        Dictionary with quick diagnosis results
    """
    print("⚡ Performing quick diagnosis...")
    
    status = integration.get_integration_status()
    debug_info = integration.get_debug_info()
    
    # Quick checks
    checks = {
        "initialized": status.get("initialized", False),
        "components_integrated": sum(status.get("components", {}).values()),
        "inventory_components_ready": sum(status.get("inventory_components", {}).values()),
        "integration_thread_running": status.get("integration_thread", {}).get("running", False),
        "performance_monitoring_enabled": debug_info.get("integration_config", {}).get("enable_performance_monitoring", False)
    }
    
    # Determine overall health
    health_score = sum(checks.values()) / len(checks)
    overall_health = "HEALTHY" if health_score >= 0.8 else "DEGRADED" if health_score >= 0.5 else "UNHEALTHY"
    
    result = {
        "overall_health": overall_health,
        "health_score": health_score,
        "checks": checks,
        "timestamp": time.time()
    }
    
    print(f"🏥 Quick Diagnosis: {overall_health} (Score: {health_score:.2f})")
    
    return result 