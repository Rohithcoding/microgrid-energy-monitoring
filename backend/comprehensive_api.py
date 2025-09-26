"""
Comprehensive API for Hybrid Microgrid Monitoring System
======================================================

This module provides a comprehensive FastAPI application that integrates all
monitoring components including sensors, alerts, analytics, and forecasting.
"""

from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
import json
import uvicorn

# Import all monitoring components
from comprehensive_models import (
    SessionLocal, SolarSystemData, ThermalSystemData, ConversionControlData,
    StorageSystemData, OutputLoadData, SystemEfficiencyData, FaultAlertData,
    PredictiveAnalyticsData, ComprehensiveSystemStatus
)
from monitoring_engine import RealTimeMonitoringEngine, MonitoringConfig
from alert_system import AlertManager, AlertSeverity
from analytics_engine import AnalyticsEngine
from forecasting_engine import ForecastingEngine

# Create FastAPI app
app = FastAPI(
    title="Hybrid Microgrid Monitoring API",
    description="Comprehensive monitoring system for hybrid microgrid with solar, thermal, and storage components",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
monitoring_engine = None
alert_manager = None
analytics_engine = None
forecasting_engine = None
websocket_manager = None

# WebSocket connection manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup event
@app.on_event("startup")
async def startup_event():
    global monitoring_engine, alert_manager, analytics_engine, forecasting_engine, websocket_manager
    
    # Initialize components
    config = MonitoringConfig(
        data_collection_interval=1.0,
        database_write_interval=5.0,
        alert_check_interval=2.0,
        efficiency_calculation_interval=10.0,
        predictive_analytics_interval=60.0
    )
    
    monitoring_engine = RealTimeMonitoringEngine(config)
    alert_manager = AlertManager()
    analytics_engine = AnalyticsEngine()
    forecasting_engine = ForecastingEngine()
    websocket_manager = WebSocketManager()
    
    # Start all engines
    await monitoring_engine.start()
    await alert_manager.start()
    await analytics_engine.start()
    await forecasting_engine.start()
    
    # Add callbacks for real-time updates
    def on_sensor_data(data):
        asyncio.create_task(websocket_manager.broadcast(json.dumps({
            "type": "sensor_data",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })))
    
    def on_alert(alert):
        asyncio.create_task(websocket_manager.broadcast(json.dumps({
            "type": "alert",
            "data": {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.alert_severity,
                "message": alert.alert_message,
                "source": alert.alert_source,
                "timestamp": alert.timestamp.isoformat()
            }
        })))
    
    monitoring_engine.add_callback(on_sensor_data)
    alert_manager.add_callback(on_alert)
    
    print("All monitoring systems started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global monitoring_engine, alert_manager, analytics_engine, forecasting_engine
    
    if monitoring_engine:
        await monitoring_engine.stop()
    if alert_manager:
        await alert_manager.stop()
    if analytics_engine:
        await analytics_engine.stop()
    if forecasting_engine:
        await forecasting_engine.stop()
    
    print("All monitoring systems stopped")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Hybrid Microgrid Monitoring API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "monitoring_engine": monitoring_engine.is_running if monitoring_engine else False,
            "alert_manager": alert_manager.is_running if alert_manager else False,
            "analytics_engine": analytics_engine.is_running if analytics_engine else False,
            "forecasting_engine": forecasting_engine.is_running if forecasting_engine else False
        }
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# =============================================================================
# SENSOR DATA ENDPOINTS
# =============================================================================

@app.get("/api/sensors/readings")
async def get_sensor_readings():
    """Get latest readings from all sensors"""
    if not monitoring_engine:
        raise HTTPException(status_code=503, detail="Monitoring engine not available")
    
    readings = monitoring_engine.get_latest_readings()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "readings": readings
    }

@app.get("/api/sensors/status")
async def get_sensor_status():
    """Get sensor system status"""
    if not monitoring_engine:
        raise HTTPException(status_code=503, detail="Monitoring engine not available")
    
    status = monitoring_engine.get_status()
    return status

# =============================================================================
# ALERT ENDPOINTS
# =============================================================================

@app.get("/api/alerts")
async def get_alerts(
    active_only: bool = Query(False),
    severity: Optional[str] = Query(None)
):
    """Get alerts with optional filtering"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not available")
    
    if active_only:
        alerts = alert_manager.get_active_alerts()
    else:
        alerts = alert_manager.alert_history[-100:]  # Last 100 alerts
    
    if severity:
        alerts = [a for a in alerts if a.alert_severity == severity]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type,
                "severity": a.alert_severity,
                "message": a.alert_message,
                "source": a.alert_source,
                "current_value": a.current_value,
                "threshold_value": a.threshold_value,
                "timestamp": a.timestamp.isoformat(),
                "is_resolved": a.is_resolved
            }
            for a in alerts
        ]
    }

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, resolved_by: str = "user"):
    """Resolve an alert"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not available")
    
    success = await alert_manager.resolve_alert(alert_id, resolved_by)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved successfully", "alert_id": alert_id}

