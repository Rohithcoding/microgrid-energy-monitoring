"""
Comprehensive Alert and Fault Detection System for Hybrid Microgrid
=================================================================

This module provides a comprehensive alert system that monitors all aspects
of the hybrid microgrid system, detects faults and inefficiencies, and
provides actionable insights with real-time notifications.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlalchemy
from sqlalchemy.orm import Session

from comprehensive_models import (
    FaultAlertData, SessionLocal, SolarSystemData, ThermalSystemData,
    ConversionControlData, StorageSystemData, OutputLoadData, SystemEfficiencyData
)
from sensor_interfaces import SensorReading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    # Solar system alerts
    SOLAR_IRRADIANCE_LOW = "solar_irradiance_low"
    PV_OUTPUT_DEGRADED = "pv_output_degraded"
    CONCENTRATOR_MISALIGNED = "concentrator_misaligned"
    TEG_EFFICIENCY_LOW = "teg_efficiency_low"
    
    # Thermal system alerts
    HOT_WATER_TEMP_LOW = "hot_water_temp_low"
    HOT_WATER_TEMP_HIGH = "hot_water_temp_high"
    STORAGE_TANK_PRESSURE_LOW = "storage_tank_pressure_low"
    STORAGE_TANK_PRESSURE_HIGH = "storage_tank_pressure_high"
    MOLTEN_SALT_FLOW_LOW = "molten_salt_flow_low"
    STEAM_OUTPUT_LOW = "steam_output_low"
    PIPE_INTEGRITY_ISSUE = "pipe_integrity_issue"
    
    # Conversion and control alerts
    INVERTER_EFFICIENCY_LOW = "inverter_efficiency_low"
    INVERTER_FAULT = "inverter_fault"
    CONTROLLER_HEALTH_DEGRADED = "controller_health_degraded"
    CONTROLLER_FAULT = "controller_fault"
    GRID_SWITCHING_ISSUE = "grid_switching_issue"
    
    # Storage system alerts
    BATTERY_SOC_LOW = "battery_soc_low"
    BATTERY_SOC_CRITICAL = "battery_soc_critical"
    BATTERY_TEMP_HIGH = "battery_temp_high"
    BATTERY_TEMP_CRITICAL = "battery_temp_critical"
    BATTERY_HEALTH_POOR = "battery_health_poor"
    THERMAL_STORAGE_EFFICIENCY_LOW = "thermal_storage_efficiency_low"
    WATER_TANK_LEVEL_LOW = "water_tank_level_low"
    
    # Output and load alerts
    TURBINE_POWER_LOW = "turbine_power_low"
    TURBINE_MECHANICAL_FAULT = "turbine_mechanical_fault"
    CONDENSER_TEMP_HIGH = "condenser_temp_high"
    CONDENSER_PRESSURE_HIGH = "condenser_pressure_high"
    CRITICAL_LOAD_SHED = "critical_load_shed"
    NON_CRITICAL_LOAD_SHED = "non_critical_load_shed"
    
    # System efficiency alerts
    EFFICIENCY_TARGET_15_NOT_MET = "efficiency_target_15_not_met"
    EFFICIENCY_TARGET_30_NOT_MET = "efficiency_target_30_not_met"
    EFFICIENCY_DECLINING = "efficiency_declining"
    
    # General system alerts
    SYSTEM_OFFLINE = "system_offline"
    DATA_QUALITY_POOR = "data_quality_poor"
    COMMUNICATION_LOST = "communication_lost"
    MAINTENANCE_REQUIRED = "maintenance_required"

@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    alert_type: AlertType
    severity: AlertSeverity
    threshold_value: float
    comparison: str  # "gt", "lt", "eq", "gte", "lte"
    message_template: str
    action_required: str
    auto_resolve: bool = True
    cooldown_minutes: int = 5

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    severity: AlertSeverity
    message_template: str
    action_required: str
    auto_resolve: bool = True
    cooldown_minutes: int = 5

class AlertManager:
    """Manages alerts and fault detection"""
    
    def __init__(self):
        self.active_alerts: Dict[str, FaultAlertData] = {}
        self.alert_history: List[FaultAlertData] = []
        self.thresholds: Dict[AlertType, AlertThreshold] = {}
        self.rules: List[AlertRule] = []
        self.callbacks: List[Callable[[FaultAlertData], None]] = []
        self.is_running = False
        
        # Initialize default thresholds and rules
        self._initialize_default_thresholds()
        self._initialize_default_rules()
        
        # Performance metrics
        self.metrics = {
            'alerts_generated': 0,
            'alerts_resolved': 0,
            'false_positives': 0,
            'response_time_avg': 0,
            'start_time': None
        }
    
    def _initialize_default_thresholds(self):
        """Initialize default alert thresholds"""
        self.thresholds = {
            # Solar system thresholds
            AlertType.SOLAR_IRRADIANCE_LOW: AlertThreshold(
                alert_type=AlertType.SOLAR_IRRADIANCE_LOW,
                severity=AlertSeverity.MEDIUM,
                threshold_value=100,
                comparison="lt",
                message_template="Solar irradiance is low: {value} W/m² (threshold: {threshold} W/m²)",
                action_required="Check weather conditions and panel cleanliness"
            ),
            AlertType.PV_OUTPUT_DEGRADED: AlertThreshold(
                alert_type=AlertType.PV_OUTPUT_DEGRADED,
                severity=AlertSeverity.HIGH,
                threshold_value=200,
                comparison="lt",
                message_template="PV output is degraded: {value} W (threshold: {threshold} W)",
                action_required="Inspect PV panels for damage or dirt"
            ),
            AlertType.CONCENTRATOR_MISALIGNED: AlertThreshold(
                alert_type=AlertType.CONCENTRATOR_MISALIGNED,
                severity=AlertSeverity.HIGH,
                threshold_value=5,
                comparison="gt",
                message_template="Solar concentrator misaligned: {value}° (threshold: {threshold}°)",
                action_required="Realign solar concentrator"
            ),
            AlertType.TEG_EFFICIENCY_LOW: AlertThreshold(
                alert_type=AlertType.TEG_EFFICIENCY_LOW,
                severity=AlertSeverity.MEDIUM,
                threshold_value=3,
                comparison="lt",
                message_template="TEG efficiency is low: {value}% (threshold: {threshold}%)",
                action_required="Check TEG temperature differential"
            ),
            
            # Thermal system thresholds
            AlertType.HOT_WATER_TEMP_LOW: AlertThreshold(
                alert_type=AlertType.HOT_WATER_TEMP_LOW,
                severity=AlertSeverity.HIGH,
                threshold_value=450,
                comparison="lt",
                message_template="Hot water temperature is low: {value}°C (threshold: {threshold}°C)",
                action_required="Check thermal system and increase heating"
            ),
            AlertType.HOT_WATER_TEMP_HIGH: AlertThreshold(
                alert_type=AlertType.HOT_WATER_TEMP_HIGH,
                severity=AlertSeverity.CRITICAL,
                threshold_value=500,
                comparison="gt",
                message_template="Hot water temperature is high: {value}°C (threshold: {threshold}°C)",
                action_required="Immediate action required - reduce heating"
            ),
            AlertType.STORAGE_TANK_PRESSURE_LOW: AlertThreshold(
                alert_type=AlertType.STORAGE_TANK_PRESSURE_LOW,
                severity=AlertSeverity.HIGH,
                threshold_value=10,
                comparison="lt",
                message_template="Storage tank pressure is low: {value} Bar (threshold: {threshold} Bar)",
                action_required="Check for leaks and increase pressure"
            ),
            AlertType.STORAGE_TANK_PRESSURE_HIGH: AlertThreshold(
                alert_type=AlertType.STORAGE_TANK_PRESSURE_HIGH,
                severity=AlertSeverity.CRITICAL,
                threshold_value=20,
                comparison="gt",
                message_template="Storage tank pressure is high: {value} Bar (threshold: {threshold} Bar)",
                action_required="Immediate action required - reduce pressure"
            ),
            AlertType.MOLTEN_SALT_FLOW_LOW: AlertThreshold(
                alert_type=AlertType.MOLTEN_SALT_FLOW_LOW,
                severity=AlertSeverity.HIGH,
                threshold_value=80,
                comparison="lt",
                message_template="Molten salt flow rate is low: {value} L/min (threshold: {threshold} L/min)",
                action_required="Check pumps and flow system"
            ),
            AlertType.STEAM_OUTPUT_LOW: AlertThreshold(
                alert_type=AlertType.STEAM_OUTPUT_LOW,
                severity=AlertSeverity.MEDIUM,
                threshold_value=100,
                comparison="lt",
                message_template="Steam output is low: {value} kg/h (threshold: {threshold} kg/h)",
                action_required="Check steam generation system"
            ),
            
            # Conversion and control thresholds
            AlertType.INVERTER_EFFICIENCY_LOW: AlertThreshold(
                alert_type=AlertType.INVERTER_EFFICIENCY_LOW,
                severity=AlertSeverity.HIGH,
                threshold_value=15,
                comparison="lt",
                message_template="Inverter efficiency is low: {value}% (threshold: {threshold}%)",
                action_required="Check inverter operation and maintenance"
            ),
            AlertType.INVERTER_FAULT: AlertThreshold(
                alert_type=AlertType.INVERTER_FAULT,
                severity=AlertSeverity.CRITICAL,
                threshold_value=0,
                comparison="eq",
                message_template="Inverter fault detected: {value}",
                action_required="Immediate action required - check inverter"
            ),
            AlertType.CONTROLLER_HEALTH_DEGRADED: AlertThreshold(
                alert_type=AlertType.CONTROLLER_HEALTH_DEGRADED,
                severity=AlertSeverity.HIGH,
                threshold_value=50,
                comparison="lt",
                message_template="Controller health is degraded: {value}% (threshold: {threshold}%)",
                action_required="Check controller operation and logs"
            ),
            AlertType.CONTROLLER_FAULT: AlertThreshold(
                alert_type=AlertType.CONTROLLER_FAULT,
                severity=AlertSeverity.CRITICAL,
                threshold_value=0,
                comparison="eq",
                message_template="Controller fault detected: {value}",
                action_required="Immediate action required - check controller"
            ),
            
            # Storage system thresholds
            AlertType.BATTERY_SOC_LOW: AlertThreshold(
                alert_type=AlertType.BATTERY_SOC_LOW,
                severity=AlertSeverity.HIGH,
                threshold_value=20,
                comparison="lt",
                message_template="Battery SOC is low: {value}% (threshold: {threshold}%)",
                action_required="Monitor battery and consider charging"
            ),
            AlertType.BATTERY_SOC_CRITICAL: AlertThreshold(
                alert_type=AlertType.BATTERY_SOC_CRITICAL,
                severity=AlertSeverity.CRITICAL,
                threshold_value=10,
                comparison="lt",
                message_template="Battery SOC is critical: {value}% (threshold: {threshold}%)",
                action_required="Immediate action required - charge battery"
            ),
            AlertType.BATTERY_TEMP_HIGH: AlertThreshold(
                alert_type=AlertType.BATTERY_TEMP_HIGH,
                severity=AlertSeverity.HIGH,
                threshold_value=35,
                comparison="gt",
                message_template="Battery temperature is high: {value}°C (threshold: {threshold}°C)",
                action_required="Check battery cooling system"
            ),
            AlertType.BATTERY_TEMP_CRITICAL: AlertThreshold(
                alert_type=AlertType.BATTERY_TEMP_CRITICAL,
                severity=AlertSeverity.CRITICAL,
                threshold_value=50,
                comparison="gt",
                message_template="Battery temperature is critical: {value}°C (threshold: {threshold}°C)",
                action_required="Immediate action required - cool battery"
            ),
            AlertType.WATER_TANK_LEVEL_LOW: AlertThreshold(
                alert_type=AlertType.WATER_TANK_LEVEL_LOW,
                severity=AlertSeverity.MEDIUM,
                threshold_value=20,
                comparison="lt",
                message_template="Water tank level is low: {value}% (threshold: {threshold}%)",
                action_required="Refill water tank"
            ),
            
            # Output and load thresholds
            AlertType.TURBINE_POWER_LOW: AlertThreshold(
                alert_type=AlertType.TURBINE_POWER_LOW,
                severity=AlertSeverity.MEDIUM,
                threshold_value=100,
                comparison="lt",
                message_template="Turbine power output is low: {value} kW (threshold: {threshold} kW)",
                action_required="Check turbine operation"
            ),
            AlertType.CONDENSER_TEMP_HIGH: AlertThreshold(
                alert_type=AlertType.CONDENSER_TEMP_HIGH,
                severity=AlertSeverity.HIGH,
                threshold_value=80,
                comparison="gt",
                message_template="Condenser temperature is high: {value}°C (threshold: {threshold}°C)",
                action_required="Check condenser cooling system"
            ),
            AlertType.CRITICAL_LOAD_SHED: AlertThreshold(
                alert_type=AlertType.CRITICAL_LOAD_SHED,
                severity=AlertSeverity.CRITICAL,
                threshold_value=0,
                comparison="eq",
                message_template="Critical load has been shed: {value}",
                action_required="Immediate action required - restore critical load"
            ),
            
            # System efficiency thresholds
            AlertType.EFFICIENCY_TARGET_15_NOT_MET: AlertThreshold(
                alert_type=AlertType.EFFICIENCY_TARGET_15_NOT_MET,
                severity=AlertSeverity.MEDIUM,
                threshold_value=15,
                comparison="lt",
                message_template="System efficiency below 15% target: {value}% (threshold: {threshold}%)",
                action_required="Optimize system operation"
            ),
            AlertType.EFFICIENCY_TARGET_30_NOT_MET: AlertThreshold(
                alert_type=AlertType.EFFICIENCY_TARGET_30_NOT_MET,
                severity=AlertSeverity.HIGH,
                threshold_value=30,
                comparison="lt",
                message_template="System efficiency below 30% target: {value}% (threshold: {threshold}%)",
                action_required="System optimization required"
            )
        }
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        self.rules = [
            AlertRule(
                name="Solar System Degradation",
                description="Detects overall solar system performance degradation",
                conditions=[
                    {"sensor": "solar_irradiance", "operator": "lt", "value": 200},
                    {"sensor": "pv_output_power", "operator": "lt", "value": 300}
                ],
                severity=AlertSeverity.HIGH,
                message_template="Solar system performance degraded - irradiance: {solar_irradiance} W/m², PV output: {pv_output_power} W",
                action_required="Check solar system components and weather conditions"
            ),
            AlertRule(
                name="Thermal System Overheating",
                description="Detects thermal system overheating conditions",
                conditions=[
                    {"sensor": "hot_water_temperature", "operator": "gt", "value": 480},
                    {"sensor": "storage_tank_pressure", "operator": "gt", "value": 18}
                ],
                severity=AlertSeverity.CRITICAL,
                message_template="Thermal system overheating - temperature: {hot_water_temperature}°C, pressure: {storage_tank_pressure} Bar",
                action_required="Immediate action required - reduce thermal system load"
            ),
            AlertRule(
                name="Battery System Stress",
                description="Detects battery system stress conditions",
                conditions=[
                    {"sensor": "battery_soc", "operator": "lt", "value": 15},
                    {"sensor": "battery_temperature", "operator": "gt", "value": 40}
                ],
                severity=AlertSeverity.CRITICAL,
                message_template="Battery system stress - SOC: {battery_soc}%, temperature: {battery_temperature}°C",
                action_required="Immediate action required - address battery system issues"
            ),
            AlertRule(
                name="System Efficiency Decline",
                description="Detects system efficiency decline",
                conditions=[
                    {"sensor": "overall_efficiency", "operator": "lt", "value": 12},
                    {"sensor": "inverter_efficiency", "operator": "lt", "value": 18}
                ],
                severity=AlertSeverity.HIGH,
                message_template="System efficiency declining - overall: {overall_efficiency}%, inverter: {inverter_efficiency}%",
                action_required="System optimization and maintenance required"
            )
        ]
    
    def add_callback(self, callback: Callable[[FaultAlertData], None]):
        """Add callback for alert notifications"""
        self.callbacks.append(callback)
    
    def add_threshold(self, threshold: AlertThreshold):
        """Add or update alert threshold"""
        self.thresholds[threshold.alert_type] = threshold
        logger.info(f"Added threshold for {threshold.alert_type.value}")
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
        logger.info(f"Added rule: {rule.name}")
    
    async def check_sensor_reading(self, reading: SensorReading) -> List[FaultAlertData]:
        """Check sensor reading against thresholds and rules"""
        alerts = []
        
        try:
            # Check against thresholds
            threshold_alerts = self._check_thresholds(reading)
            alerts.extend(threshold_alerts)
            
            # Check against rules (requires multiple sensor readings)
            # This would be called with a collection of readings
            
            # Process alerts
            for alert in alerts:
                await self._process_alert(alert)
            
            return alerts
        
        except Exception as e:
            logger.error(f"Error checking sensor reading: {e}")
            return []
    
    def _check_thresholds(self, reading: SensorReading) -> List[FaultAlertData]:
        """Check sensor reading against thresholds"""
        alerts = []
        
        # Map sensor IDs to alert types
        sensor_alert_mapping = {
            'solar_irradiance_001': AlertType.SOLAR_IRRADIANCE_LOW,
            'pv_output_001': AlertType.PV_OUTPUT_DEGRADED,
            'teg_001': AlertType.TEG_EFFICIENCY_LOW,
            'hot_water_temp_001': AlertType.HOT_WATER_TEMP_LOW,
            'tank_pressure_001': AlertType.STORAGE_TANK_PRESSURE_LOW,
            'molten_salt_flow_001': AlertType.MOLTEN_SALT_FLOW_LOW,
            'inverter_efficiency_001': AlertType.INVERTER_EFFICIENCY_LOW,
            'controller_health_001': AlertType.CONTROLLER_HEALTH_DEGRADED,
            'battery_soc_001': AlertType.BATTERY_SOC_LOW,
            'battery_temp_001': AlertType.BATTERY_TEMP_HIGH,
            'turbine_power_001': AlertType.TURBINE_POWER_LOW
        }
        
        sensor_id = getattr(reading, 'sensor_id', 'unknown')
        alert_type = sensor_alert_mapping.get(sensor_id)
        
        if alert_type and alert_type in self.thresholds:
            threshold = self.thresholds[alert_type]
            
            # Check if threshold is met
            if self._evaluate_condition(reading.value, threshold.comparison, threshold.threshold_value):
                # Check if alert already exists
                alert_key = f"{alert_type.value}_{sensor_id}"
                if alert_key not in self.active_alerts:
                    alert = FaultAlertData(
                        timestamp=datetime.utcnow(),
                        alert_type=alert_type.value,
                        alert_severity=threshold.severity.value,
                        alert_message=threshold.message_template.format(
                            value=reading.value,
                            threshold=threshold.threshold_value
                        ),
                        alert_source=sensor_id,
                        current_value=reading.value,
                        threshold_value=threshold.threshold_value,
                        alert_duration=0
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate condition based on operator"""
        if operator == "gt":
            return value > threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "eq":
            return value == threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lte":
            return value <= threshold
        else:
            return False
    
    async def _process_alert(self, alert: FaultAlertData):
        """Process and store alert"""
        try:
            # Store in active alerts
            alert_key = f"{alert.alert_type}_{alert.alert_source}"
            self.active_alerts[alert_key] = alert
            
            # Add to history
            self.alert_history.append(alert)
            
            # Store in database
            await self._store_alert_in_database(alert)
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            # Update metrics
            self.metrics['alerts_generated'] += 1
            
            logger.info(f"Alert generated: {alert.alert_type} - {alert.alert_message}")
        
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    async def _store_alert_in_database(self, alert: FaultAlertData):
        """Store alert in database"""
        db = SessionLocal()
        try:
            db.add(alert)
            db.commit()
            logger.debug(f"Stored alert {alert.alert_type} in database")
        except Exception as e:
            logger.error(f"Database error storing alert: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def resolve_alert(self, alert_id: int, resolved_by: str = "system", resolution_notes: str = ""):
        """Resolve an alert"""
        db = SessionLocal()
        try:
            alert = db.query(FaultAlertData).filter(FaultAlertData.id == alert_id).first()
            if alert:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by
                alert.resolution_notes = resolution_notes
                
                # Remove from active alerts
                alert_key = f"{alert.alert_type}_{alert.alert_source}"
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
                
                db.commit()
                self.metrics['alerts_resolved'] += 1
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def auto_resolve_alerts(self):
        """Automatically resolve alerts that meet resolution criteria"""
        resolved_count = 0
        
        for alert_key, alert in list(self.active_alerts.items()):
            try:
                # Check if alert should be auto-resolved
                if self._should_auto_resolve(alert):
                    await self.resolve_alert(alert.id, "system", "Auto-resolved based on current conditions")
                    resolved_count += 1
            except Exception as e:
                logger.error(f"Error auto-resolving alert {alert_key}: {e}")
        
        if resolved_count > 0:
            logger.info(f"Auto-resolved {resolved_count} alerts")
    
    def _should_auto_resolve(self, alert: FaultAlertData) -> bool:
        """Check if alert should be auto-resolved"""
        # Simple auto-resolution logic
        # In a real system, this would check current sensor values
        
        # Auto-resolve if alert is older than 30 minutes and severity is low
        if alert.alert_severity == "low" and alert.alert_duration > 30:
            return True
        
        # Auto-resolve if alert is older than 2 hours and severity is medium
        if alert.alert_severity == "medium" and alert.alert_duration > 120:
            return True
        
        return False
    
    def get_active_alerts(self) -> List[FaultAlertData]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[FaultAlertData]:
        """Get alerts by severity"""
        return [alert for alert in self.active_alerts.values() if alert.alert_severity == severity.value]
    
    def get_critical_alerts(self) -> List[FaultAlertData]:
        """Get all critical alerts"""
        return self.get_alerts_by_severity(AlertSeverity.CRITICAL)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        resolved_alerts = total_alerts - active_alerts
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(self.get_alerts_by_severity(severity))
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'severity_counts': severity_counts,
            'metrics': self.metrics.copy()
        }
    
    async def start(self):
        """Start the alert system"""
        if self.is_running:
            logger.warning("Alert system is already running")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.utcnow()
        
        logger.info("Alert system started")
    
    async def stop(self):
        """Stop the alert system"""
        if not self.is_running:
            logger.warning("Alert system is not running")
            return
        
        self.is_running = False
        logger.info("Alert system stopped")

