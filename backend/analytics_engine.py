"""
Comprehensive Analytics Engine for Hybrid Microgrid System
=========================================================

This module provides comprehensive analytics including efficiency calculations,
predictive analytics, performance metrics, and actionable insights for the
hybrid microgrid monitoring system.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from comprehensive_models import (
    SessionLocal, SolarSystemData, ThermalSystemData, ConversionControlData,
    StorageSystemData, OutputLoadData, SystemEfficiencyData, PredictiveAnalyticsData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EfficiencyTarget(Enum):
    """Efficiency targets"""
    TARGET_15 = 15.0  # 15% efficiency target
    TARGET_30 = 30.0  # 30% efficiency target

@dataclass
class EfficiencyMetrics:
    """Efficiency metrics data structure"""
    timestamp: datetime
    overall_efficiency: float
    solar_to_electrical_efficiency: float
    thermal_to_electrical_efficiency: float
    storage_efficiency: float
    inverter_efficiency: float
    system_availability: float
    energy_yield: float
    capacity_factor: float

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    total_generation: float
    total_consumption: float
    net_energy: float
    peak_generation: float
    peak_consumption: float
    load_factor: float
    generation_variability: float
    consumption_variability: float

@dataclass
class PredictiveInsight:
    """Predictive insight data structure"""
    timestamp: datetime
    insight_type: str
    confidence: float
    prediction_horizon: int  # hours
    predicted_value: float
    current_value: float
    trend: str
    recommendation: str

class AnalyticsEngine:
    """Comprehensive analytics engine for microgrid system"""
    
    def __init__(self):
        self.is_running = False
        self.efficiency_history: List[EfficiencyMetrics] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.predictive_insights: List[PredictiveInsight] = []
        
        # Performance metrics
        self.metrics = {
            'calculations_performed': 0,
            'predictions_generated': 0,
            'insights_generated': 0,
            'start_time': None
        }
    
    async def calculate_system_efficiency(self, hours: int = 24) -> EfficiencyMetrics:
        """Calculate comprehensive system efficiency metrics"""
        try:
            db = SessionLocal()
            
            # Get data for the specified time period
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get solar system data
            solar_data = db.query(SolarSystemData).filter(
                and_(SolarSystemData.timestamp >= start_time, SolarSystemData.timestamp <= end_time)
            ).all()
            
            # Get thermal system data
            thermal_data = db.query(ThermalSystemData).filter(
                and_(ThermalSystemData.timestamp >= start_time, ThermalSystemData.timestamp <= end_time)
            ).all()
            
            # Get conversion control data
            conversion_data = db.query(ConversionControlData).filter(
                and_(ConversionControlData.timestamp >= start_time, ConversionControlData.timestamp <= end_time)
            ).all()
            
            # Get storage system data
            storage_data = db.query(StorageSystemData).filter(
                and_(StorageSystemData.timestamp >= start_time, StorageSystemData.timestamp <= end_time)
            ).all()
            
            # Get output load data
            output_data = db.query(OutputLoadData).filter(
                and_(OutputLoadData.timestamp >= start_time, OutputLoadData.timestamp <= end_time)
            ).all()
            
            db.close()
            
            # Calculate efficiency metrics
            efficiency_metrics = self._calculate_efficiency_metrics(
                solar_data, thermal_data, conversion_data, storage_data, output_data
            )
            
            # Store in history
            self.efficiency_history.append(efficiency_metrics)
            if len(self.efficiency_history) > 1000:  # Keep last 1000 entries
                self.efficiency_history.pop(0)
            
            self.metrics['calculations_performed'] += 1
            
            return efficiency_metrics
        
        except Exception as e:
            logger.error(f"Error calculating system efficiency: {e}")
            return None
    
    def _calculate_efficiency_metrics(self, solar_data: List, thermal_data: List, 
                                    conversion_data: List, storage_data: List, 
                                    output_data: List) -> EfficiencyMetrics:
        """Calculate efficiency metrics from sensor data"""
        try:
            # Solar to electrical efficiency
            solar_efficiency = 0
            if solar_data:
                total_irradiance = sum(d.solar_irradiance for d in solar_data if d.solar_irradiance)
                total_pv_output = sum(d.pv_output_power for d in solar_data if d.pv_output_power)
                if total_irradiance > 0:
                    # Assuming 10 m² panel area
                    panel_area = 10.0
                    theoretical_power = total_irradiance * panel_area
                    solar_efficiency = (total_pv_output / theoretical_power) * 100 if theoretical_power > 0 else 0
            
            # Thermal to electrical efficiency
            thermal_efficiency = 0
            if thermal_data and output_data:
                total_thermal_energy = sum(d.energy_stored for d in thermal_data if d.energy_stored)
                total_turbine_output = sum(d.turbine_power_output for d in output_data if d.turbine_power_output)
                if total_thermal_energy > 0:
                    thermal_efficiency = (total_turbine_output / total_thermal_energy) * 100
            
            # Storage efficiency
            storage_efficiency = 0
            if storage_data:
                avg_soc = np.mean([d.battery_soc for d in storage_data if d.battery_soc is not None])
                storage_efficiency = avg_soc if avg_soc is not None else 0
            
            # Inverter efficiency
            inverter_efficiency = 0
            if conversion_data:
                avg_inverter_eff = np.mean([d.inverter_conversion_efficiency for d in conversion_data if d.inverter_conversion_efficiency is not None])
                inverter_efficiency = avg_inverter_eff if avg_inverter_eff is not None else 0
            
            # Overall efficiency
            overall_efficiency = (solar_efficiency + thermal_efficiency) * (inverter_efficiency / 100) * (storage_efficiency / 100)
            
            # System availability
            system_availability = self._calculate_system_availability(solar_data, thermal_data, conversion_data, storage_data, output_data)
            
            # Energy yield
            energy_yield = self._calculate_energy_yield(solar_data, thermal_data, output_data)
            
            # Capacity factor
            capacity_factor = self._calculate_capacity_factor(solar_data, thermal_data, output_data)
            
            return EfficiencyMetrics(
                timestamp=datetime.utcnow(),
                overall_efficiency=round(overall_efficiency, 2),
                solar_to_electrical_efficiency=round(solar_efficiency, 2),
                thermal_to_electrical_efficiency=round(thermal_efficiency, 2),
                storage_efficiency=round(storage_efficiency, 2),
                inverter_efficiency=round(inverter_efficiency, 2),
                system_availability=round(system_availability, 2),
                energy_yield=round(energy_yield, 2),
                capacity_factor=round(capacity_factor, 2)
            )
        
        except Exception as e:
            logger.error(f"Error calculating efficiency metrics: {e}")
            return EfficiencyMetrics(
                timestamp=datetime.utcnow(),
                overall_efficiency=0,
                solar_to_electrical_efficiency=0,
                thermal_to_electrical_efficiency=0,
                storage_efficiency=0,
                inverter_efficiency=0,
                system_availability=0,
                energy_yield=0,
                capacity_factor=0
            )
    
    def _calculate_system_availability(self, solar_data: List, thermal_data: List, 
                                     conversion_data: List, storage_data: List, 
                                     output_data: List) -> float:
        """Calculate system availability percentage"""
        try:
            total_data_points = 0
            available_data_points = 0
            
            # Check solar system availability
            if solar_data:
                total_data_points += len(solar_data)
                available_data_points += len([d for d in solar_data if d.solar_irradiance is not None and d.solar_irradiance > 0])
            
            # Check thermal system availability
            if thermal_data:
                total_data_points += len(thermal_data)
                available_data_points += len([d for d in thermal_data if d.hot_water_temperature is not None and d.hot_water_temperature > 0])
            
            # Check conversion system availability
            if conversion_data:
                total_data_points += len(conversion_data)
                available_data_points += len([d for d in conversion_data if d.inverter_operation_status == "online"])
            
            # Check storage system availability
            if storage_data:
                total_data_points += len(storage_data)
                available_data_points += len([d for d in storage_data if d.battery_soc is not None and d.battery_soc > 0])
            
            # Check output system availability
            if output_data:
                total_data_points += len(output_data)
                available_data_points += len([d for d in output_data if d.turbine_power_output is not None and d.turbine_power_output > 0])
            
            if total_data_points > 0:
                return (available_data_points / total_data_points) * 100
            return 0
        
        except Exception as e:
            logger.error(f"Error calculating system availability: {e}")
            return 0
    
    def _calculate_energy_yield(self, solar_data: List, thermal_data: List, output_data: List) -> float:
        """Calculate energy yield in kWh"""
        try:
            total_yield = 0
            
            # Solar energy yield
            if solar_data:
                solar_yield = sum(d.pv_output_power for d in solar_data if d.pv_output_power) / 1000  # Convert to kWh
                total_yield += solar_yield
            
            # Thermal energy yield
            if thermal_data:
                thermal_yield = sum(d.energy_stored for d in thermal_data if d.energy_stored)
                total_yield += thermal_yield
            
            # Turbine energy yield
            if output_data:
                turbine_yield = sum(d.turbine_power_output for d in output_data if d.turbine_power_output) / 1000  # Convert to kWh
                total_yield += turbine_yield
            
            return total_yield
        
        except Exception as e:
            logger.error(f"Error calculating energy yield: {e}")
            return 0
    
    def _calculate_capacity_factor(self, solar_data: List, thermal_data: List, output_data: List) -> float:
        """Calculate capacity factor percentage"""
        try:
            # Define installed capacity (in kW)
            solar_capacity = 2.0  # 2 kW solar
            thermal_capacity = 1.0  # 1 kW thermal
            turbine_capacity = 1.0  # 1 kW turbine
            total_capacity = solar_capacity + thermal_capacity + turbine_capacity
            
            if total_capacity == 0:
                return 0
            
            # Calculate actual generation
            actual_generation = 0
            
            if solar_data:
                avg_solar_power = np.mean([d.pv_output_power for d in solar_data if d.pv_output_power]) / 1000  # Convert to kW
                actual_generation += avg_solar_power
            
            if thermal_data:
                avg_thermal_power = np.mean([d.energy_stored for d in thermal_data if d.energy_stored]) / 1000  # Convert to kW
                actual_generation += avg_thermal_power
            
            if output_data:
                avg_turbine_power = np.mean([d.turbine_power_output for d in output_data if d.turbine_power_output]) / 1000  # Convert to kW
                actual_generation += avg_turbine_power
            
            # Calculate capacity factor
            capacity_factor = (actual_generation / total_capacity) * 100
            
            return capacity_factor
        
        except Exception as e:
            logger.error(f"Error calculating capacity factor: {e}")
            return 0
    
    async def calculate_performance_metrics(self, hours: int = 24) -> PerformanceMetrics:
        """Calculate system performance metrics"""
        try:
            db = SessionLocal()
            
            # Get data for the specified time period
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get solar generation data
            solar_data = db.query(SolarSystemData).filter(
                and_(SolarSystemData.timestamp >= start_time, SolarSystemData.timestamp <= end_time)
            ).all()
            
            # Get output data
            output_data = db.query(OutputLoadData).filter(
                and_(OutputLoadData.timestamp >= start_time, OutputLoadData.timestamp <= end_time)
            ).all()
            
            db.close()
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(solar_data, output_data)
            
            # Store in history
            self.performance_history.append(performance_metrics)
            if len(self.performance_history) > 1000:  # Keep last 1000 entries
                self.performance_history.pop(0)
            
            self.metrics['calculations_performed'] += 1
            
            return performance_metrics
        
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return None
    
    def _calculate_performance_metrics(self, solar_data: List, output_data: List) -> PerformanceMetrics:
        """Calculate performance metrics from sensor data"""
        try:
            # Total generation
            total_generation = 0
            if solar_data:
                total_generation = sum(d.pv_output_power for d in solar_data if d.pv_output_power) / 1000  # Convert to kWh
            
            # Total consumption
            total_consumption = 0
            if output_data:
                total_consumption = sum(d.critical_load_current + d.non_critical_load_current for d in output_data if d.critical_load_current and d.non_critical_load_current) / 1000  # Convert to kWh
            
            # Net energy
            net_energy = total_generation - total_consumption
            
            # Peak generation
            peak_generation = 0
            if solar_data:
                peak_generation = max(d.pv_output_power for d in solar_data if d.pv_output_power) / 1000  # Convert to kW
            
            # Peak consumption
            peak_consumption = 0
            if output_data:
                peak_consumption = max(d.critical_load_current + d.non_critical_load_current for d in output_data if d.critical_load_current and d.non_critical_load_current) / 1000  # Convert to kW
            
            # Load factor
            load_factor = 0
            if peak_consumption > 0:
                load_factor = (total_consumption / peak_consumption) * 100
            
            # Generation variability
            generation_variability = 0
            if solar_data and len(solar_data) > 1:
                pv_powers = [d.pv_output_power for d in solar_data if d.pv_output_power]
                if len(pv_powers) > 1:
                    generation_variability = np.std(pv_powers) / np.mean(pv_powers) * 100 if np.mean(pv_powers) > 0 else 0
            
            # Consumption variability
            consumption_variability = 0
            if output_data and len(output_data) > 1:
                consumption_values = [d.critical_load_current + d.non_critical_load_current for d in output_data if d.critical_load_current and d.non_critical_load_current]
                if len(consumption_values) > 1:
                    consumption_variability = np.std(consumption_values) / np.mean(consumption_values) * 100 if np.mean(consumption_values) > 0 else 0
            
            return PerformanceMetrics(
                timestamp=datetime.utcnow(),
                total_generation=round(total_generation, 2),
                total_consumption=round(total_consumption, 2),
                net_energy=round(net_energy, 2),
                peak_generation=round(peak_generation, 2),
                peak_consumption=round(peak_consumption, 2),
                load_factor=round(load_factor, 2),
                generation_variability=round(generation_variability, 2),
                consumption_variability=round(consumption_variability, 2)
            )
        
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.utcnow(),
                total_generation=0,
                total_consumption=0,
                net_energy=0,
                peak_generation=0,
                peak_consumption=0,
                load_factor=0,
                generation_variability=0,
                consumption_variability=0
            )
    
    async def generate_predictive_insights(self, hours: int = 24) -> List[PredictiveInsight]:
        """Generate predictive insights based on historical data"""
        try:
            insights = []
            
            # Get historical data
            db = SessionLocal()
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get solar data
            solar_data = db.query(SolarSystemData).filter(
                and_(SolarSystemData.timestamp >= start_time, SolarSystemData.timestamp <= end_time)
            ).order_by(SolarSystemData.timestamp).all()
            
            # Get storage data
            storage_data = db.query(StorageSystemData).filter(
                and_(StorageSystemData.timestamp >= start_time, StorageSystemData.timestamp <= end_time)
            ).order_by(StorageSystemData.timestamp).all()
            
            # Get efficiency data
            efficiency_data = db.query(SystemEfficiencyData).filter(
                and_(SystemEfficiencyData.timestamp >= start_time, SystemEfficiencyData.timestamp <= end_time)
            ).order_by(SystemEfficiencyData.timestamp).all()
            
            db.close()
            
            # Generate insights
            insights.extend(self._predict_solar_generation(solar_data))
            insights.extend(self._predict_battery_depletion(storage_data))
            insights.extend(self._predict_efficiency_trends(efficiency_data))
            insights.extend(self._predict_maintenance_needs(solar_data, storage_data, efficiency_data))
            
            # Store insights
            self.predictive_insights.extend(insights)
            if len(self.predictive_insights) > 100:  # Keep last 100 insights
                self.predictive_insights = self.predictive_insights[-100:]
            
            self.metrics['insights_generated'] += len(insights)
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            return []
    
    def _predict_solar_generation(self, solar_data: List) -> List[PredictiveInsight]:
        """Predict solar generation trends"""
        insights = []
        
        try:
            if len(solar_data) < 10:
                return insights
            
            # Get recent solar generation values
            recent_powers = [d.pv_output_power for d in solar_data[-10:] if d.pv_output_power]
            
            if len(recent_powers) < 5:
                return insights
            
            # Calculate trend
            trend = "stable"
            if len(recent_powers) >= 3:
                recent_avg = np.mean(recent_powers[-3:])
                earlier_avg = np.mean(recent_powers[:-3])
                if recent_avg > earlier_avg * 1.1:
                    trend = "increasing"
                elif recent_avg < earlier_avg * 0.9:
                    trend = "decreasing"
            
            # Predict next hour
            current_power = recent_powers[-1]
            predicted_power = current_power
            
            if trend == "increasing":
                predicted_power = current_power * 1.1
            elif trend == "decreasing":
                predicted_power = current_power * 0.9
            
            insight = PredictiveInsight(
                timestamp=datetime.utcnow(),
                insight_type="solar_generation",
                confidence=75.0,
                prediction_horizon=1,
                predicted_value=predicted_power,
                current_value=current_power,
                trend=trend,
                recommendation=f"Solar generation is {trend}. Expected output in 1 hour: {predicted_power:.1f}W"
            )
            insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error predicting solar generation: {e}")
        
        return insights
    
    def _predict_battery_depletion(self, storage_data: List) -> List[PredictiveInsight]:
        """Predict battery depletion"""
        insights = []
        
        try:
            if len(storage_data) < 5:
                return insights
            
            # Get recent SOC values
            recent_socs = [d.battery_soc for d in storage_data[-5:] if d.battery_soc is not None]
            
            if len(recent_socs) < 3:
                return insights
            
            # Calculate depletion rate
            soc_change = recent_socs[-1] - recent_socs[0]
            time_hours = 5  # Assuming 5 data points over 5 hours
            depletion_rate = abs(soc_change) / time_hours if time_hours > 0 else 0
            
            # Predict backup hours
            current_soc = recent_socs[-1]
            backup_hours = current_soc / depletion_rate if depletion_rate > 0 else 999
            
            # Generate insight
            if backup_hours < 24:
                insight = PredictiveInsight(
                    timestamp=datetime.utcnow(),
                    insight_type="battery_depletion",
                    confidence=80.0,
                    prediction_horizon=int(backup_hours),
                    predicted_value=backup_hours,
                    current_value=current_soc,
                    trend="depleting",
                    recommendation=f"Battery backup: {backup_hours:.1f} hours remaining. Consider charging or reducing load."
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error predicting battery depletion: {e}")
        
        return insights
    
    def _predict_efficiency_trends(self, efficiency_data: List) -> List[PredictiveInsight]:
        """Predict efficiency trends"""
        insights = []
        
        try:
            if len(efficiency_data) < 5:
                return insights
            
            # Get recent efficiency values
            recent_efficiencies = [d.overall_efficiency for d in efficiency_data[-5:] if d.overall_efficiency is not None]
            
            if len(recent_efficiencies) < 3:
                return insights
            
            # Calculate trend
            trend = "stable"
            if len(recent_efficiencies) >= 3:
                recent_avg = np.mean(recent_efficiencies[-3:])
                earlier_avg = np.mean(recent_efficiencies[:-3])
                if recent_avg > earlier_avg * 1.05:
                    trend = "improving"
                elif recent_avg < earlier_avg * 0.95:
                    trend = "declining"
            
            # Generate insight
            current_efficiency = recent_efficiencies[-1]
            if trend == "declining" and current_efficiency < 15:
                insight = PredictiveInsight(
                    timestamp=datetime.utcnow(),
                    insight_type="efficiency_trend",
                    confidence=70.0,
                    prediction_horizon=24,
                    predicted_value=current_efficiency * 0.95,
                    current_value=current_efficiency,
                    trend=trend,
                    recommendation="System efficiency is declining. Schedule maintenance and optimization."
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error predicting efficiency trends: {e}")
        
        return insights
    
    def _predict_maintenance_needs(self, solar_data: List, storage_data: List, efficiency_data: List) -> List[PredictiveInsight]:
        """Predict maintenance needs"""
        insights = []
        
        try:
            # Check for maintenance indicators
            maintenance_needed = False
            maintenance_reasons = []
            
            # Check solar system
            if solar_data:
                recent_powers = [d.pv_output_power for d in solar_data[-10:] if d.pv_output_power]
                if recent_powers:
                    avg_power = np.mean(recent_powers)
                    if avg_power < 200:  # Low power output
                        maintenance_needed = True
                        maintenance_reasons.append("Low solar output")
            
            # Check storage system
            if storage_data:
                recent_socs = [d.battery_soc for d in storage_data[-10:] if d.battery_soc is not None]
                if recent_socs:
                    avg_soc = np.mean(recent_socs)
                    if avg_soc < 30:  # Low SOC
                        maintenance_needed = True
                        maintenance_reasons.append("Low battery SOC")
            
            # Check efficiency
            if efficiency_data:
                recent_efficiencies = [d.overall_efficiency for d in efficiency_data[-10:] if d.overall_efficiency is not None]
                if recent_efficiencies:
                    avg_efficiency = np.mean(recent_efficiencies)
                    if avg_efficiency < 12:  # Low efficiency
                        maintenance_needed = True
                        maintenance_reasons.append("Low system efficiency")
            
            # Generate insight
            if maintenance_needed:
                insight = PredictiveInsight(
                    timestamp=datetime.utcnow(),
                    insight_type="maintenance",
                    confidence=85.0,
                    prediction_horizon=168,  # 1 week
                    predicted_value=1.0,  # Maintenance needed
                    current_value=0.0,  # Current status
                    trend="maintenance_required",
                    recommendation=f"Maintenance recommended: {', '.join(maintenance_reasons)}"
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"Error predicting maintenance needs: {e}")
        
        return insights
    
    async def get_efficiency_targets_status(self) -> Dict[str, Any]:
        """Get status of efficiency targets (15% and 30%)"""
        try:
            # Get latest efficiency data
            db = SessionLocal()
            latest_efficiency = db.query(SystemEfficiencyData).order_by(desc(SystemEfficiencyData.timestamp)).first()
            db.close()
            
            if not latest_efficiency:
                return {
                    'target_15_met': False,
                    'target_30_met': False,
                    'current_efficiency': 0,
                    'target_15_status': 'No data available',
                    'target_30_status': 'No data available'
                }
            
            current_efficiency = latest_efficiency.overall_efficiency
            target_15_met = current_efficiency >= EfficiencyTarget.TARGET_15.value
            target_30_met = current_efficiency >= EfficiencyTarget.TARGET_30.value
            
            return {
                'target_15_met': target_15_met,
                'target_30_met': target_30_met,
                'current_efficiency': current_efficiency,
                'target_15_status': 'Met' if target_15_met else 'Not Met',
                'target_30_status': 'Met' if target_30_met else 'Not Met',
                'target_15_gap': max(0, EfficiencyTarget.TARGET_15.value - current_efficiency),
                'target_30_gap': max(0, EfficiencyTarget.TARGET_30.value - current_efficiency)
            }
        
        except Exception as e:
            logger.error(f"Error getting efficiency targets status: {e}")
            return {
                'target_15_met': False,
                'target_30_met': False,
                'current_efficiency': 0,
                'target_15_status': 'Error',
                'target_30_status': 'Error'
            }
    
    async def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        try:
            # Get latest data from all systems
            db = SessionLocal()
            
            # Get latest efficiency
            latest_efficiency = db.query(SystemEfficiencyData).order_by(desc(SystemEfficiencyData.timestamp)).first()
            
            # Get latest storage data
            latest_storage = db.query(StorageSystemData).order_by(desc(StorageSystemData.timestamp)).first()
            
            # Get latest conversion data
            latest_conversion = db.query(ConversionControlData).order_by(desc(ConversionControlData.timestamp)).first()
            
            db.close()
            
            # Calculate health score components
            efficiency_score = 0
            if latest_efficiency:
                efficiency_score = min(100, (latest_efficiency.overall_efficiency / 30) * 100)  # Normalize to 30% max
            
            storage_score = 0
            if latest_storage:
                storage_score = latest_storage.battery_soc  # SOC as percentage
            
            conversion_score = 0
            if latest_conversion:
                conversion_score = latest_conversion.inverter_conversion_efficiency
            
            # Calculate overall health score
            overall_score = (efficiency_score + storage_score + conversion_score) / 3
            
            # Determine health status
            if overall_score >= 80:
                health_status = "Excellent"
            elif overall_score >= 60:
                health_status = "Good"
            elif overall_score >= 40:
                health_status = "Fair"
            else:
                health_status = "Poor"
            
            return {
                'overall_score': round(overall_score, 1),
                'health_status': health_status,
                'efficiency_score': round(efficiency_score, 1),
                'storage_score': round(storage_score, 1),
                'conversion_score': round(conversion_score, 1),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return {
                'overall_score': 0,
                'health_status': 'Unknown',
                'efficiency_score': 0,
                'storage_score': 0,
                'conversion_score': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            # Calculate all metrics
            efficiency_metrics = await self.calculate_system_efficiency(hours)
            performance_metrics = await self.calculate_performance_metrics(hours)
            efficiency_targets = await self.get_efficiency_targets_status()
            system_health = await self.get_system_health_score()
            predictive_insights = await self.generate_predictive_insights(hours)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'time_period_hours': hours,
                'efficiency_metrics': efficiency_metrics.__dict__ if efficiency_metrics else None,
                'performance_metrics': performance_metrics.__dict__ if performance_metrics else None,
                'efficiency_targets': efficiency_targets,
                'system_health': system_health,
                'predictive_insights': [insight.__dict__ for insight in predictive_insights],
                'metrics': self.metrics.copy()
            }
        
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'metrics': self.metrics.copy()
            }
    
    async def start(self):
        """Start the analytics engine"""
        if self.is_running:
            logger.warning("Analytics engine is already running")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.utcnow()
        logger.info("Analytics engine started")
    
    async def stop(self):
        """Stop the analytics engine"""
        if not self.is_running:
            logger.warning("Analytics engine is not running")
            return
        
        self.is_running = False
        logger.info("Analytics engine stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get analytics engine status"""
        uptime = None
        if self.metrics['start_time']:
            uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'efficiency_history_count': len(self.efficiency_history),
            'performance_history_count': len(self.performance_history),
            'predictive_insights_count': len(self.predictive_insights),
            'metrics': self.metrics.copy()
        }