@app.get("/api/alerts/statistics")
async def get_alert_statistics():
    """Get alert statistics"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not available")
    
    stats = alert_manager.get_alert_statistics()
    return stats

# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/analytics/efficiency")
async def get_efficiency_metrics(hours: int = Query(24, ge=1, le=168)):
    """Get system efficiency metrics"""
    if not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics engine not available")
    
    efficiency = await analytics_engine.calculate_system_efficiency(hours)
    if not efficiency:
        raise HTTPException(status_code=404, detail="No efficiency data available")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_period_hours": hours,
        "efficiency_metrics": efficiency.__dict__
    }

@app.get("/api/analytics/performance")
async def get_performance_metrics(hours: int = Query(24, ge=1, le=168)):
    """Get system performance metrics"""
    if not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics engine not available")
    
    performance = await analytics_engine.calculate_performance_metrics(hours)
    if not performance:
        raise HTTPException(status_code=404, detail="No performance data available")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_period_hours": hours,
        "performance_metrics": performance.__dict__
    }

@app.get("/api/analytics/health")
async def get_system_health():
    """Get system health score"""
    if not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics engine not available")
    
    health = await analytics_engine.get_system_health_score()
    return health

@app.get("/api/analytics/targets")
async def get_efficiency_targets():
    """Get efficiency targets status"""
    if not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics engine not available")
    
    targets = await analytics_engine.get_efficiency_targets_status()
    return targets

@app.get("/api/analytics/summary")
async def get_analytics_summary(hours: int = Query(24, ge=1, le=168)):
    """Get comprehensive analytics summary"""
    if not analytics_engine:
        raise HTTPException(status_code=503, detail="Analytics engine not available")
    
    summary = await analytics_engine.get_analytics_summary(hours)
    return summary

# =============================================================================
# FORECASTING ENDPOINTS
# =============================================================================

@app.get("/api/forecasts/solar")
async def get_solar_forecast(hours_ahead: int = Query(24, ge=1, le=168)):
    """Get solar generation forecast"""
    if not forecasting_engine:
        raise HTTPException(status_code=503, detail="Forecasting engine not available")
    
    forecasts = await forecasting_engine.forecast_solar_generation(hours_ahead)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "forecast_horizon_hours": hours_ahead,
        "forecasts": [f.__dict__ for f in forecasts]
    }

@app.get("/api/forecasts/battery")
async def get_battery_forecast(load_scenario: str = Query("current")):
    """Get battery depletion forecast"""
    if not forecasting_engine:
        raise HTTPException(status_code=503, detail="Forecasting engine not available")
    
    forecast = await forecasting_engine.predict_battery_depletion(load_scenario)
    if not forecast:
        raise HTTPException(status_code=404, detail="No battery data available")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "forecast": forecast.__dict__
    }

@app.get("/api/forecasts/outages")
async def get_outage_predictions():
    """Get outage predictions"""
    if not forecasting_engine:
        raise HTTPException(status_code=503, detail="Forecasting engine not available")
    
    predictions = await forecasting_engine.predict_outages()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "predictions": [p.__dict__ for p in predictions]
    }

@app.get("/api/forecasts/summary")
async def get_forecast_summary(hours_ahead: int = Query(24, ge=1, le=168)):
    """Get comprehensive forecast summary"""
    if not forecasting_engine:
        raise HTTPException(status_code=503, detail="Forecasting engine not available")
    
    summary = await forecasting_engine.get_forecast_summary(hours_ahead)
    return summary

# =============================================================================
# COMPREHENSIVE SYSTEM STATUS
# =============================================================================

@app.get("/api/system/status")
async def get_comprehensive_system_status():
    """Get comprehensive system status"""
    if not all([monitoring_engine, alert_manager, analytics_engine, forecasting_engine]):
        raise HTTPException(status_code=503, detail="System components not available")
    
    try:
        # Get latest sensor readings
        sensor_readings = monitoring_engine.get_latest_readings()
        
        # Get active alerts
        active_alerts = alert_manager.get_active_alerts()
        critical_alerts = alert_manager.get_critical_alerts()
        
        # Get system health
        system_health = await analytics_engine.get_system_health_score()
        
        # Get efficiency targets
        efficiency_targets = await analytics_engine.get_efficiency_targets_status()
        
        # Get battery forecast
        battery_forecast = await forecasting_engine.predict_battery_depletion()
        
        # Get solar forecast
        solar_forecasts = await forecasting_engine.forecast_solar_generation(6)
        
        # Determine overall system health
        overall_health = "healthy"
        if critical_alerts:
            overall_health = "critical"
        elif active_alerts:
            overall_health = "warning"
        elif system_health["overall_score"] < 60:
            overall_health = "caution"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": overall_health,
            "sensor_readings": sensor_readings,
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": len(critical_alerts),
                "recent_alerts": [
                    {
                        "type": a.alert_type,
                        "severity": a.alert_severity,
                        "message": a.alert_message,
                        "timestamp": a.timestamp.isoformat()
                    }
                    for a in active_alerts[-5:]  # Last 5 alerts
                ]
            },
            "system_health_score": system_health,
            "efficiency_targets": efficiency_targets,
            "battery_forecast": battery_forecast.__dict__ if battery_forecast else None,
            "solar_forecast_6h": solar_forecasts[0].__dict__ if solar_forecasts else None,
            "components_status": {
                "monitoring_engine": monitoring_engine.is_running,
                "alert_manager": alert_manager.is_running,
                "analytics_engine": analytics_engine.is_running,
                "forecasting_engine": forecasting_engine.is_running
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

# =============================================================================
# DATA ENDPOINTS
# =============================================================================

@app.get("/api/data/solar")
async def get_solar_data(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get solar system data"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    data = db.query(SolarSystemData).filter(
        SolarSystemData.timestamp >= start_time,
        SolarSystemData.timestamp <= end_time
    ).order_by(SolarSystemData.timestamp).all()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_period_hours": hours,
        "data": [
            {
                "id": d.id,
                "timestamp": d.timestamp.isoformat(),
                "solar_irradiance": d.solar_irradiance,
                "pv_output_power": d.pv_output_power,
                "pv_output_voltage": d.pv_output_voltage,
                "pv_efficiency": d.pv_efficiency,
                "concentrator_position": d.concentrator_position,
                "concentrator_alignment": d.concentrator_alignment,
                "concentrated_energy_level": d.concentrated_energy_level,
                "teg_temperature_diff": d.teg_temperature_diff,
                "teg_output_power": d.teg_output_power,
                "teg_efficiency": d.teg_efficiency
            }
            for d in data
        ]
    }

@app.get("/api/data/thermal")
async def get_thermal_data(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get thermal system data"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    data = db.query(ThermalSystemData).filter(
        ThermalSystemData.timestamp >= start_time,
        ThermalSystemData.timestamp <= end_time
    ).order_by(ThermalSystemData.timestamp).all()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_period_hours": hours,
        "data": [
            {
                "id": d.id,
                "timestamp": d.timestamp.isoformat(),
                "hot_water_temperature": d.hot_water_temperature,
                "storage_tank_temperature": d.storage_tank_temperature,
                "storage_tank_pressure": d.storage_tank_pressure,
                "energy_stored": d.energy_stored,
                "molten_salt_flow_rate": d.molten_salt_flow_rate,
                "molten_salt_inlet_temp": d.molten_salt_inlet_temp,
                "molten_salt_outlet_temp": d.molten_salt_outlet_temp,
                "pipe_integrity_status": d.pipe_integrity_status,
                "steam_output": d.steam_output,
                "steam_pressure": d.steam_pressure,
                "steam_temperature": d.steam_temperature
            }
            for d in data
        ]
    }

@app.get("/api/data/storage")
async def get_storage_data(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get storage system data"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    data = db.query(StorageSystemData).filter(
        StorageSystemData.timestamp >= start_time,
        StorageSystemData.timestamp <= end_time
    ).order_by(StorageSystemData.timestamp).all()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_period_hours": hours,
        "data": [
            {
                "id": d.id,
                "timestamp": d.timestamp.isoformat(),
                "battery_soc": d.battery_soc,
                "battery_charge_rate": d.battery_charge_rate,
                "battery_discharge_rate": d.battery_discharge_rate,
                "battery_temperature": d.battery_temperature,
                "battery_cycles": d.battery_cycles,
                "battery_health": d.battery_health,
                "thermal_energy_stored": d.thermal_energy_stored,
                "thermal_energy_released": d.thermal_energy_released,
                "thermal_storage_temp": d.thermal_storage_temp,
                "thermal_storage_efficiency": d.thermal_storage_efficiency,
                "water_tank_level": d.water_tank_level,
                "water_tank_temperature": d.water_tank_temperature,
                "water_flow_rate": d.water_flow_rate
            }
            for d in data
        ]
    }

# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

@app.get("/api/config")
async def get_system_config():
    """Get system configuration"""
    if not monitoring_engine:
        raise HTTPException(status_code=503, detail="Monitoring engine not available")
    
    status = monitoring_engine.get_status()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "config": status.get("config", {}),
        "components": {
            "monitoring_engine": monitoring_engine.is_running,
            "alert_manager": alert_manager.is_running if alert_manager else False,
            "analytics_engine": analytics_engine.is_running if analytics_engine else False,
            "forecasting_engine": forecasting_engine.is_running if forecasting_engine else False
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)