from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import sys
from dotenv import load_dotenv

# Load global environment variables
load_dotenv()

# Add root to path to import modules
sys.path.append(os.getcwd())

from backend.database import SessionLocal, SensorData, init_db
from notifier.alert_system import AlertSystem
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Monitoring & Automation Service")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()

# Initialize alert system
notifier = AlertSystem()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class SensorDataCreate(BaseModel):
    device_id: str
    temperature: float
    humidity: float

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

@app.post("/api/data", response_model=SensorDataResponse)
def receive_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    Endpoint to receive data from sensors (or automation script).
    """
    # 1. Save to DB
    db_item = SensorData(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 2. Trigger Automation (Alert)
    notifier.check_and_alert({
        "device_id": data.device_id,
        "temperature": data.temperature
    })
    
    return db_item

@app.get("/api/data", response_model=List[SensorDataResponse])
def get_data(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns the latest data for the dashboard.
    """
    return db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Example endpoint for reporting (avg, min, max).
    """
    # Simple calculation example
    data = db.query(SensorData).all()
    if not data:
        return {"avg_temp": 0, "count": 0}
    
    avg_temp = sum([d.temperature for d in data]) / len(data)
    return {"avg_temp": round(avg_temp, 2), "count": len(data)}

# Serve frontend statico (deve essere l'ultimo per non coprire le API)
# Assumiamo che index.html sia in 'frontend/'
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
