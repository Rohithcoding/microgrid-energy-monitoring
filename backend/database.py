from sqlalchemy.orm import Session
from models import SessionLocal, SensorData, Alert, SensorDataCreate, AlertCreate
from datetime import datetime, timedelta
from typing import List, Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_sensor_data(db: Session, sensor_data: SensorDataCreate):
    """Create new sensor data entry"""
    db_sensor_data = SensorData(
        timestamp=sensor_data.timestamp or datetime.utcnow(),
        generation=sensor_data.generation,
        storage=sensor_data.storage,
        temperature=sensor_data.temperature,
        soc=sensor_data.soc,
        voltage=sensor_data.voltage
    )
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data

def get_sensor_data(db: Session, skip: int = 0, limit: int = 100):
    """Get sensor data with pagination"""
    return db.query(SensorData).order_by(SensorData.timestamp.desc()).offset(skip).limit(limit).all()

def get_sensor_data_by_timerange(db: Session, start_time: datetime, end_time: datetime):
    """Get sensor data within a time range"""
    return db.query(SensorData).filter(
        SensorData.timestamp >= start_time,
        SensorData.timestamp <= end_time
    ).order_by(SensorData.timestamp.asc()).all()

def get_latest_sensor_data(db: Session):
    """Get the most recent sensor data entry"""
    return db.query(SensorData).order_by(SensorData.timestamp.desc()).first()

def create_alert(db: Session, alert: AlertCreate):
    """Create new alert"""
    db_alert = Alert(
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        value=alert.value,
        threshold=alert.threshold
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_active_alerts(db: Session):
    """Get all active alerts"""
    return db.query(Alert).filter(Alert.resolved == 0).order_by(Alert.timestamp.desc()).all()

def get_alerts(db: Session, skip: int = 0, limit: int = 50):
    """Get alerts with pagination"""
    return db.query(Alert).order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()

def resolve_alert(db: Session, alert_id: int):
    """Mark an alert as resolved"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.resolved = 1
        db.commit()
        db.refresh(alert)
    return alert

def check_and_create_alerts(db: Session, sensor_data: SensorData):
    """Check sensor data against thresholds and create alerts if needed"""
    alerts_created = []
    
    # Temperature threshold
    if sensor_data.temperature > 80:
        alert = AlertCreate(
            alert_type="temperature",
            message=f"High temperature detected: {sensor_data.temperature}°C",
            severity="critical" if sensor_data.temperature > 100 else "high",
            value=sensor_data.temperature,
            threshold=80.0
        )
        alerts_created.append(create_alert(db, alert))
    
    # SOC threshold
    if sensor_data.soc < 30:
        alert = AlertCreate(
            alert_type="soc",
            message=f"Low battery: {sensor_data.soc}% SOC",
            severity="critical" if sensor_data.soc < 15 else "medium",
            value=sensor_data.soc,
            threshold=30.0
        )
        alerts_created.append(create_alert(db, alert))
    
    # Voltage threshold
    if sensor_data.voltage < 200:
        alert = AlertCreate(
            alert_type="voltage",
            message=f"Voltage drop detected: {sensor_data.voltage}V",
            severity="critical" if sensor_data.voltage < 180 else "high",
            value=sensor_data.voltage,
            threshold=200.0
        )
        alerts_created.append(create_alert(db, alert))
    
    return alerts_created

def get_system_statistics(db: Session, hours: int = 24):
    """Get system statistics for the last N hours"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    data = get_sensor_data_by_timerange(db, start_time, datetime.utcnow())
    
    if not data:
        return None
    
    return {
        "avg_generation": sum(d.generation for d in data) / len(data),
        "avg_storage": sum(d.storage for d in data) / len(data),
        "avg_temperature": sum(d.temperature for d in data) / len(data),
        "avg_soc": sum(d.soc for d in data) / len(data),
        "avg_voltage": sum(d.voltage for d in data) / len(data),
        "max_temperature": max(d.temperature for d in data),
        "min_soc": min(d.soc for d in data),
        "min_voltage": min(d.voltage for d in data),
        "data_points": len(data)
    }
