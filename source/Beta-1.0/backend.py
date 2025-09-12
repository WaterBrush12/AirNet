# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uvicorn

# --- FastAPI app ---
app = FastAPI(title="ESP32 Air Quality Backend")

# --- Request model ---
class AirData(BaseModel):
    uniqueid: str
    particulateMatter: Dict[str, float]  # e.g., {"pm2_5": 12.3, "pm10": 25.6}
    volatileOrganicCompounds: float
    gases: Dict[str, float]  # e.g., {"CO": 0.4, "NO2": 0.02, "O3": 0.03}

# --- Endpoint ---
@app.post("/air")
async def receive_air_data(data: AirData):
    print("Received air data:")
    print(data.json())  # log full JSON payload
    return {"status": "ok"}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
