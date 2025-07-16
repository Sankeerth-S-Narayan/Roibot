"""
Event system for event-driven architecture and component communication.
Provides event dispatcher, handlers, and basic event types with advanced features.
"""

import asyncio
from typing import Dict, List, Callable, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
from collections import deque


class EventType(Enum):
    """Basic event types for the simulation."""
    
    # Simulation control events
    SIMULATION_START = "simulation_start"
    SIMULATION_STOP = "simulation_stop"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_RESUME = "simulation_resume"
    SIMULATION_TICK = "simulation_tick"
    
    # Configuration events
    CONFIG_LOADED = "config_loaded"
    CONFIG_CHANGED = "config_changed"
    
    # Performance events
    FRAME_UPDATE = "frame_update"
    PERFORMANCE_WARNING = "performance_warning"
    
    # Component events (for future phases)
    ROBOT_MOVED = "robot_moved"
    ROBOT_STATE_CHANGED = "robot_state_changed"
    ORDER_CREATED = "order_created"
    ORDER_ASSIGNED = "order_assigned"
    ORDER_COMPLETED = "order_completed"
    INVENTORY_UPDATED = "inventory_updated"
    
    # Enhanced navigation events
    DIRECTION_CHANGED = "direction_changed"
    ITEM_COLLECTED = "item_collected"
    SIMULATION_COMPLETED = "simulation_completed"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"


class EventPriority(Enum):
    """Event priority levels."""
    
    HIGH = 1     # Critical events (system errors, stop commands)
    MEDIUM = 2   # Important events (start/pause/resume, configuration changes)
    LOW = 3      # Normal events (tick, frame updates, component updates)


@dataclass
class Event:
    """Event data structure with enhanced features."""
    
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: Optional[str] = None
    priority: EventPriority = EventPriority.LOW
    event_id: Optional[str] = None
    processed: bool = False
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Generate event ID if not provided
        if self.event_id is None:
            self.event_id = f"{self.event_type.value}_{self.timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Set priority based on event type if not specified
        if self.priority == EventPriority.LOW:
            self.priority = self._get_default_priority()
    
    def _get_default_priority(self) -> EventPriority:
        """Get default priority based on event type."""
        high_priority_events = [
            EventType.SIMULATION_STOP,
            EventType.SYSTEM_ERROR,
            EventType.PERFORMANCE_WARNING
        ]
        
        medium_priority_events = [
            EventType.SIMULATION_START,
            EventType.SIMULATION_PAUSE,
            EventType.SIMULATION_RESUME,
            EventType.CONFIG_LOADED,
            EventType.CONFIG_CHANGED
        ]
        
        if self.event_type in high_priority_events:
            return EventPriority.HIGH
        elif self.event_type in medium_priority_events:
            return EventPriority.MEDIUM
        else:
            return EventPriority.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for logging."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.name,
            "source": self.source,
            "data": self.data,
            "processed": self.processed
        }


@dataclass
class EventFilter:
    """Event filter for selective event processing."""
    
    event_types: Optional[List[EventType]] = None
    sources: Optional[List[str]] = None
    priorities: Optional[List[EventPriority]] = None
    custom_filter: Optional[Callable[[Event], bool]] = None
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        # Check event type filter
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check source filter (handle None sources properly)
        if self.sources:
            if event.source is None and None not in self.sources:
                return False
            elif event.source is not None and event.source not in self.sources:
                return False
        
        # Check priority filter
        if self.priorities and event.priority not in self.priorities:
            return False
        
        # Check custom filter
        if self.custom_filter and not self.custom_filter(event):
            return False
        
        return True


