import copy
import random
import statistics
from typing import Dict, Any, List
from relion_engine.models.battery import BatteryInput
from relion_engine.models.analysis import EconomicInput
from relion_engine import analyze

def run_monte_carlo(
    base_battery: dict,
    base_economic: dict,
    iterations: int = 1000
) -> Dict[str, Any]:
    """
    Runs Monte Carlo simulation by adding Gaussian noise to key parameters:
    - measured_capacity (sigma: 2%)
    - internal_resistance (sigma: 5%)
    - age (sigma: 10%)
    - energy_price_per_kwh (sigma: 5%)
    """
    results_rul = []
    results_tus = []
    results_net_gain = []
    results_score = []
    
    valid_runs = 0
    errors = 0
    
    # Store distribution points for histograms (sample of max 100 to not overload frontend)
    samples = []
    
    for i in range(iterations):
        bat_dict = copy.deepcopy(base_battery)
        eco_dict = copy.deepcopy(base_economic)
        
        # Apply noise
        bat_dict["measured_capacity"] = random.gauss(bat_dict["measured_capacity"], bat_dict["measured_capacity"] * 0.02)
        bat_dict["internal_resistance"] = random.gauss(bat_dict["internal_resistance"], bat_dict["internal_resistance"] * 0.05)
        bat_dict["age"] = max(0.1, random.gauss(bat_dict["age"], bat_dict["age"] * 0.1))
        
        eco_dict["energy_price_per_kwh"] = max(0.01, random.gauss(eco_dict["energy_price_per_kwh"], eco_dict["energy_price_per_kwh"] * 0.05))
        
        try:
            battery_input = BatteryInput(**bat_dict)
            economic_input = EconomicInput(**eco_dict)
            
            res = analyze(battery_input, economic_input)
            
            results_rul.append(res.rul)
            results_tus.append(res.tus)
            results_net_gain.append(res.net_gain)
            results_score.append(res.general_score)
            
            valid_runs += 1
            if len(samples) < 100:
                samples.append({
                    "iteration": i,
                    "rul": res.rul,
                    "tus": res.tus,
                    "net_gain": res.net_gain,
                    "score": res.general_score
                })
        except Exception:
            errors += 1
            
    def compute_stats(data: List[float]) -> Dict[str, float]:
        if not data: return {}
        data.sort()
        n = len(data)
        return {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "stdev": statistics.stdev(data) if n > 1 else 0.0,
            "min": data[0],
            "max": data[-1],
            "p5": data[int(n * 0.05)],
            "p95": data[int(n * 0.95)]
        }
        
    return {
        "summary": {
            "iterations": iterations,
            "valid_runs": valid_runs,
            "errors": errors
        },
        "stats": {
            "rul": compute_stats(results_rul),
            "tus": compute_stats(results_tus),
            "net_gain": compute_stats(results_net_gain),
            "score": compute_stats(results_score)
        },
        "samples": samples
    }
