from ..models.analysis import EconomicInput, EconomicResult
from .tus import normalize_min_max

def calculate_economic_metrics(data: EconomicInput) -> EconomicResult:
    """
    Calculate Economic metrics including Net Gain, ROI, Payback Period, and EUS.
    CORRECTED FORMULA: Net Gain = (E_total * P_energy) - M_total
    """
    warnings = []
    
    revenue = data.total_energy_kwh * data.energy_price_per_kwh
    net_gain = revenue - data.total_cost
    
    if net_gain < 0:
        warnings.append("Net kazanç negatif. Proje ekonomik olarak uygun değil.")
        
    # ROI as percentage: (Net Gain / Investment Cost) * 100
    if data.investment_cost <= 0:
        roi = float('inf') if net_gain > 0 else 0.0
    else:
        roi = (net_gain / data.investment_cost) * 100.0
        
    # Payback Period (simple): Investment / Annual Net Gain
    payback = None
    if net_gain > 0 and data.project_lifetime_years > 0:
        annual_net_gain = net_gain / data.project_lifetime_years
        if annual_net_gain > 0:
            payback = data.investment_cost / annual_net_gain
            if payback > data.project_lifetime_years:
                warnings.append(f"Geri ödeme süresi ({payback:.1f} yıl) proje ömründen ({data.project_lifetime_years} yıl) uzun.")
    
    # EUS (Economic Suitability Score) — custom definition since PDF lacked one.
    # Combines normalized ROI (weight 0.6) and normalized payback speed (weight 0.4).
    if net_gain <= 0:
        eus = 0.0
    else:
        # ROI component: 0% → 0, 100%+ → 1
        norm_roi = normalize_min_max(roi, 0.0, 100.0)
        
        # Payback speed component: faster payback = higher score
        # 0 years → 1.0 (instant), project_lifetime → 0.0 (barely breaks even)
        if payback is not None and data.project_lifetime_years > 0:
            norm_payback_speed = normalize_min_max(
                data.project_lifetime_years - payback,
                0.0,
                data.project_lifetime_years
            )
        else:
            norm_payback_speed = 0.5  # unknown payback, neutral
        
        eus = (0.6 * norm_roi + 0.4 * norm_payback_speed) * 100.0
        
    return EconomicResult(
        revenue=revenue,
        net_gain=net_gain,
        roi=roi,
        payback_period_years=payback,
        eus=eus,
        warnings=warnings
    )
