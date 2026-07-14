from ..exceptions import AnalysisError
from ..models.analysis import RULResult

def calculate_rul(measured_capacity: float, threshold_capacity: float, k: float, initial_capacity: float) -> RULResult:
    """
    Calculate Remaining Useful Life (RUL) in cycles.
    CORRECTED FORMULA: RUL = (C_measured - C_threshold) / (k * C0)
    """
    warnings = []
    
    if k <= 0:
        raise AnalysisError("Degradation coefficient (k) must be greater than 0")
    if initial_capacity <= 0:
        raise AnalysisError("Initial capacity must be greater than 0")
        
    # If already past threshold
    if measured_capacity <= threshold_capacity:
        warnings.append("Battery is already at or below threshold capacity.")
        return RULResult(rul=0.0, warnings=warnings)
        
    degradation_rate_per_cycle = k * initial_capacity
    
    rul = (measured_capacity - threshold_capacity) / degradation_rate_per_cycle
    
    return RULResult(rul=rul, warnings=warnings)