class EventMiddleware:
    """Base class for event middleware."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def before_process(self, event: Event) -> Union[Event, None]:
        """
        Process event before it's dispatched to handlers.
        
        Args:
            event: Event to process
            
        Returns:
            Modified event or None to block event
        """
        return event
    
    async def after_process(self, event: Event, result: Any) -> Any:
        """
        Process event after it's been dispatched.
        
        Args:
            event: Event that was processed
            result: Result from handler
            
        Returns:
            Modified result
        """
        return result


class EventLogger(EventMiddleware):
    """Event logging middleware."""
    
    def __init__(self, max_history: int = 1000):
        super().__init__("EventLogger")
        self.max_history = max_history
        self.event_history: deque = deque(maxlen=max_history)
    
    async def before_process(self, event: Event) -> Union[Event, None]:
        """Log event before processing."""
        self.event_history.append(event.to_dict())
        
        # Print important events
        if event.priority in [EventPriority.HIGH, EventPriority.MEDIUM]:
            print(f"📋 Event Log: {event.event_type.value} ({event.priority.name}) from {event.source}")
        
        return event
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events from history."""
        return list(self.event_history)[-limit:]
    
    def get_events_by_type(self, event_type: EventType) -> List[Dict[str, Any]]:
        """Get events by type from history."""
        return [event for event in self.event_history if event["event_type"] == event_type.value]


class EventValidator(EventMiddleware):
    """Event validation middleware."""
    
    def __init__(self):
        super().__init__("EventValidator")
        self.validation_rules: Dict[EventType, Callable[[Dict[str, Any]], bool]] = {}
    
    def add_validation_rule(self, event_type: EventType, validator: Callable[[Dict[str, Any]], bool]) -> None:
        """Add validation rule for event type."""
        self.validation_rules[event_type] = validator
        print(f"📝 Validation rule added for {event_type.value}")
    
    async def before_process(self, event: Event) -> Union[Event, None]:
        """Validate event before processing."""
        # Check if validation rule exists
        if event.event_type in self.validation_rules:
            validator = self.validation_rules[event.event_type]
            
            try:
                if not validator(event.data):
                    print(f"⚠️  Event validation failed for {event.event_type.value}: {event.data}")
                    return None  # Block invalid event
            except Exception as e:
                print(f"❌ Error validating event {event.event_type.value}: {e}")
                return None
        
        return event


