import copy
from typing import List, Dict, Any
from relion_engine.models.battery import BatteryInput
from relion_engine.models.analysis import EconomicInput
from relion_engine import analyze

def run_sensitivity_sweep(
    base_battery: dict,
    base_economic: dict,
    sweep_param: str,
    param_type: str, # "battery" or "economic"
    min_val: float,
    max_val: float,
    steps: int = 20
) -> List[Dict[str, Any]]:
    """
    Runs a sensitivity analysis by varying one parameter and keeping others constant.
    Returns a list of data points suitable for plotting.
    """
    results = []
    step_size = (max_val - min_val) / max(1, (steps - 1))
    
    for i in range(steps):
        current_val = min_val + (i * step_size)
        
        # Clone bases
        bat_dict = copy.deepcopy(base_battery)
        eco_dict = copy.deepcopy(base_economic)
        
        if param_type == "battery":
            bat_dict[sweep_param] = current_val
        else:
            eco_dict[sweep_param] = current_val
            
        try:
            battery_input = BatteryInput(**bat_dict)
            economic_input = EconomicInput(**eco_dict)
            
            res = analyze(battery_input, economic_input)
            
            results.append({
                sweep_param: current_val,
                "soh": res.soh,
                "rul": res.rul,
                "tus": res.tus,
                "net_gain": res.net_gain,
                "eus": res.eus,
                "general_score": res.general_score,
                "valid": True
            })
        except Exception as e:
            results.append({
                sweep_param: current_val,
                "error": str(e),
                "valid": False
            })
            
    return results