class FaultDetectionEngine:
    """Advanced fault detection engine using pattern recognition"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.patterns: Dict[str, Any] = {}
        self.is_running = False
    
    def add_pattern(self, name: str, pattern: Dict[str, Any]):
        """Add fault detection pattern"""
        self.patterns[name] = pattern
        logger.info(f"Added fault detection pattern: {name}")
    
    async def analyze_sensor_data(self, sensor_data: Dict[str, List[SensorReading]]) -> List[FaultAlertData]:
        """Analyze sensor data for fault patterns"""
        alerts = []
        
        try:
            # Analyze each pattern
            for pattern_name, pattern in self.patterns.items():
                pattern_alerts = await self._analyze_pattern(pattern_name, pattern, sensor_data)
                alerts.extend(pattern_alerts)
            
            return alerts
        
        except Exception as e:
            logger.error(f"Error analyzing sensor data: {e}")
            return []
    
    async def _analyze_pattern(self, pattern_name: str, pattern: Dict[str, Any], sensor_data: Dict[str, List[SensorReading]]) -> List[FaultAlertData]:
        """Analyze specific fault pattern"""
        alerts = []
        
        try:
            # Get required sensor data
            required_sensors = pattern.get('required_sensors', [])
            sensor_readings = {}
            
            for sensor_id in required_sensors:
                if sensor_id in sensor_data and sensor_data[sensor_id]:
                    sensor_readings[sensor_id] = sensor_data[sensor_id][-1]  # Get latest reading
            
            # Check if all required sensors have data
            if len(sensor_readings) != len(required_sensors):
                return alerts
            
            # Evaluate pattern conditions
            if self._evaluate_pattern_conditions(pattern, sensor_readings):
                alert = FaultAlertData(
                    timestamp=datetime.utcnow(),
                    alert_type=f"pattern_{pattern_name}",
                    alert_severity=pattern.get('severity', 'medium'),
                    alert_message=pattern.get('message', f"Fault pattern detected: {pattern_name}"),
                    alert_source="fault_detection_engine",
                    current_value=0,
                    threshold_value=0,
                    alert_duration=0
                )
                alerts.append(alert)
            
            return alerts
        
        except Exception as e:
            logger.error(f"Error analyzing pattern {pattern_name}: {e}")
            return []
    
    def _evaluate_pattern_conditions(self, pattern: Dict[str, Any], sensor_readings: Dict[str, SensorReading]) -> bool:
        """Evaluate pattern conditions"""
        conditions = pattern.get('conditions', [])
        
        for condition in conditions:
            sensor_id = condition.get('sensor')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if sensor_id in sensor_readings:
                sensor_value = sensor_readings[sensor_id].value
                if not self._evaluate_condition(sensor_value, operator, value):
                    return False
            else:
                return False
        
        return True
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate condition based on operator"""
        if operator == "gt":
            return value > threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "eq":
            return value == threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lte":
            return value <= threshold
        else:
            return False
    
    async def start(self):
        """Start the fault detection engine"""
        if self.is_running:
            logger.warning("Fault detection engine is already running")
            return
        
        self.is_running = True
        logger.info("Fault detection engine started")
    
    async def stop(self):
        """Stop the fault detection engine"""
        if not self.is_running:
            logger.warning("Fault detection engine is not running")
            return
        
        self.is_running = False
        logger.info("Fault detection engine stopped")

