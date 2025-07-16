"""
Enhanced simulation controls with interactive command interface.
Provides advanced control mechanisms and user-friendly interfaces.
"""

import asyncio
import sys
from typing import Optional, Dict, Any, Callable
from enum import Enum

from .engine import SimulationEngine
from .events import EventType


class ControlCommand(Enum):
    """Available control commands."""
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    SPEED = "speed"
    STATUS = "status"
    STATS = "stats"
    HELP = "help"
    QUIT = "quit"
    RESET = "reset"


class SimulationController:
    """
    Advanced simulation controller with interactive controls.
    Provides user-friendly interface for simulation management.
    """
    
    def __init__(self, engine: SimulationEngine):
        """
        Initialize simulation controller.
        
        Args:
            engine: SimulationEngine instance to control
        """
        self.engine = engine
        self.is_interactive = False
        self.interactive_task: Optional[asyncio.Task] = None
        self.command_history = []
        
        # Command handlers
        self.command_handlers: Dict[ControlCommand, Callable] = {
            ControlCommand.START: self._handle_start,
            ControlCommand.STOP: self._handle_stop,
            ControlCommand.PAUSE: self._handle_pause,
            ControlCommand.RESUME: self._handle_resume,
            ControlCommand.SPEED: self._handle_speed,
            ControlCommand.STATUS: self._handle_status,
            ControlCommand.STATS: self._handle_stats,
            ControlCommand.HELP: self._handle_help,
            ControlCommand.QUIT: self._handle_quit,
            ControlCommand.RESET: self._handle_reset,
        }
        
        print("🎮 SimulationController initialized")
    
    async def start_interactive_mode(self) -> None:
        """Start interactive control mode."""
        if self.is_interactive:
            print("⚠️  Interactive mode already running")
            return
        
        self.is_interactive = True
        print("🎮 Starting interactive control mode...")
        print("💡 Type 'help' for available commands")
        
        self.interactive_task = asyncio.create_task(self._interactive_loop())
    
    async def stop_interactive_mode(self) -> None:
        """Stop interactive control mode."""
        if not self.is_interactive:
            return
        
        self.is_interactive = False
        
        if self.interactive_task and not self.interactive_task.done():
            self.interactive_task.cancel()
            try:
                await self.interactive_task
            except asyncio.CancelledError:
                pass
        
        print("🛑 Interactive control mode stopped")
    
    async def _interactive_loop(self) -> None:
        """Main interactive control loop."""
        print("🎮 Interactive mode active. Type commands:")
        
        while self.is_interactive:
            try:
                # Show prompt
                status = self.engine.state.status.value
                speed = self.engine.get_simulation_speed()
                prompt = f"[{status}|{speed}x] > "
                
                # Get user input (simulate for now - in real implementation would use aioconsole)
                print(prompt, end="", flush=True)
                
                # For demo purposes, we'll simulate some commands
                # In real implementation, you'd use aioconsole.ainput() for async input
                await asyncio.sleep(3.0)  # Simulate waiting for input (increased from 1.0)
                
                # Demo commands (remove this in real implementation)
                if not hasattr(self, '_demo_commands'):
                    self._demo_commands = ["status", "pause", "resume", "stats"]
                    self._demo_index = 0
                
                if self._demo_index < len(self._demo_commands):
                    command_line = self._demo_commands[self._demo_index]
                    self._demo_index += 1
                    print(command_line)  # Show what command was "entered"
                    await self._process_command(command_line)
                    await asyncio.sleep(5.0)  # Wait between demo commands (increased from 2.0)
                else:
                    await asyncio.sleep(10.0)  # Just wait when no more demo commands (increased from 5.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in interactive loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_command(self, command_line: str) -> None:
        """
        Process a command from user input.
        
        Args:
            command_line: Raw command line input
        """
        if not command_line.strip():
            return
        
        # Add to history
        self.command_history.append(command_line)
        
        # Parse command
        parts = command_line.strip().split()
        command_str = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Find matching command
        try:
            command = ControlCommand(command_str)
        except ValueError:
            print(f"❌ Unknown command: {command_str}. Type 'help' for available commands.")
            return
        
        # Execute command
        try:
            await self.command_handlers[command](args)
        except Exception as e:
            print(f"❌ Error executing command '{command_str}': {e}")
    
    # Command handlers
    async def _handle_start(self, args: list) -> None:
        """Handle start command."""
        if self.engine.state.is_running():
            print("⚠️  Simulation is already running")
            return
        
        if not self.engine.is_initialized:
            print("🔄 Initializing simulation...")
            await self.engine.load_config()
        
        print("🚀 Starting simulation...")
        await self.engine.start()
        print("✅ Simulation started successfully")
    
    async def _handle_stop(self, args: list) -> None:
        """Handle stop command."""
        if self.engine.state.is_stopped():
            print("⚠️  Simulation is already stopped")
            return
        
        print("⏹️  Stopping simulation...")
        await self.engine.stop()
        print("✅ Simulation stopped successfully")
    
    async def _handle_pause(self, args: list) -> None:
        """Handle pause command."""
        if self.engine.state.is_paused():
            print("⚠️  Simulation is already paused")
            return
        
        if not self.engine.state.is_running():
            print("⚠️  Cannot pause: simulation is not running")
            return
        
        await self.engine.pause()
        print("⏸️  Simulation paused")
    
    async def _handle_resume(self, args: list) -> None:
        """Handle resume command."""
        if not self.engine.state.is_paused():
            print("⚠️  Simulation is not paused")
            return
        
        await self.engine.resume()
        print("▶️  Simulation resumed")
    
    async def _handle_speed(self, args: list) -> None:
        """Handle speed command."""
        if not args:
            current_speed = self.engine.get_simulation_speed()
            print(f"⚡ Current simulation speed: {current_speed}x")
            print("💡 Usage: speed <multiplier> (e.g., speed 2.0)")
            return
        
        try:
            speed = float(args[0])
            if speed <= 0:
                print("❌ Speed must be positive")
                return
            
            old_speed = self.engine.get_simulation_speed()
            self.engine.set_simulation_speed(speed)
            print(f"⚡ Simulation speed changed: {old_speed}x → {speed}x")
            
        except ValueError:
            print("❌ Invalid speed value. Must be a number.")
    
    async def _handle_status(self, args: list) -> None:
        """Handle status command."""
        status = self.engine.state.status.value
        speed = self.engine.get_simulation_speed()
        sim_time = self.engine.state.simulation_time
        fps = self.engine.state.current_fps
        
        print(f"📊 Simulation Status:")
        print(f"   Status: {status}")
        print(f"   Speed: {speed}x")
        print(f"   Time: {sim_time:.1f}s")
        print(f"   FPS: {fps:.1f}")
        print(f"   Frames: {self.engine.state.frame_count}")
    
    async def _handle_stats(self, args: list) -> None:
        """Handle stats command."""
        debug_info = self.engine.get_debug_info()
        
        print(f"📈 Detailed Statistics:")
        print(f"   Engine initialized: {debug_info['is_initialized']}")
        print(f"   Performance:")
        print(f"     Frame time: {debug_info['performance']['frame_time']*1000:.2f}ms")
        print(f"     Event processing: {debug_info['performance']['event_processing_time']*1000:.2f}ms")
        print(f"     Component update: {debug_info['performance']['component_update_time']*1000:.2f}ms")
        print(f"   Events:")
        print(f"     Queue size: {debug_info['events']['queue_size']}")
        print(f"     Processed: {debug_info['events']['processed_events']}")
        print(f"     Total: {debug_info['events']['event_count']}")
    
    async def _handle_help(self, args: list) -> None:
        """Handle help command."""
        print("🎮 Available Commands:")
        print("   start    - Start the simulation")
        print("   stop     - Stop the simulation")
        print("   pause    - Pause the simulation")
        print("   resume   - Resume the simulation")
        print("   speed <x> - Set simulation speed (e.g., speed 2.0)")
        print("   status   - Show simulation status")
        print("   stats    - Show detailed statistics")
        print("   reset    - Reset simulation state")
        print("   help     - Show this help message")
        print("   quit     - Exit interactive mode")
    
    async def _handle_quit(self, args: list) -> None:
        """Handle quit command."""
        print("👋 Exiting interactive mode...")
        await self.stop_interactive_mode()
    
    async def _handle_reset(self, args: list) -> None:
        """Handle reset command."""
        print("🔄 Resetting simulation...")
        
        # Stop if running
        if not self.engine.state.is_stopped():
            await self.engine.stop()
        
        # Reset components
        self.engine.state.reset()
        self.engine.event_system.reset()
        if self.engine.timing_manager:
            self.engine.timing_manager.reset()
        
        print("✅ Simulation reset complete")
    
    def get_command_history(self) -> list:
        """Get command history."""
        return self.command_history.copy()
    
    def clear_command_history(self) -> None:
        """Clear command history."""
        self.command_history.clear()
        print("🗑️  Command history cleared") 