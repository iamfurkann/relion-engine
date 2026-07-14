from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from relion_engine import analyze
from relion_engine.models.battery import BatteryInput
from relion_engine.models.analysis import EconomicInput

app = FastAPI(title="ReLiOn Engine Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def run_analysis(request: Request):
    data = await request.json()
    
    battery_data = data.get("battery", {})
    economic_data = data.get("economic", {})
    
    try:
        battery = BatteryInput(**battery_data)
        economic = EconomicInput(**economic_data)
        
        result = analyze(battery, economic)
        
        return {
            "success": True,
            "data": result.model_dump()
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": "Doğrulama Hatası",
            "details": e.errors()
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Analiz Hatası",
            "details": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
