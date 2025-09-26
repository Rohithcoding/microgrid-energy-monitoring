"""
Solar Forecasting and Battery Depletion Prediction Engine
========================================================

This module provides advanced forecasting capabilities for solar generation,
battery depletion estimates, and predictive analytics for the hybrid microgrid system.
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
    SessionLocal, SolarSystemData, StorageSystemData, PredictiveAnalyticsData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SolarForecast:
    """Solar generation forecast data structure"""
    timestamp: datetime
    forecast_horizon: int  # hours ahead
    predicted_power: float  # Watts
    confidence: float  # 0-100%
    weather_factor: float
    seasonal_factor: float
    historical_factor: float

@dataclass
class BatteryDepletionForecast:
    """Battery depletion forecast data structure"""
    timestamp: datetime
    current_soc: float  # Current SOC percentage
    depletion_rate: float  # SOC percentage per hour
    backup_hours: float  # Hours of backup remaining
    critical_load_backup_hours: float  # Hours for critical loads only
    confidence: float  # 0-100%
    load_scenario: str  # "current", "high", "low"

@dataclass
class OutagePrediction:
    """Outage prediction data structure"""
    timestamp: datetime
    probability: float  # 0-100%
    predicted_duration: float  # hours
    cause: str
    confidence: float  # 0-100%
    mitigation_actions: List[str]

class ForecastingEngine:
    """Advanced forecasting engine for microgrid system"""
    
    def __init__(self):
        self.is_running = False
        self.forecast_history: List[SolarForecast] = []
        self.depletion_history: List[BatteryDepletionForecast] = []
        self.outage_predictions: List[OutagePrediction] = []
        
        # Performance metrics
        self.metrics = {
            'forecasts_generated': 0,
            'depletion_estimates': 0,
            'outage_predictions': 0,
            'forecast_accuracy': 0,
            'start_time': None
        }
    
    async def forecast_solar_generation(self, hours_ahead: int = 24) -> List[SolarForecast]:
        """Forecast solar generation for specified hours ahead"""
        try:
            forecasts = []
            
            # Get historical solar data
            db = SessionLocal()
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)  # Last 7 days
            
            solar_data = db.query(SolarSystemData).filter(
                and_(SolarSystemData.timestamp >= start_time, SolarSystemData.timestamp <= end_time)
            ).order_by(SolarSystemData.timestamp).all()
            
            db.close()
            
            if not solar_data:
                logger.warning("No historical solar data available for forecasting")
                return forecasts
            
            # Generate forecasts for each hour
            for hour in range(1, hours_ahead + 1):
                forecast = self._generate_solar_forecast(solar_data, hour)
                if forecast:
                    forecasts.append(forecast)
            
            # Store forecasts
            self.forecast_history.extend(forecasts)
            if len(self.forecast_history) > 1000:
                self.forecast_history = self.forecast_history[-1000:]
            
            self.metrics['forecasts_generated'] += len(forecasts)
            
            return forecasts
        
        except Exception as e:
            logger.error(f"Error forecasting solar generation: {e}")
            return []
    
    def _generate_solar_forecast(self, solar_data: List, hours_ahead: int) -> Optional[SolarForecast]:
        """Generate solar forecast for specific hour ahead"""
        try:
            # Get current time and target time
            current_time = datetime.utcnow()
            target_time = current_time + timedelta(hours=hours_ahead)
            
            # Calculate time-based factors
            time_factor = self._calculate_time_factor(target_time)
            seasonal_factor = self._calculate_seasonal_factor(target_time)
            weather_factor = self._calculate_weather_factor(solar_data, target_time)
            historical_factor = self._calculate_historical_factor(solar_data, target_time)
            
            # Get recent solar generation for baseline
            recent_data = solar_data[-24:] if len(solar_data) >= 24 else solar_data
            if not recent_data:
                return None
            
            # Calculate baseline power
            recent_powers = [d.pv_output_power for d in recent_data if d.pv_output_power]
            if not recent_powers:
                return None
            
            baseline_power = np.mean(recent_powers)
            
            # Calculate predicted power
            predicted_power = baseline_power * time_factor * seasonal_factor * weather_factor * historical_factor
            
            # Calculate confidence based on data quality and factors
            confidence = self._calculate_forecast_confidence(solar_data, time_factor, weather_factor)
            
            return SolarForecast(
                timestamp=current_time,
                forecast_horizon=hours_ahead,
                predicted_power=round(predicted_power, 2),
                confidence=round(confidence, 1),
                weather_factor=round(weather_factor, 3),
                seasonal_factor=round(seasonal_factor, 3),
                historical_factor=round(historical_factor, 3)
            )
        
        except Exception as e:
            logger.error(f"Error generating solar forecast: {e}")
            return None
    
    def _calculate_time_factor(self, target_time: datetime) -> float:
        """Calculate time-based factor for solar generation"""
        hour = target_time.hour
        minute = target_time.minute
        time_of_day = hour + minute / 60.0
        
        # Solar generation curve (peak at noon)
        if 6 <= hour <= 18:
            # Sine wave approximation
            factor = np.sin((time_of_day - 6) * np.pi / 12)
            return max(0, factor)
        return 0.0
    
    def _calculate_seasonal_factor(self, target_time: datetime) -> float:
        """Calculate seasonal factor for solar generation"""
        # Simple seasonal variation (higher in summer, lower in winter)
        day_of_year = target_time.timetuple().tm_yday
        seasonal_factor = 0.8 + 0.4 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
        return max(0.5, min(1.2, seasonal_factor))
    
    def _calculate_weather_factor(self, solar_data: List, target_time: datetime) -> float:
        """Calculate weather factor based on historical variability"""
        try:
            if len(solar_data) < 24:
                return 1.0  # Default factor
            
            # Get data for similar time periods
            similar_times = []
            for data in solar_data:
                if abs((data.timestamp.hour - target_time.hour) % 24) <= 1:  # Within 1 hour
                    similar_times.append(data.pv_output_power)
            
            if not similar_times:
                return 1.0
            
            # Calculate variability
            mean_power = np.mean(similar_times)
            std_power = np.std(similar_times)
            
            if mean_power > 0:
                variability = std_power / mean_power
                # Higher variability = lower confidence factor
                weather_factor = max(0.5, 1.0 - variability * 0.5)
            else:
                weather_factor = 1.0
            
            return weather_factor
        
        except Exception as e:
            logger.error(f"Error calculating weather factor: {e}")
            return 1.0
    
    def _calculate_historical_factor(self, solar_data: List, target_time: datetime) -> float:
        """Calculate historical performance factor"""
        try:
            if len(solar_data) < 24:
                return 1.0
            
            # Get recent performance trend
            recent_data = solar_data[-24:]
            recent_powers = [d.pv_output_power for d in recent_data if d.pv_output_power]
            
            if len(recent_powers) < 12:
                return 1.0
            
            # Calculate trend
            first_half = np.mean(recent_powers[:len(recent_powers)//2])
            second_half = np.mean(recent_powers[len(recent_powers)//2:])
            
            if first_half > 0:
                trend_factor = second_half / first_half
                return max(0.7, min(1.3, trend_factor))
            
            return 1.0
        
        except Exception as e:
            logger.error(f"Error calculating historical factor: {e}")
            return 1.0
    
    def _calculate_forecast_confidence(self, solar_data: List, time_factor: float, weather_factor: float) -> float:
        """Calculate forecast confidence"""
        try:
            # Base confidence
            base_confidence = 70.0
            
            # Time factor confidence (higher during peak hours)
            time_confidence = 20.0 * time_factor
            
            # Weather factor confidence (higher with stable weather)
            weather_confidence = 10.0 * weather_factor
            
            # Data quality confidence
            data_confidence = 0
            if len(solar_data) >= 24:
                data_confidence = 10.0
            elif len(solar_data) >= 12:
                data_confidence = 5.0
            
            total_confidence = base_confidence + time_confidence + weather_confidence + data_confidence
            
            return min(95.0, max(30.0, total_confidence))
        
        except Exception as e:
            logger.error(f"Error calculating forecast confidence: {e}")
            return 50.0
    
    async def predict_battery_depletion(self, load_scenario: str = "current") -> BatteryDepletionForecast:
        """Predict battery depletion and backup hours"""
        try:
            # Get current battery data
            db = SessionLocal()
            latest_storage = db.query(StorageSystemData).order_by(desc(StorageSystemData.timestamp)).first()
            
            # Get historical storage data for trend analysis
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            storage_data = db.query(StorageSystemData).filter(
                and_(StorageSystemData.timestamp >= start_time, StorageSystemData.timestamp <= end_time)
            ).order_by(StorageSystemData.timestamp).all()
            
            db.close()
            
            if not latest_storage:
                logger.warning("No battery data available for depletion prediction")
                return None
            
            # Calculate depletion rate
            depletion_rate = self._calculate_depletion_rate(storage_data, load_scenario)
            
            # Calculate backup hours
            current_soc = latest_storage.battery_soc
            backup_hours = current_soc / depletion_rate if depletion_rate > 0 else 999
            
            # Calculate critical load backup hours (assume 50% of current load)
            critical_load_backup_hours = backup_hours * 2 if depletion_rate > 0 else 999
            
            # Calculate confidence
            confidence = self._calculate_depletion_confidence(storage_data, depletion_rate)
            
            forecast = BatteryDepletionForecast(
                timestamp=datetime.utcnow(),
                current_soc=current_soc,
                depletion_rate=round(depletion_rate, 2),
                backup_hours=round(backup_hours, 1),
                critical_load_backup_hours=round(critical_load_backup_hours, 1),
                confidence=round(confidence, 1),
                load_scenario=load_scenario
            )
            
            # Store forecast
            self.depletion_history.append(forecast)
            if len(self.depletion_history) > 100:
                self.depletion_history = self.depletion_history[-100:]
            
            self.metrics['depletion_estimates'] += 1
            
            return forecast
        
        except Exception as e:
            logger.error(f"Error predicting battery depletion: {e}")
            return None
    
    def _calculate_depletion_rate(self, storage_data: List, load_scenario: str) -> float:
        """Calculate battery depletion rate"""
        try:
            if len(storage_data) < 5:
                return 2.0  # Default depletion rate
            
            # Get SOC values
            socs = [d.battery_soc for d in storage_data if d.battery_soc is not None]
            
            if len(socs) < 3:
                return 2.0
            
            # Calculate rate of change
            time_hours = len(socs)  # Assuming 1 hour intervals
            soc_change = socs[0] - socs[-1]  # Change from first to last
            depletion_rate = abs(soc_change) / time_hours if time_hours > 0 else 2.0
            
            # Adjust for load scenario
            if load_scenario == "high":
                depletion_rate *= 1.5
            elif load_scenario == "low":
                depletion_rate *= 0.7
            
            return max(0.1, min(10.0, depletion_rate))  # Reasonable bounds
        
        except Exception as e:
            logger.error(f"Error calculating depletion rate: {e}")
            return 2.0
    
    def _calculate_depletion_confidence(self, storage_data: List, depletion_rate: float) -> float:
        """Calculate depletion prediction confidence"""
        try:
            # Base confidence
            base_confidence = 60.0
            
            # Data quality confidence
            data_confidence = 0
            if len(storage_data) >= 24:
                data_confidence = 25.0
            elif len(storage_data) >= 12:
                data_confidence = 15.0
            elif len(storage_data) >= 6:
                data_confidence = 10.0
            
            # Rate stability confidence
            rate_confidence = 0
            if 0.5 <= depletion_rate <= 5.0:  # Reasonable range
                rate_confidence = 15.0
            elif 0.1 <= depletion_rate <= 10.0:  # Acceptable range
                rate_confidence = 10.0
            
            total_confidence = base_confidence + data_confidence + rate_confidence
            
            return min(95.0, max(30.0, total_confidence))
        
        except Exception as e:
            logger.error(f"Error calculating depletion confidence: {e}")
            return 50.0
    
    async def predict_outages(self) -> List[OutagePrediction]:
        """Predict potential system outages"""
        try:
            predictions = []
            
            # Get current system data
            db = SessionLocal()
            
            # Get latest data from all systems
            latest_solar = db.query(SolarSystemData).order_by(desc(SolarSystemData.timestamp)).first()
            latest_storage = db.query(StorageSystemData).order_by(desc(StorageSystemData.timestamp)).first()
            
            # Get recent data for trend analysis
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            solar_data = db.query(SolarSystemData).filter(
                and_(SolarSystemData.timestamp >= start_time, SolarSystemData.timestamp <= end_time)
            ).order_by(SolarSystemData.timestamp).all()
            
            storage_data = db.query(StorageSystemData).filter(
                and_(StorageSystemData.timestamp >= start_time, StorageSystemData.timestamp <= end_time)
            ).order_by(StorageSystemData.timestamp).all()
            
            db.close()
            
            # Predict battery depletion outage
            if latest_storage and latest_storage.battery_soc < 20:
                depletion_forecast = await self.predict_battery_depletion()
                if depletion_forecast and depletion_forecast.backup_hours < 4:
                    prediction = OutagePrediction(
                        timestamp=datetime.utcnow(),
                        probability=min(90, 20 + (20 - latest_storage.battery_soc) * 3),
                        predicted_duration=depletion_forecast.backup_hours,
                        cause="Battery depletion",
                        confidence=depletion_forecast.confidence,
                        mitigation_actions=[
                            "Charge battery immediately",
                            "Reduce non-critical loads",
                            "Switch to grid power if available"
                        ]
                    )
                    predictions.append(prediction)
            
            # Predict solar generation outage
            if solar_data:
                recent_powers = [d.pv_output_power for d in solar_data[-6:] if d.pv_output_power]
                if recent_powers:
                    avg_power = np.mean(recent_powers)
                    if avg_power < 100:  # Very low generation
                        # Check if it's night time
                        current_hour = datetime.utcnow().hour
                        if 6 <= current_hour <= 18:  # Daytime
                            prediction = OutagePrediction(
                                timestamp=datetime.utcnow(),
                                probability=70,
                                predicted_duration=2.0,
                                cause="Low solar generation",
                                confidence=80,
                                mitigation_actions=[
                                    "Check weather conditions",
                                    "Inspect solar panels",
                                    "Use battery backup",
                                    "Switch to grid power"
                                ]
                            )
                            predictions.append(prediction)
            
            # Predict system failure
            if latest_solar and latest_storage:
                # Check for system degradation
                if (latest_solar.pv_output_power < 50 and 
                    latest_storage.battery_soc < 30):
                    prediction = OutagePrediction(
                        timestamp=datetime.utcnow(),
                        probability=40,
                        predicted_duration=1.0,
                        cause="System degradation",
                        confidence=60,
                        mitigation_actions=[
                            "Schedule maintenance",
                            "Check all system components",
                            "Prepare backup power source"
                        ]
                    )
                    predictions.append(prediction)
            
            # Store predictions
            self.outage_predictions.extend(predictions)
            if len(self.outage_predictions) > 50:
                self.outage_predictions = self.outage_predictions[-50:]
            
            self.metrics['outage_predictions'] += len(predictions)
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error predicting outages: {e}")
            return []
    
    async def get_forecast_summary(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Get comprehensive forecast summary"""
        try:
            # Generate forecasts
            solar_forecasts = await self.forecast_solar_generation(hours_ahead)
            battery_forecast = await self.predict_battery_depletion()
            outage_predictions = await self.predict_outages()
            
            # Calculate summary statistics
            total_predicted_generation = sum(f.predicted_power for f in solar_forecasts)
            avg_confidence = np.mean([f.confidence for f in solar_forecasts]) if solar_forecasts else 0
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'forecast_horizon_hours': hours_ahead,
                'solar_forecasts': [f.__dict__ for f in solar_forecasts],
                'battery_forecast': battery_forecast.__dict__ if battery_forecast else None,
                'outage_predictions': [p.__dict__ for p in outage_predictions],
                'summary': {
                    'total_predicted_generation_kwh': round(total_predicted_generation / 1000, 2),
                    'average_forecast_confidence': round(avg_confidence, 1),
                    'battery_backup_hours': battery_forecast.backup_hours if battery_forecast else 0,
                    'outage_probability': max([p.probability for p in outage_predictions]) if outage_predictions else 0
                },
                'metrics': self.metrics.copy()
            }
        
        except Exception as e:
            logger.error(f"Error generating forecast summary: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'metrics': self.metrics.copy()
            }
    
    async def start(self):
        """Start the forecasting engine"""
        if self.is_running:
            logger.warning("Forecasting engine is already running")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.utcnow()
        logger.info("Forecasting engine started")
    
    async def stop(self):
        """Stop the forecasting engine"""
        if not self.is_running:
            logger.warning("Forecasting engine is not running")
            return
        
        self.is_running = False
        logger.info("Forecasting engine stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get forecasting engine status"""
        uptime = None
        if self.metrics['start_time']:
            uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'forecast_history_count': len(self.forecast_history),
            'depletion_history_count': len(self.depletion_history),
            'outage_predictions_count': len(self.outage_predictions),
            'metrics': self.metrics.copy()
        }

# Example usage and testing
async def main():
    """Example usage of the forecasting engine"""
    # Create forecasting engine
    engine = ForecastingEngine()
    
    # Start engine
    await engine.start()
    
    # Forecast solar generation
    solar_forecasts = await engine.forecast_solar_generation(24)
    logger.info(f"Generated {len(solar_forecasts)} solar forecasts")
    
    # Predict battery depletion
    battery_forecast = await engine.predict_battery_depletion()
    if battery_forecast:
        logger.info(f"Battery backup: {battery_forecast.backup_hours} hours")
    
    # Predict outages
    outage_predictions = await engine.predict_outages()
    logger.info(f"Generated {len(outage_predictions)} outage predictions")
    
    # Get forecast summary
    summary = await engine.get_forecast_summary(24)
    logger.info(f"Forecast summary: {summary['summary']}")
    
    # Get status
    status = engine.get_status()
    logger.info(f"Engine status: {status}")
    
    # Stop engine
    await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())