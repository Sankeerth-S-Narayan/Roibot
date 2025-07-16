#!/usr/bin/env python3
"""
Roibot - Warehouse Robot Simulation
Main entry point for the unified application.
"""

import asyncio
import threading
import time
from flask import Flask
from flask_socketio import SocketIO
import logging

from core.engine import SimulationEngine
from web_interface.server.web_server import create_app
from web_interface.server.data_bridge import DataBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedRoibotApp:
    """Unified application that runs both simulation engine and web interface."""
    
    def __init__(self):
        self.engine = SimulationEngine()
        self.data_bridge = DataBridge()
        self.app = create_app()
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Register data bridge with socketio
        self.data_bridge.register_socketio(self.socketio)
        
        # Connect engine to data bridge
        self.engine.set_data_bridge(self.data_bridge)
        
    def start_engine(self):
        """Start the simulation engine in a separate thread."""
        logger.info("🚀 Starting simulation engine...")
        
        # The simulation engine is now started by the data_bridge via async methods
        # This sync update loop is no longer needed and conflicts with the async loop
        logger.info("ℹ️  Simulation engine is started by data_bridge - skipping sync loop")
        
        # Comment out the old sync loop to avoid conflicts
        # self.is_running = True
        # 
        # while self.is_running:
        #     try:
        #         # Update engine
        #         self.engine.update(1/60)  # 60 FPS
        #         
        #         # Send data to web interface
        #         self.data_bridge.send_simulation_data(self.engine)
        #         
        #         # Small delay to maintain 60 FPS
        #         time.sleep(1/60)
        #         
        #     except Exception as e:
        #         logger.error(f"Engine error: {e}")
        #         break
        #         
        # logger.info("🛑 Simulation engine stopped")
    
    def start(self):
        """Start the unified application."""
        logger.info("🎯 Starting Unified Roibot Application...")
        
        # The simulation engine is started by data_bridge via async methods
        # No need for separate engine thread anymore
        logger.info("🚀 Starting simulation engine...")
        # Note: The actual engine start happens in data_bridge.start_simulation_engine()
        
        # Start web server
        logger.info("🌐 Starting web server on http://localhost:5000")
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=False)
    
    def stop(self):
        """Stop the unified application."""
        logger.info("🛑 Stopping Unified Roibot Application...")
        # Engine is managed by data_bridge, no need to stop separate thread

def main():
    """Main entry point."""
    try:
        app = UnifiedRoibotApp()
        app.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main() 