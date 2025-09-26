"""
Comprehensive Sensor Interface Classes for Hybrid Microgrid Monitoring
=====================================================================

This module provides sensor interface classes for all monitoring points
in the hybrid microgrid system, including data collection, validation,
and communication protocols.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """Standardized sensor reading data structure"""
    timestamp: datetime
    value: float
    unit: str
    quality: str  # "good", "warning", "error"
    metadata: Dict[str, Any]

class SensorInterface(ABC):
    """Abstract base class for all sensor interfaces"""
    
    def __init__(self, sensor_id: str, name: str, unit: str, update_interval: float = 1.0):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.update_interval = update_interval
        self.last_reading: Optional[SensorReading] = None
        self.is_connected = False
        self.callbacks: List[Callable[[SensorReading], None]] = []
        
    @abstractmethod
    async def read_sensor(self) -> SensorReading:
        """Read current sensor value"""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to sensor hardware"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from sensor hardware"""
        pass
    
    def add_callback(self, callback: Callable[[SensorReading], None]):
        """Add callback for sensor readings"""
        self.callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if not await self.connect():
            logger.error(f"Failed to connect to sensor {self.sensor_id}")
            return
        
        while self.is_connected:
            try:
                reading = await self.read_sensor()
                self.last_reading = reading
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(reading)
                    except Exception as e:
                        logger.error(f"Callback error for sensor {self.sensor_id}: {e}")
                
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error reading sensor {self.sensor_id}: {e}")
                await asyncio.sleep(self.update_interval)

# =============================================================================
# SOLAR SYSTEM SENSORS
# =============================================================================

class SolarIrradianceSensor(SensorInterface):
    """Solar irradiance sensor (W/m²)"""
    
    def __init__(self, sensor_id: str = "solar_irradiance_001"):
        super().__init__(sensor_id, "Solar Irradiance", "W/m²", 5.0)
        self.base_irradiance = 800  # Base irradiance for simulation
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to solar irradiance sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from solar irradiance sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate solar irradiance based on time of day
        hour = datetime.now().hour
        minute = datetime.now().minute
        time_factor = self._calculate_solar_factor(hour, minute)
        
        # Add some randomness and weather effects
        weather_factor = random.uniform(0.7, 1.3)
        value = self.base_irradiance * time_factor * weather_factor
        
        quality = "good"
        if value < 100:
            quality = "warning"
        elif value < 50:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 2),
            unit="W/m²",
            quality=quality,
            metadata={
                "time_factor": time_factor,
                "weather_factor": weather_factor,
                "sensor_type": "pyranometer"
            }
        )
    
    def _calculate_solar_factor(self, hour: int, minute: int) -> float:
        """Calculate solar factor based on time of day"""
        # Peak sun hours: 10 AM to 4 PM
        if 6 <= hour <= 18:
            # Sine wave approximation for solar curve
            time_of_day = hour + minute / 60.0
            peak_time = 12.0
            factor = math.sin((time_of_day - 6) * math.pi / 12)
            return max(0, factor)
        return 0.0

class PVOutputSensor(SensorInterface):
    """PV panel output power sensor (Watts)"""
    
    def __init__(self, sensor_id: str = "pv_output_001"):
        super().__init__(sensor_id, "PV Output Power", "Watts", 2.0)
        self.max_power = 2000  # Maximum PV output in Watts
        self.efficiency = 0.18  # 18% efficiency
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to PV output sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from PV output sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Get solar irradiance from irradiance sensor if available
        irradiance = 800  # Default value
        if hasattr(self, 'irradiance_sensor') and self.irradiance_sensor.last_reading:
            irradiance = self.irradiance_sensor.last_reading.value
        
        # Calculate PV output based on irradiance and efficiency
        # Assuming 10 m² panel area
        panel_area = 10.0
        theoretical_power = irradiance * panel_area * self.efficiency
        
        # Add temperature derating and other losses
        temp_derating = random.uniform(0.85, 0.95)
        value = theoretical_power * temp_derating
        
        quality = "good"
        if value < 100:
            quality = "warning"
        elif value < 50:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 2),
            unit="Watts",
            quality=quality,
            metadata={
                "irradiance": irradiance,
                "efficiency": self.efficiency,
                "temp_derating": temp_derating,
                "panel_area": panel_area
            }
        )

