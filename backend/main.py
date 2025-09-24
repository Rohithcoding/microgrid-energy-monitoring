from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn

from models import (
    SensorDataCreate, SensorDataResponse, AlertResponse, SystemStatus,
    SensorData, Alert
)
from database import (
    get_db, create_sensor_data, get_sensor_data, get_sensor_data_by_timerange,
    get_latest_sensor_data, get_active_alerts, get_alerts, resolve_alert,
    check_and_create_alerts, get_system_statistics
)
from ai_predictions import MicrogridAI

app = FastAPI(title="Microgrid Energy Monitoring API", version="1.0.0")

# Initialize AI system
ai_system = MicrogridAI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Microgrid Energy Monitoring API", "version": "1.0.0"}

@app.post("/api/sensordata", response_model=SensorDataResponse)
async def create_sensor_reading(sensor_data: SensorDataCreate, db: Session = Depends(get_db)):
    """Accept new sensor data from IoT devices"""
    try:
        # Create sensor data entry
        db_sensor_data = create_sensor_data(db, sensor_data)
        
        # Check for alerts
        alerts = check_and_create_alerts(db, db_sensor_data)
        
        return db_sensor_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sensor data: {str(e)}")

@app.get("/api/sensordata", response_model=List[SensorDataResponse])
async def get_sensor_readings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    hours: Optional[int] = Query(None, ge=1, le=168),  # Max 1 week
    db: Session = Depends(get_db)
):
    """Get sensor data with optional time filtering"""
    try:
        if hours:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            end_time = datetime.utcnow()
            return get_sensor_data_by_timerange(db, start_time, end_time)
        else:
            return get_sensor_data(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sensor data: {str(e)}")

@app.get("/api/sensordata/latest", response_model=SensorDataResponse)
async def get_latest_reading(db: Session = Depends(get_db)):
    """Get the most recent sensor reading"""
    try:
        latest = get_latest_sensor_data(db)
        if not latest:
            raise HTTPException(status_code=404, detail="No sensor data found")
        return latest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving latest data: {str(e)}")

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_all_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    try:
        if active_only:
            return get_active_alerts(db)
        else:
            return get_alerts(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert_endpoint(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    try:
        alert = resolve_alert(db, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert resolved successfully", "alert_id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status(db: Session = Depends(get_db)):
    """Get current system status and health"""
    try:
        latest = get_latest_sensor_data(db)
        if not latest:
            raise HTTPException(status_code=404, detail="No sensor data available")
        
        active_alerts = get_active_alerts(db)
        
        # Determine system health
        health = "healthy"
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        high_alerts = [a for a in active_alerts if a.severity == "high"]
        
        if critical_alerts:
            health = "critical"
        elif high_alerts:
            health = "warning"
        elif active_alerts:
            health = "caution"
        
        return SystemStatus(
            current_generation=latest.generation,
            current_storage=latest.storage,
            current_temperature=latest.temperature,
            current_soc=latest.soc,
            current_voltage=latest.voltage,
            active_alerts=len(active_alerts),
            system_health=health,
            last_updated=latest.timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system status: {str(e)}")

@app.get("/api/analytics/statistics")
async def get_analytics(hours: int = Query(24, ge=1, le=168), db: Session = Depends(get_db)):
    """Get system analytics and statistics"""
    try:
        stats = get_system_statistics(db, hours)
        if not stats:
            raise HTTPException(status_code=404, detail="No data available for analysis")
        
        # Add efficiency calculations
        stats["efficiency_score"] = min(100, (stats["avg_soc"] + (240 - abs(240 - stats["avg_voltage"])) / 2.4) / 2)
        stats["generation_trend"] = "increasing" if stats["avg_generation"] > 300 else "decreasing"
        
        # Predictions (simulated)
        stats["predictions"] = {
            "next_hour_generation": stats["avg_generation"] * 1.1 if stats["avg_generation"] > 100 else 0,
            "storage_depletion_hours": max(1, stats["avg_storage"] / 0.4) if stats["avg_storage"] > 0 else 0,
            "maintenance_recommendation": "Schedule maintenance" if stats["max_temperature"] > 90 else "System operating normally"
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@app.get("/api/ai/solar-predictions")
async def get_solar_predictions(hours: int = Query(6, ge=1, le=24), db: Session = Depends(get_db)):
    """Get AI-powered solar generation predictions"""
    try:
        predictions = ai_system.predict_solar_generation(db, hours)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating solar predictions: {str(e)}")

@app.get("/api/ai/load-predictions")
async def get_load_predictions(hours: int = Query(24, ge=1, le=48), db: Session = Depends(get_db)):
    """Get AI-powered load demand predictions"""
    try:
        predictions = ai_system.predict_load_demand(db, hours)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating load predictions: {str(e)}")

@app.get("/api/ai/grid-switching")
async def get_grid_switching_analysis(db: Session = Depends(get_db)):
    """Get AI analysis for grid switching decisions"""
    try:
        analysis = ai_system.analyze_grid_switching_need(db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing grid switching: {str(e)}")

@app.get("/api/ai/fault-detection")
async def get_fault_detection(db: Session = Depends(get_db)):
    """Get AI-powered fault detection analysis"""
    try:
        faults = ai_system.detect_system_faults(db)
        return faults
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting faults: {str(e)}")

@app.get("/api/ai/load-management")
async def get_load_management_optimization(db: Session = Depends(get_db)):
    """Get AI-powered load management optimization"""
    try:
        optimization = ai_system.optimize_load_management(db)
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing load management: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
