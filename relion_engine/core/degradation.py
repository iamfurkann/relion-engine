from ..models.chemistry import ChemistryType, ChemistryProfile, CHEMISTRY_PROFILES
from ..exceptions import ValidationError
from typing import List, Dict

def get_chemistry_profile(chemistry_type: ChemistryType) -> ChemistryProfile:
    """Get the profile for a given chemistry."""
    if chemistry_type not in CHEMISTRY_PROFILES:
        raise ValidationError(f"Unknown chemistry type: {chemistry_type}")
    return CHEMISTRY_PROFILES[chemistry_type]

def calculate_degradation(initial_capacity: float, k: float, cycles: int) -> float:
    """
    Calculate expected capacity after 'cycles' using the linear model.
    C(n) = C0 * (1 - k * n)
    """
    if initial_capacity < 0 or k < 0 or cycles < 0:
        raise ValueError("Initial capacity, k, and cycles must be non-negative")
        
    capacity = initial_capacity * (1 - (k * cycles))
    # Cap at 0
    return max(0.0, capacity)

def generate_degradation_curve(
    initial_capacity: float,
    k: float,
    max_cycles: int,
    step: int = 100
) -> List[Dict[str, float]]:
    """
    Generate a series of (cycle, capacity) data points for charting.
    Used by the frontend for the "Bozunma Eğrisi" line chart.
    Stops early if capacity reaches 0.
    """
    if initial_capacity <= 0 or k < 0 or max_cycles < 0:
        raise ValueError("Invalid parameters for degradation curve")
    
    curve = []
    for n in range(0, max_cycles + 1, step):
        cap = calculate_degradation(initial_capacity, k, n)
        soh_pct = (cap / initial_capacity) * 100.0
        curve.append({
            "cycle": n,
            "capacity": round(cap, 4),
            "soh_percent": round(soh_pct, 2)
        })
        if cap <= 0:
            break
    return curve
