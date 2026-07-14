"""
ReLiOn Analysis Engine
A modular python package for calculating battery second-life feasibility.
"""

from .core.soh import calculate_soh
from .core.degradation import calculate_degradation, get_chemistry_profile, generate_degradation_curve
from .core.rul import calculate_rul
from .core.tus import calculate_tus
from .core.economic import calculate_economic_metrics
from .core.score import calculate_general_score
from .core.labels import (
    get_soh_label, get_rul_label, get_tus_label,
    get_eus_label, get_score_label, get_score_color
)
from .models.battery import BatteryInput, UsageScenario
from .models.analysis import (
    EconomicInput, AnalysisResult, ChemistryInfo, DegradationPoint
)
from .exceptions import AnalysisError, ValidationError

def analyze(battery: BatteryInput, economic: EconomicInput) -> AnalysisResult:
    """
    Run the complete analysis pipeline for a battery.
    Returns a rich AnalysisResult with metrics, labels, chart data, and warnings.
    """
    all_warnings = []
    
    # 1. State of Health (SoH)
    soh_result = calculate_soh(battery.measured_capacity, battery.nominal_capacity)
    all_warnings.extend(soh_result.warnings)
    
    # 2. Chemistry Profile
    profile = get_chemistry_profile(battery.chemistry_type)
    threshold_capacity = profile.threshold_capacity_ratio * battery.nominal_capacity
    
    # 3. Remaining Useful Life (RUL)
    rul_result = calculate_rul(
        battery.measured_capacity, threshold_capacity,
        profile.k, battery.nominal_capacity
    )
    all_warnings.extend(rul_result.warnings)
    
    # 4. Technical Suitability Score (TUS)
    tus_result = calculate_tus(soh_result.soh, battery.internal_resistance, rul_result.rul)
    all_warnings.extend(tus_result.warnings)
    
    # 5. Economic Analysis
    economic_result = calculate_economic_metrics(economic)
    all_warnings.extend(economic_result.warnings)
    
    # 6. General Score
    score_result = calculate_general_score(tus_result.tus, economic_result.eus)
    
    # 7. Degradation Curve (for frontend chart)
    max_future_cycles = int(rul_result.rul * 1.3) if rul_result.rul > 0 else 5000
    max_future_cycles = max(1000, min(max_future_cycles, 20000))
    curve_raw = generate_degradation_curve(
        battery.nominal_capacity, profile.k,
        max_cycles=max_future_cycles, step=max(1, max_future_cycles // 100)
    )
    curve = [DegradationPoint(**pt) for pt in curve_raw]
    
    # 8. Chemistry Info
    chem_info = ChemistryInfo(
        name=battery.chemistry_type.value,
        k=profile.k,
        threshold_soh=profile.threshold_capacity_ratio * 100,
        typical_resistance=profile.typical_internal_resistance
    )
    
    return AnalysisResult(
        # Core metrics
        soh=soh_result.soh,
        rul=rul_result.rul,
        tus=tus_result.tus,
        net_gain=economic_result.net_gain,
        revenue=economic_result.revenue,
        roi=economic_result.roi,
        payback_period_years=economic_result.payback_period_years,
        eus=economic_result.eus,
        general_score=score_result.score,
        
        # Labels
        soh_label=get_soh_label(soh_result.soh),
        rul_label=get_rul_label(rul_result.rul),
        tus_label=get_tus_label(tus_result.tus),
        eus_label=get_eus_label(economic_result.eus),
        score_label=get_score_label(score_result.score),
        score_color=get_score_color(score_result.score),
        
        # Chart data
        degradation_curve=curve,
        
        # Context
        chemistry_info=chem_info,
        
        # System
        warnings=all_warnings
    )
