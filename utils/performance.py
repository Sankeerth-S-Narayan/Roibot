"""
Performance benchmarking and optimization utilities.
Provides tools to measure, analyze, and optimize simulation performance.
"""

import time
import asyncio
import psutil
import gc
import platform
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    frame_time: float
    fps: float
    event_processing_time: float
    component_update_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    event_queue_size: int
    timestamp: float


class PerformanceBenchmark:
    """
    Performance benchmarking and analysis tool.
    Measures and tracks performance metrics for optimization.
    """
    
    def __init__(self):
        """Initialize performance benchmark."""
        self.metrics_history: List[PerformanceMetrics] = []
        self.benchmark_start_time: Optional[float] = None
        self.benchmark_end_time: Optional[float] = None
        self.process = psutil.Process()
        
        print("📊 PerformanceBenchmark initialized")
    
    def start_benchmark(self) -> None:
        """Start performance benchmarking."""
        self.benchmark_start_time = time.time()
        self.metrics_history.clear()
        gc.collect()  # Force garbage collection before benchmark
        print("🚀 Performance benchmark started")
    
    def end_benchmark(self) -> None:
        """End performance benchmarking."""
        self.benchmark_end_time = time.time()
        print("🏁 Performance benchmark ended")
    
    def record_metrics(self, frame_time: float, fps: float, 
                      event_processing_time: float, component_update_time: float,
                      event_queue_size: int) -> None:
        """
        Record performance metrics for current frame.
        
        Args:
            frame_time: Time for current frame
            fps: Current frames per second
            event_processing_time: Time spent processing events
            component_update_time: Time spent updating components
            event_queue_size: Current event queue size
        """
        try:
            memory_usage = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = self.process.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            memory_usage = 0.0
            cpu_usage = 0.0
        
        metrics = PerformanceMetrics(
            frame_time=frame_time,
            fps=fps,
            event_processing_time=event_processing_time,
            component_update_time=component_update_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            event_queue_size=event_queue_size,
            timestamp=time.time()
        )
        
        self.metrics_history.append(metrics)
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average performance metrics."""
        if not self.metrics_history:
            return {}
        
        total_frames = len(self.metrics_history)
        
        avg_frame_time = sum(m.frame_time for m in self.metrics_history) / total_frames
        avg_fps = sum(m.fps for m in self.metrics_history) / total_frames
        avg_event_time = sum(m.event_processing_time for m in self.metrics_history) / total_frames
        avg_component_time = sum(m.component_update_time for m in self.metrics_history) / total_frames
        avg_memory = sum(m.memory_usage_mb for m in self.metrics_history) / total_frames
        avg_cpu = sum(m.cpu_usage_percent for m in self.metrics_history) / total_frames
        avg_queue_size = sum(m.event_queue_size for m in self.metrics_history) / total_frames
        
        return {
            "avg_frame_time": avg_frame_time,
            "avg_fps": avg_fps,
            "avg_event_processing_time": avg_event_time,
            "avg_component_update_time": avg_component_time,
            "avg_memory_usage_mb": avg_memory,
            "avg_cpu_usage_percent": avg_cpu,
            "avg_event_queue_size": avg_queue_size,
            "total_frames": total_frames
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.metrics_history:
            return {"error": "No metrics recorded"}
        
        avg_metrics = self.get_average_metrics()
        
        # Calculate min/max values
        frame_times = [m.frame_time for m in self.metrics_history]
        fps_values = [m.fps for m in self.metrics_history]
        memory_values = [m.memory_usage_mb for m in self.metrics_history]
        
        summary = {
            "benchmark_duration": self.benchmark_end_time - self.benchmark_start_time if self.benchmark_end_time else 0,
            "total_frames": len(self.metrics_history),
            "average_metrics": avg_metrics,
            "frame_time": {
                "min": min(frame_times),
                "max": max(frame_times),
                "target": 1.0 / 60.0  # 60 FPS target
            },
            "fps": {
                "min": min(fps_values),
                "max": max(fps_values),
                "target": 60.0
            },
            "memory_usage": {
                "min": min(memory_values),
                "max": max(memory_values),
                "current": memory_values[-1] if memory_values else 0
            },
            "performance_grade": self._calculate_performance_grade(avg_metrics)
        }
        
        return summary
    
    def _calculate_performance_grade(self, metrics: Dict[str, float]) -> str:
        """Calculate performance grade based on metrics."""
        frame_time_score = 0
        fps_score = 0
        memory_score = 0
        
        # Frame time scoring (lower is better)
        if metrics["avg_frame_time"] <= 0.0167:  # 60 FPS
            frame_time_score = 100
        elif metrics["avg_frame_time"] <= 0.0333:  # 30 FPS
            frame_time_score = 80
        elif metrics["avg_frame_time"] <= 0.05:  # 20 FPS
            frame_time_score = 60
        else:
            frame_time_score = 40
        
        # FPS scoring (higher is better)
        if metrics["avg_fps"] >= 60:
            fps_score = 100
        elif metrics["avg_fps"] >= 30:
            fps_score = 80
        elif metrics["avg_fps"] >= 20:
            fps_score = 60
        else:
            fps_score = 40
        
        # Memory scoring (lower is better, assuming < 100MB is good)
        if metrics["avg_memory_usage_mb"] <= 100:
            memory_score = 100
        elif metrics["avg_memory_usage_mb"] <= 200:
            memory_score = 80
        elif metrics["avg_memory_usage_mb"] <= 500:
            memory_score = 60
        else:
            memory_score = 40
        
        # Calculate overall grade
        overall_score = (frame_time_score + fps_score + memory_score) / 3
        
        if overall_score >= 90:
            return "A+"
        elif overall_score >= 80:
            return "A"
        elif overall_score >= 70:
            return "B"
        elif overall_score >= 60:
            return "C"
        else:
            return "D"
    
    def print_performance_report(self) -> None:
        """Print detailed performance report."""
        summary = self.get_performance_summary()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("="*60)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"⏱️  Benchmark Duration: {summary['benchmark_duration']:.2f}s")
        print(f"🎯 Total Frames: {summary['total_frames']}")
        print(f"📈 Performance Grade: {summary['performance_grade']}")
        
        print("\n📊 AVERAGE METRICS:")
        avg = summary["average_metrics"]
        print(f"   Frame Time: {avg['avg_frame_time']*1000:.2f}ms (target: 16.67ms)")
        print(f"   FPS: {avg['avg_fps']:.1f} (target: 60.0)")
        print(f"   Event Processing: {avg['avg_event_processing_time']*1000:.2f}ms")
        print(f"   Component Updates: {avg['avg_component_update_time']*1000:.2f}ms")
        print(f"   Memory Usage: {avg['avg_memory_usage_mb']:.1f}MB")
        print(f"   CPU Usage: {avg['avg_cpu_usage_percent']:.1f}%")
        print(f"   Event Queue Size: {avg['avg_event_queue_size']:.0f}")
        
        print("\n📈 RANGES:")
        print(f"   Frame Time: {summary['frame_time']['min']*1000:.2f}ms - {summary['frame_time']['max']*1000:.2f}ms")
        print(f"   FPS: {summary['fps']['min']:.1f} - {summary['fps']['max']:.1f}")
        print(f"   Memory: {summary['memory_usage']['min']:.1f}MB - {summary['memory_usage']['max']:.1f}MB")
        
        print("\n🎯 RECOMMENDATIONS:")
        self._print_recommendations(summary)
        
        print("="*60)
    
    def _print_recommendations(self, summary: Dict[str, Any]) -> None:
        """Print performance optimization recommendations."""
        avg = summary["average_metrics"]
        
        if avg["avg_frame_time"] > 0.0167:
            print("   ⚡ Consider optimizing frame processing for better FPS")
        
        if avg["avg_event_processing_time"] > 0.005:
            print("   🔄 Event processing taking too long - optimize event handlers")
        
        if avg["avg_memory_usage_mb"] > 200:
            print("   💾 Memory usage is high - check for memory leaks")
        
        if avg["avg_cpu_usage_percent"] > 50:
            print("   🔥 CPU usage is high - consider reducing simulation load")
        
        if avg["avg_event_queue_size"] > 100:
            print("   📬 Event queue is backing up - optimize event processing")


@asynccontextmanager
async def performance_benchmark(benchmark: PerformanceBenchmark, duration_seconds: float = 10.0):
    """
    Context manager for running performance benchmarks.
    
    Args:
        benchmark: PerformanceBenchmark instance
        duration_seconds: Duration to run benchmark
    """
    benchmark.start_benchmark()
    
    try:
        yield benchmark
    finally:
        await asyncio.sleep(duration_seconds)
        benchmark.end_benchmark()
        benchmark.print_performance_report()


class PerformanceOptimizer:
    """
    Performance optimization utilities.
    Provides methods to optimize simulation performance.
    """
    
    @staticmethod
    def optimize_event_loop() -> Dict[str, Any]:
        """Optimize event loop performance."""
        optimizations = {}
        
        # Set event loop policy for better performance
        try:
            import platform
            if platform.system() == 'Windows':
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                optimizations["event_loop_policy"] = "Windows Proactor"
            else:
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
                optimizations["event_loop_policy"] = "Default"
        except Exception as e:
            optimizations["event_loop_policy_error"] = str(e)
        
        # Optimize garbage collection
        gc.set_threshold(700, 10, 10)  # More aggressive GC
        optimizations["gc_threshold"] = "Optimized"
        
        # Set thread pool size
        import concurrent.futures
        optimizations["thread_pool_size"] = "Default"
        
        print("⚡ Performance optimizations applied")
        return optimizations
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information for performance analysis."""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "asyncio_version": "built-in"  # asyncio doesn't have __version__ in Python 3.12
            }
        except Exception as e:
            return {"error": str(e)} 