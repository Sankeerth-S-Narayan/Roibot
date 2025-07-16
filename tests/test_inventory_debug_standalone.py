#!/usr/bin/env python3
"""
Standalone test script for inventory debugging tools.

This script tests the comprehensive debugging utilities for the inventory system,
including diagnostic tools, troubleshooting helpers, and performance analyzers.
"""

import sys
import os
import time
import json
import tempfile
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.inventory_debug_tools import (
    InventoryDebugger, InventoryTroubleshooter, InventoryPerformanceAnalyzer,
    InventoryLogAnalyzer, create_debug_report, quick_diagnosis, DebugReport
)
from core.inventory.inventory_integration import InventorySystemIntegration
from core.inventory.inventory_config import InventoryConfigManager, PerformanceMetricType


def test_inventory_debugger():
    """Test InventoryDebugger functionality."""
    print("🧪 Testing InventoryDebugger...")
    
    debugger = InventoryDebugger()
    
    # Create mock integration
    mock_integration = Mock(spec=InventorySystemIntegration)
    mock_config_manager = Mock(spec=InventoryConfigManager)
    
    # Setup mock integration with healthy system
    mock_integration.get_integration_status.return_value = {
        "initialized": True,
        "components": {
            "simulation_engine": True,
            "event_system": True,
            "warehouse_layout": True,
            "order_management": True
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
    
    mock_integration.get_debug_info.return_value = {
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
    
    mock_integration.config_manager = mock_config_manager
    
    # Setup mock config manager
    mock_config_manager.get_performance_analytics.return_value = {
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
    
    mock_config_manager.check_performance_thresholds.return_value = {
        "operation_time_violations": [],
        "memory_usage_violations": []
    }
    
    mock_config_manager.config.max_operation_time_ms = 10.0
    mock_config_manager.config.max_memory_usage_mb = 100.0
    
    # Test healthy system diagnosis
    print("  Testing healthy system diagnosis...")
    report = debugger.diagnose_system_health(mock_integration)
    
    assert isinstance(report, DebugReport), "Report should be DebugReport instance"
    assert len(report.error_log) == 0, "Healthy system should have no errors"
    assert len(report.warnings) == 0, "Healthy system should have no warnings"
    assert len(report.recommendations) > 0, "Should have recommendations"
    
    print("  ✅ Healthy system diagnosis passed")
    
    # Test unhealthy system diagnosis
    print("  Testing unhealthy system diagnosis...")
    mock_integration.get_integration_status.return_value = {
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
    
    mock_integration.get_debug_info.return_value = {
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
    
    report = debugger.diagnose_system_health(mock_integration)
    
    assert len(report.error_log) > 0, "Unhealthy system should have errors"
    assert len(report.warnings) > 0, "Unhealthy system should have warnings"
    assert len(report.recommendations) > 0, "Should have recommendations"
    
    print("  ✅ Unhealthy system diagnosis passed")
    print("✅ InventoryDebugger tests passed")


def test_inventory_troubleshooter():
    """Test InventoryTroubleshooter functionality."""
    print("🧪 Testing InventoryTroubleshooter...")
    
    troubleshooter = InventoryTroubleshooter()
    mock_config_manager = Mock(spec=InventoryConfigManager)
    
    # Setup mock config manager
    mock_config_manager.validate_configuration.return_value = {
        "valid": True,
        "errors": []
    }
    
    mock_config_manager.config.warehouse_width = 26
    mock_config_manager.config.warehouse_height = 20
    mock_config_manager.config.total_items = 500
    mock_config_manager.config.packout_zone_width = 1
    mock_config_manager.config.packout_zone_height = 1
    
    # Test initialization troubleshooting with success
    print("  Testing initialization troubleshooting (success)...")
    context = {"config_manager": mock_config_manager}
    result = troubleshooter.troubleshoot_issue("initialization_failure", context)
    
    assert result["issue"] == "Initialization Failure", "Should have correct issue type"
    assert "Configuration validation: PASS" in result["checks"], "Should have validation check"
    assert len(result["solutions"]) == 0, "Successful validation should have no solutions"
    
    print("  ✅ Initialization troubleshooting (success) passed")
    
    # Test initialization troubleshooting with errors
    print("  Testing initialization troubleshooting (errors)...")
    mock_config_manager.validate_configuration.return_value = {
        "valid": False,
        "errors": ["Invalid warehouse dimensions", "Invalid item count"]
    }
    
    mock_config_manager.config.warehouse_width = 0
    mock_config_manager.config.total_items = 1000
    
    result = troubleshooter.troubleshoot_issue("initialization_failure", context)
    
    assert "Configuration validation: FAIL" in result["checks"], "Should have failed validation"
    assert "Fix configuration errors" in result["solutions"], "Should have error solutions"
    assert "Set valid warehouse dimensions" in result["solutions"], "Should have dimension solution"
    
    print("  ✅ Initialization troubleshooting (errors) passed")
    
    # Test integration troubleshooting
    print("  Testing integration troubleshooting...")
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
    result = troubleshooter.troubleshoot_issue("integration_failure", context)
    
    assert result["issue"] == "Integration Failure", "Should have correct issue type"
    assert "simulation_engine: NOT INTEGRATED" in result["checks"], "Should detect missing integration"
    assert "Integrate with simulation_engine" in result["solutions"], "Should have integration solution"
    
    print("  ✅ Integration troubleshooting passed")
    
    # Test performance troubleshooting
    print("  Testing performance troubleshooting...")
    mock_config_manager.check_performance_thresholds.return_value = {
        "operation_time_violations": ["violation1"],
        "memory_usage_violations": ["violation2"]
    }
    
    mock_config_manager.config.performance_monitoring_enabled = False
    
    context = {"config_manager": mock_config_manager}
    result = troubleshooter.troubleshoot_issue("performance_issues", context)
    
    assert result["issue"] == "Performance Issues", "Should have correct issue type"
    assert "operation_time_violations: 1 violations" in result["checks"], "Should detect violations"
    assert "Enable performance monitoring" in result["solutions"], "Should have monitoring solution"
    
    print("  ✅ Performance troubleshooting passed")
    
    # Test unknown issue type
    print("  Testing unknown issue type...")
    result = troubleshooter.troubleshoot_issue("unknown_issue", {})
    
    assert "error" in result, "Should return error for unknown issue"
    assert "Unknown issue type: unknown_issue" in result["error"], "Should have correct error message"
    
    print("  ✅ Unknown issue type test passed")
    print("✅ InventoryTroubleshooter tests passed")


def test_inventory_performance_analyzer():
    """Test InventoryPerformanceAnalyzer functionality."""
    print("🧪 Testing InventoryPerformanceAnalyzer...")
    
    analyzer = InventoryPerformanceAnalyzer()
    mock_config_manager = Mock(spec=InventoryConfigManager)
    
    # Setup mock config manager
    mock_config_manager.get_performance_analytics.return_value = {
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
            "operation_time": [1.0, 2.0, 3.0, 4.0, 5.0],  # Increasing trend
            "memory_usage": [45.0, 50.0, 55.0]  # Increasing trend
        }
    }
    
    mock_config_manager.check_performance_thresholds.return_value = {
        "operation_time_violations": [],
        "memory_usage_violations": []
    }
    
    # Test successful performance analysis
    print("  Testing successful performance analysis...")
    analysis = analyzer.analyze_performance(mock_config_manager)
    
    assert "analytics" in analysis, "Should have analytics"
    assert "violations" in analysis, "Should have violations"
    assert "trends" in analysis, "Should have trends"
    assert "recommendations" in analysis, "Should have recommendations"
    assert "timestamp" in analysis, "Should have timestamp"
    
    # Check trends
    assert "operation_time" in analysis["trends"], "Should have operation time trend"
    assert analysis["trends"]["operation_time"] == "increasing", "Should detect increasing trend"
    
    print("  ✅ Successful performance analysis passed")
    
    # Test performance analysis with violations
    print("  Testing performance analysis with violations...")
    mock_config_manager.check_performance_thresholds.return_value = {
        "operation_time_violations": ["violation1"],
        "memory_usage_violations": ["violation2"]
    }
    
    analysis = analyzer.analyze_performance(mock_config_manager)
    
    assert "Address operation_time_violations violations" in analysis["recommendations"], "Should have violation recommendation"
    assert "Address memory_usage_violations violations" in analysis["recommendations"], "Should have violation recommendation"
    
    print("  ✅ Performance analysis with violations passed")
    
    # Test performance analysis with error
    print("  Testing performance analysis with error...")
    mock_config_manager.get_performance_analytics.side_effect = Exception("Test error")
    
    analysis = analyzer.analyze_performance(mock_config_manager)
    
    assert "error" in analysis, "Should have error field"
    assert analysis["error"] == "Test error", "Should have correct error message"
    
    print("  ✅ Performance analysis with error passed")
    print("✅ InventoryPerformanceAnalyzer tests passed")


def test_inventory_log_analyzer():
    """Test InventoryLogAnalyzer functionality."""
    print("🧪 Testing InventoryLogAnalyzer...")
    
    analyzer = InventoryLogAnalyzer()
    
    # Test successful log analysis
    print("  Testing successful log analysis...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("2024-01-01 10:00:00 - INFO - System started\n")
        f.write("2024-01-01 10:01:00 - ERROR - Configuration error\n")
        f.write("2024-01-01 10:02:00 - WARNING - High memory usage\n")
        f.write("2024-01-01 10:03:00 - INFO - Performance metric recorded\n")
        f.write("2024-01-01 10:04:00 - INFO - Integration successful\n")
        log_file = f.name
    
    try:
        analysis = analyzer.analyze_logs(log_file)
        
        assert analysis["total_lines"] == 5, "Should have correct total lines"
        assert analysis["error_count"] == 1, "Should have correct error count"
        assert analysis["warning_count"] == 1, "Should have correct warning count"
        assert analysis["performance_entries"] == 1, "Should have correct performance entries"
        assert analysis["integration_entries"] == 1, "Should have correct integration entries"
        assert len(analysis["recent_errors"]) == 1, "Should have recent errors"
        assert len(analysis["recent_warnings"]) == 1, "Should have recent warnings"
        
        print("  ✅ Successful log analysis passed")
        
    finally:
        os.unlink(log_file)
    
    # Test log analysis with non-existent file
    print("  Testing log analysis with non-existent file...")
    analysis = analyzer.analyze_logs("nonexistent.log")
    
    assert "error" in analysis, "Should have error field"
    assert "Failed to analyze logs" in analysis["error"], "Should have correct error message"
    
    print("  ✅ Non-existent file test passed")
    
    # Test log analysis with empty file
    print("  Testing log analysis with empty file...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        log_file = f.name
    
    try:
        analysis = analyzer.analyze_logs(log_file)
        
        assert analysis["total_lines"] == 0, "Should have zero lines"
        assert analysis["error_count"] == 0, "Should have zero errors"
        assert analysis["warning_count"] == 0, "Should have zero warnings"
        
        print("  ✅ Empty file test passed")
        
    finally:
        os.unlink(log_file)
    
    print("✅ InventoryLogAnalyzer tests passed")


def test_debug_report_functions():
    """Test debug report functions."""
    print("🧪 Testing debug report functions...")
    
    mock_integration = Mock(spec=InventorySystemIntegration)
    mock_config_manager = Mock(spec=InventoryConfigManager)
    
    # Setup mock integration
    mock_integration.get_integration_status.return_value = {
        "initialized": True,
        "components": {
            "simulation_engine": True,
            "event_system": True
        }
    }
    
    mock_integration.get_debug_info.return_value = {
        "integration_config": {
            "enable_performance_monitoring": True
        }
    }
    
    # Setup mock config manager
    mock_config_manager.get_performance_analytics.return_value = {
        "total_metrics": 10
    }
    
    mock_config_manager.check_performance_thresholds.return_value = {
        "operation_time_violations": []
    }
    
    mock_config_manager.export_configuration.return_value = {
        "warehouse_dimensions": {"width": 26, "height": 20}
    }
    
    # Test create debug report with log file
    print("  Testing create debug report with log file...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Test log content\n")
        log_file = f.name
    
    try:
        with patch('utils.inventory_debug_tools.InventoryLogAnalyzer') as mock_log_analyzer:
            mock_log_analyzer.return_value.analyze_logs.return_value = {
                "total_lines": 10,
                "error_count": 0
            }
            
            report = create_debug_report(mock_integration, mock_config_manager, log_file)
            
            assert "timestamp" in report, "Should have timestamp"
            assert "diagnosis" in report, "Should have diagnosis"
            assert "performance_analysis" in report, "Should have performance analysis"
            assert "log_analysis" in report, "Should have log analysis"
            assert "system_info" in report, "Should have system info"
            
            print("  ✅ Create debug report with log file passed")
            
    finally:
        os.unlink(log_file)
    
    # Test create debug report without log file
    print("  Testing create debug report without log file...")
    report = create_debug_report(mock_integration, mock_config_manager)
    
    assert "timestamp" in report, "Should have timestamp"
    assert "diagnosis" in report, "Should have diagnosis"
    assert "performance_analysis" in report, "Should have performance analysis"
    assert "log_analysis" in report, "Should have log analysis"
    assert "system_info" in report, "Should have system info"
    
    print("  ✅ Create debug report without log file passed")
    
    # Test quick diagnosis with healthy system
    print("  Testing quick diagnosis with healthy system...")
    result = quick_diagnosis(mock_integration)
    
    assert "overall_health" in result, "Should have overall health"
    assert "health_score" in result, "Should have health score"
    assert "checks" in result, "Should have checks"
    assert "timestamp" in result, "Should have timestamp"
    
    assert result["health_score"] > 0.5, "Healthy system should have good score"
    assert "initialized" in result["checks"], "Should check initialization"
    assert "components_integrated" in result["checks"], "Should check component integration"
    
    print("  ✅ Quick diagnosis with healthy system passed")
    
    # Test quick diagnosis with unhealthy system
    print("  Testing quick diagnosis with unhealthy system...")
    mock_integration.get_integration_status.return_value = {
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
    
    mock_integration.get_debug_info.return_value = {
        "integration_config": {
            "enable_performance_monitoring": False
        }
    }
    
    result = quick_diagnosis(mock_integration)
    
    assert result["health_score"] < 0.5, "Unhealthy system should have poor score"
    assert result["overall_health"] == "UNHEALTHY", "Should be marked as unhealthy"
    
    print("  ✅ Quick diagnosis with unhealthy system passed")
    print("✅ Debug report functions tests passed")


def main():
    """Run all tests."""
    print("🚀 Starting inventory debugging tools tests...")
    print("=" * 60)
    
    try:
        test_inventory_debugger()
        print()
        
        test_inventory_troubleshooter()
        print()
        
        test_inventory_performance_analyzer()
        print()
        
        test_inventory_log_analyzer()
        print()
        
        test_debug_report_functions()
        print()
        
        print("=" * 60)
        print("🎉 All inventory debugging tools tests passed!")
        print("✅ InventoryDebugger")
        print("✅ InventoryTroubleshooter")
        print("✅ InventoryPerformanceAnalyzer")
        print("✅ InventoryLogAnalyzer")
        print("✅ Debug report functions")
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 