class EventSystem:
    """
    Enhanced event dispatcher and handler system.
    Manages event subscriptions, dispatching, and advanced features.
    """
    
    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize event system.
        
        Args:
            max_queue_size: Maximum event queue size
        """
        self.max_queue_size = max_queue_size
        
        # Separate queues for different priorities
        self.high_priority_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size // 4)
        self.medium_priority_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size // 2)
        self.low_priority_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        # Event handlers
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.filtered_handlers: Dict[EventType, List[tuple]] = {}  # (handler, filter)
        
        # System state
        self.is_running = False
        self.event_count = 0
        self.processed_events = 0
        self.failed_events = 0
        
        # Middleware
        self.middleware: List[EventMiddleware] = []
        
        # Built-in middleware
        self.logger = EventLogger()
        self.validator = EventValidator()
        self.add_middleware(self.logger)
        self.add_middleware(self.validator)
        
        # Performance tracking
        self.processing_times: deque = deque(maxlen=100)
        
        print(f"🔌 Enhanced EventSystem initialized (max queue: {max_queue_size})")
    
    def add_middleware(self, middleware: EventMiddleware) -> None:
        """Add event middleware."""
        self.middleware.append(middleware)
        print(f"🔧 Middleware added: {middleware.name}")
    
    def remove_middleware(self, middleware_name: str) -> None:
        """Remove event middleware by name."""
        self.middleware = [m for m in self.middleware if m.name != middleware_name]
        print(f"🗑️  Middleware removed: {middleware_name}")
    
    def subscribe(self, event_type: EventType, handler: Callable, event_filter: Optional[EventFilter] = None) -> None:
        """
        Subscribe to an event type with optional filtering.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Handler function to call when event occurs
            event_filter: Optional filter for selective processing
        """
        # Initialize lists only if they don't exist
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        if event_type not in self.filtered_handlers:
            self.filtered_handlers[event_type] = []
        
        if event_filter:
            self.filtered_handlers[event_type].append((handler, event_filter))
            print(f"📝 Subscribed to {event_type.value} event with filter")
        else:
            self.event_handlers[event_type].append(handler)
            print(f"📝 Subscribed to {event_type.value} event")
    
    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        removed = False
        
        # Remove from regular handlers
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                removed = True
            except ValueError:
                pass
        
        # Remove from filtered handlers
        if event_type in self.filtered_handlers:
            self.filtered_handlers[event_type] = [
                (h, f) for h, f in self.filtered_handlers[event_type] if h != handler
            ]
            if not removed:
                removed = True
        
        if removed:
            print(f"🗑️  Unsubscribed from {event_type.value} event")
        else:
            print(f"⚠️  Handler not found for {event_type.value} event")
    
    async def emit(self, event_type: EventType, data: Dict[str, Any] = None, source: str = None, 
                   priority: EventPriority = None) -> None:
        """
        Emit an event with enhanced features.
        
        Args:
            event_type: Type of event to emit
            data: Event data dictionary
            source: Source component name
            priority: Event priority (auto-determined if not specified)
        """
        if data is None:
            data = {}
        
        event = Event(
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source,
            priority=priority or EventPriority.LOW
        )
        
        # Set priority from event type if not specified
        if priority is None:
            event.priority = event._get_default_priority()
        
        try:
            # Select appropriate queue based on priority
            if event.priority == EventPriority.HIGH:
                await self.high_priority_queue.put(event)
            elif event.priority == EventPriority.MEDIUM:
                await self.medium_priority_queue.put(event)
            else:
                await self.low_priority_queue.put(event)
            
            self.event_count += 1
            
            # Debug print for important events
            if event.priority in [EventPriority.HIGH, EventPriority.MEDIUM]:
                print(f"📡 Event emitted: {event_type.value} ({event.priority.name}) from {source}")
            
        except asyncio.QueueFull:
            print(f"⚠️  Event queue full, dropping event: {event_type.value} ({event.priority.name})")
            self.failed_events += 1
    
    async def process_events(self) -> None:
        """Process events from queues with priority ordering."""
        if not self.is_running:
            return
        
        # Process up to max_concurrent_events per frame
        max_concurrent = getattr(self, 'max_concurrent_events', 50)
        processed_count = 0
        
        # Process high priority events first
        processed_count += await self._process_priority_queue(
            self.high_priority_queue, max_concurrent - processed_count
        )
        
        # Process medium priority events
        if processed_count < max_concurrent:
            processed_count += await self._process_priority_queue(
                self.medium_priority_queue, max_concurrent - processed_count
            )
        
        # Process low priority events
        if processed_count < max_concurrent:
            processed_count += await self._process_priority_queue(
                self.low_priority_queue, max_concurrent - processed_count
            )
    
    async def _process_priority_queue(self, queue: asyncio.Queue, max_events: int) -> int:
        """Process events from a specific priority queue."""
        processed_count = 0
        
        while not queue.empty() and processed_count < max_events:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.001)
                
                # Apply middleware before processing
                for middleware in self.middleware:
                    event = await middleware.before_process(event)
                    if event is None:
                        break  # Event blocked by middleware
                
                if event is not None:
                    await self._dispatch_event(event)
                    processed_count += 1
                    self.processed_events += 1
                
            except asyncio.TimeoutError:
                break
            except Exception as e:
                print(f"❌ Error processing event: {e}")
                self.failed_events += 1
        
        return processed_count
    
    async def _dispatch_event(self, event: Event) -> None:
        """
        Dispatch event to registered handlers with filtering.
        
        Args:
            event: Event to dispatch
        """
        start_time = asyncio.get_event_loop().time()
        
        # Get regular handlers
        handlers = self.event_handlers.get(event.event_type, [])
        
        # Get filtered handlers
        filtered_handlers = self.filtered_handlers.get(event.event_type, [])
        
        # Dispatch to regular handlers
        for handler in handlers:
            try:
                await self._call_handler(handler, event)
            except Exception as e:
                print(f"❌ Error in event handler for {event.event_type.value}: {e}")
                self.failed_events += 1
        
        # Dispatch to filtered handlers
        for handler, event_filter in filtered_handlers:
            try:
                if event_filter.matches(event):
                    await self._call_handler(handler, event)
            except Exception as e:
                print(f"❌ Error in filtered handler for {event.event_type.value}: {e}")
                self.failed_events += 1
        
        # Apply middleware after processing
        for middleware in self.middleware:
            try:
                await middleware.after_process(event, None)
            except Exception as e:
                print(f"❌ Error in middleware {middleware.name}: {e}")
        
        # Track processing time
        processing_time = asyncio.get_event_loop().time() - start_time
        self.processing_times.append(processing_time)
        
        # Mark event as processed
        event.processed = True
    
    async def _call_handler(self, handler: Callable, event: Event) -> None:
        """Call event handler (sync or async)."""
        if asyncio.iscoroutinefunction(handler):
            await handler(event)
        else:
            handler(event)
    
    def configure(self, max_queue_size: int = None, max_concurrent_events: int = None) -> None:
        """
        Configure event system parameters.
        
        Args:
            max_queue_size: Maximum queue size
            max_concurrent_events: Maximum concurrent events per frame
        """
        if max_queue_size:
            self.max_queue_size = max_queue_size
        if max_concurrent_events:
            self.max_concurrent_events = max_concurrent_events
        else:
            self.max_concurrent_events = 50
        
        print(f"⚙️  EventSystem configured: queue={self.max_queue_size}, concurrent={self.max_concurrent_events}")
    
    def add_validation_rule(self, event_type: EventType, validator: Callable[[Dict[str, Any]], bool]) -> None:
        """Add validation rule for event type."""
        self.validator.add_validation_rule(event_type, validator)
    
    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent event history."""
        return self.logger.get_recent_events(limit)
    
    def get_events_by_type(self, event_type: EventType) -> List[Dict[str, Any]]:
        """Get events by type from history."""
        return self.logger.get_events_by_type(event_type)
    
    async def start(self) -> None:
        """Start the event system."""
        self.is_running = True
        print("🚀 Enhanced EventSystem started")
        
        # Emit system start event
        await self.emit(EventType.SIMULATION_START, {"system": "event_system"}, "EventSystem")
    
    async def stop(self) -> None:
        """Stop the event system."""
        self.is_running = False
        
        # Process remaining events from all queues
        await self._drain_all_queues()
        
        print("⏹️  Enhanced EventSystem stopped")
        print(f"📊 Events processed: {self.processed_events}/{self.event_count} (failed: {self.failed_events})")
    
    async def _drain_all_queues(self) -> None:
        """Drain all event queues."""
        for queue in [self.high_priority_queue, self.medium_priority_queue, self.low_priority_queue]:
            while not queue.empty():
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=0.1)
                    await self._dispatch_event(event)
                except asyncio.TimeoutError:
                    break
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get enhanced event system statistics.
        
        Returns:
            Statistics dictionary
        """
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            "is_running": self.is_running,
            "queue_sizes": {
                "high_priority": self.high_priority_queue.qsize(),
                "medium_priority": self.medium_priority_queue.qsize(),
                "low_priority": self.low_priority_queue.qsize(),
                "total": (self.high_priority_queue.qsize() + 
                         self.medium_priority_queue.qsize() + 
                         self.low_priority_queue.qsize())
            },
            "max_queue_size": self.max_queue_size,
            "event_count": self.event_count,
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "success_rate": (self.processed_events / self.event_count * 100) if self.event_count > 0 else 0,
            "handler_count": sum(len(handlers) for handlers in self.event_handlers.values()),
            "filtered_handler_count": sum(len(handlers) for handlers in self.filtered_handlers.values()),
            "middleware_count": len(self.middleware),
            "performance": {
                "avg_processing_time": avg_processing_time,
                "recent_processing_times": list(self.processing_times)[-10:]
            }
        }
    
    def reset(self) -> None:
        """Reset event system state."""
        # Clear all queues
        for queue in [self.high_priority_queue, self.medium_priority_queue, self.low_priority_queue]:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        # Clear all event handlers
        self.event_handlers.clear()
        self.filtered_handlers.clear()
        
        # Reset counters
        self.event_count = 0
        self.processed_events = 0
        self.failed_events = 0
        self.is_running = False
        
        # Clear processing times
        self.processing_times.clear()
        
        # Reset middleware
        self.logger.event_history.clear()
        
        print("🔄 Enhanced EventSystem reset") 