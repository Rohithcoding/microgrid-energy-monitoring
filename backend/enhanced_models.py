from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./enhanced_microgrid.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enhanced Database Models
class EnhancedSensorData(Base):
    __tablename__ = "enhanced_sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    solar_generation = Column(Float)
    storage_level = Column(Float)
    battery_temperature = Column(Float)
    solar_panel_temp = Column(Float)
    soc = Column(Float)
    voltage = Column(Float)
    consumption_load = Column(Float)
    alert_status = Column(String)
    predicted_generation = Column(Float)
    predicted_load = Column(Float)
    alert_type = Column(String)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="operator")  # operator, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String)
    key_hash = Column(String, unique=True, index=True)
    user_id = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)

# Enhanced Pydantic Models with Strict Validation
class EnhancedSensorDataCreate(BaseModel):
    timestamp: Optional[datetime] = None
    solar_generation: float = Field(..., ge=0, le=2000, description="Solar generation in Watts")
    storage_level: float = Field(..., ge=0, le=10, description="Storage level in kWh")
    battery_temperature: float = Field(..., ge=-20, le=150, description="Battery temperature in Celsius")
    solar_panel_temp: float = Field(..., ge=-20, le=150, description="Solar panel temperature in Celsius")
    soc: float = Field(..., ge=0, le=100, description="State of charge in percentage")
    voltage: float = Field(..., ge=100, le=300, description="Voltage in Volts")
    consumption_load: float = Field(..., ge=0, le=5000, description="Consumption load in Watts")
    alert_status: Literal["healthy", "warning", "critical"] = Field(default="healthy")
    predicted_generation: Optional[float] = Field(None, ge=0, le=2000)
    predicted_load: Optional[float] = Field(None, ge=0, le=5000)
    alert_type: Optional[str] = Field(None, max_length=200)
    
    @validator('solar_generation')
    def validate_solar_generation(cls, v):
        if v < 0:
            raise ValueError('Solar generation cannot be negative')
        return v
    
    @validator('soc')
    def validate_soc(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('SOC must be between 0 and 100')
        return v
    
    @validator('voltage')
    def validate_voltage(cls, v):
        if v < 100 or v > 300:
            logger.warning(f"Voltage {v}V is outside normal range (100-300V)")
        return v

class EnhancedSensorDataResponse(BaseModel):
    id: int
    timestamp: datetime
    solar_generation: float
    storage_level: float
    battery_temperature: float
    solar_panel_temp: float
    soc: float
    voltage: float
    consumption_load: float
    alert_status: str
    predicted_generation: Optional[float]
    predicted_load: Optional[float]
    alert_type: Optional[str]
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)
    role: Literal["operator", "admin"] = Field(default="operator")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SystemHealthResponse(BaseModel):
    status: Literal["healthy", "warning", "critical"]
    timestamp: datetime
    active_alerts: int
    system_uptime: str
    database_status: str
    api_version: str

class WebSocketMessage(BaseModel):
    type: Literal["sensor_data", "alert", "system_status"]
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)
