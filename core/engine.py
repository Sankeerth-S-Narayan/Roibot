"""
Core simulation engine for the Roibot warehouse robot simulation.

This module provides the main SimulationEngine class that coordinates all simulation
components including timing, state management, event processing, and performance monitoring.

Key Features:
- Asyncio-based event loop for smooth 60 FPS operation
- Real-time performance monitoring and optimization
- Event-driven architecture for component communication
- Configuration management with validation
- Comprehensive debug information and logging

The engine follows a clear lifecycle:
1. Initialization (load_config)
2. Start (start)
3. Run (run) - main simulation loop
4. Stop (stop)
5. Shutdown (shutdown)

Performance monitoring is integrated throughout the lifecycle to ensure
smooth operation and provide real-time feedback on system health.

Author: Roibot Development Team
Version: 1.0
"""

import asyncio
import time
import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .state import SimulationState, SimulationStatus
from .events import EventSystem, EventType
from .main_config import get_config
from utils.timing import TimingManager
from utils.performance import PerformanceBenchmark, PerformanceOptimizer
from .layout.coordinate import Coordinate, SmoothCoordinate
from .layout.distance_tracker import DistanceTracker
from .layout.snake_pattern import SnakePattern
from .layout.warehouse_layout import WarehouseLayoutManager
from .layout.bidirectional_path_calculator import BidirectionalPathCalculator
from .layout.movement_trail_manager import MovementTrailManager
from .layout.aisle_timing_manager import AisleTimingManager

logger = logging.getLogger(__name__)

class RobotState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    PICKING = "picking"
    COLLECTING = "collecting"
    RETURNING = "returning"
    COMPLETED = "completed"

@dataclass
class Robot:
    """Robot entity with enhanced navigation capabilities."""
    position: SmoothCoordinate
    state: RobotState = RobotState.IDLE
    current_path: List[Coordinate] = field(default_factory=list)
    path_index: int = 0
    target_item: Optional[str] = None
    collected_items: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    movement_start_time: Optional[float] = None
    last_direction_change: Optional[float] = None
    direction_change_cooldown: float = 0.5  # seconds
    
    # Enhanced navigation properties
    current_direction: Optional[str] = None
    path_execution_state: str = "ready"  # ready, executing, paused, completed
    trail_points: List[Tuple[Coordinate, float]] = field(default_factory=list)
    
    # Smooth movement tracking
    movement_target: Optional[Coordinate] = None
    movement_start_position: Optional[SmoothCoordinate] = None
    
    # Picking operation tracking
    picking_start_time: Optional[float] = None
    picking_duration: float = 3.0  # seconds to pick an item
    current_picking_item: Optional[str] = None
    
    def __post_init__(self):
        self.movement_start_time = time.time()
        self.last_direction_change = time.time()

