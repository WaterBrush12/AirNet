import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# --- FastAPI app ---
app = FastAPI(title="ESP32 Air Quality Backend")
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve images, CSS, and JS
app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./air_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class Device(Base):
    """Represents a unique air quality sensor device."""
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    uniqueid = Column(String, unique=True, index=True)
    name = Column(String, default="Unnamed Device")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    last_seen = Column(DateTime, default=datetime.now(timezone.utc))

class AirDataLog(Base):
    """Represents a log of sensor data from a device."""
    __tablename__ = "air_data_logs"
    id = Column(Integer, primary_key=True, index=True)
    uniqueid = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    pm2_5 = Column(Float)
    pm10 = Column(Float)
    volatile_organic_compounds = Column(Float)
    co = Column(Float)
    no2 = Column(Float)
    o3 = Column(Float)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Pydantic Models for data validation ---
class ParticulateMatter(BaseModel):
    pm2_5: float
    pm10: float

class Gases(BaseModel):
    co: float
    no2: float
    o3: float

class AirData(BaseModel):
    uniqueid: str
    particulateMatter: ParticulateMatter
    volatileOrganicCompounds: float
    gases: Gases

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# --- Helper Functions ---
def get_air_quality_status(pm2_5: Optional[float], pm10: Optional[float]) -> str:
    """
    Determines the air quality status based on PM2.5 and PM10 values.
    Returns the worst status of the two.
    """
    if pm2_5 is None or pm10 is None:
        return "unknown"
    
    # Define thresholds
    pm2_5_status = "good"
    if 12.0 <= pm2_5 <= 35.4:
        pm2_5_status = "mid"
    elif pm2_5 > 35.4:
        pm2_5_status = "bad"
        
    pm10_status = "good"
    if 54.0 <= pm10 <= 154.0:
        pm10_status = "mid"
    elif pm10 > 154.0:
        pm10_status = "bad"
    
    # Return the "worst" status
    if "bad" in [pm2_5_status, pm10_status]:
        return "bad"
    if "mid" in [pm2_5_status, pm10_status]:
        return "mid"
    return "good"

def get_relative_time(dt: datetime) -> str:
    """Returns a human-readable relative time string."""
    now = datetime.now(timezone.utc)
    # Ensure both datetimes are timezone-aware for a safe comparison
    dt_aware = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    diff = now - dt_aware
    
    if diff.total_seconds() < 60:
        return "just now"
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    if diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = int(diff.total_seconds() / 86400)
    return f"{days} day{'s' if days > 1 else ''} ago"


# --- API Endpoints ---
@app.get("/")
def read_root(request: Request):
    """Serves the main page."""
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/map")
def read_map_page(request: Request):
    """Serves the map page."""
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/sensors")
def read_sensors_page(request: Request):
    """Serves the sensors page."""
    return templates.TemplateResponse("sensors.html", {"request": request})

@app.post("/air")
async def log_air_data(data: AirData):
    """Logs new air quality data from a device."""
    db = SessionLocal()
    try:
        # Update last_seen for the device
        device = db.query(Device).filter(Device.uniqueid == data.uniqueid).first()
        if not device:
            # Create a new device if it doesn't exist
            device = Device(uniqueid=data.uniqueid)
            db.add(device)
        
        device.last_seen = datetime.now(timezone.utc)
        
        # Log the new data
        log = AirDataLog(
            uniqueid=data.uniqueid,
            pm2_5=data.particulateMatter.pm2_5,
            pm10=data.particulateMatter.pm10,
            volatile_organic_compounds=data.volatileOrganicCompounds,
            co=data.gases.co,
            no2=data.gases.no2,
            o3=data.gases.o3
        )
        db.add(log)
        db.commit()
        db.refresh(device)
        db.refresh(log)
        return {"message": "Data logged successfully."}
    finally:
        db.close()

@app.get("/devices/latest")
async def get_latest_device_data():
    """
    Returns a list of all devices with their latest air quality data and status.
    Ensures only unique device IDs are returned and that the data is the most recent.
    """
    db = SessionLocal()
    try:
        # Get the latest log for each unique device ID
        subquery = db.query(
            AirDataLog.uniqueid, 
            func.max(AirDataLog.timestamp).label("max_timestamp")
        ).group_by(AirDataLog.uniqueid).subquery()
        
        latest_logs = db.query(AirDataLog).join(
            subquery,
            (AirDataLog.uniqueid == subquery.c.uniqueid) & (AirDataLog.timestamp == subquery.c.max_timestamp)
        ).all()
        
        devices_dict = {log.uniqueid: log for log in latest_logs}
        
        result = []
        all_devices = db.query(Device).all()

        for device in all_devices:
            latest_log = devices_dict.get(device.uniqueid)
            
            # --- UPDATED OFFLINE LOGIC ---
            is_online = (datetime.now(timezone.utc) - device.last_seen.replace(tzinfo=timezone.utc)) < timedelta(seconds=8)
            
            pm2_5_val = latest_log.pm2_5 if latest_log else None
            pm10_val = latest_log.pm10 if latest_log else None
            
            device_data = {
                "uniqueid": device.uniqueid,
                "name": device.name,
                "latitude": device.latitude,
                "longitude": device.longitude,
                "is_online": is_online,
                "last_seen_timestamp": int(device.last_seen.replace(tzinfo=timezone.utc).timestamp()),
                "last_seen_relative": get_relative_time(device.last_seen),
                "pm2_5": pm2_5_val,
                "pm10": pm10_val,
                "volatileOrganicCompounds": latest_log.volatile_organic_compounds if latest_log else None,
                "CO": latest_log.co if latest_log else None,
                "NO2": latest_log.no2 if latest_log else None,
                "O3": latest_log.o3 if latest_log else None,
                "airQualityStatus": get_air_quality_status(pm2_5_val, pm10_val)
            }
            result.append(device_data)
        return result
    finally:
        db.close()

@app.post("/devices/{uniqueid}")
async def update_device(uniqueid: str, update: DeviceUpdate):
    """Updates a device's name or location."""
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.uniqueid == uniqueid).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found.")

        if update.name is not None:
            device.name = update.name
        if update.latitude is not None:
            device.latitude = update.latitude
        if update.longitude is not None:
            device.longitude = update.longitude

        db.commit()
        db.refresh(device)
        return {"message": "Device updated successfully."}
    finally:
        db.close()

@app.delete("/devices/{uniqueid}")
async def delete_device(uniqueid: str):
    """Deletes a device and its associated air data logs."""
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.uniqueid == uniqueid).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found.")

        # Delete all logs associated with the device
        db.query(AirDataLog).filter(AirDataLog.uniqueid == uniqueid).delete()
        # Delete the device itself
        db.delete(device)
        db.commit()
        return {"message": "Device and associated data deleted successfully."}
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)