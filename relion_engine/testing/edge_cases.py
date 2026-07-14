import copy
from typing import List, Dict, Any
from relion_engine.models.battery import BatteryInput, ChemistryType, UsageScenario
from relion_engine.models.analysis import EconomicInput
from relion_engine import analyze
from pydantic import ValidationError

def create_valid_bases():
    bat = {
        "chemistry_type": "LFP",
        "nominal_capacity": 100.0,
        "measured_capacity": 95.0,
        "cycle_count": 500,
        "internal_resistance": 0.015,
        "age": 2.0,
        "usage_scenario": "BESS",
        "expected_lifetime_years": 10.0
    }
    eco = {
        "total_energy_kwh": 80000.0,
        "energy_price_per_kwh": 0.20,
        "total_cost": 3000.0,
        "investment_cost": 1500.0,
        "project_lifetime_years": 10.0
    }
    return bat, eco

def run_edge_cases() -> List[Dict[str, Any]]:
    results = []
    
    def run_case(name: str, desc: str, bat_override: dict, eco_override: dict, expected_status: str):
        bat, eco = create_valid_bases()
        bat.update(bat_override)
        eco.update(eco_override)
        
        status = "UNKNOWN"
        error_msg = ""
        try:
            battery_input = BatteryInput(**bat)
            economic_input = EconomicInput(**eco)
            res = analyze(battery_input, economic_input)
            status = "SUCCESS"
        except ValidationError as ve:
            status = "VALIDATION_ERROR"
            error_msg = str(ve)
        except Exception as e:
            status = "ANALYSIS_ERROR"
            error_msg = str(e)
            
        match = (status == expected_status)
        results.append({
            "name": name,
            "description": desc,
            "expected_status": expected_status,
            "actual_status": status,
            "error_msg": error_msg[:100] + "..." if len(error_msg) > 100 else error_msg,
            "pass": match
        })
        
    # 1. Zero nominal capacity (Should fail validation according to Section 8)
    run_case("Sıfır Nominal Kapasite", "C_nominal = 0 sıfıra bölme hatası oluşturur.", 
             {"nominal_capacity": 0}, {}, "VALIDATION_ERROR")
             
    # 2. Measured capacity > Nominal Capacity * 1.1 (Validation error)
    run_case("Aşırı Ölçülen Kapasite", "C_measured > C_nominal * 1.1", 
             {"measured_capacity": 120.0}, {}, "VALIDATION_ERROR")
             
    # 3. Measured capacity = 0 (Dead battery - Should return SUCCESS but SoH=0)
    # Note: BatteryInput might enforce >0, let's see what happens. The report says C_measured 0.1-nominal*1.1
    # So C_measured = 0 might be validation error. We will test 0.0, if it fails validation, it's correct based on constraints.
    run_case("Ölü Batarya (C_meas=0)", "C_measured = 0", 
             {"measured_capacity": 0.0}, {}, "VALIDATION_ERROR")
             
    # 4. Negative values (Validation error)
    run_case("Negatif Direnç", "R_ic < 0", 
             {"internal_resistance": -0.05}, {}, "VALIDATION_ERROR")
             
    # 5. Dead battery below threshold (SUCCESS but RUL=0)
    run_case("Eşik Kapasitesi Altında", "C_measured <= C_threshold", 
             {"measured_capacity": 70.0}, {}, "SUCCESS") # LFP threshold is usually 0.8 * 100 = 80. So 70 is below threshold.
             
    # 6. Zero investment cost
    run_case("Sıfır Yatırım Maliyeti", "investment_cost = 0", 
             {}, {"investment_cost": 0.0}, "SUCCESS") # Actually, can be 0? The report doesn't explicitly restrict to >0 but typically should be handled. If it succeeds, ROI is inf. Let's expect SUCCESS or VALIDATION_ERROR. Let's put SUCCESS as economic.py handles investment=0.
    
    return results
