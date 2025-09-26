#!/usr/bin/env python3
"""
Comprehensive Hybrid Microgrid Monitoring System Startup Script
=============================================================

This script starts the complete monitoring system including:
- Real-time monitoring engine
- Alert system
- Analytics engine
- Forecasting engine
- Comprehensive API server
"""

import asyncio
import logging
import signal
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from comprehensive_api import app
from monitoring_engine import RealTimeMonitoringEngine, MonitoringConfig
from alert_system import AlertManager
from analytics_engine import AnalyticsEngine
from forecasting_engine import ForecastingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ComprehensiveSystem:
    """Main system coordinator"""
    
    def __init__(self):
        self.monitoring_engine = None
        self.alert_manager = None
        self.analytics_engine = None
        self.forecasting_engine = None
        self.is_running = False
        
    async def start(self):
        """Start all system components"""
        try:
            logger.info("Starting Comprehensive Hybrid Microgrid Monitoring System...")
            
            # Initialize configuration
            config = MonitoringConfig(
                data_collection_interval=1.0,
                database_write_interval=5.0,
                alert_check_interval=2.0,
                efficiency_calculation_interval=10.0,
                predictive_analytics_interval=60.0,
                enable_real_time_alerts=True,
                enable_predictive_analytics=True
            )
            
            # Initialize components
            self.monitoring_engine = RealTimeMonitoringEngine(config)
            self.alert_manager = AlertManager()
            self.analytics_engine = AnalyticsEngine()
            self.forecasting_engine = ForecastingEngine()
            
            # Start all engines
            await self.monitoring_engine.start()
            await self.alert_manager.start()
            await self.analytics_engine.start()
            await self.forecasting_engine.start()
            
            # Add callbacks for real-time updates
            def on_sensor_data(data):
                asyncio.create_task(self.alert_manager.check_sensor_reading(data))
            
            self.monitoring_engine.add_callback(on_sensor_data)
            
            self.is_running = True
            logger.info("All system components started successfully")
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop all system components"""
        try:
            logger.info("Stopping system components...")
            
            if self.monitoring_engine:
                await self.monitoring_engine.stop()
            if self.alert_manager:
                await self.alert_manager.stop()
            if self.analytics_engine:
                await self.analytics_engine.stop()
            if self.forecasting_engine:
                await self.forecasting_engine.stop()
            
            self.is_running = False
            logger.info("All system components stopped")
            
        except Exception as e:
            logger.error(f"Error stopping system: {e}")

# Global system instance
system = ComprehensiveSystem()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(system.stop())
    sys.exit(0)

async def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the system
        await system.start()
        
        # Start the API server
        logger.info("Starting API server on http://0.0.0.0:8000")
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    print("=" * 60)
    print("Comprehensive Hybrid Microgrid Monitoring System")
    print("=" * 60)
    print("Features:")
    print("• Real-time sensor monitoring")
    print("• Advanced alert system")
    print("• Efficiency analytics")
    print("• Solar forecasting")
    print("• Battery depletion prediction")
    print("• WebSocket real-time updates")
    print("• Comprehensive REST API")
    print("=" * 60)
    print("Starting system...")
    print("API will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    asyncio.run(main())