class SimulationEngine:
    """Enhanced simulation engine with bidirectional navigation."""
    
    def __init__(self):
        """Initialize the simulation engine."""
        # Core components
        self.state = SimulationState()
        self.event_system = EventSystem()
        self.timing_manager: Optional[TimingManager] = None
        
        # Data bridge for web interface
        self.data_bridge = None
        
        # Initialize layout components
        self.warehouse_layout = WarehouseLayoutManager()
        self.snake_pattern = SnakePattern(25, 20)  # Use integer values instead of warehouse_layout
        self.distance_tracker = DistanceTracker()
        
        # Enhanced navigation components
        self.path_calculator = BidirectionalPathCalculator(
            self.warehouse_layout, 
            self.snake_pattern,
            {}
        )
        self.trail_manager = MovementTrailManager({})
        self.aisle_timing = AisleTimingManager({})
        
        # Configuration and performance monitoring
        from core.config.bidirectional_config import get_bidirectional_config
        from core.performance.path_performance_monitor import PathPerformanceMonitor
        
        self.bidirectional_config = get_bidirectional_config()
        self.path_performance_monitor = PathPerformanceMonitor()
        
        # Robot and simulation state
        self.robot = Robot(SmoothCoordinate(1.0, 1.0))
        self.robot.state = RobotState.IDLE
        self.robot.collected_items = []
        self.robot.current_path = []
        self.robot.path_index = 0
        self.robot.path_execution_state = "idle"
        self.robot.current_direction = "forward"  # Track current direction
        self.orders: List[Dict[str, Any]] = []
        self.current_order_index = 0
        self.simulation_time = 0.0
        self.is_running = False
        
        # Performance tracking
        self.performance_metrics = {
            "total_distance": 0.0,
            "items_collected": 0,
            "orders_completed": 0,
            "direction_changes": 0,
            "path_optimizations": 0,
            "order_distances": {},  # Track distance for each order
            "current_order_distance": 0.0  # Real-time distance for current order
        }
        
        # Performance monitoring
        self.performance_benchmark = PerformanceBenchmark()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Engine state
        self.is_initialized = False
        self.main_task: Optional[asyncio.Task] = None
        self.last_frame_time = 0.0
        
        logger.info("Enhanced SimulationEngine initialized with bidirectional navigation")
    
    def set_data_bridge(self, data_bridge):
        """Set the data bridge for web interface communication."""
        self.data_bridge = data_bridge
        logger.info("Data bridge connected to simulation engine")
    
    async def load_config(self) -> None:
        """Load configuration and initialize components."""
        print("⚙️  Loading configuration...")
        
        # Load configuration into state
        self.state.load_configuration()
        
        # Initialize timing manager with configuration
        config_manager = get_config()
        self.timing_manager = TimingManager(target_fps=config_manager.timing.TARGET_FPS)
        
        # Register engine as component
        self.state.register_component("engine")
        
        # Configure event system
        self.event_system.configure(
            max_queue_size=config_manager.get_value("engine", "event_queue_size", 1000),
            max_concurrent_events=config_manager.get_value("engine", "max_concurrent_events", 50)
        )
        
        # Initialize enhanced navigation components with config
        self.path_calculator.configure(config_manager.simulation["path_optimization"])
        self.trail_manager.configure(config_manager.simulation["trail_config"])
        self.aisle_timing.configure(config_manager.simulation["aisle_timing"])
        
        # Configure bidirectional navigation components
        bidirectional_config = config_manager.get_value("simulation", "bidirectional_navigation", {})
        self.bidirectional_config.reload_configuration()
        self.path_performance_monitor.configure(bidirectional_config.get("performance_monitoring", {}))

        self.is_initialized = True
        print("✅ Configuration loaded and engine initialized")
    
    async def start(self) -> None:
        """Start the simulation."""
        if not self.is_initialized:
            print("🔄 [DEBUG] Engine not initialized, loading config...")
            await self.load_config()
        
        if self.is_running:
            print("⚠️ [DEBUG] Simulation is already running")
            return
        
        print("🚀 [DEBUG] Starting simulation engine...")
        print(f"🔍 [DEBUG] Engine state before start: is_running={self.is_running}, simulation_time={self.simulation_time}")
        
        # Set running flag
        self.is_running = True
        print("✅ [DEBUG] Set is_running = True")
        
        # Start state
        self.state.start()
        
        # Start event system
        await self.event_system.start()
        
        # Start timing manager
        if self.timing_manager:
            self.timing_manager.start()
        
        # Fire start event
        await self.event_system.emit(EventType.SIMULATION_START, {
            "timestamp": time.time(),
            "config_loaded": self.state.config_loaded
        })
        
        print("✅ Simulation engine started")
        print(f"🔍 [DEBUG] Engine state after start: is_running={self.is_running}, simulation_time={self.simulation_time}")
    
    async def stop(self) -> None:
        """Stop the simulation."""
        if not self.is_running:
            print("⚠️  Simulation is not running")
            return
        
        print("⏹️  Stopping simulation engine...")
        
        # Stop main loop if running
        if self.main_task and not self.main_task.done():
            self.main_task.cancel()
            try:
                await self.main_task
            except asyncio.CancelledError:
                pass
        
        # Fire stop event
        await self.event_system.emit(EventType.SIMULATION_STOP, {
            "timestamp": time.time(),
            "total_frames": self.state.frame_count,
            "total_time": self.state.simulation_time
        })
        
        # Stop components
        await self.event_system.stop()
        
        if self.timing_manager:
            self.timing_manager.stop()
        
        # Stop state
        self.state.stop()
        
        # End performance monitoring and print report
        self.performance_benchmark.end_benchmark()
        self.performance_benchmark.print_performance_report()
        
        self.is_running = False
        print("✅ Simulation engine stopped")
    
    async def pause(self) -> None:
        """Pause the simulation."""
        if not self.is_running:
            print("⚠️  Cannot pause: simulation is not running")
            return
        
        print("⏸️  Pausing simulation...")
        
        # Pause state
        self.state.pause()
        
        # Pause timing manager
        if self.timing_manager:
            self.timing_manager.pause()
        
        # Fire pause event
        await self.event_system.emit(EventType.SIMULATION_PAUSE, {
            "timestamp": time.time(),
            "frames_at_pause": self.state.frame_count
        })
        
        print("✅ Simulation paused")
    
    async def resume(self) -> None:
        """Resume the simulation."""
        if not self.state.is_paused():
            print("⚠️  Cannot resume: simulation is not paused")
            return
        
        print("▶️  Resuming simulation...")
        
        # Resume state
        self.state.resume()
        
        # Resume timing manager
        if self.timing_manager:
            self.timing_manager.resume()
        
        # Fire resume event
        await self.event_system.emit(EventType.SIMULATION_RESUME, {
            "timestamp": time.time(),
            "frames_at_resume": self.state.frame_count
        })
        
        print("✅ Simulation resumed")
    
    async def run(self) -> None:
        """Run the main simulation loop."""
        if not self.is_running:
            print("⚠️  Cannot run: simulation is not started")
            return
        
        print("🔄 Starting main simulation loop...")
        
        # Start the main loop
        self.main_task = asyncio.create_task(self._main_loop())
        
        try:
            await self.main_task
        except asyncio.CancelledError:
            print("🛑 Main simulation loop cancelled")
        except Exception as e:
            print(f"❌ Error in main simulation loop: {e}")
            raise
    
    async def _main_loop(self) -> None:
        """Main simulation loop with enhanced timing and performance monitoring."""
        print("🎯 [DEBUG] Main simulation loop started")
        print(f"🔍 [DEBUG] Initial state: is_running={self.is_running}, simulation_time={self.simulation_time}")
        
        # Start performance monitoring
        self.performance_benchmark.start_benchmark()
        
        frame_count = 0
        while self.is_running:
            try:
                frame_start = time.time()
                frame_count += 1
                
                # Debug print every 60 frames (once per second at 60fps)
                if frame_count % 60 == 0:
                    print(f"🔄 [DEBUG] Main loop frame {frame_count}, simulation_time={self.simulation_time:.1f}s")
                
                # Wait for next frame first
                if self.timing_manager:
                    await self.timing_manager.wait_for_next_frame()
                    delta_time = self.timing_manager.delta_time
                else:
                    await asyncio.sleep(1.0 / 60.0)  # Fallback to 60 FPS
                    delta_time = 1.0 / 60.0
                
                # Skip update if paused
                if self.state.is_paused():
                    print("⏸️ [DEBUG] Simulation is paused, skipping update")
                    continue
                
                # Update simulation state
                self.state.update(delta_time)
                
                # Process events
                event_start = time.time()
                await self.event_system.process_events()
                event_time = time.time() - event_start
                
                # Update performance metrics
                self.state.performance.event_processing_time = event_time
                
                # Update component states (placeholder for future phases)
                component_start = time.time()
                await self._update_components(delta_time)
                component_time = time.time() - component_start
                
                # Update performance metrics
                self.state.performance.component_update_time = component_time
                
                # Record performance metrics
                frame_time = time.time() - frame_start
                event_stats = self.event_system.get_statistics()
                queue_size = event_stats.get("queue_sizes", {}).get("total", 0)
                
                self.performance_benchmark.record_metrics(
                    frame_time=frame_time,
                    fps=self.state.current_fps,
                    event_processing_time=event_time,
                    component_update_time=component_time,
                    event_queue_size=queue_size
                )
                
                # Fire frame update event every 60 frames (once per second at 60fps)
                if self.state.frame_count % 60 == 0:
                    await self.event_system.emit(EventType.FRAME_UPDATE, {
                        "frame_count": self.state.frame_count,
                        "simulation_time": self.state.simulation_time,
                        "delta_time": delta_time,
                        "fps": self.state.current_fps
                    })
                
                # Store last frame time
                self.last_frame_time = delta_time
                
                # Debug output (configurable) - every 5 seconds instead of 3
                if self.state.config_loaded:
                    debug_enabled = self.state.get_config("engine.debug_prints", True)
                    if debug_enabled and self.state.frame_count % 300 == 0:  # Every 5 seconds at 60fps
                        await self._print_debug_stats()
                
            except asyncio.CancelledError:
                print("🛑 [DEBUG] Main loop cancelled")
                break
            except Exception as e:
                print(f"❌ [DEBUG] Error in simulation loop: {e}")
                import traceback
                traceback.print_exc()
                # Continue running unless it's a critical error
                await asyncio.sleep(0.1)
        
        print("🏁 [DEBUG] Main simulation loop ended")
        print(f"🔍 [DEBUG] Final state: is_running={self.is_running}, simulation_time={self.simulation_time}")
    
    async def _update_components(self, delta_time: float) -> None:
        """Update all simulation components."""
        # Update simulation time
        self.simulation_time += delta_time
        
        # Update state
        self.state.update(delta_time)
        
        # Generate orders periodically (every 45 seconds)
        # Use a range check instead of exact match to avoid timing issues
        if self.simulation_time > 0 and len(self.orders) < 10:
            # Check if we've passed a 45-second interval
            current_interval = int(self.simulation_time // 45)
            if not hasattr(self, '_last_order_interval'):
                self._last_order_interval = -1
            
            if current_interval > self._last_order_interval:
                print(f"🔄 [DEBUG] Generating order at time {self.simulation_time:.1f}s (interval {current_interval})")
                self._generate_new_order()
                self._last_order_interval = current_interval
        
        # Debug: Print current state every 10 seconds
        if int(self.simulation_time) % 10 == 0 and self.simulation_time > 0:
            print(f"📊 [DEBUG] Simulation time: {self.simulation_time:.1f}s, Orders: {len(self.orders)}, Robot state: {self.robot.state}")
            print(f"📊 [DEBUG] Robot position: {self.robot.position}, Path index: {self.robot.path_index}")
        
        # Simple snake path movement with order collection
        if self.is_running and not self.state.is_paused():
            print(f"🤖 [DEBUG] Updating robot movement at time {self.simulation_time:.1f}s")
            self._update_robot_snake_movement(delta_time)
        else:
            if self.state.frame_count % 300 == 0:  # Every 10 seconds at 30fps
                print(f"[DEBUG] Robot movement skipped - is_running: {self.is_running}, is_paused: {self.state.is_paused()}")
    
    def _update_robot_snake_movement(self, delta_time: float) -> None:
        """Update robot movement with order processing."""
        if self.robot.state == RobotState.IDLE:
            if self.current_order_index < len(self.orders):
                print(f"📦 [DEBUG] Assigning order {self.current_order_index + 1}/{len(self.orders)} to robot at time {self.simulation_time:.1f}s")
                self._initialize_current_order()
                self.robot.state = RobotState.MOVING
                print(f"🤖 [DEBUG] Robot state changed to MOVING for order processing")
            else:
                print(f"✅ [DEBUG] All orders completed! Robot idle at time {self.simulation_time:.1f}s")
            return
        
        # Handle picking state with 3-second delay
        if self.robot.state == RobotState.PICKING:
            self._update_robot_picking(delta_time)
            return
        
        if self.robot.state == RobotState.RETURNING:
            print(f"🔄 [DEBUG] Robot is returning to starting point")
            # Use the same movement logic for returning
            
        if self.robot.state != RobotState.MOVING and self.robot.state != RobotState.RETURNING:
            print(f"🤖 [DEBUG] Robot state is {self.robot.state}, not MOVING or RETURNING")
            return
        
        # Check if path is complete
        if self.robot.path_index >= len(self.robot.current_path):
            if self.robot.state == RobotState.RETURNING:
                print(f"🏠 [DEBUG] Robot returned to starting point! Finalizing order completion")
                
                # Set completion timestamp NOW when robot actually returns
                if self.current_order_index > 0 and len(self.orders) >= self.current_order_index:
                    completed_order = self.orders[self.current_order_index - 1]  # Previous order that was completed
                    if completed_order.get('status') == 'completed' and not completed_order.get('return_completed'):
                        import time
                        from datetime import datetime, timezone, timedelta
                        
                        # Set the ACTUAL completion time when robot returns
                        completed_order['completed_time'] = time.time()
                        completed_order['completed_timestamp'] = time.time()  # Also set this for the frontend
                        completed_order['return_completed'] = True  # Mark as fully completed
                        
                        # Recalculate total time taken with actual completion time
                        if completed_order.get('created_time'):
                            total_time_seconds = completed_order['completed_time'] - completed_order['created_time']
                            completed_order['total_time_taken'] = f"{int(total_time_seconds // 60):02d}:{int(total_time_seconds % 60):02d}"
                        
                        # Emit order completion event with the correct timestamp
                        if hasattr(self, 'event_system') and self.event_system:
                            self.event_system.emit('order_completed', {
                                'order_id': completed_order.get('id', 'unknown'),
                                'completion_time': completed_order['completed_time'],
                                'timestamp': completed_order['completed_time'],
                                'total_distance': completed_order.get('total_distance', '0m'),
                                'efficiency_score': 1.0,
                                'robot_id': 'ROBOT_001'
                            })
                        
                        # Get current time in EST for logging
                        est_offset = timedelta(hours=-5)  # EST is UTC-5
                        est_tz = timezone(est_offset)
                        est_time = datetime.now(est_tz)
                        
                        print(f"✅ [DEBUG] Order {completed_order.get('id', 'unknown')} FULLY completed at {est_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        print(f"🕒 [DEBUG] Final completion time: {completed_order['total_time_taken']}")
                
                self.robot.state = RobotState.IDLE
                # Clear order-related robot data
                self.robot.current_order = None
                self.robot.target_items = []
                self.robot.collected_items = []
                return
            else:
                print(f"🎯 [DEBUG] Order path complete! Processing order completion at time {self.simulation_time:.1f}s")
                self._complete_current_order()
                return
        
        # Check for item collection at current position (only when not returning)
        if self.robot.state == RobotState.MOVING:
            self._check_order_completion()
        
        # Get current target
        target = self.robot.current_path[self.robot.path_index]
        if target is None:
            print(f"❌ [DEBUG] Target is None at path index {self.robot.path_index}, skipping")
            self.robot.path_index += 1
            return
        
        # Initialize movement if needed
        if not hasattr(self.robot, 'movement_start_time') or self.robot.movement_start_time is None:
            self.robot.movement_start_time = self.simulation_time
            self.robot.movement_target = target
            self.robot.movement_start_position = self.robot.position
            if self.robot.state == RobotState.RETURNING:
                print(f"🔄 [DEBUG] Robot continuing return to starting point: {self.robot.position} -> {target}")
            else:
                print(f"🚀 [DEBUG] Robot starting movement to {target} from {self.robot.position}")
                print(f"🗺️ [DEBUG] Path index {self.robot.path_index}/{len(self.robot.current_path)}")
                print(f"🎯 [DEBUG] Next few targets: {self.robot.current_path[self.robot.path_index:self.robot.path_index+3]}")
        
        # Calculate movement progress
        start_pos = self.robot.movement_start_position
        if start_pos is None:
            print(f"[DEBUG] start_pos is None, setting to current position {self.robot.position}")
            start_pos = self.robot.position
            self.robot.movement_start_position = start_pos
        
        distance = start_pos.distance_to(target)
        if distance == 0:
            print(f"[DEBUG] Distance is 0, robot already at target {target}, moving to next point")
            self.robot.position = target
            self.robot.path_index += 1
            self.robot.movement_start_time = None
            self.robot.movement_target = None
            self.robot.movement_start_position = None
            return
        
        # Increased movement speed for faster but still smooth movement
        movement_speed = 1.0  # 1.0 units per second (faster but still smooth)
        movement_duration = distance / movement_speed if movement_speed > 0 else 1.0
        elapsed_time = self.simulation_time - self.robot.movement_start_time
        progress = min(elapsed_time / movement_duration, 1.0)
        
        # Update robot position with smooth interpolation
        if progress < 1.0:
            new_aisle = start_pos.aisle + (target.aisle - start_pos.aisle) * progress
            new_rack = start_pos.rack + (target.rack - start_pos.rack) * progress
            self.robot.position = SmoothCoordinate(new_aisle, new_rack)
            
            # Check for orders to collect at current position (only when not returning)
            if self.robot.state == RobotState.MOVING:
                self._check_order_completion()
            
            # Log progress every 10 seconds
            if self.state.frame_count % 600 == 0:  # Every 10 seconds at 60fps
                state_text = "returning" if self.robot.state == RobotState.RETURNING else "collecting"
                print(f"[DEBUG] Robot {state_text}: {self.robot.position} -> {target} (progress: {progress:.2f})")
        else:
            # Arrived at target
            self.robot.position = target
            
            # Check for orders to collect at target position (only when not returning)
            if self.robot.state == RobotState.MOVING:
                self._check_order_completion()
            
            self.robot.path_index += 1
            self.robot.movement_start_time = None
            self.robot.movement_target = None
            self.robot.movement_start_position = None
            
            # Log arrival at every point for debugging
            if self.robot.state == RobotState.RETURNING:
                print(f"🔄 [DEBUG] Robot return progress: arrived at {target}, path index: {self.robot.path_index}/{len(self.robot.current_path)}")
            else:
                print(f"✅ [DEBUG] Robot arrived at {target}, path index: {self.robot.path_index}/{len(self.robot.current_path)}")
            
            # Show next target if available
            if self.robot.path_index < len(self.robot.current_path):
                next_target = self.robot.current_path[self.robot.path_index]
                print(f"➡️ [DEBUG] Next target: {next_target}")
    
    def _update_robot_picking(self, delta_time: float) -> None:
        """Update robot picking state with 3-second delay."""
        if self.robot.picking_start_time is None:
            # Something went wrong, reset to moving state
            print(f"❌ [DEBUG] Picking start time is None, resetting to MOVING state")
            self.robot.state = RobotState.MOVING
            return
        
        elapsed_time = self.simulation_time - self.robot.picking_start_time
        
        # Log picking progress every second
        if int(elapsed_time) != int(elapsed_time - delta_time):
            remaining_time = max(0, self.robot.picking_duration - elapsed_time)
            print(f"🏷️ [DEBUG] Robot picking item {self.robot.current_picking_item} - {remaining_time:.1f}s remaining")
        
        if elapsed_time >= self.robot.picking_duration:
            # Picking complete - collect the item
            if self.robot.current_picking_item:
                self.robot.collected_items.append(self.robot.current_picking_item)
                print(f"✅ [DEBUG] Robot successfully picked item {self.robot.current_picking_item}")
                print(f"📦 [DEBUG] Items collected: {len(self.robot.collected_items)}")
                
                # Clear picking state
                self.robot.picking_start_time = None
                self.robot.current_picking_item = None
                
                # Check if all items for current order are collected
                if self.current_order_index < len(self.orders):
                    order = self.orders[self.current_order_index]
                    items = order.get("items", [])
                    
                    if all(item in self.robot.collected_items for item in items):
                        print(f"🎯 [DEBUG] All items collected for order! Completing order...")
                        self._complete_current_order()
                        return
                
                # More items to collect, resume moving
                self.robot.state = RobotState.MOVING
                print(f"🚚 [DEBUG] Robot resuming movement to collect remaining items")
            else:
                print(f"❌ [DEBUG] No current picking item, resetting to MOVING state")
                self.robot.state = RobotState.MOVING
    
    def _initialize_snake_path(self) -> None:
        """Initialize a complete snake path through the warehouse."""
        print("🐍 Initializing snake path through warehouse...")
        
        # Create snake path through all aisles
        path = []
        current_pos = Coordinate(1, 1)  # Start at (1,1)
        path.append(current_pos)
        
        # Snake pattern: go through each aisle
        for aisle in range(1, 26):  # 25 aisles
            if aisle % 2 == 1:  # Odd aisle - left to right
                for rack in range(1, 21):  # 20 racks
                    if rack == 1 and aisle > 1:
                        # Move to next aisle (vertical movement)
                        path.append(Coordinate(aisle, 1))
                    elif rack > 1:
                        # Move right in current aisle
                        path.append(Coordinate(aisle, rack))
            else:  # Even aisle - right to left
                for rack in range(20, 0, -1):  # 20 to 1
                    if rack == 20 and aisle > 1:
                        # Move to next aisle (vertical movement)
                        path.append(Coordinate(aisle, 20))
                    elif rack < 20:
                        # Move left in current aisle
                        path.append(Coordinate(aisle, rack))
        
        # Return to start
        path.append(Coordinate(1, 1))
        
        # Convert to SmoothCoordinate for smooth movement
        smooth_path = [SmoothCoordinate(point.aisle, point.rack) for point in path]
        
        self.robot.current_path = smooth_path
        self.robot.path_index = 0
        self.robot.movement_start_time = None
        self.robot.movement_target = None
        self.robot.movement_start_position = None
        
        print(f"✅ Snake path initialized with {len(smooth_path)} points")
        print(f"📍 Path starts at {smooth_path[0]} and ends at {smooth_path[-1]}")

    def _generate_new_order(self) -> None:
        """Generate a new order and add it to the queue."""
        print(f"📦 [DEBUG] Generating new order at time {self.simulation_time:.1f}s...")
        try:
            # Create a simple order with 1-4 random items
            import random
            import time
            
            # Generate order ID
            order_id = f"ORDER_{int(self.simulation_time):03d}"
            
            # Select random number of items (1-4)
            num_items = random.randint(1, 4)
            
            # Generate random items with positions
            items = []
            for i in range(num_items):
                # Random aisle (1-25) and rack (1-20)
                aisle = random.randint(1, 25)
                rack = random.randint(1, 20)
                # Convert aisle number to letter (1=A, 2=B, etc.)
                aisle_letter = chr(64 + aisle)  # 65 is 'A', so 64 + 1 = 65 = 'A'
                item_id = f"ITEM_{aisle_letter}_{rack:02d}"
                items.append(item_id)
            
            # Use actual Unix timestamp for created_time
            current_timestamp = time.time()
            
            # Create order with location information
            order = {
                "id": order_id,
                "items": items,
                "timestamp": current_timestamp,  # Use actual timestamp
                "status": "pending",
                "location": f"{chr(64 + random.randint(1, 25))}{random.randint(1, 20)}",  # A1, B2, etc.
                "order_id": order_id,
                "created_time": current_timestamp,  # Use actual timestamp
                "time_received": current_timestamp,  # Add time_received field
                "priority": random.randint(1, 5)
            }
            
            # Add to orders list
            self.orders.append(order)
            
            print(f"✅ [DEBUG] Generated order {order_id} with {len(items)} items at location {order['location']}")
            print(f"📊 [DEBUG] Total orders now: {len(self.orders)}")
            print(f"📊 [DEBUG] All orders: {[o['id'] for o in self.orders]}")
            logger.info(f"Generated order {order_id} with {len(items)} items")
            
            # Start simulation if robot is idle and we have orders to process
            if self.robot.state == RobotState.IDLE and len(self.orders) > 0:
                print(f"🤖 [DEBUG] Robot is IDLE with {len(self.orders)} orders, robot ready for work!")
            else:
                print(f"📊 [DEBUG] Robot state is {self.robot.state}, orders: {len(self.orders)}")
            
        except Exception as e:
            print(f"❌ [DEBUG] Error generating order: {e}")
            logger.error(f"Error generating order: {e}")

    async def _print_debug_stats(self) -> None:
        """Print debug statistics."""
        config_manager = get_config()
        
        # Get event system statistics
        event_stats = self.event_system.get_statistics()
        total_queue_size = event_stats["queue_sizes"]["total"]
        
        # Get performance metrics
        performance_summary = self.performance_benchmark.get_performance_summary()
        avg_metrics = performance_summary.get("average_metrics", {})
        
        print(f"📊 Debug Stats - Frame: {self.state.frame_count}")
        print(f"   Time: {self.state.simulation_time:.1f}s | FPS: {self.state.current_fps:.1f}")
        print(f"   Speed: {self.state.simulation_speed}x | Target: {config_manager.timing.TARGET_FPS}")
        print(f"   Events: {total_queue_size} queued, {self.event_system.processed_events} processed")
        print(f"   Components: {len(self.state.get_active_components())} active")
        
        # Distance tracking information
        if self.current_order_index < len(self.orders):
            current_order_id = self.orders[self.current_order_index].get("id", f"order_{self.current_order_index}")
            current_distance = self.performance_metrics.get("current_order_distance", 0.0)
            total_distance = self.performance_metrics.get("total_distance", 0.0)
            print(f"   Distance: Current Order ({current_order_id}): {current_distance:.2f} | Total: {total_distance:.2f}")
        
        # Performance monitoring
        if avg_metrics:
            print(f"   Performance Grade: {performance_summary.get('performance_grade', 'N/A')}")
            print(f"   Avg Frame Time: {avg_metrics.get('avg_frame_time', 0)*1000:.2f}ms")
            print(f"   Memory Usage: {avg_metrics.get('avg_memory_usage_mb', 0):.1f}MB")
            print(f"   CPU Usage: {avg_metrics.get('avg_cpu_usage_percent', 0):.1f}%")
        
        # Performance warnings
        if self.last_frame_time > 0.033:  # > 30 FPS
            print(f"⚠️  Performance: Frame time {self.last_frame_time*1000:.1f}ms")
        
        if avg_metrics and avg_metrics.get('avg_memory_usage_mb', 0) > 200:
            print(f"⚠️  Memory: High usage {avg_metrics.get('avg_memory_usage_mb', 0):.1f}MB")
        
        if avg_metrics and avg_metrics.get('avg_cpu_usage_percent', 0) > 50:
            print(f"⚠️  CPU: High usage {avg_metrics.get('avg_cpu_usage_percent', 0):.1f}%")
    
    def _print_debug_stats_sync(self) -> None:
        """Synchronous version of debug stats for testing."""
        config_manager = get_config()
        
        # Get event system statistics
        event_stats = self.event_system.get_statistics()
        total_queue_size = event_stats["queue_sizes"]["total"]
        
        # Get performance metrics
        performance_summary = self.performance_benchmark.get_performance_summary()
        avg_metrics = performance_summary.get("average_metrics", {})
        
        print(f"📊 Debug Stats - Frame: {self.state.frame_count}")
        print(f"   Time: {self.state.simulation_time:.1f}s | FPS: {self.state.current_fps:.1f}")
        print(f"   Speed: {self.state.simulation_speed}x | Target: {config_manager.timing.TARGET_FPS}")
        print(f"   Events: {total_queue_size} queued, {self.event_system.processed_events} processed")
        print(f"   Components: {len(self.state.get_active_components())} active")
        
        # Distance tracking information
        if self.current_order_index < len(self.orders):
            current_order_id = self.orders[self.current_order_index].get("id", f"order_{self.current_order_index}")
            current_distance = self.performance_metrics.get("current_order_distance", 0.0)
            total_distance = self.performance_metrics.get("total_distance", 0.0)
            print(f"   Distance: Current Order ({current_order_id}): {current_distance:.2f} | Total: {total_distance:.2f}")
        
        # Performance monitoring
        if avg_metrics:
            print(f"   Performance Grade: {performance_summary.get('performance_grade', 'N/A')}")
            print(f"   Avg Frame Time: {avg_metrics.get('avg_frame_time', 0)*1000:.2f}ms")
            print(f"   Memory Usage: {avg_metrics.get('avg_memory_usage_mb', 0):.1f}MB")
            print(f"   CPU Usage: {avg_metrics.get('avg_cpu_usage_percent', 0):.1f}%")
        
        # Performance warnings
        if self.last_frame_time > 0.033:  # > 30 FPS
            print(f"⚠️  Performance: Frame time {self.last_frame_time*1000:.1f}ms")
        
        if avg_metrics and avg_metrics.get('avg_memory_usage_mb', 0) > 200:
            print(f"⚠️  Memory: High usage {avg_metrics.get('avg_memory_usage_mb', 0):.1f}MB")
        
        if avg_metrics and avg_metrics.get('avg_cpu_usage_percent', 0) > 50:
            print(f"⚠️  CPU: High usage {avg_metrics.get('avg_cpu_usage_percent', 0):.1f}%")
    
    def get_simulation_speed(self) -> float:
        """Get current simulation speed."""
        return self.state.get_simulation_speed()
    
    def set_simulation_speed(self, speed: float) -> None:
        """Set simulation speed."""
        self.state.set_simulation_speed(speed)
        
        # Update timing manager if available
        if self.timing_manager:
            self.timing_manager.set_simulation_speed(speed)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get comprehensive debug information."""
        config_manager = get_config()
        
        # Get event system statistics
        event_stats = self.event_system.get_statistics()
        
        # Get performance summary
        performance_summary = self.performance_benchmark.get_performance_summary()
        
        debug_info = {
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "performance": {
                "frame_time": self.last_frame_time,
                "event_processing_time": self.state.performance.event_processing_time,
                "component_update_time": self.state.performance.component_update_time,
                "current_fps": self.state.current_fps,
                "target_fps": config_manager.timing.TARGET_FPS,
                "performance_grade": performance_summary.get("performance_grade", "N/A"),
                "avg_frame_time": performance_summary.get("average_metrics", {}).get("avg_frame_time", 0),
                "avg_memory_usage_mb": performance_summary.get("average_metrics", {}).get("avg_memory_usage_mb", 0),
                "avg_cpu_usage_percent": performance_summary.get("average_metrics", {}).get("avg_cpu_usage_percent", 0)
            },
            "events": {
                "queue_sizes": event_stats["queue_sizes"],
                "processed_events": self.event_system.processed_events,
                "event_count": self.event_system.event_count,
                "failed_events": self.event_system.failed_events,
                "success_rate": event_stats["success_rate"]
            },
            "timing": {
                "target_fps": self.timing_manager.target_fps if self.timing_manager else 60,
                "simulation_speed": self.get_simulation_speed(),
                "is_paused": self.timing_manager.is_paused if self.timing_manager else False
            },
            "system": self.performance_optimizer.get_system_info()
        }
        
        # Add state debug info
        debug_info.update(self.state.get_debug_info())
        
        return debug_info
    
    async def reload_config(self) -> None:
        """Reload configuration and update engine."""
        print("🔄 Reloading configuration...")
        
        # Reload configuration
        config_manager = get_config()
        config_manager.reload_configuration()
        
        # Update state
        self.state.load_configuration()
        
        # Update timing manager
        if self.timing_manager:
            self.timing_manager.set_target_fps(config_manager.timing.TARGET_FPS)
            self.timing_manager.set_simulation_speed(config_manager.timing.SIMULATION_SPEED)
        
        # Update event system
        self.event_system.configure(
            max_queue_size=config_manager.get_value("engine", "event_queue_size", 1000),
            max_concurrent_events=config_manager.get_value("engine", "max_concurrent_events", 50)
        )

        # Update enhanced navigation components
        self.path_calculator.configure(config_manager.simulation["path_optimization"])
        self.trail_manager.configure(config_manager.simulation["trail_config"])
        self.aisle_timing.configure(config_manager.simulation["aisle_timing"])
        
        print("✅ Configuration reloaded")
    
    def add_order(self, order: Dict[str, Any]) -> None:
        """Add an order to the simulation."""
        self.orders.append(order)
        logger.info(f"Added order: {order.get('id', 'unknown')}")

    def start_simulation(self) -> None:
        """Start the simulation with simple snake path movement."""
        print("🚀 Starting simulation with snake path movement...")
        logger.info("Starting simulation with snake path movement")
        
        self.is_running = True
        self.robot.state = RobotState.IDLE  # Will start moving when idle
        
        # Initialize robot at starting position
        self.robot.position = SmoothCoordinate(1.0, 1.0)
        self.robot.collected_items = []
        self.robot.current_path = []
        self.robot.path_index = 0
        
        # Don't clear orders - let them be processed
        # Only reset current order index if this is the first initialization
        if not hasattr(self, '_simulation_initialized'):
            self.current_order_index = 0
            self._simulation_initialized = True
        
        print("✅ Simulation started - robot ready for order processing")
        print(f"📊 Current orders: {len(self.orders)}")
        print(f"📊 Current order index: {self.current_order_index}")
        
        # Generate initial order if none exist
        if len(self.orders) == 0:
            print("🔄 No orders exist, generating initial order...")
            self._generate_new_order()
        
        logger.info("Simulation started with order processing")

    def _initialize_current_order(self) -> None:
        """Initialize the current order with complete path planning using snake pattern."""
        if self.current_order_index >= len(self.orders):
            return
            
        order = self.orders[self.current_order_index]
        items = order.get("items", [])
        
        if not items:
            print(f"[DEBUG] No items in order {order.get('id', 'unknown')}")
            return
            
        # Convert item IDs to coordinates
        item_coordinates = []
        for item in items:
            try:
                parts = item.split('_')
                if len(parts) == 3:
                    # New format: ITEM_B_02 -> aisle=B (2), rack=02
                    aisle_letter = parts[1]
                    rack_str = parts[2]
                    
                    # Convert letter to number (A=1, B=2, etc.)
                    aisle = ord(aisle_letter) - 64  # 'A' is 65, so 65-64=1
                    rack = int(rack_str)
                    
                    item_coordinates.append(Coordinate(aisle, rack))
                else:
                    import random
                    aisle = random.randint(1, 25)
                    rack = random.randint(1, 20)
                    item_coordinates.append(Coordinate(aisle, rack))
            except (ValueError, IndexError):
                import random
                aisle = random.randint(1, 25)
                rack = random.randint(1, 20)
                item_coordinates.append(Coordinate(aisle, rack))
        
        if not item_coordinates:
            print(f"[DEBUG] No valid item positions for order {order.get('id', 'unknown')}")
            return
        
        # Calculate snake path for all items
        start_pos = self.robot.position.to_coordinate()
        print(f"🎯 [DEBUG] Calculating path from {start_pos} to items at {item_coordinates}")
        path_coordinates = self._calculate_snake_path(start_pos, item_coordinates)
        
        if not path_coordinates:
            print(f"❌ [DEBUG] Failed to calculate snake path for order {order.get('id', 'unknown')}")
            return
        
        print(f"🛣️ [DEBUG] Raw path coordinates: {path_coordinates}")
        
        # Convert all path points to SmoothCoordinate for movement
        smooth_path = [SmoothCoordinate(c.aisle, c.rack) for c in path_coordinates]
        print(f"✅ [DEBUG] Final smooth path for order {order.get('id', 'unknown')}: {smooth_path}")
        
        # Set up robot for path execution
        self.robot.current_path = smooth_path
        self.robot.path_index = 0
        self.robot.path_execution_state = "executing"
        
        # Set current order information on robot
        self.robot.current_order = order.get('id', f'ORDER_{self.current_order_index}')
        self.robot.target_items = items
        self.robot.collected_items = []
        
        print(f"📦 [DEBUG] Robot assigned order {self.robot.current_order} with {len(items)} items")
        print(f"📦 [DEBUG] Target items: {items}")
        print(f"📦 [DEBUG] Path has {len(smooth_path)} waypoints")
        self.robot.target_item = items[0] if items else None
        self.robot.state = RobotState.MOVING  # Force MOVING state
        print(f"[DEBUG] Robot state set to {self.robot.state}, path length: {len(smooth_path)}")
        
        # Update performance metrics
        self.performance_metrics["path_optimizations"] += 1
        self.performance_metrics["direction_changes"] += self._count_direction_changes(path_coordinates)
        print(f"[DEBUG] Initialized order {order.get('id', 'unknown')} with {len(path_coordinates)} path points")

    def _calculate_snake_path(self, start: Coordinate, targets: List[Coordinate]) -> List[Coordinate]:
        """Calculate warehouse-compliant path for multiple targets."""
        if not targets:
            return []
        
        path = [start]
        current = start
        
        # Sort targets by aisle for efficient warehouse traversal
        sorted_targets = self._sort_targets_by_aisle(targets)
        
        for target in sorted_targets:
            # Calculate warehouse-compliant path to this target
            warehouse_path = self._calculate_warehouse_path(current, target)
            if warehouse_path:
                # Add path points (excluding the start point to avoid duplication)
                path.extend(warehouse_path[1:])
                current = target
                print(f"🎯 [DEBUG] Path includes target: {target}")
        
        print(f"📍 [DEBUG] Final path: {path}")
        return path

    def _sort_targets_by_aisle(self, targets: List[Coordinate]) -> List[Coordinate]:
        """Sort targets by aisle for efficient warehouse traversal."""
        # Sort by aisle first, then by rack within each aisle
        return sorted(targets, key=lambda coord: (coord.aisle, coord.rack))

    def _calculate_warehouse_path(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Calculate path following STRICT warehouse boundary rules.
        
        MANDATORY Navigation Rules:
        1. VERTICAL MOVEMENT: ONLY allowed in rack A (1) and rack T (20)
        2. HORIZONTAL MOVEMENT: ONLY allowed within the SAME aisle
        3. To reach ANY target: MUST go to target aisle via boundary FIRST, then move horizontally
        4. NO horizontal movement across different aisles
        """
        print(f"🏭 [DEBUG] Calculating warehouse path from {start} to {target}")
        
        if start == target:
            print(f"✅ [DEBUG] Already at target, returning empty path")
            return []
        
        path = [start]
        current = start
        
        # RULE: If different aisles, MUST reach target aisle via boundary FIRST
        if current.aisle != target.aisle:
            print(f"🚛 [DEBUG] Cross-aisle movement required: aisle {current.aisle} → aisle {target.aisle}")
            
            # Step 1: Move to boundary rack (A=1 or T=20) in CURRENT aisle (if not already there)
            if current.rack != 1 and current.rack != 20:
                print(f"📍 [DEBUG] Must reach boundary rack in current aisle {current.aisle}")
                
                # Choose closest boundary rack
                distance_to_rack_1 = abs(current.rack - 1)
                distance_to_rack_20 = abs(current.rack - 20)
                
                if distance_to_rack_1 <= distance_to_rack_20:
                    boundary_rack = 1
                    print(f"🎯 [DEBUG] Moving to rack A (1) in aisle {current.aisle}")
                else:
                    boundary_rack = 20
                    print(f"🎯 [DEBUG] Moving to rack T (20) in aisle {current.aisle}")
                
                # Move horizontally to boundary rack within CURRENT aisle
                boundary_point = Coordinate(current.aisle, boundary_rack)
                horizontal_path = self._move_horizontally_in_aisle(current, boundary_point)
                path.extend(horizontal_path[1:])  # Skip duplicate start
                current = boundary_point
                print(f"📍 [DEBUG] Reached boundary in current aisle: {current}")
            
            # Step 2: Move vertically along boundary rack to TARGET aisle
            print(f"🛣️ [DEBUG] Moving vertically in boundary rack {current.rack}: aisle {current.aisle} → aisle {target.aisle}")
            target_aisle_boundary = Coordinate(target.aisle, current.rack)
            vertical_path = self._move_vertically_in_boundary_rack(current, target_aisle_boundary)
            path.extend(vertical_path[1:])  # Skip duplicate start
            current = target_aisle_boundary
            print(f"📍 [DEBUG] Reached target aisle via boundary: {current}")
        
        # Step 3: Move horizontally within TARGET aisle to final target (if needed)
        if current.rack != target.rack:
            print(f"🎯 [DEBUG] Moving horizontally in target aisle {target.aisle}: rack {current.rack} → rack {target.rack}")
            horizontal_path = self._move_horizontally_in_aisle(current, target)
            path.extend(horizontal_path[1:])  # Skip duplicate start
            print(f"📍 [DEBUG] Reached final target: {target}")
        
        print(f"✅ [DEBUG] Complete warehouse path: {path}")
        return path
    
    def _move_horizontally_in_aisle(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Move horizontally within the same aisle from start rack to target rack.
        This is allowed movement within any aisle level.
        
        Args:
            start: Starting position (must be same aisle as target)
            target: Target position (must be same aisle as start)
            
        Returns:
            List of coordinates for horizontal movement within aisle
        """
        if start.aisle != target.aisle:
            raise ValueError(f"Cannot move within aisle: different aisles {start.aisle} vs {target.aisle}")
        
        if start.rack == target.rack:
            return [start]
        
        path = [start]
        current_rack = start.rack
        step = 1 if target.rack > start.rack else -1
        
        print(f"🏃 [DEBUG] Horizontal movement in aisle {start.aisle}: rack {start.rack} → {target.rack}")
        while current_rack != target.rack:
            current_rack += step
            path.append(Coordinate(start.aisle, current_rack))
        
        return path
    
    def _move_vertically_in_boundary_rack(self, start: Coordinate, target: Coordinate) -> List[Coordinate]:
        """
        Move vertically within the boundary rack to reach the target aisle.
        
        Args:
            start: Starting position (must be within the boundary rack)
            target: Target aisle number
            
        Returns:
            List of coordinates for vertical movement within boundary rack
        """
        if start.rack != 1 and start.rack != 20:
            raise ValueError(f"Must start from boundary rack (A or T), got rack {start.rack}")
        
        if start.aisle == target.aisle:
            return [start]
        
        path = [start]
        current_aisle = start.aisle
        step = 1 if target.aisle > start.aisle else -1
        
        print(f"🚃 [DEBUG] Vertical movement in boundary rack {start.rack}: aisle {start.aisle} → {target.aisle}")
        while current_aisle != target.aisle:
            current_aisle += step
            path.append(Coordinate(current_aisle, start.rack))
        
        return path

    def _count_direction_changes(self, path: List[Coordinate]) -> int:
        """Count direction changes in the path."""
        if len(path) < 3:
            return 0
        
        changes = 0
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_pos = path[i + 1]
            
            # Check if direction changed
            if self._is_direction_change(prev, curr, next_pos):
                changes += 1
        
        return changes

    def _is_direction_change(self, prev: Coordinate, curr: Coordinate, next_pos: Coordinate) -> bool:
        """Check if there's a direction change between three consecutive points."""
        # Calculate direction vectors
        dir1 = (curr.aisle - prev.aisle, curr.rack - prev.rack)
        dir2 = (next_pos.aisle - curr.aisle, next_pos.rack - curr.rack)
        
        # Check if directions are different
        return dir1 != dir2

    def _update_robot_movement(self, delta_time: float) -> None:
        """Update robot movement with enhanced navigation logic and smooth interpolation."""
        if self.robot.state != RobotState.MOVING:
            if self.state.frame_count % 60 == 0:  # Every second at 60fps
                print(f"[DEBUG] Robot not MOVING, state is {self.robot.state}")
            return
        if self.robot.path_index >= len(self.robot.current_path):
            print(f"[DEBUG] Path complete, calling _handle_path_completion")
            self._handle_path_completion()
            return
        target = self.robot.current_path[self.robot.path_index]
        if target is None:
            print(f"[DEBUG] Target is None at path index {self.robot.path_index}, skipping")
            self.robot.path_index += 1
            return
        if not hasattr(self.robot, 'movement_start_time') or self.robot.movement_start_time is None:
            self.robot.movement_start_time = self.simulation_time
            self.robot.movement_target = target
            self.robot.movement_start_position = self.robot.position
            print(f"[DEBUG] Robot starting movement to {target} from {self.robot.position}")
        start_pos = self.robot.movement_start_position
        if start_pos is None:
            print(f"[DEBUG] start_pos is None, setting to current position {self.robot.position}")
            start_pos = self.robot.position
            self.robot.movement_start_position = start_pos
        distance = start_pos.distance_to(target)
        if distance == 0:
            print(f"[DEBUG] Distance is 0, robot already at target {target}, moving to next point")
            self.robot.position = target
            self.robot.path_index += 1
            self.robot.movement_start_time = None
            self.robot.movement_target = None
            self.robot.movement_start_position = None
            return
        movement_speed = 0.1  # units per second (much slower for smooth movement)
        movement_duration = distance / movement_speed if movement_speed > 0 else 1.0
        elapsed_time = self.simulation_time - self.robot.movement_start_time
        progress = min(elapsed_time / movement_duration, 1.0)
        # Only print movement debug every 30 frames (once per second at 30fps)
        if self.state.frame_count % 30 == 0:
            print(f"[DEBUG] Movement: distance={distance:.2f}, duration={movement_duration:.2f}, elapsed={elapsed_time:.2f}, progress={progress:.2f}")
        if progress < 1.0:
            new_aisle = start_pos.aisle + (target.aisle - start_pos.aisle) * progress
            new_rack = start_pos.rack + (target.rack - start_pos.rack) * progress
            self.robot.position = SmoothCoordinate(new_aisle, new_rack)
        else:
            self.robot.position = target
            self.robot.path_index += 1
            self.robot.movement_start_time = None
            self.robot.movement_target = None
            self.robot.movement_start_position = None
            # Only print arrival debug every 10 path points
            if self.robot.path_index % 10 == 0:
                print(f"[DEBUG] Robot arrived at {target}, path index: {self.robot.path_index}/{len(self.robot.current_path)}")

    def _interpolate_position(self, start: SmoothCoordinate, end: Coordinate, progress: float) -> SmoothCoordinate:
        """Interpolate between two positions using linear interpolation with floating-point precision."""
        aisle = start.aisle + (end.aisle - start.aisle) * progress
        rack = start.rack + (end.rack - start.rack) * progress
        return SmoothCoordinate(aisle, rack)  # Keep as float for smooth movement

    def _determine_movement_type(self, start: Coordinate, end: Coordinate) -> str:
        """Determine the type of movement between two points."""
        if start.aisle == end.aisle:
            return "vertical"
        elif start.rack == end.rack:
            return "horizontal"
        else:
            return "diagonal"

    def _calculate_direction(self, start: Coordinate, end: Coordinate) -> str:
        """Calculate the direction from start to end."""
        if start.aisle < end.aisle:
            return "east"
        elif start.aisle > end.aisle:
            return "west"
        elif start.rack < end.rack:
            return "south"
        elif start.rack > end.rack:
            return "north"
        else:
            return "none"

    def _handle_direction_change(self, new_direction: str) -> None:
        """Handle robot direction change with cooldown."""
        current_time = self.simulation_time
        old_direction = self.robot.current_direction
        
        # Check if enough time has passed since last direction change
        time_since_last = current_time - self.robot.last_direction_change if self.robot.last_direction_change else float('inf')
        cooldown_remaining = self.robot.direction_change_cooldown - time_since_last
        cooldown_respected = time_since_last > self.robot.direction_change_cooldown
        
        logger.debug(f"Direction change check: current_time={current_time}, last_change={self.robot.last_direction_change}, cooldown={self.robot.direction_change_cooldown}, time_since_last={time_since_last}, cooldown_remaining={cooldown_remaining}")
        
        if (self.robot.last_direction_change is None or cooldown_respected):
            
            self.robot.current_direction = new_direction
            self.robot.last_direction_change = current_time
            self.performance_metrics["direction_changes"] += 1
            
            # Record direction change for performance monitoring
            self.path_performance_monitor.record_direction_change(
                old_direction or "none", new_direction, cooldown_respected
            )
            
            # Emit direction change event
            self.event_system.emit(EventType.DIRECTION_CHANGED, {
                "robot": self.robot,
                "new_direction": new_direction,
                "timestamp": current_time
            })
            
            logger.debug(f"Robot direction changed to {new_direction}")
        else:
            # Direction change blocked by cooldown
            logger.debug(f"Direction change to {new_direction} blocked by cooldown")

    def _handle_path_completion(self) -> None:
        """Handle completion of a path segment."""
        if self.current_order_index >= len(self.orders):
            return
            
        order = self.orders[self.current_order_index]
        items = order.get("items", [])
        
        # Check if we're at the starting point (1,1)
        current_pos = self.robot.position.to_coordinate()
        if current_pos.aisle == 1 and current_pos.rack == 1:
            # Robot has returned to starting point
            if self.robot.state == RobotState.RETURNING:
                # Robot was returning, now check for next order
                self._check_for_next_order()
                return
        
        # Check if we're at an item location
        current_item = None
        
        for item in items:
            try:
                parts = item.split('_')
                if len(parts) == 3:
                    # New format: ITEM_B_02 -> aisle=B (2), rack=02
                    aisle_letter = parts[1]
                    rack_str = parts[2]
                    
                    # Convert letter to number (A=1, B=2, etc.)
                    item_aisle = ord(aisle_letter) - 64  # 'A' is 65, so 65-64=1
                    item_rack = int(rack_str)
                    
                    if current_pos.aisle == item_aisle and current_pos.rack == item_rack:
                        current_item = item
                        break
            except (ValueError, IndexError):
                continue
        
        if current_item and current_item not in self.robot.collected_items:
            # Collect the item
            self.robot.state = RobotState.COLLECTING
            self.robot.collected_items.append(current_item)
            self.performance_metrics["items_collected"] += 1
            
            logger.info(f"Robot collected item {current_item} at position {current_pos}")
            
            # Check if all items for this order are collected
            if len(self.robot.collected_items) >= len(items):
                # All items collected, complete the order
                self._complete_current_order()
            else:
                # More items to collect, continue to next item
                self.robot.state = RobotState.MOVING
                # Recalculate path for remaining items
                remaining_items = [item for item in items if item not in self.robot.collected_items]
                if remaining_items:
                    self._initialize_current_order()
        else:
            # No item to collect at this position, move to next path point
            if self.robot.path_index < len(self.robot.current_path):
                self.robot.path_index += 1
            else:
                # Path completed but no items collected, something went wrong
                logger.warning("Path completed but no items collected")
                self._complete_current_order()

    def _return_to_start(self) -> None:
        """Return robot to starting point after completing an order."""
        # Set robot state to returning
        self.robot.state = RobotState.RETURNING
        
        # Calculate path back to starting point (base location)
        base_location = Coordinate(1, 1)  # Starting point
        return_path = self._calculate_path_to_target(self.robot.position.to_coordinate(), base_location)
        
        if return_path:
            # Convert path coordinates to SmoothCoordinate for movement
            smooth_return_path = [SmoothCoordinate(c.aisle, c.rack) for c in return_path]
            
            self.robot.current_path = smooth_return_path
            self.robot.path_index = 0
            self.robot.target_item = None  # No target item when returning
            self.robot.state = RobotState.MOVING  # Start moving back
            
            logger.info(f"Robot returning to starting point")
        else:
            logger.error(f"Failed to calculate return path to starting point")
            # If return path fails, check for next order
            self._check_for_next_order()

    def _move_to_next_item(self) -> None:
        """Move robot to the next item in the current order."""
        if self.current_order_index >= len(self.orders):
            return
            
        order = self.orders[self.current_order_index]
        items = order.get("items", [])
        
        # Find next uncollected item
        collected_items = set(self.robot.collected_items)
        remaining_items = [item for item in items if item not in collected_items]
        
        if remaining_items:
            # Get position of next item
            next_item = remaining_items[0]
            next_pos = self.warehouse_layout.get_item_position(next_item)
            
            if next_pos:
                # Calculate path to next item
                complete_path = self.path_calculator.calculate_complete_path_for_items(
                    self.robot.position, [next_pos]
                )
                
                if complete_path.segments:
                    # Extract path coordinates from segments
                    path_coordinates = []
                    for segment in complete_path.segments:
                        path_coordinates.append(segment.start)
                    if complete_path.segments:
                        path_coordinates.append(complete_path.segments[-1].end)
                    
                    self.robot.current_path = path_coordinates
                    self.robot.path_index = 0
                    self.robot.target_item = next_item
                    self.robot.state = RobotState.MOVING
                    
                    logger.info(f"Moving to next item: {next_item}")
                else:
                    logger.error(f"Failed to calculate path to item: {next_item}")
            else:
                logger.error(f"Item position not found: {next_item}")
        else:
            # All items collected, return to starting point
            self._return_to_start()

    def _complete_current_order(self) -> None:
        """Complete current order and return to starting point."""
        print(f"🎯 [DEBUG] Completing current order at time {self.simulation_time:.1f}s")
        
        # Mark order as completed
        if self.current_order_index < len(self.orders):
            order = self.orders[self.current_order_index]
            
            # Only set basic completion status if order is not already completed
            if order.get('status') != 'completed':
                order['status'] = 'completed'
                
                # DON'T set completion time here - will be set when robot returns
                # Just add item details for display
                order['items_picked'] = self.robot.collected_items.copy()
                order['robot_id'] = 'ROBOT_001'
                order['total_distance'] = f"{self.performance_metrics.get('current_order_distance', 0):.1f}m"
                
                print(f"📦 [DEBUG] Order {order.get('id', 'unknown')} marked as completed (awaiting robot return)")
            else:
                print(f"📝 [DEBUG] Order {order.get('id', 'unknown')} already completed, skipping status update")
        
        # Move to next order
        self.current_order_index += 1
        
        # Return robot to starting point before next order
        starting_point = SmoothCoordinate(1.0, 1.0)  # A1 position
        if self.robot.position.aisle != 1.0 or self.robot.position.rack != 1.0:
            print(f"🔄 [DEBUG] Robot returning to starting point from {self.robot.position}")
            return_path = self._calculate_warehouse_path(
                self.robot.position.to_coordinate(), 
                Coordinate(1, 1)
            )
            
            # Convert to smooth coordinates
            smooth_return_path = [SmoothCoordinate(c.aisle, c.rack) for c in return_path]
            
            # Set robot to return path
            self.robot.current_path = smooth_return_path
            self.robot.path_index = 0
            self.robot.movement_start_time = None
            self.robot.movement_target = None
            self.robot.movement_start_position = None
            self.robot.state = RobotState.RETURNING
            
            print(f"🔄 [DEBUG] Robot set to return to starting point with {len(smooth_return_path)} waypoints")
        else:
            print(f"✅ [DEBUG] Robot already at starting point, ready for next order")
            self.robot.state = RobotState.IDLE
            
            # Clear order-related robot data
            self.robot.current_order = None
            self.robot.target_items = []
            self.robot.collected_items = []

    def _complete_simulation(self) -> None:
        """Complete the simulation."""
        self.is_running = False
        self.robot.state = RobotState.COMPLETED
        
        # Emit simulation completion event
        self.event_system.emit(EventType.SIMULATION_COMPLETED, {
            "robot": self.robot,
            "performance_metrics": self.performance_metrics,
            "total_time": self.simulation_time
        })
        
        logger.info("Simulation completed successfully")

    def _check_for_next_order(self) -> None:
        """Check if there are more orders to process."""
        if self.current_order_index < len(self.orders):
            # Initialize next order
            self._initialize_current_order()
        else:
            # All orders completed, set robot to idle
            self.robot.state = RobotState.IDLE
            logger.info("All orders completed, robot returning to idle state")

    def _check_order_completion(self) -> None:
        """Check if robot reached an item location and start picking process."""
        if self.current_order_index >= len(self.orders):
            return
            
        order = self.orders[self.current_order_index]
        items = order.get("items", [])
        
        # Check if robot is at any item location and start picking
        robot_pos = self.robot.position
        # Convert aisle number to letter (1=A, 2=B, etc.)
        aisle_letter = chr(64 + int(robot_pos.aisle))  # 65 is 'A', so 64 + 1 = 65 = 'A'
        current_location = f"ITEM_{aisle_letter}_{int(robot_pos.rack):02d}"
        
        for item in items:
            if item not in self.robot.collected_items and item == current_location:
                # Robot reached an item location - start picking process
                print(f"🎯 [DEBUG] Robot reached item {item} at position {robot_pos}")
                print(f"🏷️ [DEBUG] Starting picking process (3 seconds)...")
                
                # Set robot to picking state
                self.robot.state = RobotState.PICKING
                self.robot.picking_start_time = self.simulation_time
                self.robot.current_picking_item = item
                
                # Stop movement temporarily
                self.robot.movement_start_time = None
                self.robot.movement_target = None
                self.robot.movement_start_position = None
                
                print(f"⏱️ [DEBUG] Robot state changed to PICKING for item {item}")
                break

    def update(self, delta_time: float) -> None:
        """Update the simulation engine (called by unified app)."""
        # Update simulation time
        self.simulation_time += delta_time
        
        # Update state
        self.state.update(delta_time)
        
        # Simple snake path movement - no orders for now
        if self.is_running and not self.state.is_paused():
            self._update_robot_snake_movement(delta_time)
        else:
            if self.state.frame_count % 300 == 0:  # Every 10 seconds at 30fps
                print(f"[DEBUG] Robot movement skipped - is_running: {self.is_running}, is_paused: {self.state.is_paused()}")
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state."""
        return {
            "robot": self.robot,
            "orders": self.orders,
            "current_order_index": self.current_order_index,
            "simulation_time": self.simulation_time,
            "is_running": self.is_running,
            "performance_metrics": self.performance_metrics,
            "trail_points": self.trail_manager.get_trail_points(),
            "current_order_distance": self.performance_metrics.get("current_order_distance", 0.0),
            "order_distances": self.performance_metrics.get("order_distances", {})
        }

    def pause_simulation(self) -> None:
        """Pause the simulation."""
        if self.is_running:
            self.is_running = False
            self.robot.path_execution_state = "paused"
            logger.info("Simulation paused")

    def resume_simulation(self) -> None:
        """Resume the simulation."""
        if not self.is_running and self.robot.state != RobotState.COMPLETED:
            self.is_running = True
            self.robot.path_execution_state = "executing"
            logger.info("Simulation resumed")

    def stop_simulation(self) -> None:
        """Stop the simulation."""
        self.is_running = False
        self.robot.state = RobotState.IDLE
        self.robot.path_execution_state = "ready"
        logger.info("Simulation stopped")

    def reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        self.robot = Robot(SmoothCoordinate(1.0, 1.0))
        self.current_order_index = 0
        self.simulation_time = 0.0
        self.is_running = False
        self.performance_metrics = {
            "total_distance": 0.0,
            "items_collected": 0,
            "orders_completed": 0,
            "direction_changes": 0,
            "path_optimizations": 0
        }
        self.trail_manager.clear_trail()
        logger.info("Simulation reset to initial state")
    
    async def shutdown(self) -> None:
        """Perform clean shutdown."""
        print("🧹 Shutting down simulation engine...")
        
        # Stop if running
        if self.is_running:
            await self.stop()
        
        # Cleanup components
        if self.timing_manager:
            self.timing_manager.cleanup()
        
        # Reset state
        self.state.reset()
        
        # Clear event system
        self.event_system.reset()
        
        self.is_initialized = False
        print("✅ Simulation engine shutdown complete") 