from typing import Dict, Any, List
from relion_engine.models.battery import BatteryInput
from relion_engine.models.analysis import EconomicInput
from relion_engine.core.soh import calculate_soh
from relion_engine.core.rul import calculate_rul
from relion_engine.core.tus import calculate_tus, normalize_min_max
from relion_engine.core.economic import calculate_economic_metrics
from relion_engine.core.score import calculate_general_score
from relion_engine.core.degradation import get_chemistry_profile

class TraceableAnalyzer:
    """
    Wraps the core analysis engine to provide deep tracing of formulas, 
    intermediate variables, and strict mathematical validation.
    """
    def __init__(self, battery: BatteryInput, economic: EconomicInput):
        self.battery = battery
        self.economic = economic
        self.trace: List[Dict[str, Any]] = []

    def _log_step(self, step_name: str, formula: str, variables: Dict[str, Any], 
                  intermediates: Dict[str, Any], final_result: Any, 
                  engine_result: Any, match: bool):
        self.trace.append({
            "step": step_name,
            "formula": formula,
            "inputs": variables,
            "intermediates": intermediates,
            "lab_result": final_result,
            "engine_result": engine_result,
            "match": match,
            "status": "PASS" if match else "FAIL"
        })

    def run(self) -> Dict[str, Any]:
        try:
            # 1. State of Health
            b = self.battery
            e = self.economic
            
            # SoH Trace
            soh_lab = (b.measured_capacity / b.nominal_capacity) * 100.0 if b.nominal_capacity > 0 else 0
            if soh_lab > 100.0: soh_lab = 100.0
            soh_engine = calculate_soh(b.measured_capacity, b.nominal_capacity).soh
            
            self._log_step(
                "SoH (Pil Sağlığı Durumu)", 
                "SoH = (C_measured / C_nominal) * 100",
                {"C_measured": b.measured_capacity, "C_nominal": b.nominal_capacity},
                {},
                soh_lab, soh_engine, abs(soh_lab - soh_engine) < 1e-5
            )

            # Chemistry Profile
            profile = get_chemistry_profile(b.chemistry_type)
            threshold_capacity = profile.threshold_capacity_ratio * b.nominal_capacity
            
            # RUL Trace
            degradation_rate = profile.k * b.nominal_capacity
            rul_lab = (b.measured_capacity - threshold_capacity) / degradation_rate if degradation_rate > 0 else 0
            if b.measured_capacity <= threshold_capacity: rul_lab = 0.0
            
            rul_engine = calculate_rul(b.measured_capacity, threshold_capacity, profile.k, b.nominal_capacity).rul
            
            self._log_step(
                "RUL (Kalan Ömür)", 
                "RUL = (C_measured - C_threshold) / (k * C_nominal)",
                {"C_measured": b.measured_capacity, "C_threshold": threshold_capacity, "k": profile.k, "C_nominal": b.nominal_capacity},
                {"degradation_rate_per_cycle": degradation_rate},
                rul_lab, rul_engine, abs(rul_lab - rul_engine) < 1e-5
            )

            # TUS Trace
            norm_soh = normalize_min_max(soh_lab, 0.0, 100.0)
            inv_r = 1.0 / b.internal_resistance if b.internal_resistance > 0 else 0
            norm_inv_r = normalize_min_max(inv_r, 1.0/50.0, 1.0/1.0)
            norm_rul = normalize_min_max(rul_lab, 0.0, 5000.0)
            tus_lab = ((0.4 * norm_soh) + (0.3 * norm_inv_r) + (0.3 * norm_rul)) * 100.0
            
            tus_engine = calculate_tus(soh_lab, b.internal_resistance, rul_lab).tus
            
            self._log_step(
                "TUS (Teknik Uygunluk Skoru)",
                "TUS = 100 * (w1*norm_soh + w2*norm_inv_r + w3*norm_rul)",
                {"soh": soh_lab, "R_internal": b.internal_resistance, "rul": rul_lab, "w1": 0.4, "w2": 0.3, "w3": 0.3},
                {"norm_soh": norm_soh, "inv_R": inv_r, "norm_inv_r": norm_inv_r, "norm_rul": norm_rul},
                tus_lab, tus_engine, abs(tus_lab - tus_engine) < 1e-5
            )

            # Economic Trace
            revenue = e.total_energy_kwh * e.energy_price_per_kwh
            net_gain_lab = revenue - e.total_cost
            roi_lab = (net_gain_lab / e.investment_cost) * 100.0 if e.investment_cost > 0 else 0
            
            payback_lab = None
            if net_gain_lab > 0 and e.project_lifetime_years > 0:
                annual = net_gain_lab / e.project_lifetime_years
                if annual > 0: payback_lab = e.investment_cost / annual
            
            norm_roi = normalize_min_max(roi_lab, 0.0, 100.0)
            norm_payback = normalize_min_max(e.project_lifetime_years - payback_lab, 0.0, e.project_lifetime_years) if payback_lab else 0.5
            eus_lab = (0.6 * norm_roi + 0.4 * norm_payback) * 100.0 if net_gain_lab > 0 else 0.0
            
            eco_engine = calculate_economic_metrics(e)
            
            self._log_step(
                "Ekonomik Metrikler ve EUS",
                "Net_Gain = (E * P) - Cost; EUS = 100 * (0.6*norm_roi + 0.4*norm_payback)",
                {"E_total": e.total_energy_kwh, "Price": e.energy_price_per_kwh, "Cost": e.total_cost, "Investment": e.investment_cost, "Lifetime": e.project_lifetime_years},
                {"revenue": revenue, "net_gain": net_gain_lab, "roi": roi_lab, "payback": payback_lab, "norm_roi": norm_roi, "norm_payback": norm_payback},
                eus_lab, eco_engine.eus, abs(eus_lab - eco_engine.eus) < 1e-5
            )

            # General Score
            score_lab = (0.5 * tus_lab) + (0.5 * eus_lab)
            score_engine = calculate_general_score(tus_engine, eco_engine.eus).score
            
            self._log_step(
                "Genel Skor",
                "Score = alpha * TUS + beta * EUS",
                {"TUS": tus_lab, "EUS": eus_lab, "alpha": 0.5, "beta": 0.5},
                {},
                score_lab, score_engine, abs(score_lab - score_engine) < 1e-5
            )

            return {
                "success": True,
                "overall_match": all(t["match"] for t in self.trace),
                "trace": self.trace
            }
        except Exception as ex:
            return {
                "success": False,
                "error": str(ex),
                "trace": self.trace
            }
