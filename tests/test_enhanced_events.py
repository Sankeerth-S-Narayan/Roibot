"""
Test suite for the enhanced event system.
Tests priority handling, filtering, middleware, validation, and logging.
"""

import asyncio
import unittest
from datetime import datetime
from core.events import (
    EventSystem, EventType, EventPriority, Event, EventFilter, 
    EventMiddleware, EventLogger, EventValidator
)


class TestEnhancedEventSystem(unittest.TestCase):
    """Test the enhanced event system functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.event_system = EventSystem()
        self.received_events = []
        
    def tearDown(self):
        """Clean up after tests."""
        self.event_system.reset()
        self.received_events.clear()
    
    def test_event_priorities(self):
        """Test event priority assignment."""
        # Test default priority assignment
        high_priority_event = Event(EventType.SIMULATION_STOP, datetime.now(), {})
        self.assertEqual(high_priority_event.priority, EventPriority.HIGH)
        
        medium_priority_event = Event(EventType.SIMULATION_START, datetime.now(), {})
        self.assertEqual(medium_priority_event.priority, EventPriority.MEDIUM)
        
        low_priority_event = Event(EventType.SIMULATION_TICK, datetime.now(), {})
        self.assertEqual(low_priority_event.priority, EventPriority.LOW)
        
        # Test manual priority assignment
        custom_event = Event(EventType.SIMULATION_TICK, datetime.now(), {}, priority=EventPriority.HIGH)
        self.assertEqual(custom_event.priority, EventPriority.HIGH)
        
        print("✅ Event priorities test passed")
    
    def test_event_id_generation(self):
        """Test event ID generation."""
        event = Event(EventType.SIMULATION_START, datetime.now(), {})
        self.assertIsNotNone(event.event_id)
        self.assertIn("simulation_start", event.event_id)
        
        # Test custom event ID
        custom_event = Event(EventType.SIMULATION_START, datetime.now(), {}, event_id="custom_id")
        self.assertEqual(custom_event.event_id, "custom_id")
        
        print("✅ Event ID generation test passed")
    
    def test_event_to_dict(self):
        """Test event serialization."""
        event = Event(EventType.SIMULATION_START, datetime.now(), {"test": "data"}, source="test")
        event_dict = event.to_dict()
        
        self.assertIn("event_id", event_dict)
        self.assertIn("event_type", event_dict)
        self.assertIn("timestamp", event_dict)
        self.assertIn("priority", event_dict)
        self.assertIn("source", event_dict)
        self.assertIn("data", event_dict)
        self.assertIn("processed", event_dict)
        
        print("✅ Event serialization test passed")
    
    def test_event_filter(self):
        """Test event filtering."""
        # Test event type filter
        type_filter = EventFilter(event_types=[EventType.SIMULATION_START])
        
        start_event = Event(EventType.SIMULATION_START, datetime.now(), {})
        stop_event = Event(EventType.SIMULATION_STOP, datetime.now(), {})
        
        self.assertTrue(type_filter.matches(start_event))
        self.assertFalse(type_filter.matches(stop_event))
        
        # Test source filter
        source_filter = EventFilter(sources=["test_source"])
        
        test_event = Event(EventType.SIMULATION_START, datetime.now(), {}, source="test_source")
        other_event = Event(EventType.SIMULATION_START, datetime.now(), {}, source="other_source")
        
        self.assertTrue(source_filter.matches(test_event))
        self.assertFalse(source_filter.matches(other_event))
        
        # Test priority filter
        priority_filter = EventFilter(priorities=[EventPriority.HIGH])
        
        high_event = Event(EventType.SIMULATION_STOP, datetime.now(), {})  # Auto-high priority
        low_event = Event(EventType.SIMULATION_TICK, datetime.now(), {})   # Auto-low priority
        
        self.assertTrue(priority_filter.matches(high_event))
        self.assertFalse(priority_filter.matches(low_event))
        
        print("✅ Event filtering test passed")
    
    def test_event_middleware(self):
        """Test event middleware functionality."""
        class TestMiddleware(EventMiddleware):
            def __init__(self):
                super().__init__("TestMiddleware")
                self.processed_events = []
            
            async def before_process(self, event):
                self.processed_events.append(event.event_type)
                return event
        
        middleware = TestMiddleware()
        self.event_system.add_middleware(middleware)
        
        # Check middleware was added
        self.assertEqual(len(self.event_system.middleware), 3)  # Logger, Validator, TestMiddleware
        
        # Remove middleware
        self.event_system.remove_middleware("TestMiddleware")
        self.assertEqual(len(self.event_system.middleware), 2)  # Logger, Validator
        
        print("✅ Event middleware test passed")
    
    def test_event_logger(self):
        """Test event logging functionality."""
        logger = EventLogger(max_history=10)
        
        # Create test events
        event1 = Event(EventType.SIMULATION_START, datetime.now(), {})
        event2 = Event(EventType.SIMULATION_STOP, datetime.now(), {})
        
        # Process events through logger
        asyncio.run(logger.before_process(event1))
        asyncio.run(logger.before_process(event2))
        
        # Test history retrieval
        history = logger.get_recent_events(5)
        self.assertEqual(len(history), 2)
        
        # Test events by type
        start_events = logger.get_events_by_type(EventType.SIMULATION_START)
        self.assertEqual(len(start_events), 1)
        
        print("✅ Event logging test passed")
    
    def test_event_validator(self):
        """Test event validation functionality."""
        validator = EventValidator()
        
        # Add validation rule
        def validate_simulation_start(data):
            return "system" in data
        
        validator.add_validation_rule(EventType.SIMULATION_START, validate_simulation_start)
        
        # Test valid event
        valid_event = Event(EventType.SIMULATION_START, datetime.now(), {"system": "test"})
        result = asyncio.run(validator.before_process(valid_event))
        self.assertIsNotNone(result)
        
        # Test invalid event
        invalid_event = Event(EventType.SIMULATION_START, datetime.now(), {"invalid": "data"})
        result = asyncio.run(validator.before_process(invalid_event))
        self.assertIsNone(result)
        
        print("✅ Event validation test passed")
    
    async def test_priority_queue_processing(self):
        """Test priority-based event processing."""
        # Set up event handler
        def event_handler(event):
            self.received_events.append(event)
        
        # Subscribe to all event types
        self.event_system.subscribe(EventType.SIMULATION_START, event_handler)
        self.event_system.subscribe(EventType.SIMULATION_STOP, event_handler)
        self.event_system.subscribe(EventType.SIMULATION_TICK, event_handler)
        
        # Start event system (this will emit an auto SIMULATION_START event)
        await self.event_system.start()
        
        # Process the auto-emitted start event first
        await self.event_system.process_events()
        
        # Clear received events to focus on our test events
        self.received_events.clear()
        
        # Emit events in reverse priority order
        await self.event_system.emit(EventType.SIMULATION_TICK, {}, "test")      # LOW
        await self.event_system.emit(EventType.SIMULATION_START, {}, "test")     # MEDIUM
        await self.event_system.emit(EventType.SIMULATION_STOP, {}, "test")      # HIGH
        
        # Process events
        await self.event_system.process_events()
        
        # Verify high priority events were processed first
        self.assertEqual(len(self.received_events), 3)
        self.assertEqual(self.received_events[0].event_type, EventType.SIMULATION_STOP)   # HIGH
        self.assertEqual(self.received_events[1].event_type, EventType.SIMULATION_START)  # MEDIUM
        self.assertEqual(self.received_events[2].event_type, EventType.SIMULATION_TICK)   # LOW
        
        await self.event_system.stop()
        
        print("✅ Priority queue processing test passed")
    
    async def test_filtered_event_handling(self):
        """Test filtered event handling."""
        # Set up filtered handler
        def filtered_handler(event):
            self.received_events.append(event)
        
        # Create filter for specific source
        source_filter = EventFilter(sources=["test_source"])
        
        # Subscribe with filter
        self.event_system.subscribe(EventType.SIMULATION_START, filtered_handler, source_filter)
        
        # Start event system (this will emit an auto SIMULATION_START event from "EventSystem" source)
        await self.event_system.start()
        
        # Process the auto-emitted start event first (it will be filtered out)
        await self.event_system.process_events()
        
        # Clear received events to focus on our test events
        self.received_events.clear()
        
        # Emit events from different sources
        await self.event_system.emit(EventType.SIMULATION_START, {}, "test_source")
        await self.event_system.emit(EventType.SIMULATION_START, {}, "other_source")
        
        # Process events
        await self.event_system.process_events()
        
        # Verify only filtered events were processed
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].source, "test_source")
        
        await self.event_system.stop()
        
        print("✅ Filtered event handling test passed")
    
    def test_statistics_tracking(self):
        """Test enhanced statistics tracking."""
        stats = self.event_system.get_statistics()
        
        # Check all required statistics are present
        self.assertIn("is_running", stats)
        self.assertIn("queue_sizes", stats)
        self.assertIn("max_queue_size", stats)
        self.assertIn("event_count", stats)
        self.assertIn("processed_events", stats)
        self.assertIn("failed_events", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("handler_count", stats)
        self.assertIn("filtered_handler_count", stats)
        self.assertIn("middleware_count", stats)
        self.assertIn("performance", stats)
        
        # Check queue sizes structure
        self.assertIn("high_priority", stats["queue_sizes"])
        self.assertIn("medium_priority", stats["queue_sizes"])
        self.assertIn("low_priority", stats["queue_sizes"])
        self.assertIn("total", stats["queue_sizes"])
        
        # Check performance metrics
        self.assertIn("avg_processing_time", stats["performance"])
        self.assertIn("recent_processing_times", stats["performance"])
        
        print("✅ Statistics tracking test passed")
    
    async def test_event_system_integration(self):
        """Test complete event system integration."""
        # Set up handler
        def integration_handler(event):
            self.received_events.append(event)
        
        # Subscribe to events
        self.event_system.subscribe(EventType.SIMULATION_START, integration_handler)
        
        # Add custom validation rule
        def validate_start_event(data):
            return "valid" in data
        
        self.event_system.add_validation_rule(EventType.SIMULATION_START, validate_start_event)
        
        # Start event system (this will emit an auto SIMULATION_START event that will be blocked by validation)
        await self.event_system.start()
        
        # Process the auto-emitted start event first (it will be blocked by validation)
        await self.event_system.process_events()
        
        # Clear received events to focus on our test events
        self.received_events.clear()
        
        # Emit valid event
        await self.event_system.emit(EventType.SIMULATION_START, {"valid": True}, "test")
        
        # Emit invalid event
        await self.event_system.emit(EventType.SIMULATION_START, {"invalid": True}, "test")
        
        # Process events
        await self.event_system.process_events()
        
        # Verify only valid event was processed
        self.assertEqual(len(self.received_events), 1)
        self.assertTrue(self.received_events[0].data["valid"])
        
        # Check statistics (3 events total: auto-start + valid + invalid, but only 1 processed)
        stats = self.event_system.get_statistics()
        self.assertEqual(stats["event_count"], 3)
        self.assertEqual(stats["processed_events"], 1)
        
        # Check event history (all events get logged before validation, so we have 3 events in history)
        history = self.event_system.get_event_history()
        # We expect 3 events in history: auto-start + valid + invalid (all logged before validation)
        self.assertEqual(len(history), 3)
        
        await self.event_system.stop()
        
        print("✅ Event system integration test passed")


async def run_async_tests():
    """Run async tests."""
    test_instance = TestEnhancedEventSystem()
    
    try:
        # Test 1: Priority queue processing
        test_instance.setUp()
        await test_instance.test_priority_queue_processing()
        test_instance.tearDown()
        
        # Test 2: Filtered event handling
        test_instance.setUp()
        await test_instance.test_filtered_event_handling()
        test_instance.tearDown()
        
        # Test 3: Event system integration
        test_instance.setUp()
        await test_instance.test_event_system_integration()
        test_instance.tearDown()
        
        print("✅ All async tests passed")
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        raise


def run_sync_tests():
    """Run synchronous tests."""
    test_instance = TestEnhancedEventSystem()
    
    try:
        test_instance.setUp()
        test_instance.test_event_priorities()
        test_instance.setUp()
        test_instance.test_event_id_generation()
        test_instance.setUp()
        test_instance.test_event_to_dict()
        test_instance.setUp()
        test_instance.test_event_filter()
        test_instance.setUp()
        test_instance.test_event_middleware()
        test_instance.setUp()
        test_instance.test_event_logger()
        test_instance.setUp()
        test_instance.test_event_validator()
        test_instance.setUp()
        test_instance.test_statistics_tracking()
        print("✅ All sync tests passed")
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
        raise
    finally:
        test_instance.tearDown()


if __name__ == "__main__":
    print("🧪 Testing Enhanced Event System...")
    print("=" * 50)
    
    # Run synchronous tests
    print("\n📋 Running synchronous tests...")
    run_sync_tests()
    
    # Run asynchronous tests
    print("\n📋 Running asynchronous tests...")
    asyncio.run(run_async_tests())
    
    print("\n🎉 All Enhanced Event System tests completed successfully!") 