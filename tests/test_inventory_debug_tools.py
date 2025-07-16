"""
Tests for inventory debugging tools.

This module tests the comprehensive debugging utilities for the inventory system,
including diagnostic tools, troubleshooting helpers, and performance analyzers.
"""

import unittest
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from utils.inventory_debug_tools import (
    InventoryDebugger, InventoryTroubleshooter, InventoryPerformanceAnalyzer,
    InventoryLogAnalyzer, create_debug_report, quick_diagnosis, DebugReport
)
from core.inventory.inventory_integration import InventorySystemIntegration
from core.inventory.inventory_config import InventoryConfigManager, PerformanceMetricType


class TestInventoryDebugger(unittest.TestCase):
    """Test cases for InventoryDebugger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.debugger = InventoryDebugger()
        self.mock_integration = Mock(spec=InventorySystemIntegration)
        self.mock_config_manager = Mock(spec=InventoryConfigManager)
        
        # Setup mock integration
        self.mock_integration.get_integration_status.return_value = {
            "initialized": True,
            "components": {
                "simulation_engine": True,
                "event_system": True,
                "warehouse_layout": True,
                "order_management": False
            },
            "inventory_components": {
                "inventory_manager": True,
                "sync_manager": True,
                "config_manager": True
            },
            "integration_thread": {
                "running": True
            }
        }
        
        self.mock_integration.get_debug_info.return_value = {
            "integration_config": {
                "enable_performance_monitoring": True
            },
            "configuration": {
                "performance": {
                    "monitoring_enabled": True,
                    "debug_mode": True
                }
            },
            "config_manager": {
                "performance_metrics": {
                    "total_metrics": 10
                }
            }
        }
        
        self.mock_integration.config_manager = self.mock_config_manager
        
        # Setup mock config manager
        self.mock_config_manager.get_performance_analytics.return_value = {
            "total_metrics": 10,
            "performance_summary": {
                "operation_time": {
                    "count": 5,
                    "average": 3.5,
                    "min": 1.0,
                    "max": 8.0
                }
            }
        }
        
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": [],
            "memory_usage_violations": []
        }
        
        self.mock_config_manager.config.max_operation_time_ms = 10.0
        self.mock_config_manager.config.max_memory_usage_mb = 100.0
    
    def test_diagnose_system_health_success(self):
        """Test successful system health diagnosis."""
        report = self.debugger.diagnose_system_health(self.mock_integration)
        
        self.assertIsInstance(report, DebugReport)
        self.assertEqual(len(report.error_log), 0)
        self.assertEqual(len(report.warnings), 0)
        self.assertGreater(len(report.recommendations), 0)
        
        # Verify mock calls
        self.mock_integration.get_integration_status.assert_called_once()
        self.mock_integration.get_debug_info.assert_called_once()
        self.mock_config_manager.get_performance_analytics.assert_called_once()
        self.mock_config_manager.check_performance_thresholds.assert_called_once()
    
    def test_diagnose_system_health_with_errors(self):
        """Test system health diagnosis with errors."""
        # Setup mock with errors
        self.mock_integration.get_integration_status.return_value = {
            "initialized": False,
            "components": {
                "simulation_engine": False,
                "event_system": False,
                "warehouse_layout": False,
                "order_management": False
            },
            "inventory_components": {
                "inventory_manager": False,
                "sync_manager": False,
                "config_manager": False
            },
            "integration_thread": {
                "running": False
            }
        }
        
        self.mock_integration.get_debug_info.return_value = {
            "integration_config": {
                "enable_performance_monitoring": False
            },
            "configuration": {
                "performance": {
                    "monitoring_enabled": False,
                    "debug_mode": False
                }
            },
            "config_manager": {
                "performance_metrics": {
                    "total_metrics": 0
                }
            }
        }
        
        report = self.debugger.diagnose_system_health(self.mock_integration)
        
        self.assertGreater(len(report.error_log), 0)
        self.assertGreater(len(report.warnings), 0)
        self.assertGreater(len(report.recommendations), 0)
    
    def test_analyze_performance_success(self):
        """Test successful performance analysis."""
        performance_metrics = self.debugger._analyze_performance(self.mock_config_manager)
        
        self.assertIn("analytics", performance_metrics)
        self.assertIn("violations", performance_metrics)
        self.assertIn("thresholds", performance_metrics)
        
        self.assertEqual(performance_metrics["thresholds"]["max_operation_time_ms"], 10.0)
        self.assertEqual(performance_metrics["thresholds"]["max_memory_usage_mb"], 100.0)
    
    def test_analyze_performance_with_error(self):
        """Test performance analysis with error."""
        self.mock_config_manager.get_performance_analytics.side_effect = Exception("Test error")
        
        performance_metrics = self.debugger._analyze_performance(self.mock_config_manager)
        
        self.assertIn("error", performance_metrics)
        self.assertEqual(performance_metrics["error"], "Test error")
    
    def test_check_for_errors(self):
        """Test error checking functionality."""
        status = {
            "initialized": False,
            "components": {
                "simulation_engine": False,
                "event_system": True
            },
            "inventory_components": {
                "inventory_manager": False
            }
        }
        
        debug_info = {
            "config_manager": {
                "performance_metrics": {
                    "total_metrics": 0
                }
            }
        }
        
        errors = self.debugger._check_for_errors(status, debug_info)
        
        self.assertIn("System not initialized", errors)
        self.assertIn("simulation_engine not integrated", errors)
        self.assertIn("inventory_manager not initialized", errors)
        self.assertIn("No performance metrics recorded", errors)
    
    def test_check_for_warnings(self):
        """Test warning checking functionality."""
        status = {
            "integration_thread": {
                "running": False
            }
        }
        
        debug_info = {
            "configuration": {
                "performance": {
                    "monitoring_enabled": False,
                    "debug_mode": False
                }
            }
        }
        
        warnings = self.debugger._check_for_warnings(status, debug_info)
        
        self.assertIn("Integration thread not running", warnings)
        self.assertIn("Performance monitoring disabled", warnings)
        self.assertIn("Debug mode disabled", warnings)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        status = {
            "initialized": False,
            "components": {
                "simulation_engine": False,
                "event_system": True
            }
        }
        
        debug_info = {
            "integration_config": {
                "enable_performance_monitoring": False
            }
        }
        
        performance_metrics = {
            "violations": {
                "operation_time_violations": ["violation1"],
                "memory_usage_violations": []
            }
        }
        
        recommendations = self.debugger._generate_recommendations(status, debug_info, performance_metrics)
        
        self.assertIn("Initialize the inventory system", recommendations)
        self.assertIn("Integrate missing components: simulation_engine", recommendations)
        self.assertIn("Review performance thresholds and optimize operations", recommendations)
        self.assertIn("Enable performance monitoring for better diagnostics", recommendations)


class TestInventoryTroubleshooter(unittest.TestCase):
    """Test cases for InventoryTroubleshooter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.troubleshooter = InventoryTroubleshooter()
        self.mock_config_manager = Mock(spec=InventoryConfigManager)
        
        # Setup mock config manager
        self.mock_config_manager.validate_configuration.return_value = {
            "valid": True,
            "errors": []
        }
        
        self.mock_config_manager.config.warehouse_width = 26
        self.mock_config_manager.config.warehouse_height = 20
        self.mock_config_manager.config.total_items = 500
        self.mock_config_manager.config.packout_zone_width = 1
        self.mock_config_manager.config.packout_zone_height = 1
    
    def test_troubleshoot_initialization_success(self):
        """Test successful initialization troubleshooting."""
        context = {"config_manager": self.mock_config_manager}
        
        result = self.troubleshooter.troubleshoot_issue("initialization_failure", context)
        
        self.assertEqual(result["issue"], "Initialization Failure")
        self.assertIn("Configuration validation: PASS", result["checks"])
        self.assertEqual(len(result["solutions"]), 0)
    
    def test_troubleshoot_initialization_with_errors(self):
        """Test initialization troubleshooting with errors."""
        # Setup mock with errors
        self.mock_config_manager.validate_configuration.return_value = {
            "valid": False,
            "errors": ["Invalid warehouse dimensions", "Invalid item count"]
        }
        
        self.mock_config_manager.config.warehouse_width = 0
        self.mock_config_manager.config.total_items = 1000
        
        context = {"config_manager": self.mock_config_manager}
        
        result = self.troubleshooter.troubleshoot_issue("initialization_failure", context)
        
        self.assertEqual(result["issue"], "Initialization Failure")
        self.assertIn("Configuration validation: FAIL", result["checks"])
        self.assertIn("Fix configuration errors", result["solutions"])
        self.assertIn("Set valid warehouse dimensions", result["solutions"])
        self.assertIn("Reduce total_items", result["solutions"])
    
    def test_troubleshoot_integration_success(self):
        """Test successful integration troubleshooting."""
        mock_integration = Mock()
        mock_integration.get_integration_status.return_value = {
            "components": {
                "simulation_engine": True,
                "event_system": True,
                "warehouse_layout": True,
                "order_management": True
            }
        }
        
        context = {"integration": mock_integration}
        
        result = self.troubleshooter.troubleshoot_issue("integration_failure", context)
        
        self.assertEqual(result["issue"], "Integration Failure")
        self.assertIn("simulation_engine: INTEGRATED", result["checks"])
        self.assertEqual(len(result["solutions"]), 0)
    
    def test_troubleshoot_integration_with_failures(self):
        """Test integration troubleshooting with failures."""
        mock_integration = Mock()
        mock_integration.get_integration_status.return_value = {
            "components": {
                "simulation_engine": False,
                "event_system": True,
                "warehouse_layout": False,
                "order_management": True
            }
        }
        
        context = {"integration": mock_integration}
        
        result = self.troubleshooter.troubleshoot_issue("integration_failure", context)
        
        self.assertEqual(result["issue"], "Integration Failure")
        self.assertIn("simulation_engine: NOT INTEGRATED", result["checks"])
        self.assertIn("warehouse_layout: NOT INTEGRATED", result["checks"])
        self.assertIn("Integrate with simulation_engine", result["solutions"])
        self.assertIn("Integrate with warehouse_layout", result["solutions"])
    
    def test_troubleshoot_performance_success(self):
        """Test successful performance troubleshooting."""
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": [],
            "memory_usage_violations": []
        }
        
        context = {"config_manager": self.mock_config_manager}
        
        result = self.troubleshooter.troubleshoot_issue("performance_issues", context)
        
        self.assertEqual(result["issue"], "Performance Issues")
        self.assertEqual(len(result["solutions"]), 0)
    
    def test_troubleshoot_performance_with_violations(self):
        """Test performance troubleshooting with violations."""
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": ["violation1", "violation2"],
            "memory_usage_violations": ["violation3"]
        }
        
        self.mock_config_manager.config.performance_monitoring_enabled = False
        
        context = {"config_manager": self.mock_config_manager}
        
        result = self.troubleshooter.troubleshoot_issue("performance_issues", context)
        
        self.assertEqual(result["issue"], "Performance Issues")
        self.assertIn("operation_time_violations: 2 violations", result["checks"])
        self.assertIn("memory_usage_violations: 1 violations", result["checks"])
        self.assertIn("Review operation_time_violations thresholds", result["solutions"])
        self.assertIn("Review memory_usage_violations thresholds", result["solutions"])
        self.assertIn("Enable performance monitoring", result["solutions"])
    
    def test_troubleshoot_unknown_issue(self):
        """Test troubleshooting with unknown issue type."""
        context = {}
        
        result = self.troubleshooter.troubleshoot_issue("unknown_issue", context)
        
        self.assertIn("error", result)
        self.assertIn("Unknown issue type: unknown_issue", result["error"])


