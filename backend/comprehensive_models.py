from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./comprehensive_microgrid.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =============================================================================
# COMPREHENSIVE MONITORING DATA MODELS
# =============================================================================

class SolarSystemData(Base):
    """Solar irradiance and PV output monitoring"""
    __tablename__ = "solar_system_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Solar irradiance and PV output
    solar_irradiance = Column(Float)  # W/m²
    pv_output_power = Column(Float)   # Watts
    pv_output_voltage = Column(Float) # Volts
    pv_efficiency = Column(Float)     # Percentage
    
    # Solar concentrator health
    concentrator_position = Column(Float)  # Degrees
    concentrator_alignment = Column(Float) # Degrees
    concentrated_energy_level = Column(Float) # W/m²
    
    # Thermoelectric generator status
    teg_temperature_diff = Column(Float)  # Celsius
    teg_output_power = Column(Float)      # Watts
    teg_efficiency = Column(Float)        # Percentage

class ThermalSystemData(Base):
    """Hot water, storage tank, and thermal loop monitoring"""
    __tablename__ = "thermal_system_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Hot water & storage tank state
    hot_water_temperature = Column(Float)  # Celsius (450-500°C target)
    storage_tank_temperature = Column(Float) # Celsius
    storage_tank_pressure = Column(Float)    # Bar
    energy_stored = Column(Float)            # kWh
    
    # Molten salts/oils loop
    molten_salt_flow_rate = Column(Float)   # L/min
    molten_salt_inlet_temp = Column(Float)  # Celsius
    molten_salt_outlet_temp = Column(Float) # Celsius
    pipe_integrity_status = Column(String)  # "healthy", "warning", "critical"
    
    # Steam generation
    steam_output = Column(Float)            # kg/h
    steam_pressure = Column(Float)          # Bar
    steam_temperature = Column(Float)       # Celsius
    steam_fault_alerts = Column(JSON)       # List of fault alerts

class ConversionControlData(Base):
    """Inverter and hybrid microgrid controller monitoring"""
    __tablename__ = "conversion_control_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Inverter data
    inverter_input_voltage = Column(Float)   # Volts
    inverter_output_voltage = Column(Float)  # Volts
    inverter_conversion_efficiency = Column(Float) # Percentage (>15% target)
    inverter_operation_status = Column(String)     # "online", "offline", "fault"
    
    # Hybrid microgrid controller
    controller_algorithm_health = Column(String)   # "healthy", "degraded", "fault"
    controller_mode = Column(String)               # "grid", "islanded", "transition"
    scheduling_status = Column(String)             # "active", "inactive", "error"
    switching_status = Column(String)              # "normal", "switching", "fault"
    controller_logs = Column(JSON)                 # Recent controller logs

class StorageSystemData(Base):
    """BESS, thermal energy storage, and water storage monitoring"""
    __tablename__ = "storage_system_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # BESS Energy Storage
    battery_soc = Column(Float)              # State of Charge %
    battery_charge_rate = Column(Float)      # kW
    battery_discharge_rate = Column(Float)   # kW
    battery_temperature = Column(Float)      # Celsius
    battery_cycles = Column(Integer)         # Total charge/discharge cycles
    battery_health = Column(String)          # "excellent", "good", "fair", "poor"
    
    # Thermal Energy Storage
    thermal_energy_stored = Column(Float)    # kWh
    thermal_energy_released = Column(Float)  # kWh
    thermal_storage_temp = Column(Float)     # Celsius
    thermal_storage_efficiency = Column(Float) # Percentage
    
    # Water Storage Tank
    water_tank_level = Column(Float)         # Percentage
    water_tank_temperature = Column(Float)   # Celsius
    water_flow_rate = Column(Float)          # L/min

class OutputLoadData(Base):
    """Turbine, condenser, and load monitoring"""
    __tablename__ = "output_load_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Turbine operation
    turbine_rpm = Column(Float)              # RPM
    turbine_power_output = Column(Float)     # kW
    turbine_mechanical_faults = Column(JSON) # List of mechanical faults
    
    # Condenser status
    condenser_water_temp = Column(Float)     # Celsius
    condenser_flow_rate = Column(Float)      # L/min
    condenser_pressure = Column(Float)       # Bar
    
    # Critical/Non-critical loads
    critical_load_current = Column(Float)    # Amperes
    non_critical_load_current = Column(Float) # Amperes
    critical_load_status = Column(String)    # "active", "shed", "fault"
    non_critical_load_status = Column(String) # "active", "shed", "fault"
    load_scheduling_status = Column(String)  # "scheduled", "unscheduled", "error"

