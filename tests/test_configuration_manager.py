import unittest
import json
import tempfile
import os
from pathlib import Path
from entities.configuration_manager import (
    ConfigurationManager, 
    OrderGenerationConfig, 
    RobotConfig, 
    WarehouseLayoutConfig,
    AnalyticsConfig,
    ExportConfig,
    SystemConfig
)

class TestConfigurationManager(unittest.TestCase):
    """Test cases for ConfigurationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test config files
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, "test_config.json")
        
        # Create configuration manager
        self.config_manager = ConfigurationManager(self.test_config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        
        # Clean up any other files in temp directory
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            try:
                os.rmdir(self.temp_dir)
            except OSError:
                # Directory might not be empty, that's okay for tests
                pass
    
    def test_initialization(self):
        """Test ConfigurationManager initialization."""
        self.assertIsInstance(self.config_manager.order_generation, OrderGenerationConfig)
        self.assertIsInstance(self.config_manager.robot, RobotConfig)
        self.assertIsInstance(self.config_manager.warehouse_layout, WarehouseLayoutConfig)
        self.assertIsInstance(self.config_manager.analytics, AnalyticsConfig)
        self.assertIsInstance(self.config_manager.export, ExportConfig)
        self.assertIsInstance(self.config_manager.system, SystemConfig)
        
        # Check default values
        self.assertEqual(self.config_manager.order_generation.generation_interval, 30.0)
        self.assertEqual(self.config_manager.robot.robot_id, "ROBOT_001")
        self.assertEqual(self.config_manager.warehouse_layout.num_aisles, 20)
        self.assertEqual(self.config_manager.analytics.efficiency_threshold, 0.7)
        self.assertEqual(self.config_manager.export.export_formats, ["json", "csv"])
        self.assertEqual(self.config_manager.system.log_level, "INFO")
    
    def test_load_configuration_new_file(self):
        """Test loading configuration when file doesn't exist."""
        # Remove existing config file
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        
        # Create new config manager
        config_manager = ConfigurationManager(self.test_config_path)
        
        # Should create default config file
        self.assertTrue(os.path.exists(self.test_config_path))
        
        # Verify default configuration was saved
        with open(self.test_config_path, 'r') as f:
            config_data = json.load(f)
        
        self.assertIn('order_generation', config_data)
        self.assertIn('robot', config_data)
        self.assertIn('warehouse_layout', config_data)
        self.assertIn('analytics', config_data)
        self.assertIn('export', config_data)
        self.assertIn('system', config_data)
    
    def test_load_configuration_existing_file(self):
        """Test loading configuration from existing file."""
        # Create test configuration
        test_config = {
            'order_generation': {
                'generation_interval': 45.0,
                'min_items_per_order': 2,
                'max_items_per_order': 6,
                'enabled': False,
                'auto_start': False
            },
            'robot': {
                'robot_id': 'ROBOT_002',
                'max_speed': 1.5,
                'battery_capacity': 80.0
            },
            'warehouse_layout': {
                'num_aisles': 25,
                'num_racks_per_aisle': 30,
                'aisle_width': 4.0
            },
            'analytics': {
                'efficiency_threshold': 0.8,
                'completion_time_threshold': 400.0
            },
            'export': {
                'export_formats': ['json'],
                'auto_export_enabled': False
            },
            'system': {
                'log_level': 'DEBUG',
                'debug_mode': True
            }
        }
        
        # Save test configuration
        with open(self.test_config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Create new config manager
        config_manager = ConfigurationManager(self.test_config_path)
        
        # Verify configuration was loaded
        self.assertEqual(config_manager.order_generation.generation_interval, 45.0)
        self.assertEqual(config_manager.order_generation.min_items_per_order, 2)
        self.assertEqual(config_manager.order_generation.max_items_per_order, 6)
        self.assertEqual(config_manager.order_generation.enabled, False)
        self.assertEqual(config_manager.robot.robot_id, 'ROBOT_002')
        self.assertEqual(config_manager.robot.max_speed, 1.5)
        self.assertEqual(config_manager.warehouse_layout.num_aisles, 25)
        self.assertEqual(config_manager.analytics.efficiency_threshold, 0.8)
        self.assertEqual(config_manager.export.export_formats, ['json'])
        self.assertEqual(config_manager.system.log_level, 'DEBUG')
    
    def test_save_configuration(self):
        """Test saving configuration to file."""
        # Modify some configuration values
        self.config_manager.order_generation.generation_interval = 60.0
        self.config_manager.robot.robot_id = "ROBOT_003"
        self.config_manager.warehouse_layout.num_aisles = 30
        self.config_manager.analytics.efficiency_threshold = 0.9
        self.config_manager.export.export_formats = ["csv"]
        self.config_manager.system.log_level = "WARNING"
        
        # Save configuration
        result = self.config_manager.save_configuration()
        self.assertTrue(result)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.test_config_path))
        
        # Verify configuration was saved correctly
        with open(self.test_config_path, 'r') as f:
            config_data = json.load(f)
        
        self.assertEqual(config_data['order_generation']['generation_interval'], 60.0)
        self.assertEqual(config_data['robot']['robot_id'], 'ROBOT_003')
        self.assertEqual(config_data['warehouse_layout']['num_aisles'], 30)
        self.assertEqual(config_data['analytics']['efficiency_threshold'], 0.9)
        self.assertEqual(config_data['export']['export_formats'], ['csv'])
        self.assertEqual(config_data['system']['log_level'], 'WARNING')
    
    def test_validation_valid_configuration(self):
        """Test validation with valid configuration."""
        # This should not raise any exceptions
        try:
            self.config_manager._validate_configuration()
        except ValueError:
            self.fail("Validation should pass with valid configuration")
    
    def test_validation_invalid_order_generation(self):
        """Test validation with invalid order generation settings."""
        # Test negative generation interval
        self.config_manager.order_generation.generation_interval = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test invalid item range
        self.config_manager.order_generation.generation_interval = 30.0
        self.config_manager.order_generation.min_items_per_order = 5
        self.config_manager.order_generation.max_items_per_order = 3
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test max items too high
        self.config_manager.order_generation.min_items_per_order = 1
        self.config_manager.order_generation.max_items_per_order = 15
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
    
    def test_validation_invalid_robot_settings(self):
        """Test validation with invalid robot settings."""
        # Test negative max speed
        self.config_manager.robot.max_speed = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test invalid battery capacity
        self.config_manager.robot.max_speed = 1.0
        self.config_manager.robot.battery_capacity = 150
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
    
    def test_validation_invalid_warehouse_layout(self):
        """Test validation with invalid warehouse layout."""
        # Test negative number of aisles
        self.config_manager.warehouse_layout.num_aisles = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test negative aisle width
        self.config_manager.warehouse_layout.num_aisles = 20
        self.config_manager.warehouse_layout.aisle_width = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
    
    def test_validation_invalid_analytics_thresholds(self):
        """Test validation with invalid analytics thresholds."""
        # Test efficiency threshold out of range
        self.config_manager.analytics.efficiency_threshold = 1.5
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test negative completion time threshold
        self.config_manager.analytics.efficiency_threshold = 0.7
        self.config_manager.analytics.completion_time_threshold = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
    
    def test_validation_invalid_system_settings(self):
        """Test validation with invalid system settings."""
        # Test invalid log level
        self.config_manager.system.log_level = "INVALID"
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
        
        # Reset and test negative log file size
        self.config_manager.system.log_level = "INFO"
        self.config_manager.system.max_log_file_size = -1
        with self.assertRaises(ValueError):
            self.config_manager._validate_configuration()
    
    def test_get_configuration_methods(self):
        """Test getting configuration sections."""
        order_config = self.config_manager.get_order_generation_config()
        robot_config = self.config_manager.get_robot_config()
        warehouse_config = self.config_manager.get_warehouse_layout_config()
        analytics_config = self.config_manager.get_analytics_config()
        export_config = self.config_manager.get_export_config()
        system_config = self.config_manager.get_system_config()
        
        self.assertIsInstance(order_config, OrderGenerationConfig)
        self.assertIsInstance(robot_config, RobotConfig)
        self.assertIsInstance(warehouse_config, WarehouseLayoutConfig)
        self.assertIsInstance(analytics_config, AnalyticsConfig)
        self.assertIsInstance(export_config, ExportConfig)
        self.assertIsInstance(system_config, SystemConfig)
    
    def test_update_configuration(self):
        """Test updating specific configuration values."""
        # Update order generation interval
        result = self.config_manager.update_configuration('order_generation', 'generation_interval', 45.0)
        self.assertTrue(result)
        self.assertEqual(self.config_manager.order_generation.generation_interval, 45.0)
        
        # Update robot ID
        result = self.config_manager.update_configuration('robot', 'robot_id', 'ROBOT_004')
        self.assertTrue(result)
        self.assertEqual(self.config_manager.robot.robot_id, 'ROBOT_004')
        
        # Test invalid section
        result = self.config_manager.update_configuration('invalid_section', 'key', 'value')
        self.assertFalse(result)
        
        # Test invalid key
        result = self.config_manager.update_configuration('order_generation', 'invalid_key', 'value')
        self.assertFalse(result)
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # Modify some values
        self.config_manager.order_generation.generation_interval = 60.0
        self.config_manager.robot.robot_id = "ROBOT_999"
        self.config_manager.warehouse_layout.num_aisles = 50
        
        # Reset to defaults
        self.config_manager.reset_to_defaults()
        
        # Verify values are back to defaults
        self.assertEqual(self.config_manager.order_generation.generation_interval, 30.0)
        self.assertEqual(self.config_manager.robot.robot_id, "ROBOT_001")
        self.assertEqual(self.config_manager.warehouse_layout.num_aisles, 20)
        self.assertEqual(self.config_manager.analytics.efficiency_threshold, 0.7)
        self.assertEqual(self.config_manager.export.export_formats, ["json", "csv"])
        self.assertEqual(self.config_manager.system.log_level, "INFO")
    
    def test_get_configuration_summary(self):
        """Test getting configuration summary."""
        summary = self.config_manager.get_configuration_summary()
        
        self.assertIn('config_file_path', summary)
        self.assertIn('order_generation', summary)
        self.assertIn('robot', summary)
        self.assertIn('warehouse_layout', summary)
        self.assertIn('analytics', summary)
        self.assertIn('export', summary)
        self.assertIn('system', summary)
        
        # Check some specific values
        self.assertEqual(summary['order_generation']['generation_interval'], 30.0)
        self.assertEqual(summary['robot']['robot_id'], 'ROBOT_001')
        self.assertEqual(summary['warehouse_layout']['dimensions'], '20x20')
        self.assertEqual(summary['analytics']['efficiency_threshold'], 0.7)
        self.assertEqual(summary['export']['formats'], ['json', 'csv'])
        self.assertEqual(summary['system']['log_level'], 'INFO')
    
    def test_validate_config_file(self):
        """Test validating a configuration file."""
        # Create a valid config file
        valid_config = {
            'order_generation': {
                'generation_interval': 30.0,
                'min_items_per_order': 1,
                'max_items_per_order': 4,
                'enabled': True,
                'auto_start': True
            },
            'robot': {
                'robot_id': 'ROBOT_001',
                'max_speed': 1.0,
                'acceleration': 0.5,
                'deceleration': 0.5,
                'turning_speed': 0.3,
                'battery_capacity': 100.0,
                'charging_rate': 10.0
            },
            'warehouse_layout': {
                'num_aisles': 20,
                'num_racks_per_aisle': 20,
                'aisle_width': 3.0,
                'rack_depth': 2.0,
                'rack_height': 5.0,
                'item_spacing': 0.5,
                'robot_start_position': {'aisle': 10, 'rack': 10}
            },
            'analytics': {
                'efficiency_threshold': 0.7,
                'completion_time_threshold': 300.0,
                'distance_threshold': 1000.0,
                'direction_changes_threshold': 10,
                'auto_export_interval': 300.0,
                'export_directory': 'exports',
                'dashboard_refresh_interval': 1.0
            },
            'export': {
                'export_formats': ['json', 'csv'],
                'auto_export_enabled': True,
                'export_filename_prefix': 'warehouse_analytics',
                'include_timestamps': True,
                'compression_enabled': False,
                'max_export_file_size': 100
            },
            'system': {
                'log_level': 'INFO',
                'log_file': 'warehouse_simulation.log',
                'max_log_file_size': 10,
                'backup_logs': True,
                'debug_mode': False,
                'performance_monitoring': True
            }
        }
        
        valid_config_path = os.path.join(self.temp_dir, "valid_config.json")
        with open(valid_config_path, 'w') as f:
            json.dump(valid_config, f)
        
        # Test valid config file
        result = self.config_manager.validate_config_file(valid_config_path)
        self.assertTrue(result)
        
        # Create an invalid config file
        invalid_config = {
            'order_generation': {
                'generation_interval': -1  # Invalid negative value
            }
        }
        
        invalid_config_path = os.path.join(self.temp_dir, "invalid_config.json")
        with open(invalid_config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        # Test invalid config file
        result = self.config_manager.validate_config_file(invalid_config_path)
        self.assertFalse(result)
        
        # Clean up
        os.remove(valid_config_path)
        os.remove(invalid_config_path)


if __name__ == '__main__':
    unittest.main() 