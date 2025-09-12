# main.py
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- FastAPI app ---
app = FastAPI(title="ESP32 Air Quality Backend")
templates = Jinja2Templates(directory="templates")

# --- Database setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./air_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    uniqueid = Column(String, unique=True, index=True)
    last_seen = Column(DateTime)

class AirDataLog(Base):
    __tablename__ = "air_data_log"
    id = Column(Integer, primary_key=True, index=True)
    uniqueid = Column(String)
    pm2_5 = Column(Float)
    pm10 = Column(Float)
    volatile_organic_compounds = Column(Float)
    co = Column(Float)
    no2 = Column(Float)
    o3 = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Request model ---
class AirData(BaseModel):
    uniqueid: str
    particulateMatter: Dict[str, float]
    volatileOrganicCompounds: float
    gases: Dict[str, float]

# --- Endpoints ---
@app.post("/air")
async def receive_air_data(data: AirData):
    print("Received air data:")
    print(data.json())
    
    db = SessionLocal()
    try:
        # Log data to persistent storage
        air_log = AirDataLog(
            uniqueid=data.uniqueid,
            pm2_5=data.particulateMatter.get("pm2_5"),
            pm10=data.particulateMatter.get("pm10"),
            volatile_organic_compounds=data.volatileOrganicCompounds,
            co=data.gases.get("CO"),
            no2=data.gases.get("NO2"),
            o3=data.gases.get("O3")
        )
        db.add(air_log)
        
        # Update device status (last seen)
        device = db.query(Device).filter(Device.uniqueid == data.uniqueid).first()
        if not device:
            device = Device(uniqueid=data.uniqueid)
            db.add(device)
        device.last_seen = datetime.now(timezone.utc)
        
        db.commit()
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
        
    return {"status": "ok"}

@app.get("/")
async def get_dashboard(request: Request):
    """Serves the web dashboard HTML page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/status")
async def get_device_status():
    """Returns the real-time online/offline status of all devices."""
    db = SessionLocal()
    devices = db.query(Device).all()
    db.close()
    
    online_threshold = datetime.now(timezone.utc) - timedelta(seconds=10)
    statuses = []
    for device in devices:
        status = "offline"
        if device.last_seen:
            # Check if the last_seen time is timezone-naive and convert if necessary
            if device.last_seen.tzinfo is None:
                device_last_seen_aware = device.last_seen.replace(tzinfo=timezone.utc)
            else:
                device_last_seen_aware = device.last_seen
            
            if device_last_seen_aware > online_threshold:
                status = "online"
                
        statuses.append({"uniqueid": device.uniqueid, "status": status})
        
    return {"devices": statuses}

@app.get("/air_data")
async def get_latest_air_data():
    """Returns the latest air quality data for each unique device."""
    db = SessionLocal()
    try:
        # Get a list of all unique device IDs
        unique_device_ids = db.query(AirDataLog.uniqueid).distinct().all()
        
        latest_data = {}
        for (device_id,) in unique_device_ids:
            # Find the most recent entry for each device
            latest_entry = (
                db.query(AirDataLog)
                .filter(AirDataLog.uniqueid == device_id)
                .order_by(AirDataLog.timestamp.desc())
                .first()
            )
            if latest_entry:
                latest_data[device_id] = {
                    "pm2_5": latest_entry.pm2_5,
                    "pm10": latest_entry.pm10,
                    "volatile_organic_compounds": latest_entry.volatile_organic_compounds,
                    "co": latest_entry.co,
                    "no2": latest_entry.no2,
                    "o3": latest_entry.o3,
                    "timestamp": latest_entry.timestamp.isoformat()
                }
    finally:
        db.close()
    
    return latest_data

# --- Run server ---
if __name__ == "__main__":
    # Create a 'templates' directory if it doesn't exist
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)