class TestInventoryPerformanceAnalyzer(unittest.TestCase):
    """Test cases for InventoryPerformanceAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = InventoryPerformanceAnalyzer()
        self.mock_config_manager = Mock(spec=InventoryConfigManager)
        
        # Setup mock config manager
        self.mock_config_manager.get_performance_analytics.return_value = {
            "total_metrics": 10,
            "performance_summary": {
                "operation_time": {
                    "count": 5,
                    "average": 3.5,
                    "min": 1.0,
                    "max": 8.0
                },
                "memory_usage": {
                    "count": 3,
                    "average": 50.0,
                    "min": 45.0,
                    "max": 55.0
                }
            },
            "metric_types": {
                "operation_time": [1.0, 2.0, 3.0, 4.0, 5.0],
                "memory_usage": [45.0, 50.0, 55.0]
            }
        }
        
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": [],
            "memory_usage_violations": []
        }
    
    def test_analyze_performance_success(self):
        """Test successful performance analysis."""
        analysis = self.analyzer.analyze_performance(self.mock_config_manager)
        
        self.assertIn("analytics", analysis)
        self.assertIn("violations", analysis)
        self.assertIn("trends", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("timestamp", analysis)
        
        # Verify trends
        self.assertIn("operation_time", analysis["trends"])
        self.assertEqual(analysis["trends"]["operation_time"], "increasing")
    
    def test_analyze_performance_with_violations(self):
        """Test performance analysis with violations."""
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": ["violation1"],
            "memory_usage_violations": ["violation2"]
        }
        
        analysis = self.analyzer.analyze_performance(self.mock_config_manager)
        
        self.assertIn("Address operation_time_violations violations", analysis["recommendations"])
        self.assertIn("Address memory_usage_violations violations", analysis["recommendations"])
    
    def test_analyze_performance_with_error(self):
        """Test performance analysis with error."""
        self.mock_config_manager.get_performance_analytics.side_effect = Exception("Test error")
        
        analysis = self.analyzer.analyze_performance(self.mock_config_manager)
        
        self.assertIn("error", analysis)
        self.assertEqual(analysis["error"], "Test error")
    
    def test_analyze_trends(self):
        """Test trend analysis functionality."""
        analytics = {
            "performance_summary": {
                "operation_time": {
                    "count": 3
                }
            },
            "metric_types": {
                "operation_time": [1.0, 2.0, 3.0]  # Increasing trend
            }
        }
        
        trends = self.analyzer._analyze_trends(analytics)
        
        self.assertIn("operation_time", trends)
        self.assertEqual(trends["operation_time"], "increasing")
    
    def test_generate_performance_recommendations(self):
        """Test performance recommendation generation."""
        analytics = {
            "total_metrics": 5,  # Low count
            "performance_summary": {
                "operation_time": {
                    "average": 8.0  # High average
                }
            }
        }
        
        violations = {
            "operation_time_violations": ["violation1"],
            "memory_usage_violations": []
        }
        
        recommendations = self.analyzer._generate_performance_recommendations(analytics, violations)
        
        self.assertIn("Address operation_time_violations violations", recommendations)
        self.assertIn("Increase performance monitoring frequency", recommendations)
        self.assertIn("Optimize operation performance", recommendations)


class TestInventoryLogAnalyzer(unittest.TestCase):
    """Test cases for InventoryLogAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = InventoryLogAnalyzer()
    
    def test_analyze_logs_success(self):
        """Test successful log analysis."""
        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("2024-01-01 10:00:00 - INFO - System started\n")
            f.write("2024-01-01 10:01:00 - ERROR - Configuration error\n")
            f.write("2024-01-01 10:02:00 - WARNING - High memory usage\n")
            f.write("2024-01-01 10:03:00 - INFO - Performance metric recorded\n")
            f.write("2024-01-01 10:04:00 - INFO - Integration successful\n")
            log_file = f.name
        
        try:
            analysis = self.analyzer.analyze_logs(log_file)
            
            self.assertEqual(analysis["total_lines"], 5)
            self.assertEqual(analysis["error_count"], 1)
            self.assertEqual(analysis["warning_count"], 1)
            self.assertEqual(analysis["performance_entries"], 1)
            self.assertEqual(analysis["integration_entries"], 1)
            self.assertEqual(len(analysis["recent_errors"]), 1)
            self.assertEqual(len(analysis["recent_warnings"]), 1)
            
        finally:
            os.unlink(log_file)
    
    def test_analyze_logs_file_not_found(self):
        """Test log analysis with non-existent file."""
        analysis = self.analyzer.analyze_logs("nonexistent.log")
        
        self.assertIn("error", analysis)
        self.assertIn("Failed to analyze logs", analysis["error"])
    
    def test_analyze_logs_empty_file(self):
        """Test log analysis with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name
        
        try:
            analysis = self.analyzer.analyze_logs(log_file)
            
            self.assertEqual(analysis["total_lines"], 0)
            self.assertEqual(analysis["error_count"], 0)
            self.assertEqual(analysis["warning_count"], 0)
            
        finally:
            os.unlink(log_file)


class TestDebugReportFunctions(unittest.TestCase):
    """Test cases for debug report functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_integration = Mock(spec=InventorySystemIntegration)
        self.mock_config_manager = Mock(spec=InventoryConfigManager)
        
        # Setup mock integration
        self.mock_integration.get_integration_status.return_value = {
            "initialized": True,
            "components": {
                "simulation_engine": True,
                "event_system": True
            }
        }
        
        self.mock_integration.get_debug_info.return_value = {
            "integration_config": {
                "enable_performance_monitoring": True
            }
        }
        
        # Setup mock config manager
        self.mock_config_manager.get_performance_analytics.return_value = {
            "total_metrics": 10
        }
        
        self.mock_config_manager.check_performance_thresholds.return_value = {
            "operation_time_violations": []
        }
        
        self.mock_config_manager.export_configuration.return_value = {
            "warehouse_dimensions": {"width": 26, "height": 20}
        }
    
    @patch('utils.inventory_debug_tools.InventoryLogAnalyzer')
    def test_create_debug_report_success(self, mock_log_analyzer):
        """Test successful debug report creation."""
        mock_log_analyzer.return_value.analyze_logs.return_value = {
            "total_lines": 10,
            "error_count": 0
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test log content\n")
            log_file = f.name
        
        try:
            report = create_debug_report(self.mock_integration, self.mock_config_manager, log_file)
            
            self.assertIn("timestamp", report)
            self.assertIn("diagnosis", report)
            self.assertIn("performance_analysis", report)
            self.assertIn("log_analysis", report)
            self.assertIn("system_info", report)
            
        finally:
            os.unlink(log_file)
    
    def test_create_debug_report_without_log_file(self):
        """Test debug report creation without log file."""
        report = create_debug_report(self.mock_integration, self.mock_config_manager)
        
        self.assertIn("timestamp", report)
        self.assertIn("diagnosis", report)
        self.assertIn("performance_analysis", report)
        self.assertIn("log_analysis", report)
        self.assertIn("system_info", report)
    
    def test_quick_diagnosis_success(self):
        """Test successful quick diagnosis."""
        result = quick_diagnosis(self.mock_integration)
        
        self.assertIn("overall_health", result)
        self.assertIn("health_score", result)
        self.assertIn("checks", result)
        self.assertIn("timestamp", result)
        
        self.assertGreater(result["health_score"], 0.5)
        self.assertIn("initialized", result["checks"])
        self.assertIn("components_integrated", result["checks"])
    
    def test_quick_diagnosis_unhealthy_system(self):
        """Test quick diagnosis with unhealthy system."""
        self.mock_integration.get_integration_status.return_value = {
            "initialized": False,
            "components": {
                "simulation_engine": False,
                "event_system": False
            },
            "inventory_components": {
                "inventory_manager": False
            },
            "integration_thread": {
                "running": False
            }
        }
        
        self.mock_integration.get_debug_info.return_value = {
            "integration_config": {
                "enable_performance_monitoring": False
            }
        }
        
        result = quick_diagnosis(self.mock_integration)
        
        self.assertLess(result["health_score"], 0.5)
        self.assertEqual(result["overall_health"], "UNHEALTHY")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 