from relion_engine import analyze
from relion_engine.models.battery import BatteryInput, ChemistryType, UsageScenario
from relion_engine.models.analysis import EconomicInput

def test_full_analysis_healthy_profitable():
    battery = BatteryInput(
        chemistry_type=ChemistryType.LFP,
        nominal_capacity=100.0,
        measured_capacity=85.0,
        cycle_count=1000,
        internal_resistance=2.5,
        age=3.0,
        usage_scenario=UsageScenario.BESS,
        expected_lifetime_years=10.0
    )
    economic = EconomicInput(
        total_energy_kwh=50000.0,
        energy_price_per_kwh=0.15,
        total_cost=2500.0,
        investment_cost=1000.0,
        project_lifetime_years=10.0
    )
    
    result = analyze(battery, economic)
    
    # Core metrics
    assert result.soh == 85.0
    assert result.rul > 0
    assert result.net_gain == 5000.0
    assert result.revenue == 7500.0
    assert result.eus > 0
    assert result.tus > 0
    assert result.general_score > 0
    
    # Labels exist
    assert result.soh_label == "İyi"
    assert result.score_label in ["Çok Uygun", "Uygun", "Şartlı Uygun", "Riskli", "Uygun Değil"]
    assert result.score_color.startswith("#")
    
    # Chart data
    assert len(result.degradation_curve) > 10
    assert result.degradation_curve[0].cycle == 0
    
    # Chemistry info
    assert result.chemistry_info.name == "LFP"
    assert result.chemistry_info.k > 0

def test_full_analysis_dead_battery():
    battery = BatteryInput(
        chemistry_type=ChemistryType.NMC,
        nominal_capacity=100.0,
        measured_capacity=70.0,
        cycle_count=2000,
        internal_resistance=5.0,
        usage_scenario=UsageScenario.HOME
    )
    economic = EconomicInput(
        total_energy_kwh=10000.0,
        energy_price_per_kwh=0.15,
        total_cost=2500.0,
        investment_cost=1000.0,
        project_lifetime_years=5.0
    )
    
    result = analyze(battery, economic)
    
    assert result.soh == 70.0
    assert result.rul == 0.0
    assert result.rul_label == "Ömrünü Tamamlamış"
    assert len([w for w in result.warnings if "threshold" in w.lower() or "eşik" in w.lower() or "already" in w.lower()]) > 0

def test_full_analysis_microgrid():
    """Test MICROGRID scenario passes through correctly."""
    battery = BatteryInput(
        chemistry_type=ChemistryType.NCA,
        nominal_capacity=60.0,
        measured_capacity=50.0,
        cycle_count=800,
        internal_resistance=3.0,
        usage_scenario=UsageScenario.MICROGRID,
        expected_lifetime_years=7.0
    )
    economic = EconomicInput(
        total_energy_kwh=30000.0,
        energy_price_per_kwh=0.12,
        total_cost=1500.0,
        investment_cost=800.0,
        project_lifetime_years=7.0
    )
    
    result = analyze(battery, economic)
    assert result.general_score > 0
    assert result.chemistry_info.name == "NCA"
    assert result.payback_period_years is not None