# Example usage and testing
async def main():
    """Example usage of the analytics engine"""
    # Create analytics engine
    engine = AnalyticsEngine()
    
    # Start engine
    await engine.start()
    
    # Calculate efficiency metrics
    efficiency = await engine.calculate_system_efficiency(24)
    if efficiency:
        logger.info(f"System efficiency: {efficiency.overall_efficiency}%")
    
    # Calculate performance metrics
    performance = await engine.calculate_performance_metrics(24)
    if performance:
        logger.info(f"Total generation: {performance.total_generation} kWh")
    
    # Get efficiency targets status
    targets = await engine.get_efficiency_targets_status()
    logger.info(f"Efficiency targets: {targets}")
    
    # Get system health score
    health = await engine.get_system_health_score()
    logger.info(f"System health: {health['health_status']} ({health['overall_score']}%)")
    
    # Generate predictive insights
    insights = await engine.generate_predictive_insights(24)
    for insight in insights:
        logger.info(f"Insight: {insight.recommendation}")
    
    # Get analytics summary
    summary = await engine.get_analytics_summary(24)
    logger.info(f"Analytics summary generated: {len(summary.get('predictive_insights', []))} insights")
    
    # Get status
    status = engine.get_status()
    logger.info(f"Engine status: {status}")
    
    # Stop engine
    await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())