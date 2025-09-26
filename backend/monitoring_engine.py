"""
Comprehensive Real-Time Monitoring Engine for Hybrid Microgrid System
====================================================================

This module provides a real-time monitoring engine that collects data from all
sensors, processes it, stores it in the database, and provides real-time updates
to the dashboard and alert systems.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import sqlalchemy
from sqlalchemy.orm import Session

from comprehensive_models import (
    SolarSystemData, ThermalSystemData, ConversionControlData,
    StorageSystemData, OutputLoadData, SystemEfficiencyData,
    FaultAlertData, PredictiveAnalyticsData, SessionLocal
)
from sensor_interfaces import SensorManager, SensorReading, SensorFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration for the monitoring engine"""
    data_collection_interval: float = 1.0  # seconds
    database_write_interval: float = 5.0   # seconds
    alert_check_interval: float = 2.0      # seconds
    efficiency_calculation_interval: float = 10.0  # seconds
    predictive_analytics_interval: float = 60.0    # seconds
    max_data_buffer_size: int = 1000
    enable_real_time_alerts: bool = True
    enable_predictive_analytics: bool = True

class DataBuffer:
    """Buffer for storing sensor data before database writes"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.solar_data: List[Dict] = []
        self.thermal_data: List[Dict] = []
        self.conversion_data: List[Dict] = []
        self.storage_data: List[Dict] = []
        self.output_data: List[Dict] = []
        self.efficiency_data: List[Dict] = []
        self.alert_data: List[Dict] = []
        self.analytics_data: List[Dict] = []
    
    def add_solar_data(self, data: Dict):
        self.solar_data.append(data)
        if len(self.solar_data) > self.max_size:
            self.solar_data.pop(0)
    
    def add_thermal_data(self, data: Dict):
        self.thermal_data.append(data)
        if len(self.thermal_data) > self.max_size:
            self.thermal_data.pop(0)
    
    def add_conversion_data(self, data: Dict):
        self.conversion_data.append(data)
        if len(self.conversion_data) > self.max_size:
            self.conversion_data.pop(0)
    
    def add_storage_data(self, data: Dict):
        self.storage_data.append(data)
        if len(self.storage_data) > self.max_size:
            self.storage_data.pop(0)
    
    def add_output_data(self, data: Dict):
        self.output_data.append(data)
        if len(self.output_data) > self.max_size:
            self.output_data.pop(0)
    
    def add_efficiency_data(self, data: Dict):
        self.efficiency_data.append(data)
        if len(self.efficiency_data) > self.max_size:
            self.efficiency_data.pop(0)
    
    def add_alert_data(self, data: Dict):
        self.alert_data.append(data)
        if len(self.alert_data) > self.max_size:
            self.alert_data.pop(0)
    
    def add_analytics_data(self, data: Dict):
        self.analytics_data.append(data)
        if len(self.analytics_data) > self.max_size:
            self.analytics_data.pop(0)
    
    def get_all_data(self) -> Dict[str, List[Dict]]:
        """Get all buffered data and clear buffers"""
        data = {
            'solar': self.solar_data.copy(),
            'thermal': self.thermal_data.copy(),
            'conversion': self.conversion_data.copy(),
            'storage': self.storage_data.copy(),
            'output': self.output_data.copy(),
            'efficiency': self.efficiency_data.copy(),
            'alerts': self.alert_data.copy(),
            'analytics': self.analytics_data.copy()
        }
        
        # Clear buffers
        self.solar_data.clear()
        self.thermal_data.clear()
        self.conversion_data.clear()
        self.storage_data.clear()
        self.output_data.clear()
        self.efficiency_data.clear()
        self.alert_data.clear()
        self.analytics_data.clear()
        
        return data

class RealTimeMonitoringEngine:
    """Real-time monitoring engine for the hybrid microgrid system"""
    
    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.sensor_manager = SensorManager()
        self.data_buffer = DataBuffer(self.config.max_data_buffer_size)
        self.is_running = False
        self.tasks: List[asyncio.Task] = []
        self.callbacks: List[Callable[[Dict], None]] = []
        
        # Initialize sensors
        self._initialize_sensors()
        
        # Performance metrics
        self.metrics = {
            'data_points_collected': 0,
            'database_writes': 0,
            'alerts_generated': 0,
            'errors': 0,
            'start_time': None
        }
    
    def _initialize_sensors(self):
        """Initialize all sensors"""
        sensors = SensorFactory.create_all_sensors()
        for sensor in sensors:
            self.sensor_manager.add_sensor(sensor)
            # Add callback to process sensor readings
            sensor.add_callback(self._process_sensor_reading)
        
        logger.info(f"Initialized {len(sensors)} sensors")
    
    def add_callback(self, callback: Callable[[Dict], None]):
        """Add callback for real-time data updates"""
        self.callbacks.append(callback)
    
    def _process_sensor_reading(self, reading: SensorReading):
        """Process incoming sensor reading"""
        try:
            # Convert sensor reading to appropriate data structure
            data = self._convert_sensor_reading_to_data(reading)
            
            # Add to appropriate buffer
            self._add_to_buffer(data)
            
            # Update metrics
            self.metrics['data_points_collected'] += 1
            
            # Check for immediate alerts
            if self.config.enable_real_time_alerts:
                self._check_immediate_alerts(reading)
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
                    self.metrics['errors'] += 1
        
        except Exception as e:
            logger.error(f"Error processing sensor reading: {e}")
            self.metrics['errors'] += 1
    
    def _convert_sensor_reading_to_data(self, reading: SensorReading) -> Dict:
        """Convert sensor reading to standardized data structure"""
        return {
            'timestamp': reading.timestamp,
            'sensor_id': getattr(reading, 'sensor_id', 'unknown'),
            'value': reading.value,
            'unit': reading.unit,
            'quality': reading.quality,
            'metadata': reading.metadata
        }
    
    def _add_to_buffer(self, data: Dict):
        """Add data to appropriate buffer based on sensor type"""
        sensor_id = data['sensor_id']
        
        # Categorize data based on sensor ID
        if 'solar' in sensor_id or 'pv' in sensor_id or 'teg' in sensor_id:
            self.data_buffer.add_solar_data(data)
        elif 'thermal' in sensor_id or 'hot_water' in sensor_id or 'tank' in sensor_id or 'molten' in sensor_id:
            self.data_buffer.add_thermal_data(data)
        elif 'inverter' in sensor_id or 'controller' in sensor_id:
            self.data_buffer.add_conversion_data(data)
        elif 'battery' in sensor_id or 'storage' in sensor_id:
            self.data_buffer.add_storage_data(data)
        elif 'turbine' in sensor_id or 'load' in sensor_id or 'condenser' in sensor_id:
            self.data_buffer.add_output_data(data)
        else:
            # Default to solar data for unknown sensors
            self.data_buffer.add_solar_data(data)
    
    def _check_immediate_alerts(self, reading: SensorReading):
        """Check for immediate alerts based on sensor reading"""
        alerts = []
        
        # Check for critical conditions
        if reading.quality == "error":
            alerts.append({
                'alert_type': 'sensor_error',
                'severity': 'critical',
                'message': f"Sensor {getattr(reading, 'sensor_id', 'unknown')} reading error",
                'source': getattr(reading, 'sensor_id', 'unknown'),
                'current_value': reading.value,
                'threshold_value': 0,
                'alert_duration': 0
            })
        elif reading.quality == "warning":
            alerts.append({
                'alert_type': 'sensor_warning',
                'severity': 'medium',
                'message': f"Sensor {getattr(reading, 'sensor_id', 'unknown')} reading warning",
                'source': getattr(reading, 'sensor_id', 'unknown'),
                'current_value': reading.value,
                'threshold_value': 0,
                'alert_duration': 0
            })
        
        # Add alerts to buffer
        for alert in alerts:
            self.data_buffer.add_alert_data(alert)
            self.metrics['alerts_generated'] += 1
    
    async def _database_writer(self):
        """Periodically write buffered data to database"""
        while self.is_running:
            try:
                # Get all buffered data
                data = self.data_buffer.get_all_data()
                
                if any(data.values()):  # If there's any data to write
                    await self._write_to_database(data)
                    self.metrics['database_writes'] += 1
                
                await asyncio.sleep(self.config.database_write_interval)
            
            except Exception as e:
                logger.error(f"Database writer error: {e}")
                self.metrics['errors'] += 1
                await asyncio.sleep(self.config.database_write_interval)
    
    async def _write_to_database(self, data: Dict[str, List[Dict]]):
        """Write data to database"""
        db = SessionLocal()
        try:
            # Write solar system data
            for item in data['solar']:
                if 'solar_irradiance' in item['sensor_id']:
                    db_solar = SolarSystemData(
                        timestamp=item['timestamp'],
                        solar_irradiance=item['value'],
                        pv_output_power=0,  # Will be updated by other sensors
                        pv_output_voltage=0,
                        pv_efficiency=0,
                        concentrator_position=0,
                        concentrator_alignment=0,
                        concentrated_energy_level=0,
                        teg_temperature_diff=0,
                        teg_output_power=0,
                        teg_efficiency=0
                    )
                    db.add(db_solar)
            
            # Write thermal system data
            for item in data['thermal']:
                if 'hot_water_temp' in item['sensor_id']:
                    db_thermal = ThermalSystemData(
                        timestamp=item['timestamp'],
                        hot_water_temperature=item['value'],
                        storage_tank_temperature=0,
                        storage_tank_pressure=0,
                        energy_stored=0,
                        molten_salt_flow_rate=0,
                        molten_salt_inlet_temp=0,
                        molten_salt_outlet_temp=0,
                        pipe_integrity_status="healthy",
                        steam_output=0,
                        steam_pressure=0,
                        steam_temperature=0,
                        steam_fault_alerts=[]
                    )
                    db.add(db_thermal)
            
            # Write storage system data
            for item in data['storage']:
                if 'battery_soc' in item['sensor_id']:
                    db_storage = StorageSystemData(
                        timestamp=item['timestamp'],
                        battery_soc=item['value'],
                        battery_charge_rate=0,
                        battery_discharge_rate=0,
                        battery_temperature=0,
                        battery_cycles=0,
                        battery_health="good",
                        thermal_energy_stored=0,
                        thermal_energy_released=0,
                        thermal_storage_temp=0,
                        thermal_storage_efficiency=0,
                        water_tank_level=0,
                        water_tank_temperature=0,
                        water_flow_rate=0
                    )
                    db.add(db_storage)
            
            # Write alert data
            for item in data['alerts']:
                db_alert = FaultAlertData(
                    timestamp=item['timestamp'],
                    alert_type=item['alert_type'],
                    alert_severity=item['severity'],
                    alert_message=item['message'],
                    alert_source=item['source'],
                    current_value=item['current_value'],
                    threshold_value=item['threshold_value'],
                    alert_duration=item['alert_duration']
                )
                db.add(db_alert)
            
            db.commit()
            logger.debug(f"Written {sum(len(v) for v in data.values())} data points to database")
        
        except Exception as e:
            logger.error(f"Database write error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _efficiency_calculator(self):
        """Calculate system efficiency metrics"""
        while self.is_running:
            try:
                # Get latest sensor readings
                readings = self.sensor_manager.get_all_readings()
                
                if readings:
                    efficiency_data = self._calculate_efficiency(readings)
                    if efficiency_data:
                        self.data_buffer.add_efficiency_data(efficiency_data)
                
                await asyncio.sleep(self.config.efficiency_calculation_interval)
            
            except Exception as e:
                logger.error(f"Efficiency calculator error: {e}")
                self.metrics['errors'] += 1
                await asyncio.sleep(self.config.efficiency_calculation_interval)
    
    def _calculate_efficiency(self, readings: Dict[str, Optional[SensorReading]]) -> Optional[Dict]:
        """Calculate system efficiency from sensor readings"""
        try:
            # Get relevant readings
            pv_power = None
            solar_irradiance = None
            battery_soc = None
            inverter_efficiency = None
            
            for sensor_id, reading in readings.items():
                if reading:
                    if 'pv_output' in sensor_id:
                        pv_power = reading.value
                    elif 'solar_irradiance' in sensor_id:
                        solar_irradiance = reading.value
                    elif 'battery_soc' in sensor_id:
                        battery_soc = reading.value
                    elif 'inverter_efficiency' in sensor_id:
                        inverter_efficiency = reading.value
            
            if not all([pv_power, solar_irradiance, battery_soc, inverter_efficiency]):
                return None
            
            # Calculate efficiencies
            solar_to_electrical = (pv_power / (solar_irradiance * 10)) * 100 if solar_irradiance > 0 else 0  # Assuming 10m² panel
            overall_efficiency = (solar_to_electrical * inverter_efficiency) / 100
            
            return {
                'timestamp': datetime.utcnow(),
                'overall_efficiency': round(overall_efficiency, 2),
                'solar_to_electrical_efficiency': round(solar_to_electrical, 2),
                'thermal_to_electrical_efficiency': 0,  # Placeholder
                'storage_efficiency': round(battery_soc, 2),
                'efficiency_target_15': overall_efficiency > 15,
                'efficiency_target_30': overall_efficiency > 30,
                'efficiency_trend': 'stable',  # Placeholder
                'efficiency_vs_previous_hour': 0,  # Placeholder
                'efficiency_vs_previous_day': 0   # Placeholder
            }
        
        except Exception as e:
            logger.error(f"Efficiency calculation error: {e}")
            return None
    
    async def _predictive_analytics(self):
        """Generate predictive analytics"""
        while self.is_running:
            try:
                if self.config.enable_predictive_analytics:
                    analytics_data = self._generate_predictive_analytics()
                    if analytics_data:
                        self.data_buffer.add_analytics_data(analytics_data)
                
                await asyncio.sleep(self.config.predictive_analytics_interval)
            
            except Exception as e:
                logger.error(f"Predictive analytics error: {e}")
                self.metrics['errors'] += 1
                await asyncio.sleep(self.config.predictive_analytics_interval)
    
    def _generate_predictive_analytics(self) -> Optional[Dict]:
        """Generate predictive analytics data"""
        try:
            # Get latest sensor readings
            readings = self.sensor_manager.get_all_readings()
            
            if not readings:
                return None
            
            # Get battery SOC for backup calculations
            battery_soc = None
            for sensor_id, reading in readings.items():
                if reading and 'battery_soc' in sensor_id:
                    battery_soc = reading.value
                    break
            
            if battery_soc is None:
                return None
            
            # Calculate backup hours (simplified)
            battery_backup_hours = (battery_soc / 100) * 24  # Assuming 24h at 100% SOC
            
            return {
                'timestamp': datetime.utcnow(),
                'solar_forecast_1h': 0,  # Placeholder
                'solar_forecast_6h': 0,  # Placeholder
                'solar_forecast_24h': 0,  # Placeholder
                'solar_forecast_confidence': 85,  # Placeholder
                'battery_backup_hours': round(battery_backup_hours, 1),
                'battery_depletion_rate': 0.5,  # Placeholder
                'critical_load_backup_hours': round(battery_backup_hours * 1.5, 1),
                'predicted_outage_probability': 5,  # Placeholder
                'predicted_outage_duration': 0,  # Placeholder
                'predicted_outage_cause': 'none',  # Placeholder
                'predicted_load_1h': 0,  # Placeholder
                'predicted_load_6h': 0,  # Placeholder
                'predicted_load_24h': 0   # Placeholder
            }
        
        except Exception as e:
            logger.error(f"Predictive analytics generation error: {e}")
            return None
    
    async def start(self):
        """Start the monitoring engine"""
        if self.is_running:
            logger.warning("Monitoring engine is already running")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.utcnow()
        
        logger.info("Starting real-time monitoring engine")
        
        # Start sensor monitoring
        await self.sensor_manager.start_all_sensors()
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._database_writer()),
            asyncio.create_task(self._efficiency_calculator()),
            asyncio.create_task(self._predictive_analytics())
        ]
        
        logger.info("Monitoring engine started successfully")
    
    async def stop(self):
        """Stop the monitoring engine"""
        if not self.is_running:
            logger.warning("Monitoring engine is not running")
            return
        
        self.is_running = False
        
        logger.info("Stopping real-time monitoring engine")
        
        # Stop background tasks
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Stop sensor monitoring
        await self.sensor_manager.stop_all_sensors()
        
        # Write any remaining buffered data
        data = self.data_buffer.get_all_data()
        if any(data.values()):
            await self._write_to_database(data)
        
        self.tasks.clear()
        
        logger.info("Monitoring engine stopped successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring engine status"""
        uptime = None
        if self.metrics['start_time']:
            uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'sensors_connected': len([s for s in self.sensor_manager.sensors.values() if s.is_connected]),
            'total_sensors': len(self.sensor_manager.sensors),
            'uptime_seconds': uptime,
            'metrics': self.metrics.copy(),
            'config': {
                'data_collection_interval': self.config.data_collection_interval,
                'database_write_interval': self.config.database_write_interval,
                'alert_check_interval': self.config.alert_check_interval,
                'efficiency_calculation_interval': self.config.efficiency_calculation_interval,
                'predictive_analytics_interval': self.config.predictive_analytics_interval,
                'max_data_buffer_size': self.config.max_data_buffer_size,
                'enable_real_time_alerts': self.config.enable_real_time_alerts,
                'enable_predictive_analytics': self.config.enable_predictive_analytics
            }
        }
    
    def get_latest_readings(self) -> Dict[str, Any]:
        """Get latest readings from all sensors"""
        readings = self.sensor_manager.get_all_readings()
        return {
            sensor_id: {
                'value': reading.value if reading else None,
                'unit': reading.unit if reading else None,
                'quality': reading.quality if reading else None,
                'timestamp': reading.timestamp.isoformat() if reading else None
            }
            for sensor_id, reading in readings.items()
        }

# Example usage and testing
async def main():
    """Example usage of the monitoring engine"""
    # Create monitoring engine
    config = MonitoringConfig(
        data_collection_interval=1.0,
        database_write_interval=5.0,
        alert_check_interval=2.0,
        efficiency_calculation_interval=10.0,
        predictive_analytics_interval=60.0
    )
    
    engine = RealTimeMonitoringEngine(config)
    
    # Add callback to log data updates
    def log_data_update(data):
        logger.info(f"Data update: {data['sensor_id']} = {data['value']} {data['unit']}")
    
    engine.add_callback(log_data_update)
    
    # Start monitoring
    await engine.start()
    
    # Monitor for 60 seconds
    await asyncio.sleep(60)
    
    # Get status
    status = engine.get_status()
    logger.info(f"Engine status: {status}")
    
    # Stop monitoring
    await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())