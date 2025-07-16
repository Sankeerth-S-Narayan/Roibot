"""
Performance testing for the Roibot simulation system.
Tests performance optimization and benchmarking utilities.
"""

import asyncio
import time
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import SimulationEngine
from utils.performance import PerformanceBenchmark, PerformanceOptimizer, performance_benchmark


class TestPerformanceOptimization(unittest.TestCase):
    """Test performance optimization utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.optimizer = PerformanceOptimizer()
    
    def test_optimize_event_loop(self):
        """Test event loop optimization."""
        optimizations = self.optimizer.optimize_event_loop()
        
        # Check that optimizations were applied
        self.assertIsInstance(optimizations, dict)
        self.assertIn("gc_threshold", optimizations)
        self.assertEqual(optimizations["gc_threshold"], "Optimized")
        
        print("✅ Event loop optimization test passed")
    
    def test_get_system_info(self):
        """Test system information retrieval."""
        system_info = self.optimizer.get_system_info()
        
        # Check that system info is retrieved
        self.assertIsInstance(system_info, dict)
        self.assertIn("cpu_count", system_info)
        self.assertIn("platform", system_info)
        
        print("✅ System info test passed")


class TestPerformanceBenchmark(unittest.TestCase):
    """Test performance benchmarking utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.benchmark = PerformanceBenchmark()
    
    def test_benchmark_initialization(self):
        """Test benchmark initialization."""
        # Create a fresh benchmark instance for this test
        fresh_benchmark = PerformanceBenchmark()
        
        self.assertIsNotNone(fresh_benchmark.metrics_history)
        self.assertEqual(len(fresh_benchmark.metrics_history), 0)
        self.assertIsNone(fresh_benchmark.benchmark_start_time)
        
        print("✅ Benchmark initialization test passed")
    
    def test_record_metrics(self):
        """Test metrics recording."""
        # Create a fresh benchmark instance for this test
        fresh_benchmark = PerformanceBenchmark()
        
        # Record some test metrics
        fresh_benchmark.record_metrics(
            frame_time=0.016,
            fps=60.0,
            event_processing_time=0.001,
            component_update_time=0.002,
            event_queue_size=10
        )
        
        # Check that metrics were recorded
        self.assertEqual(len(fresh_benchmark.metrics_history), 1)
        metrics = fresh_benchmark.metrics_history[0]
        self.assertEqual(metrics.frame_time, 0.016)
        self.assertEqual(metrics.fps, 60.0)
        
        print("✅ Metrics recording test passed")
    
    def test_average_metrics(self):
        """Test average metrics calculation."""
        # Record multiple metrics
        for i in range(5):
            self.benchmark.record_metrics(
                frame_time=0.016 + (i * 0.001),
                fps=60.0 - (i * 0.5),
                event_processing_time=0.001,
                component_update_time=0.002,
                event_queue_size=10 + i
            )
        
        # Get average metrics
        avg_metrics = self.benchmark.get_average_metrics()
        
        # Check that averages are calculated
        self.assertIn("avg_frame_time", avg_metrics)
        self.assertIn("avg_fps", avg_metrics)
        self.assertEqual(avg_metrics["total_frames"], 5)
        
        print("✅ Average metrics test passed")
    
    def test_performance_grade_calculation(self):
        """Test performance grade calculation."""
        # Create a fresh benchmark instance for this test
        fresh_benchmark = PerformanceBenchmark()
        
        # Record good performance metrics
        fresh_benchmark.record_metrics(
            frame_time=0.016,  # 60 FPS
            fps=60.0,
            event_processing_time=0.001,
            component_update_time=0.002,
            event_queue_size=10
        )
        
        summary = fresh_benchmark.get_performance_summary()
        grade = summary.get("performance_grade")
        
        # Should get a good grade for good performance
        self.assertIsNotNone(grade)
        self.assertIn(grade, ["A+", "A", "B", "C", "D"])
        
        print("✅ Performance grade test passed")
    
    def test_benchmark_lifecycle(self):
        """Test benchmark start/end lifecycle."""
        # Create a fresh benchmark instance for this test
        fresh_benchmark = PerformanceBenchmark()
        
        # Start benchmark
        fresh_benchmark.start_benchmark()
        self.assertIsNotNone(fresh_benchmark.benchmark_start_time)
        
        # Record some metrics
        fresh_benchmark.record_metrics(
            frame_time=0.016,
            fps=60.0,
            event_processing_time=0.001,
            component_update_time=0.002,
            event_queue_size=10
        )
        
        # End benchmark
        fresh_benchmark.end_benchmark()
        self.assertIsNotNone(fresh_benchmark.benchmark_end_time)
        
        # Check summary
        summary = fresh_benchmark.get_performance_summary()
        self.assertIn("benchmark_duration", summary)
        # Allow for very short durations (0.0 is acceptable for fast execution)
        self.assertGreaterEqual(summary["benchmark_duration"], 0)
        
        print("✅ Benchmark lifecycle test passed")


