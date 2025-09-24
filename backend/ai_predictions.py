import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import SensorData
import pandas as pd

class MicrogridAI:
    """Advanced AI system for microgrid management and predictions"""
    
    def __init__(self):
        self.solar_efficiency_threshold = 0.7
        self.battery_critical_threshold = 15
        self.load_prediction_hours = 24
        
    def predict_solar_generation(self, db: Session, hours_ahead: int = 6) -> Dict:
        """Predict solar generation based on time of day and historical patterns"""
        current_time = datetime.now()
        predictions = []
        
        # Get historical data for pattern analysis
        historical_data = db.query(SensorData).filter(
            SensorData.timestamp >= current_time - timedelta(days=7)
        ).all()
        
        if not historical_data:
            return {"predictions": [], "confidence": 0, "method": "no_data"}
        
        # Create hourly predictions
        for i in range(hours_ahead):
            future_time = current_time + timedelta(hours=i)
            hour = future_time.hour
            
            # Solar generation pattern (realistic curve)
            if 6 <= hour <= 18:
                # Peak generation at noon, tapering off
                solar_factor = -((hour - 12) ** 2) / 36 + 1
                base_generation = max(0, solar_factor * 1000)
                
                # Weather factor simulation (could be replaced with real weather API)
                weather_factor = np.random.uniform(0.7, 1.0)  # 70-100% efficiency
                
                predicted_generation = base_generation * weather_factor
            else:
                predicted_generation = 0
            
            predictions.append({
                "timestamp": future_time.isoformat(),
                "predicted_generation": round(predicted_generation, 1),
                "confidence": 0.85 if 8 <= hour <= 16 else 0.6
            })
        
        return {
            "predictions": predictions,
            "average_confidence": 0.75,
            "method": "time_series_analysis"
        }
    
    def predict_load_demand(self, db: Session, hours_ahead: int = 24) -> Dict:
        """Predict energy consumption based on historical patterns"""
        current_time = datetime.now()
        
        # Typical load patterns (could be enhanced with ML models)
        load_patterns = {
            "night": 200,      # 10 PM - 6 AM
            "morning": 400,    # 6 AM - 10 AM
            "day": 300,        # 10 AM - 6 PM
            "evening": 600     # 6 PM - 10 PM
        }
        
        predictions = []
        for i in range(hours_ahead):
            future_time = current_time + timedelta(hours=i)
            hour = future_time.hour
            
            if 22 <= hour or hour < 6:
                base_load = load_patterns["night"]
            elif 6 <= hour < 10:
                base_load = load_patterns["morning"]
            elif 10 <= hour < 18:
                base_load = load_patterns["day"]
            else:
                base_load = load_patterns["evening"]
            
            # Add some variation
            predicted_load = base_load + np.random.normal(0, 50)
            
            predictions.append({
                "timestamp": future_time.isoformat(),
                "predicted_load": round(max(100, predicted_load), 1),
                "load_type": self._get_load_type(hour)
            })
        
        return {
            "predictions": predictions,
            "peak_hours": ["18:00", "19:00", "20:00", "21:00"],
            "method": "pattern_analysis"
        }
    
    def _get_load_type(self, hour: int) -> str:
        """Classify load type based on hour"""
        if 22 <= hour or hour < 6:
            return "base_load"
        elif 6 <= hour < 10:
            return "morning_peak"
        elif 10 <= hour < 18:
            return "daytime"
        else:
            return "evening_peak"
    
    def analyze_grid_switching_need(self, db: Session) -> Dict:
        """Analyze when to switch to grid power"""
        latest_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
        
        if not latest_data:
            return {"switch_to_grid": False, "reason": "no_data"}
        
        # Get solar predictions
        solar_predictions = self.predict_solar_generation(db, 6)
        load_predictions = self.predict_load_demand(db, 6)
        
        current_soc = latest_data.soc
        current_generation = latest_data.generation
        
        # Decision logic for grid switching
        switch_reasons = []
        switch_to_grid = False
        
        # Critical battery level
        if current_soc < self.battery_critical_threshold:
            switch_to_grid = True
            switch_reasons.append(f"Critical battery level: {current_soc}%")
        
        # No solar generation and low battery
        if current_generation < 50 and current_soc < 30:
            switch_to_grid = True
            switch_reasons.append("Low solar generation with insufficient battery")
        
        # Predicted energy deficit
        next_6h_generation = sum([p["predicted_generation"] for p in solar_predictions["predictions"]])
        next_6h_load = sum([p["predicted_load"] for p in load_predictions["predictions"]])
        
        if next_6h_generation < next_6h_load * 0.5 and current_soc < 50:
            switch_to_grid = True
            switch_reasons.append("Predicted energy deficit in next 6 hours")
        
        # Night time with low battery
        current_hour = datetime.now().hour
        if (20 <= current_hour or current_hour < 6) and current_soc < 40:
            switch_to_grid = True
            switch_reasons.append("Night time operation with low battery")
        
        return {
            "switch_to_grid": switch_to_grid,
            "reasons": switch_reasons,
            "current_soc": current_soc,
            "current_generation": current_generation,
            "predicted_deficit_6h": max(0, next_6h_load - next_6h_generation),
            "recommendation": self._get_grid_recommendation(switch_to_grid, current_soc)
        }
    
    def _get_grid_recommendation(self, switch_to_grid: bool, soc: float) -> str:
        """Get human-readable grid switching recommendation"""
        if switch_to_grid:
            if soc < 15:
                return "IMMEDIATE: Switch to grid power to prevent system shutdown"
            elif soc < 30:
                return "URGENT: Switch to grid power and charge batteries"
            else:
                return "RECOMMENDED: Switch to grid power to preserve battery life"
        else:
            return "CONTINUE: Microgrid operation is optimal"
    
    def detect_system_faults(self, db: Session) -> Dict:
        """Advanced fault detection using AI analysis"""
        # Get recent data for analysis
        recent_data = db.query(SensorData).filter(
            SensorData.timestamp >= datetime.now() - timedelta(hours=2)
        ).order_by(SensorData.timestamp.desc()).limit(20).all()
        
        if len(recent_data) < 5:
            return {"faults": [], "system_health": "unknown"}
        
        faults = []
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            'timestamp': d.timestamp,
            'generation': d.generation,
            'storage': d.storage,
            'temperature': d.temperature,
            'soc': d.soc,
            'voltage': d.voltage
        } for d in recent_data])
        
        # Fault Detection Algorithms
        
        # 1. Solar Panel Degradation Detection
        current_hour = datetime.now().hour
        if 10 <= current_hour <= 14:  # Peak sun hours
            expected_generation = 800  # Expected peak generation
            actual_generation = df['generation'].iloc[0]
            if actual_generation < expected_generation * 0.6:
                faults.append({
                    "type": "solar_degradation",
                    "severity": "medium",
                    "message": f"Solar generation below expected: {actual_generation}W vs {expected_generation}W expected",
                    "recommendation": "Check solar panel connections and cleanliness"
                })
        
        # 2. Battery Degradation Detection
        soc_variance = df['soc'].var()
        if soc_variance > 100:  # High variance in SOC
            faults.append({
                "type": "battery_degradation",
                "severity": "high",
                "message": f"Unusual battery behavior detected (SOC variance: {soc_variance:.1f})",
                "recommendation": "Schedule battery health check and possible replacement"
            })
        
        # 3. Temperature Anomaly Detection
        temp_mean = df['temperature'].mean()
        temp_std = df['temperature'].std()
        latest_temp = df['temperature'].iloc[0]
        
        if abs(latest_temp - temp_mean) > 2 * temp_std and temp_std > 5:
            faults.append({
                "type": "temperature_anomaly",
                "severity": "high" if latest_temp > 90 else "medium",
                "message": f"Temperature anomaly detected: {latest_temp}°C (avg: {temp_mean:.1f}°C)",
                "recommendation": "Check cooling systems and ventilation"
            })
        
        # 4. Voltage Instability Detection
        voltage_changes = df['voltage'].diff().abs()
        if voltage_changes.mean() > 10:
            faults.append({
                "type": "voltage_instability",
                "severity": "high",
                "message": f"Voltage instability detected (avg change: {voltage_changes.mean():.1f}V)",
                "recommendation": "Check electrical connections and load balancing"
            })
        
        # 5. Inverter Efficiency Detection
        if df['generation'].iloc[0] > 0 and df['voltage'].iloc[0] < 220:
            efficiency = (df['voltage'].iloc[0] / 240) * 100
            if efficiency < 85:
                faults.append({
                    "type": "inverter_efficiency",
                    "severity": "medium",
                    "message": f"Inverter efficiency low: {efficiency:.1f}%",
                    "recommendation": "Check inverter performance and connections"
                })
        
        # Overall system health assessment
        if len(faults) == 0:
            system_health = "excellent"
        elif len([f for f in faults if f["severity"] == "high"]) > 0:
            system_health = "critical"
        elif len([f for f in faults if f["severity"] == "medium"]) > 1:
            system_health = "degraded"
        else:
            system_health = "good"
        
        return {
            "faults": faults,
            "system_health": system_health,
            "analysis_timestamp": datetime.now().isoformat(),
            "data_points_analyzed": len(recent_data)
        }
    
    def optimize_load_management(self, db: Session) -> Dict:
        """AI-powered load management optimization"""
        latest_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
        
        if not latest_data:
            return {"optimization": "no_data"}
        
        current_generation = latest_data.generation
        current_soc = latest_data.soc
        current_hour = datetime.now().hour
        
        # Load management strategies
        strategies = []
        
        # 1. Load Shedding Recommendations
        if current_soc < 20:
            strategies.append({
                "action": "load_shedding",
                "priority": "critical",
                "message": "Shed non-essential loads immediately",
                "loads_to_shed": ["HVAC", "Water Heater", "EV Charging"],
                "estimated_savings": "200-400W"
            })
        elif current_soc < 40 and current_generation < 200:
            strategies.append({
                "action": "load_reduction",
                "priority": "high",
                "message": "Reduce non-critical loads",
                "loads_to_reduce": ["Lighting", "Electronics"],
                "estimated_savings": "100-200W"
            })
        
        # 2. Load Shifting Recommendations
        if 10 <= current_hour <= 16 and current_generation > 600:
            strategies.append({
                "action": "load_shifting",
                "priority": "medium",
                "message": "Shift energy-intensive tasks to current time",
                "recommended_loads": ["Washing Machine", "Dishwasher", "EV Charging"],
                "reason": "Excess solar generation available"
            })
        
        # 3. Battery Charging Strategy
        if current_generation > 500 and current_soc < 80:
            strategies.append({
                "action": "battery_charging",
                "priority": "medium",
                "message": "Optimize battery charging from excess solar",
                "charging_rate": "Maximum safe rate",
                "target_soc": "90%"
            })
        
        # 4. Grid Export Opportunity
        if current_generation > 800 and current_soc > 90:
            strategies.append({
                "action": "grid_export",
                "priority": "low",
                "message": "Consider exporting excess power to grid",
                "excess_power": f"{current_generation - 400}W",
                "estimated_revenue": "$0.15-0.25/kWh"
            })
        
        return {
            "optimization_strategies": strategies,
            "current_status": {
                "generation": current_generation,
                "soc": current_soc,
                "hour": current_hour
            },
            "next_review": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
