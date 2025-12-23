from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Rent Prediction Service")

class RentRequest(BaseModel):
    lat: float
    lon: float
    square: float
    property_type: str = "office"

@app.post("/predict")
async def predict(request: RentRequest):
    start = datetime.now()
    
    async def get_maps():
        await asyncio.sleep(0.3)
        return {"metro": 500, "poi": 42}
    
    async def get_yandex():
        await asyncio.sleep(0.4)
        return {"rubrics": ["office", "business"]}
    
    maps_data, ya_data = await asyncio.gather(get_maps(), get_yandex())
    
    price = request.square * 1500 * (1.3 if maps_data["metro"] < 500 else 1.0)
    
    return {
        "price": round(price, 2),
        "processing_ms": (datetime.now() - start).total_seconds() * 1000,
        "features": {
            "metro_distance": maps_data["metro"],
            "rubrics": ya_data["rubrics"]
        }
    }

@app.get("/")
def root():
    return {"service": "Rent Prediction API"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