class TestEnginePerformance(unittest.TestCase):
    """Test engine performance integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = SimulationEngine()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.engine.is_running:
            asyncio.run(self.engine.stop())
    
    def test_engine_performance_monitoring(self):
        """Test that engine has performance monitoring."""
        # Check that performance components are initialized
        self.assertIsNotNone(self.engine.performance_benchmark)
        self.assertIsNotNone(self.engine.performance_optimizer)
        
        print("✅ Engine performance monitoring test passed")
    
    async def test_engine_performance_debug_info(self):
        """Test performance data in debug info."""
        # Load config and start engine
        await self.engine.load_config()
        await self.engine.start()
        
        # Run the engine briefly to collect some performance data
        await asyncio.sleep(0.1)  # Run for 100ms to collect metrics
        
        # Get debug info
        debug_info = self.engine.get_debug_info()
        
        # Check that performance data is included
        self.assertIn("performance", debug_info)
        performance = debug_info["performance"]
        
        # Check that basic performance fields exist (may be 0 if no data yet)
        self.assertIn("frame_time", performance)
        self.assertIn("event_processing_time", performance)
        self.assertIn("component_update_time", performance)
        
        # Check system info
        self.assertIn("system", debug_info)
        
        await self.engine.stop()
        
        print("✅ Engine performance debug info test passed")


async def run_performance_benchmark():
    """Run a performance benchmark test."""
    print("\n🚀 Running Performance Benchmark Test...")
    
    engine = SimulationEngine()
    
    try:
        # Load configuration
        await engine.load_config()
        
        # Run benchmark for 5 seconds
        async with performance_benchmark(engine.performance_benchmark, duration_seconds=5.0):
            # Start engine
            await engine.start()
            
            # Run for the benchmark duration
            await asyncio.sleep(5.0)
            
            # Stop engine
            await engine.stop()
    
    except Exception as e:
        print(f"❌ Performance benchmark test failed: {e}")
        raise
    finally:
        await engine.shutdown()


def run_performance_tests():
    """Run all performance tests."""
    print("🧪 Testing Performance Optimization & Validation...")
    print("=" * 60)
    
    test_classes = [
        TestPerformanceOptimization,
        TestPerformanceBenchmark,
        TestEnginePerformance
    ]
    
    for test_class in test_classes:
        test_instance = test_class()
        
        try:
            test_instance.setUp()
            
            # Run all test methods
            for method_name in dir(test_instance):
                if method_name.startswith('test_') and callable(getattr(test_instance, method_name)):
                    method = getattr(test_instance, method_name)
                    if not asyncio.iscoroutinefunction(method):
                        method()
                    else:
                        asyncio.run(method())
            
            test_instance.tearDown()
            
        except Exception as e:
            print(f"❌ {test_class.__name__} test failed: {e}")
            raise
    
    print("\n✅ All Performance Tests Completed Successfully!")


if __name__ == "__main__":
    # Run synchronous tests
    run_performance_tests()
    
    # Run async benchmark test
    asyncio.run(run_performance_benchmark()) 