class SystemEfficiencyData(Base):
    """System efficiency calculations and targets"""
    __tablename__ = "system_efficiency_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Efficiency calculations
    overall_efficiency = Column(Float)       # Percentage
    solar_to_electrical_efficiency = Column(Float) # Percentage
    thermal_to_electrical_efficiency = Column(Float) # Percentage
    storage_efficiency = Column(Float)       # Percentage
    
    # Target tracking
    efficiency_target_15 = Column(Boolean)   # >15% target achieved
    efficiency_target_30 = Column(Boolean)   # >30% target achieved
    efficiency_trend = Column(String)        # "improving", "stable", "declining"
    
    # Historical comparison
    efficiency_vs_previous_hour = Column(Float) # Percentage change
    efficiency_vs_previous_day = Column(Float)  # Percentage change

class FaultAlertData(Base):
    """Comprehensive fault detection and alerting"""
    __tablename__ = "fault_alert_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Alert details
    alert_type = Column(String)              # "overheating", "low_soc", "pressure_drop", etc.
    alert_severity = Column(String)          # "low", "medium", "high", "critical"
    alert_message = Column(Text)             # Detailed alert message
    alert_source = Column(String)            # Which system component
    
    # Alert data
    current_value = Column(Float)            # Current measured value
    threshold_value = Column(Float)          # Threshold that triggered alert
    alert_duration = Column(Float)           # Minutes since alert started
    
    # Alert management
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String)             # User who resolved
    resolution_notes = Column(Text)

class PredictiveAnalyticsData(Base):
    """Solar forecasting and predictive analytics"""
    __tablename__ = "predictive_analytics_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Solar resource forecast
    solar_forecast_1h = Column(Float)        # Predicted solar generation 1 hour ahead
    solar_forecast_6h = Column(Float)        # Predicted solar generation 6 hours ahead
    solar_forecast_24h = Column(Float)       # Predicted solar generation 24 hours ahead
    solar_forecast_confidence = Column(Float) # Confidence level (0-100%)
    
    # Battery depletion estimates
    battery_backup_hours = Column(Float)     # Hours of backup remaining
    battery_depletion_rate = Column(Float)   # kWh/hour depletion rate
    critical_load_backup_hours = Column(Float) # Hours for critical loads only
    
    # Predicted outages
    predicted_outage_probability = Column(Float) # 0-100% probability
    predicted_outage_duration = Column(Float)    # Hours
    predicted_outage_cause = Column(String)      # Cause of predicted outage
    
    # Load predictions
    predicted_load_1h = Column(Float)        # Predicted load 1 hour ahead
    predicted_load_6h = Column(Float)        # Predicted load 6 hours ahead
    predicted_load_24h = Column(Float)       # Predicted load 24 hours ahead

# =============================================================================
# PYDANTIC MODELS FOR API VALIDATION
# =============================================================================

class SolarSystemDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    solar_irradiance: float = Field(..., ge=0, le=1500, description="Solar irradiance in W/m²")
    pv_output_power: float = Field(..., ge=0, le=5000, description="PV output power in Watts")
    pv_output_voltage: float = Field(..., ge=0, le=1000, description="PV output voltage in Volts")
    pv_efficiency: float = Field(..., ge=0, le=100, description="PV efficiency percentage")
    concentrator_position: float = Field(..., ge=0, le=360, description="Concentrator position in degrees")
    concentrator_alignment: float = Field(..., ge=0, le=360, description="Concentrator alignment in degrees")
    concentrated_energy_level: float = Field(..., ge=0, le=10000, description="Concentrated energy level in W/m²")
    teg_temperature_diff: float = Field(..., ge=0, le=500, description="TEG temperature differential in Celsius")
    teg_output_power: float = Field(..., ge=0, le=1000, description="TEG output power in Watts")
    teg_efficiency: float = Field(..., ge=0, le=100, description="TEG efficiency percentage")

class ThermalSystemDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    hot_water_temperature: float = Field(..., ge=0, le=600, description="Hot water temperature in Celsius")
    storage_tank_temperature: float = Field(..., ge=0, le=600, description="Storage tank temperature in Celsius")
    storage_tank_pressure: float = Field(..., ge=0, le=50, description="Storage tank pressure in Bar")
    energy_stored: float = Field(..., ge=0, le=1000, description="Energy stored in kWh")
    molten_salt_flow_rate: float = Field(..., ge=0, le=1000, description="Molten salt flow rate in L/min")
    molten_salt_inlet_temp: float = Field(..., ge=0, le=600, description="Molten salt inlet temperature in Celsius")
    molten_salt_outlet_temp: float = Field(..., ge=0, le=600, description="Molten salt outlet temperature in Celsius")
    pipe_integrity_status: Literal["healthy", "warning", "critical"] = Field(default="healthy")
    steam_output: float = Field(..., ge=0, le=10000, description="Steam output in kg/h")
    steam_pressure: float = Field(..., ge=0, le=100, description="Steam pressure in Bar")
    steam_temperature: float = Field(..., ge=0, le=600, description="Steam temperature in Celsius")
    steam_fault_alerts: Optional[List[str]] = Field(default=[])

class ConversionControlDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    inverter_input_voltage: float = Field(..., ge=0, le=1000, description="Inverter input voltage in Volts")
    inverter_output_voltage: float = Field(..., ge=0, le=1000, description="Inverter output voltage in Volts")
    inverter_conversion_efficiency: float = Field(..., ge=0, le=100, description="Inverter conversion efficiency percentage")
    inverter_operation_status: Literal["online", "offline", "fault"] = Field(default="online")
    controller_algorithm_health: Literal["healthy", "degraded", "fault"] = Field(default="healthy")
    controller_mode: Literal["grid", "islanded", "transition"] = Field(default="grid")
    scheduling_status: Literal["active", "inactive", "error"] = Field(default="active")
    switching_status: Literal["normal", "switching", "fault"] = Field(default="normal")
    controller_logs: Optional[List[Dict[str, Any]]] = Field(default=[])

class StorageSystemDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    battery_soc: float = Field(..., ge=0, le=100, description="Battery state of charge percentage")
    battery_charge_rate: float = Field(..., ge=0, le=1000, description="Battery charge rate in kW")
    battery_discharge_rate: float = Field(..., ge=0, le=1000, description="Battery discharge rate in kW")
    battery_temperature: float = Field(..., ge=-20, le=150, description="Battery temperature in Celsius")
    battery_cycles: int = Field(..., ge=0, description="Total battery cycles")
    battery_health: Literal["excellent", "good", "fair", "poor"] = Field(default="good")
    thermal_energy_stored: float = Field(..., ge=0, le=10000, description="Thermal energy stored in kWh")
    thermal_energy_released: float = Field(..., ge=0, le=10000, description="Thermal energy released in kWh")
    thermal_storage_temp: float = Field(..., ge=0, le=600, description="Thermal storage temperature in Celsius")
    thermal_storage_efficiency: float = Field(..., ge=0, le=100, description="Thermal storage efficiency percentage")
    water_tank_level: float = Field(..., ge=0, le=100, description="Water tank level percentage")
    water_tank_temperature: float = Field(..., ge=0, le=100, description="Water tank temperature in Celsius")
    water_flow_rate: float = Field(..., ge=0, le=1000, description="Water flow rate in L/min")

class OutputLoadDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    turbine_rpm: float = Field(..., ge=0, le=10000, description="Turbine RPM")
    turbine_power_output: float = Field(..., ge=0, le=5000, description="Turbine power output in kW")
    turbine_mechanical_faults: Optional[List[str]] = Field(default=[])
    condenser_water_temp: float = Field(..., ge=0, le=100, description="Condenser water temperature in Celsius")
    condenser_flow_rate: float = Field(..., ge=0, le=1000, description="Condenser flow rate in L/min")
    condenser_pressure: float = Field(..., ge=0, le=10, description="Condenser pressure in Bar")
    critical_load_current: float = Field(..., ge=0, le=1000, description="Critical load current in Amperes")
    non_critical_load_current: float = Field(..., ge=0, le=1000, description="Non-critical load current in Amperes")
    critical_load_status: Literal["active", "shed", "fault"] = Field(default="active")
    non_critical_load_status: Literal["active", "shed", "fault"] = Field(default="active")
    load_scheduling_status: Literal["scheduled", "unscheduled", "error"] = Field(default="scheduled")

class SystemEfficiencyDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    overall_efficiency: float = Field(..., ge=0, le=100, description="Overall system efficiency percentage")
    solar_to_electrical_efficiency: float = Field(..., ge=0, le=100, description="Solar to electrical efficiency percentage")
    thermal_to_electrical_efficiency: float = Field(..., ge=0, le=100, description="Thermal to electrical efficiency percentage")
    storage_efficiency: float = Field(..., ge=0, le=100, description="Storage efficiency percentage")
    efficiency_target_15: bool = Field(default=False, description=">15% efficiency target achieved")
    efficiency_target_30: bool = Field(default=False, description=">30% efficiency target achieved")
    efficiency_trend: Literal["improving", "stable", "declining"] = Field(default="stable")
    efficiency_vs_previous_hour: float = Field(default=0, description="Efficiency change vs previous hour")
    efficiency_vs_previous_day: float = Field(default=0, description="Efficiency change vs previous day")

class FaultAlertDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    alert_type: str = Field(..., max_length=100, description="Type of alert")
    alert_severity: Literal["low", "medium", "high", "critical"] = Field(default="medium")
    alert_message: str = Field(..., max_length=1000, description="Alert message")
    alert_source: str = Field(..., max_length=100, description="Source system component")
    current_value: float = Field(..., description="Current measured value")
    threshold_value: float = Field(..., description="Threshold value")
    alert_duration: float = Field(default=0, description="Alert duration in minutes")

class PredictiveAnalyticsDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    solar_forecast_1h: float = Field(..., ge=0, le=5000, description="Solar forecast 1 hour ahead in Watts")
    solar_forecast_6h: float = Field(..., ge=0, le=5000, description="Solar forecast 6 hours ahead in Watts")
    solar_forecast_24h: float = Field(..., ge=0, le=5000, description="Solar forecast 24 hours ahead in Watts")
    solar_forecast_confidence: float = Field(..., ge=0, le=100, description="Forecast confidence percentage")
    battery_backup_hours: float = Field(..., ge=0, le=100, description="Battery backup hours remaining")
    battery_depletion_rate: float = Field(..., ge=0, le=1000, description="Battery depletion rate in kWh/hour")
    critical_load_backup_hours: float = Field(..., ge=0, le=100, description="Critical load backup hours")
    predicted_outage_probability: float = Field(..., ge=0, le=100, description="Predicted outage probability percentage")
    predicted_outage_duration: float = Field(..., ge=0, le=168, description="Predicted outage duration in hours")
    predicted_outage_cause: str = Field(..., max_length=200, description="Predicted outage cause")
    predicted_load_1h: float = Field(..., ge=0, le=10000, description="Predicted load 1 hour ahead in Watts")
    predicted_load_6h: float = Field(..., ge=0, le=10000, description="Predicted load 6 hours ahead in Watts")
    predicted_load_24h: float = Field(..., ge=0, le=10000, description="Predicted load 24 hours ahead in Watts")

# Response models (inherit from create models with additional fields)
class SolarSystemDataResponse(SolarSystemDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ThermalSystemDataResponse(ThermalSystemDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ConversionControlDataResponse(ConversionControlDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class StorageSystemDataResponse(StorageSystemDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class OutputLoadDataResponse(OutputLoadDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SystemEfficiencyDataResponse(SystemEfficiencyDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class FaultAlertDataResponse(FaultAlertDataCreate):
    id: int
    timestamp: datetime
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_notes: Optional[str]
    
    class Config:
        from_attributes = True

class PredictiveAnalyticsDataResponse(PredictiveAnalyticsDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# COMPREHENSIVE SYSTEM STATUS MODEL
# =============================================================================

class ComprehensiveSystemStatus(BaseModel):
    """Comprehensive system status combining all monitoring data"""
    timestamp: datetime
    
    # Solar system status
    solar_irradiance: float
    pv_output_power: float
    pv_efficiency: float
    concentrator_health: str
    
    # Thermal system status
    hot_water_temperature: float
    storage_tank_pressure: float
    energy_stored: float
    steam_output: float
    
    # Conversion and control status
    inverter_efficiency: float
    controller_mode: str
    controller_health: str
    
    # Storage system status
    battery_soc: float
    battery_health: str
    thermal_storage_efficiency: float
    water_tank_level: float
    
    # Output and load status
    turbine_power_output: float
    critical_load_status: str
    non_critical_load_status: str
    
    # System efficiency
    overall_efficiency: float
    efficiency_target_15: bool
    efficiency_target_30: bool
    efficiency_trend: str
    
    # Alerts and faults
    active_alerts: int
    critical_alerts: int
    system_health: Literal["healthy", "warning", "critical", "offline"]
    
    # Predictive analytics
    battery_backup_hours: float
    solar_forecast_6h: float
    predicted_outage_probability: float
    
    # System metadata
    last_updated: datetime
    data_completeness: float  # Percentage of data points available

# Create all tables
Base.metadata.create_all(bind=engine)