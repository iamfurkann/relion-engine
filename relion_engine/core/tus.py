from ..exceptions import AnalysisError
from ..models.analysis import TUSResult

def normalize_min_max(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-1 range. Clamps to 0-1 if outside bounds."""
    if min_val == max_val:
        return 1.0 if value >= max_val else 0.0
    norm = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, norm))

def calculate_tus(soh: float, internal_resistance_mohm: float, rul: float, 
                 w1: float = 0.4, w2: float = 0.3, w3: float = 0.3) -> TUSResult:
    """
    Calculate Technical Suitability Score (TUS).
    Components are normalized before weighting.
    """
    warnings = []
    
    if abs((w1 + w2 + w3) - 1.0) > 0.001:
        raise AnalysisError("Weights must sum to 1.0")
        
    if internal_resistance_mohm <= 0:
        raise AnalysisError("Internal resistance must be greater than 0")
        
    # Normalization references (these could be configurable)
    # SoH: 0 to 100
    norm_soh = normalize_min_max(soh, 0.0, 100.0)
    
    # 1/R: R typically 1 to 50 mOhm. 1/R is larger for better batteries.
    # We normalize 1/R where R=50 is bad (0) and R=1 is good (1).
    inv_r = 1.0 / internal_resistance_mohm
    min_inv_r = 1.0 / 50.0  # 0.02
    max_inv_r = 1.0 / 1.0   # 1.0
    norm_inv_r = normalize_min_max(inv_r, min_inv_r, max_inv_r)
    
    # RUL: 0 to 5000 cycles
    norm_rul = normalize_min_max(rul, 0.0, 5000.0)
    
    tus_normalized = (w1 * norm_soh) + (w2 * norm_inv_r) + (w3 * norm_rul)
    tus_final = tus_normalized * 100.0 # Scale to 0-100
    
    return TUSResult(tus=tus_final, warnings=warnings)