class ThermoelectricGeneratorSensor(SensorInterface):
    """Thermoelectric generator sensor"""
    
    def __init__(self, sensor_id: str = "teg_001"):
        super().__init__(sensor_id, "TEG Output", "Watts", 3.0)
        self.max_power = 500  # Maximum TEG output
        self.base_efficiency = 0.05  # 5% efficiency
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to TEG sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from TEG sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate TEG output based on temperature differential
        temp_diff = random.uniform(50, 200)  # Temperature differential in Celsius
        efficiency = self.base_efficiency * (temp_diff / 100)  # Efficiency scales with temp diff
        value = self.max_power * efficiency * random.uniform(0.8, 1.2)
        
        quality = "good"
        if temp_diff < 30:
            quality = "warning"
        elif temp_diff < 20:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 2),
            unit="Watts",
            quality=quality,
            metadata={
                "temp_differential": temp_diff,
                "efficiency": efficiency,
                "max_power": self.max_power
            }
        )

# =============================================================================
# THERMAL SYSTEM SENSORS
# =============================================================================

class HotWaterTemperatureSensor(SensorInterface):
    """Hot water temperature sensor (450-500°C target)"""
    
    def __init__(self, sensor_id: str = "hot_water_temp_001"):
        super().__init__(sensor_id, "Hot Water Temperature", "°C", 1.0)
        self.target_temp = 475  # Target temperature
        self.temp_range = (450, 500)  # Acceptable range
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to hot water temperature sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from hot water temperature sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate temperature around target with some variation
        base_temp = self.target_temp
        variation = random.uniform(-25, 25)  # ±25°C variation
        value = base_temp + variation
        
        quality = "good"
        if not (self.temp_range[0] <= value <= self.temp_range[1]):
            quality = "warning"
        if value < 400 or value > 550:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 1),
            unit="°C",
            quality=quality,
            metadata={
                "target_temp": self.target_temp,
                "temp_range": self.temp_range,
                "sensor_type": "thermocouple"
            }
        )

class StorageTankPressureSensor(SensorInterface):
    """Storage tank pressure sensor (Bar)"""
    
    def __init__(self, sensor_id: str = "tank_pressure_001"):
        super().__init__(sensor_id, "Storage Tank Pressure", "Bar", 2.0)
        self.target_pressure = 15  # Target pressure in Bar
        self.pressure_range = (10, 20)  # Acceptable range
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to storage tank pressure sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from storage tank pressure sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate pressure around target
        base_pressure = self.target_pressure
        variation = random.uniform(-2, 2)  # ±2 Bar variation
        value = base_pressure + variation
        
        quality = "good"
        if not (self.pressure_range[0] <= value <= self.pressure_range[1]):
            quality = "warning"
        if value < 5 or value > 25:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 2),
            unit="Bar",
            quality=quality,
            metadata={
                "target_pressure": self.target_pressure,
                "pressure_range": self.pressure_range,
                "sensor_type": "pressure_transducer"
            }
        )

class MoltenSaltFlowSensor(SensorInterface):
    """Molten salt flow rate sensor (L/min)"""
    
    def __init__(self, sensor_id: str = "molten_salt_flow_001"):
        super().__init__(sensor_id, "Molten Salt Flow Rate", "L/min", 1.0)
        self.target_flow = 100  # Target flow rate
        self.flow_range = (80, 120)  # Acceptable range
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to molten salt flow sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from molten salt flow sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate flow rate
        base_flow = self.target_flow
        variation = random.uniform(-10, 10)  # ±10 L/min variation
        value = base_flow + variation
        
        quality = "good"
        if not (self.flow_range[0] <= value <= self.flow_range[1]):
            quality = "warning"
        if value < 50 or value > 150:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 1),
            unit="L/min",
            quality=quality,
            metadata={
                "target_flow": self.target_flow,
                "flow_range": self.flow_range,
                "sensor_type": "flow_meter"
            }
        )

# =============================================================================
# CONVERSION AND CONTROL SENSORS
# =============================================================================

class InverterEfficiencySensor(SensorInterface):
    """Inverter conversion efficiency sensor (>15% target)"""
    
    def __init__(self, sensor_id: str = "inverter_efficiency_001"):
        super().__init__(sensor_id, "Inverter Efficiency", "%", 2.0)
        self.target_efficiency = 20  # Target efficiency percentage
        self.min_efficiency = 15  # Minimum acceptable efficiency
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to inverter efficiency sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from inverter efficiency sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate inverter efficiency
        base_efficiency = self.target_efficiency
        variation = random.uniform(-3, 3)  # ±3% variation
        value = base_efficiency + variation
        
        quality = "good"
        if value < self.min_efficiency:
            quality = "warning"
        if value < 10:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 2),
            unit="%",
            quality=quality,
            metadata={
                "target_efficiency": self.target_efficiency,
                "min_efficiency": self.min_efficiency,
                "sensor_type": "calculated"
            }
        )

