from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./microgrid.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class SensorData(Base):
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    generation = Column(Float)  # Watts
    storage = Column(Float)     # kWh
    temperature = Column(Float) # Celsius
    soc = Column(Float)         # State of Charge %
    voltage = Column(Float)     # Volts

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String)
    message = Column(String)
    severity = Column(String)  # low, medium, high, critical
    value = Column(Float)
    threshold = Column(Float)
    resolved = Column(Integer, default=0)  # 0 = active, 1 = resolved

# Pydantic Models for API
class SensorDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    generation: float
    storage: float
    temperature: float
    soc: float
    voltage: float

class SensorDataResponse(BaseModel):
    id: int
    timestamp: datetime
    generation: float
    storage: float
    temperature: float
    soc: float
    voltage: float
    
    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    alert_type: str
    message: str
    severity: str
    value: float
    threshold: float

class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    alert_type: str
    message: str
    severity: str
    value: float
    threshold: float
    resolved: int
    
    class Config:
        from_attributes = True

class SystemStatus(BaseModel):
    current_generation: float
    current_storage: float
    current_temperature: float
    current_soc: float
    current_voltage: float
    active_alerts: int
    system_health: str
    last_updated: datetime

# Create tables
Base.metadata.create_all(bind=engine)
