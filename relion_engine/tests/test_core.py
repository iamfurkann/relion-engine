import pytest
from pydantic import ValidationError
from relion_engine.models.battery import BatteryInput, ChemistryType, UsageScenario
from relion_engine.core.soh import calculate_soh
from relion_engine.core.degradation import calculate_degradation, generate_degradation_curve
from relion_engine.core.rul import calculate_rul
from relion_engine.core.tus import calculate_tus
from relion_engine.core.economic import calculate_economic_metrics
from relion_engine.core.score import calculate_general_score
from relion_engine.core.labels import get_soh_label, get_score_label, get_score_color
from relion_engine.models.analysis import EconomicInput
from relion_engine.exceptions import AnalysisError


# === Battery Input Validation ===

def test_battery_valid():
    b = BatteryInput(
        chemistry_type=ChemistryType.NCA,
        nominal_capacity=50.0,
        measured_capacity=45.0,
        cycle_count=500,
        internal_resistance=1.5,
        usage_scenario=UsageScenario.BESS,
        expected_lifetime_years=10.0
    )
    assert b.usage_scenario == UsageScenario.BESS
    assert b.expected_lifetime_years == 10.0

def test_battery_defaults():
    """usage_scenario defaults to BESS, expected_lifetime defaults to 5."""
    b = BatteryInput(
        chemistry_type=ChemistryType.LFP,
        nominal_capacity=100.0,
        measured_capacity=80.0,
        cycle_count=1000,
        internal_resistance=2.0
    )
    assert b.usage_scenario == UsageScenario.BESS
    assert b.expected_lifetime_years == 5.0

def test_battery_invalid_overcapacity():
    with pytest.raises(ValidationError):
        BatteryInput(
            chemistry_type=ChemistryType.NCA,
            nominal_capacity=50.0,
            measured_capacity=60.0,
            cycle_count=500,
            internal_resistance=1.5
        )

def test_battery_invalid_negative_cycle():
    with pytest.raises(ValidationError):
        BatteryInput(
            chemistry_type=ChemistryType.NCA,
            nominal_capacity=50.0,
            measured_capacity=45.0,
            cycle_count=-1,
            internal_resistance=1.5
        )

def test_battery_invalid_zero_resistance():
    with pytest.raises(ValidationError):
        BatteryInput(
            chemistry_type=ChemistryType.NCA,
            nominal_capacity=50.0,
            measured_capacity=45.0,
            cycle_count=500,
            internal_resistance=0
        )


# === SoH ===

def test_soh_normal():
    res = calculate_soh(80.0, 100.0)
    assert res.soh == 80.0
    assert len(res.warnings) == 0

def test_soh_capped():
    res = calculate_soh(105.0, 100.0)
    assert res.soh == 100.0
    assert len(res.warnings) == 1

def test_soh_dead():
    res = calculate_soh(0.0, 100.0)
    assert res.soh == 0.0
    assert any("0" in w for w in res.warnings)

def test_soh_division_by_zero():
    with pytest.raises(AnalysisError):
        calculate_soh(50.0, 0.0)


# === Degradation ===

def test_degradation_basic():
    cap = calculate_degradation(100.0, 0.00005, 2000)
    assert cap == pytest.approx(90.0, abs=0.1)

def test_degradation_caps_at_zero():
    cap = calculate_degradation(100.0, 0.001, 2000)
    assert cap == 0.0

def test_degradation_curve():
    curve = generate_degradation_curve(100.0, 0.00005, 5000, step=1000)
    assert len(curve) >= 5
    assert curve[0]["cycle"] == 0
    assert curve[0]["capacity"] == 100.0
    assert curve[-1]["soh_percent"] <= 100.0
    # Each point should be <= previous
    for i in range(1, len(curve)):
        assert curve[i]["capacity"] <= curve[i-1]["capacity"]


# === RUL ===

def test_rul_positive():
    res = calculate_rul(85.0, 80.0, 0.000035, 100.0)
    assert res.rul > 0
    assert len(res.warnings) == 0

def test_rul_below_threshold():
    res = calculate_rul(70.0, 80.0, 0.000035, 100.0)
    assert res.rul == 0.0
    assert len(res.warnings) == 1

def test_rul_zero_k():
    with pytest.raises(AnalysisError):
        calculate_rul(85.0, 80.0, 0.0, 100.0)


# === TUS ===

def test_tus_perfect():
    """Perfect battery should get high TUS."""
    res = calculate_tus(100.0, 1.0, 5000.0)
    assert res.tus > 90.0

def test_tus_bad():
    """Bad battery should get low TUS."""
    res = calculate_tus(50.0, 40.0, 100.0)
    assert res.tus < 30.0

def test_tus_weights_must_sum():
    with pytest.raises(AnalysisError):
        calculate_tus(80.0, 2.0, 1000.0, w1=0.5, w2=0.5, w3=0.5)


# === Economic ===

def test_economic_profitable():
    inp = EconomicInput(
        total_energy_kwh=100.0,
        energy_price_per_kwh=2.0,
        total_cost=50.0,
        investment_cost=100.0,
        project_lifetime_years=5.0
    )
    res = calculate_economic_metrics(inp)
    assert res.revenue == 200.0
    assert res.net_gain == 150.0
    assert res.roi == 150.0
    assert res.payback_period_years is not None
    assert res.eus > 0
    assert len(res.warnings) == 0

def test_economic_loss():
    inp = EconomicInput(
        total_energy_kwh=10.0,
        energy_price_per_kwh=2.0,
        total_cost=50.0,
        investment_cost=100.0,
        project_lifetime_years=5.0
    )
    res = calculate_economic_metrics(inp)
    assert res.net_gain == -30.0
    assert res.eus == 0.0
    assert len(res.warnings) >= 1


# === Score ===

def test_score_balanced():
    res = calculate_general_score(80.0, 60.0)
    assert res.score == 70.0

def test_score_weights_must_sum():
    with pytest.raises(AnalysisError):
        calculate_general_score(80.0, 60.0, alpha=0.8, beta=0.8)


# === Labels ===

def test_labels():
    assert get_soh_label(95.0) == "Mükemmel"
    assert get_soh_label(85.0) == "İyi"
    assert get_soh_label(75.0) == "Orta"
    assert get_soh_label(55.0) == "Kritik"
    
    assert get_score_label(90.0) == "Çok Uygun"
    assert get_score_label(30.0) == "Riskli"

def test_score_colors():
    assert get_score_color(90.0) == "#22c55e"
    assert get_score_color(15.0) == "#ef4444"