class ControllerHealthSensor(SensorInterface):
    """Microgrid controller health sensor"""
    
    def __init__(self, sensor_id: str = "controller_health_001"):
        super().__init__(sensor_id, "Controller Health", "status", 5.0)
        self.health_states = ["healthy", "degraded", "fault"]
        self.current_state = "healthy"
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to controller health sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from controller health sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate controller health with occasional state changes
        if random.random() < 0.05:  # 5% chance of state change
            self.current_state = random.choice(self.health_states)
        
        # Convert state to numeric value for consistency
        state_values = {"healthy": 100, "degraded": 50, "fault": 0}
        value = state_values[self.current_state]
        
        quality = "good" if self.current_state == "healthy" else "warning" if self.current_state == "degraded" else "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=value,
            unit="status",
            quality=quality,
            metadata={
                "state": self.current_state,
                "sensor_type": "status_monitor"
            }
        )

# =============================================================================
# STORAGE SYSTEM SENSORS
# =============================================================================

class BatterySOCSensor(SensorInterface):
    """Battery State of Charge sensor (%)"""
    
    def __init__(self, sensor_id: str = "battery_soc_001"):
        super().__init__(sensor_id, "Battery SOC", "%", 1.0)
        self.current_soc = 75  # Current SOC percentage
        self.discharge_rate = 0.1  # SOC decrease per hour
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to battery SOC sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from battery SOC sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate SOC changes based on load and generation
        # In real implementation, this would be calculated from actual battery data
        
        # Simulate gradual discharge with some charging periods
        if random.random() < 0.3:  # 30% chance of charging
            self.current_soc += random.uniform(0.5, 2.0)
        else:
            self.current_soc -= random.uniform(0.1, 0.5)
        
        # Keep SOC within bounds
        self.current_soc = max(0, min(100, self.current_soc))
        
        quality = "good"
        if self.current_soc < 20:
            quality = "warning"
        if self.current_soc < 10:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(self.current_soc, 1),
            unit="%",
            quality=quality,
            metadata={
                "discharge_rate": self.discharge_rate,
                "sensor_type": "battery_management_system"
            }
        )

class BatteryTemperatureSensor(SensorInterface):
    """Battery temperature sensor (°C)"""
    
    def __init__(self, sensor_id: str = "battery_temp_001"):
        super().__init__(sensor_id, "Battery Temperature", "°C", 2.0)
        self.optimal_temp = 25  # Optimal temperature
        self.temp_range = (15, 35)  # Acceptable range
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to battery temperature sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from battery temperature sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate battery temperature
        base_temp = self.optimal_temp
        variation = random.uniform(-5, 5)  # ±5°C variation
        value = base_temp + variation
        
        quality = "good"
        if not (self.temp_range[0] <= value <= self.temp_range[1]):
            quality = "warning"
        if value < 10 or value > 50:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 1),
            unit="°C",
            quality=quality,
            metadata={
                "optimal_temp": self.optimal_temp,
                "temp_range": self.temp_range,
                "sensor_type": "thermistor"
            }
        )

# =============================================================================
# OUTPUT AND LOAD SENSORS
# =============================================================================

class TurbinePowerSensor(SensorInterface):
    """Turbine power output sensor (kW)"""
    
    def __init__(self, sensor_id: str = "turbine_power_001"):
        super().__init__(sensor_id, "Turbine Power Output", "kW", 2.0)
        self.max_power = 1000  # Maximum turbine power
        self.current_power = 500  # Current power output
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to turbine power sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from turbine power sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate turbine power output
        variation = random.uniform(-50, 50)  # ±50 kW variation
        self.current_power += variation
        self.current_power = max(0, min(self.max_power, self.current_power))
        
        quality = "good"
        if self.current_power < 100:
            quality = "warning"
        if self.current_power < 50:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(self.current_power, 1),
            unit="kW",
            quality=quality,
            metadata={
                "max_power": self.max_power,
                "sensor_type": "power_meter"
            }
        )

class LoadCurrentSensor(SensorInterface):
    """Load current sensor (Amperes)"""
    
    def __init__(self, sensor_id: str = "load_current_001", load_type: str = "critical"):
        super().__init__(sensor_id, f"{load_type.title()} Load Current", "A", 1.0)
        self.load_type = load_type
        self.base_current = 50 if load_type == "critical" else 100
    
    async def connect(self) -> bool:
        self.is_connected = True
        logger.info(f"Connected to {self.load_type} load current sensor {self.sensor_id}")
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        logger.info(f"Disconnected from {self.load_type} load current sensor {self.sensor_id}")
        return True
    
    async def read_sensor(self) -> SensorReading:
        # Simulate load current
        variation = random.uniform(-10, 10)  # ±10 A variation
        value = self.base_current + variation
        
        quality = "good"
        if value < 10:
            quality = "warning"
        if value < 5:
            quality = "error"
        
        return SensorReading(
            timestamp=datetime.utcnow(),
            value=round(value, 1),
            unit="A",
            quality=quality,
            metadata={
                "load_type": self.load_type,
                "base_current": self.base_current,
                "sensor_type": "current_transformer"
            }
        )