# Example usage and testing
async def main():
    """Example usage of the alert system"""
    # Create alert manager
    alert_manager = AlertManager()
    
    # Add callback to log alerts
    def log_alert(alert: FaultAlertData):
        logger.info(f"ALERT: {alert.alert_severity.upper()} - {alert.alert_message}")
    
    alert_manager.add_callback(log_alert)
    
    # Start alert system
    await alert_manager.start()
    
    # Create fault detection engine
    fault_engine = FaultDetectionEngine(alert_manager)
    
    # Add fault detection pattern
    fault_engine.add_pattern("thermal_overheating", {
        'required_sensors': ['hot_water_temp_001', 'tank_pressure_001'],
        'conditions': [
            {'sensor': 'hot_water_temp_001', 'operator': 'gt', 'value': 480},
            {'sensor': 'tank_pressure_001', 'operator': 'gt', 'value': 18}
        ],
        'severity': 'critical',
        'message': 'Thermal system overheating detected'
    })
    
    await fault_engine.start()
    
    # Simulate sensor readings
    from sensor_interfaces import SensorReading
    
    # Simulate high temperature and pressure
    high_temp_reading = SensorReading(
        timestamp=datetime.utcnow(),
        value=485,
        unit="°C",
        quality="warning",
        metadata={}
    )
    high_temp_reading.sensor_id = "hot_water_temp_001"
    
    high_pressure_reading = SensorReading(
        timestamp=datetime.utcnow(),
        value=19,
        unit="Bar",
        quality="warning",
        metadata={}
    )
    high_pressure_reading.sensor_id = "tank_pressure_001"
    
    # Check readings
    await alert_manager.check_sensor_reading(high_temp_reading)
    await alert_manager.check_sensor_reading(high_pressure_reading)
    
    # Analyze pattern
    sensor_data = {
        'hot_water_temp_001': [high_temp_reading],
        'tank_pressure_001': [high_pressure_reading]
    }
    await fault_engine.analyze_sensor_data(sensor_data)
    
    # Get statistics
    stats = alert_manager.get_alert_statistics()
    logger.info(f"Alert statistics: {stats}")
    
    # Stop systems
    await fault_engine.stop()
    await alert_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())