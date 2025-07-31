#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Simple test script to verify snake path movement works in backend.
"""

import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import SimulationEngine

def test_snake_movement():
    """Test snake path movement without frontend."""
    print("🧪 Testing Snake Path Movement...")
    
    # Create engine
    engine = SimulationEngine()
    
    # Start simulation
    engine.start_simulation()
    
    # Run for 30 seconds to see movement
    print("🤖 Starting robot movement test...")
    print("📍 Robot should follow snake pattern through warehouse")
    print("⏱️  Running for 30 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        # Update engine
        engine.update(1/60)  # 60 FPS
        
        # Print robot status every 5 seconds
        if int(time.time() - start_time) % 5 == 0:
            print(f"🤖 Robot: {engine.robot.state.value} at {engine.robot.position}")
            print(f"📊 Path: {engine.robot.path_index}/{len(engine.robot.current_path)}")
            print(f"⏰ Time: {engine.simulation_time:.1f}s")
            print("---")
        
        time.sleep(1/60)  # 60 FPS
    
    print("✅ Test completed!")
    print(f"🎯 Final robot position: {engine.robot.position}")
    print(f"📊 Total path points: {len(engine.robot.current_path)}")

if __name__ == "__main__":
    test_snake_movement() 