"""
Test suite for enhanced simulation controls and validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from core.controls import SimulationController, ControlCommand
from core.validation import SimulationValidator, ValidationError, ErrorSeverity
from core.state import SimulationStatus
from core.engine import SimulationEngine


class TestSimulationController:
    """Test cases for SimulationController."""
    
    @pytest.fixture
    def mock_engine(self):
        """Create a mock simulation engine."""
        engine = Mock(spec=SimulationEngine)
        engine.state = Mock()
        engine.state.status = SimulationStatus.STOPPED
        engine.state.is_running.return_value = False
        engine.state.is_stopped.return_value = True
        engine.state.is_paused.return_value = False
        engine.state.simulation_time = 0.0
        engine.state.current_fps = 60.0
        engine.state.frame_count = 0
        engine.get_simulation_speed.return_value = 1.0
        engine.set_simulation_speed = Mock()
        engine.get_debug_info.return_value = {
            'is_initialized': True,
            'performance': {
                'frame_time': 0.016,
                'event_processing_time': 0.001,
                'component_update_time': 0.002
            },
            'events': {
                'queue_size': 10,
                'processed_events': 100,
                'event_count': 110
            }
        }
        engine.start = AsyncMock()
        engine.stop = AsyncMock()
        engine.pause = AsyncMock()
        engine.resume = AsyncMock()
        engine.load_config = AsyncMock()
        engine.is_initialized = True
        return engine
    
    @pytest.fixture
    def controller(self, mock_engine):
        """Create a controller instance."""
        return SimulationController(mock_engine)
    
    def test_controller_initialization(self, controller, mock_engine):
        """Test controller initialization."""
        assert controller.engine == mock_engine
        assert not controller.is_interactive
        assert controller.interactive_task is None
        assert controller.command_history == []
        assert len(controller.command_handlers) == 10
    
    @pytest.mark.asyncio
    async def test_start_interactive_mode(self, controller):
        """Test starting interactive mode."""
        with patch('asyncio.create_task') as mock_create_task:
            await controller.start_interactive_mode()
            assert controller.is_interactive
            mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_interactive_mode(self, controller):
        """Test stopping interactive mode."""
        # Start interactive mode first
        controller.is_interactive = True
        mock_task = AsyncMock()
        controller.interactive_task = mock_task
        
        await controller.stop_interactive_mode()
        
        assert not controller.is_interactive
        mock_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_command_start(self, controller, mock_engine):
        """Test processing start command."""
        await controller._process_command("start")
        
        assert "start" in controller.command_history
        mock_engine.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_command_stop(self, controller, mock_engine):
        """Test processing stop command."""
        mock_engine.state.is_stopped.return_value = False
        
        await controller._process_command("stop")
        
        assert "stop" in controller.command_history
        mock_engine.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_command_speed(self, controller, mock_engine):
        """Test processing speed command."""
        await controller._process_command("speed 2.0")
        
        assert "speed 2.0" in controller.command_history
        mock_engine.set_simulation_speed.assert_called_once_with(2.0)
    
    @pytest.mark.asyncio
    async def test_process_command_invalid(self, controller):
        """Test processing invalid command."""
        with patch('builtins.print') as mock_print:
            await controller._process_command("invalid_command")
            
            assert "invalid_command" in controller.command_history
            mock_print.assert_called_with("❌ Unknown command: invalid_command. Type 'help' for available commands.")
    
    @pytest.mark.asyncio
    async def test_handle_status(self, controller, mock_engine):
        """Test status command handler."""
        with patch('builtins.print') as mock_print:
            await controller._handle_status([])
            
            # Check that status information was printed
            mock_print.assert_called()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Status:" in call for call in print_calls)
    
    @pytest.mark.asyncio
    async def test_handle_stats(self, controller, mock_engine):
        """Test stats command handler."""
        with patch('builtins.print') as mock_print:
            await controller._handle_stats([])
            
            # Check that detailed statistics were printed
            mock_print.assert_called()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Detailed Statistics:" in call for call in print_calls)
    
    def test_command_history_management(self, controller):
        """Test command history management."""
        controller.command_history = ["test1", "test2", "test3"]
        
        # Test getting history
        history = controller.get_command_history()
        assert history == ["test1", "test2", "test3"]
        assert history is not controller.command_history  # Should be a copy
        
        # Test clearing history
        controller.clear_command_history()
        assert controller.command_history == []


class TestSimulationValidator:
    """Test cases for SimulationValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return SimulationValidator()
    
    def test_validator_initialization(self, validator):
        """Test validator initialization."""
        assert validator.error_count == 0
        assert validator.warning_count == 0
        assert validator.error_history == []
    
    def test_validate_speed_valid(self, validator):
        """Test valid speed validation."""
        assert validator.validate_speed(1.0) is True
        assert validator.validate_speed(2.5) is True
        assert validator.validate_speed(0.5) is True
    
    def test_validate_speed_invalid(self, validator):
        """Test invalid speed validation."""
        with pytest.raises(ValidationError, match="Speed must be a number"):
            validator.validate_speed("invalid")
        
        with pytest.raises(ValidationError, match="Speed must be positive"):
            validator.validate_speed(-1.0)
        
        with pytest.raises(ValidationError, match="Speed must be positive"):
            validator.validate_speed(0.0)
    
    def test_validate_speed_warnings(self, validator):
        """Test speed validation warnings."""
        # High speed should generate warning but still pass
        assert validator.validate_speed(15.0) is True
        assert validator.warning_count == 1
        
        # Low speed should generate warning but still pass
        validator.reset_error_counters()
        assert validator.validate_speed(0.05) is True
        assert validator.warning_count == 1
    
    def test_validate_state_transition_valid(self, validator):
        """Test valid state transitions."""
        assert validator.validate_state_transition(
            SimulationStatus.STOPPED, SimulationStatus.STARTING
        ) is True
        
        assert validator.validate_state_transition(
            SimulationStatus.RUNNING, SimulationStatus.PAUSED
        ) is True
        
        assert validator.validate_state_transition(
            SimulationStatus.PAUSED, SimulationStatus.RUNNING
        ) is True
    
    def test_validate_state_transition_invalid(self, validator):
        """Test invalid state transitions."""
        with pytest.raises(ValidationError, match="Invalid state transition"):
            validator.validate_state_transition(
                SimulationStatus.STOPPED, SimulationStatus.RUNNING
            )
        
        with pytest.raises(ValidationError, match="Invalid state transition"):
            validator.validate_state_transition(
                SimulationStatus.RUNNING, SimulationStatus.STARTING
            )
    
    def test_validate_config_value_valid(self, validator):
        """Test valid configuration value validation."""
        assert validator.validate_config_value("test_key", 42, int) is True
        assert validator.validate_config_value("test_key", "hello", str) is True
        assert validator.validate_config_value("test_key", 5.5, float, 0.0, 10.0) is True
    
    def test_validate_config_value_invalid_type(self, validator):
        """Test invalid configuration value type."""
        with pytest.raises(ValidationError, match="expected int, got str"):
            validator.validate_config_value("test_key", "invalid", int)
    
    def test_validate_config_value_invalid_range(self, validator):
        """Test invalid configuration value range."""
        with pytest.raises(ValidationError, match="below minimum"):
            validator.validate_config_value("test_key", -1, int, 0, 10)
        
        with pytest.raises(ValidationError, match="above maximum"):
            validator.validate_config_value("test_key", 15, int, 0, 10)
    
    def test_validate_fps_target_valid(self, validator):
        """Test valid FPS target validation."""
        assert validator.validate_fps_target(60) is True
        assert validator.validate_fps_target(30) is True
        assert validator.validate_fps_target(120) is True
    
    def test_validate_fps_target_invalid(self, validator):
        """Test invalid FPS target validation."""
        with pytest.raises(ValidationError, match="FPS must be an integer"):
            validator.validate_fps_target(60.5)
        
        with pytest.raises(ValidationError, match="FPS must be at least 1"):
            validator.validate_fps_target(0)
    
    def test_validate_fps_target_warnings(self, validator):
        """Test FPS target validation warnings."""
        # High FPS should generate warning but still pass
        assert validator.validate_fps_target(144) is True
        assert validator.warning_count == 1
        
        # Low FPS should generate warning but still pass
        validator.reset_error_counters()
        assert validator.validate_fps_target(5) is True
        assert validator.warning_count == 1
    
    def test_check_system_health_healthy(self, validator):
        """Test system health check with healthy metrics."""
        health = validator.check_system_health(
            frame_time=0.016,  # 60 FPS
            event_queue_size=100,
            memory_usage=100.0  # 100MB
        )
        
        assert health["overall"] == "healthy"
        assert health["frame_time_ok"] is True
        assert health["event_queue_ok"] is True
        assert health["memory_ok"] is True
        assert len(health["issues"]) == 0
        assert len(health["warnings"]) == 0
    
    def test_check_system_health_warnings(self, validator):
        """Test system health check with warnings."""
        health = validator.check_system_health(
            frame_time=0.040,  # 25 FPS - warning
            event_queue_size=600,  # 60% full - warning
            memory_usage=700.0  # 700MB - warning
        )
        
        assert health["overall"] == "warning"
        assert health["frame_time_ok"] is False
        assert health["event_queue_ok"] is False
        assert health["memory_ok"] is False
        assert len(health["issues"]) == 0
        assert len(health["warnings"]) == 3
    
    def test_check_system_health_critical(self, validator):
        """Test system health check with critical issues."""
        health = validator.check_system_health(
            frame_time=0.200,  # 5 FPS - critical
            event_queue_size=900,  # 90% full - critical
            memory_usage=1200.0  # 1.2GB - critical
        )
        
        assert health["overall"] == "critical"
        assert health["frame_time_ok"] is False
        assert health["event_queue_ok"] is False
        assert health["memory_ok"] is False
        assert len(health["issues"]) == 3
        assert len(health["warnings"]) == 0
    
    @pytest.mark.asyncio
    async def test_recovery_attempt_success(self, validator):
        """Test successful recovery attempt."""
        success = await validator.recovery_attempt("frame_time_high")
        assert success is True
    
    @pytest.mark.asyncio
    async def test_recovery_attempt_unknown_error(self, validator):
        """Test recovery attempt for unknown error type."""
        success = await validator.recovery_attempt("unknown_error")
        assert success is False
    
    def test_error_logging_and_summary(self, validator):
        """Test error logging and summary generation."""
        # Log some errors
        validator._log_error(ErrorSeverity.ERROR, "Test error")
        validator._log_error(ErrorSeverity.WARNING, "Test warning")
        
        # Check counters
        assert validator.error_count == 1
        assert validator.warning_count == 1
        
        # Check summary
        summary = validator.get_error_summary()
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 1
        assert len(summary["recent_errors"]) == 2
        
        # Test reset
        validator.reset_error_counters()
        assert validator.error_count == 0
        assert validator.warning_count == 0
        assert len(validator.error_history) == 0
    
    def test_error_severity_levels(self, validator):
        """Test different error severity levels."""
        validator._log_error(ErrorSeverity.INFO, "Info message")
        validator._log_error(ErrorSeverity.WARNING, "Warning message")
        validator._log_error(ErrorSeverity.ERROR, "Error message")
        validator._log_error(ErrorSeverity.CRITICAL, "Critical message")
        
        assert len(validator.error_history) == 4
        assert validator.error_count == 1  # Only ERROR severity increments error count
        assert validator.warning_count == 1  # Only WARNING severity increments warning count


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 