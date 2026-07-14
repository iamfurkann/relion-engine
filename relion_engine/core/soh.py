from ..exceptions import AnalysisError
from ..models.analysis import SoHResult

def calculate_soh(measured_capacity: float, nominal_capacity: float) -> SoHResult:
    """
    Calculate State of Health (SoH).
    SoH = (C_measured / C_nominal) * 100
    """
    if nominal_capacity <= 0:
        raise AnalysisError("Nominal capacity must be greater than 0")
        
    warnings = []
    
    if measured_capacity == 0:
        warnings.append("Battery measured capacity is 0 (Dead battery)")
        return SoHResult(soh=0.0, warnings=warnings)
        
    soh = (measured_capacity / nominal_capacity) * 100.0
    
    if soh > 100.0:
        warnings.append(f"SoH ({soh:.1f}%) > 100%. Capping at 100%.")
        soh = 100.0
        
    return SoHResult(soh=soh, warnings=warnings)