# =============================================================================
# SENSOR MANAGER
# =============================================================================

class SensorManager:
    """Manages all sensors in the microgrid system"""
    
    def __init__(self):
        self.sensors: Dict[str, SensorInterface] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
    
    def add_sensor(self, sensor: SensorInterface):
        """Add a sensor to the manager"""
        self.sensors[sensor.sensor_id] = sensor
        logger.info(f"Added sensor {sensor.sensor_id} to manager")
    
    def remove_sensor(self, sensor_id: str):
        """Remove a sensor from the manager"""
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            logger.info(f"Removed sensor {sensor_id} from manager")
    
    async def start_all_sensors(self):
        """Start monitoring all sensors"""
        self.is_running = True
        for sensor_id, sensor in self.sensors.items():
            task = asyncio.create_task(sensor.start_monitoring())
            self.monitoring_tasks[sensor_id] = task
            logger.info(f"Started monitoring sensor {sensor_id}")
    
    async def stop_all_sensors(self):
        """Stop monitoring all sensors"""
        self.is_running = False
        for sensor_id, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped monitoring sensor {sensor_id}")
        
        # Disconnect all sensors
        for sensor in self.sensors.values():
            await sensor.disconnect()
        
        self.monitoring_tasks.clear()
    
    def get_sensor_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Get latest reading from a specific sensor"""
        if sensor_id in self.sensors:
            return self.sensors[sensor_id].last_reading
        return None
    
    def get_all_readings(self) -> Dict[str, Optional[SensorReading]]:
        """Get latest readings from all sensors"""
        return {sensor_id: sensor.last_reading for sensor_id, sensor in self.sensors.items()}
    
    def get_sensors_by_type(self, sensor_type: str) -> List[SensorInterface]:
        """Get sensors by type (e.g., 'temperature', 'pressure')"""
        return [sensor for sensor in self.sensors.values() if sensor_type in sensor.name.lower()]

# =============================================================================
# SENSOR FACTORY
# =============================================================================

class SensorFactory:
    """Factory for creating sensor instances"""
    
    @staticmethod
    def create_solar_sensors() -> List[SensorInterface]:
        """Create all solar system sensors"""
        return [
            SolarIrradianceSensor(),
            PVOutputSensor(),
            ThermoelectricGeneratorSensor()
        ]
    
    @staticmethod
    def create_thermal_sensors() -> List[SensorInterface]:
        """Create all thermal system sensors"""
        return [
            HotWaterTemperatureSensor(),
            StorageTankPressureSensor(),
            MoltenSaltFlowSensor()
        ]
    
    @staticmethod
    def create_conversion_sensors() -> List[SensorInterface]:
        """Create all conversion and control sensors"""
        return [
            InverterEfficiencySensor(),
            ControllerHealthSensor()
        ]
    
    @staticmethod
    def create_storage_sensors() -> List[SensorInterface]:
        """Create all storage system sensors"""
        return [
            BatterySOCSensor(),
            BatteryTemperatureSensor()
        ]
    
    @staticmethod
    def create_output_sensors() -> List[SensorInterface]:
        """Create all output and load sensors"""
        return [
            TurbinePowerSensor(),
            LoadCurrentSensor("critical_load_001", "critical"),
            LoadCurrentSensor("non_critical_load_001", "non_critical")
        ]
    
    @staticmethod
    def create_all_sensors() -> List[SensorInterface]:
        """Create all sensors for the microgrid system"""
        sensors = []
        sensors.extend(SensorFactory.create_solar_sensors())
        sensors.extend(SensorFactory.create_thermal_sensors())
        sensors.extend(SensorFactory.create_conversion_sensors())
        sensors.extend(SensorFactory.create_storage_sensors())
        sensors.extend(SensorFactory.create_output_sensors())
        return sensors

# Example usage and testing
async def main():
    """Example usage of the sensor system"""
    # Create sensor manager
    manager = SensorManager()
    
    # Create and add all sensors
    sensors = SensorFactory.create_all_sensors()
    for sensor in sensors:
        manager.add_sensor(sensor)
    
    # Add callback to log all readings
    def log_reading(reading: SensorReading):
        logger.info(f"Sensor reading: {reading.value} {reading.unit} (quality: {reading.quality})")
    
    for sensor in sensors:
        sensor.add_callback(log_reading)
    
    # Start monitoring
    await manager.start_all_sensors()
    
    # Monitor for 30 seconds
    await asyncio.sleep(30)
    
    # Stop monitoring
    await manager.stop_all_sensors()

if __name__ == "__main__":
    asyncio.run(main())