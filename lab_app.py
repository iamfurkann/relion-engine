from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from relion_engine.models.battery import BatteryInput
from relion_engine.models.analysis import EconomicInput

from relion_engine.testing import (
    TraceableAnalyzer,
    run_sensitivity_sweep,
    run_monte_carlo,
    run_edge_cases
)

app = FastAPI(title="ReLiOn Analysis Engine Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("lab.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/lab/evaluate")
async def lab_evaluate(request: Request):
    """Deep trace evaluation of formulas"""
    data = await request.json()
    try:
        battery = BatteryInput(**data.get("battery", {}))
        economic = EconomicInput(**data.get("economic", {}))
        
        analyzer = TraceableAnalyzer(battery, economic)
        return analyzer.run()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/lab/sensitivity")
async def lab_sensitivity(request: Request):
    """Sensitivity sweep on a parameter"""
    data = await request.json()
    try:
        results = run_sensitivity_sweep(
            base_battery=data.get("battery", {}),
            base_economic=data.get("economic", {}),
            sweep_param=data.get("sweep_param"),
            param_type=data.get("param_type"),
            min_val=data.get("min_val"),
            max_val=data.get("max_val"),
            steps=data.get("steps", 20)
        )
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/lab/monte_carlo")
async def lab_monte_carlo(request: Request):
    """Monte carlo simulation for uncertainty"""
    data = await request.json()
    try:
        results = run_monte_carlo(
            base_battery=data.get("battery", {}),
            base_economic=data.get("economic", {}),
            iterations=data.get("iterations", 1000)
        )
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/lab/edge_cases")
async def lab_edge_cases():
    """Run predefined edge cases"""
    try:
        results = run_edge_cases()
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab_app:app", host="127.0.0.1", port=8080, reload=True)
