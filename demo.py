import json
from relion_engine import analyze
from relion_engine.models.battery import BatteryInput, ChemistryType, UsageScenario
from relion_engine.models.analysis import EconomicInput
from pydantic import ValidationError

def run_scenario(name, battery_data, economic_data):
    print(f"\n{'='*60}")
    print(f"SENARYO: {name}")
    print(f"{'='*60}")
    
    try:
        battery = BatteryInput(**battery_data)
        economic = EconomicInput(**economic_data)
        sonuc = analyze(battery, economic)
        
        print(f"\n📊 TEMEL METRIKLER:")
        print(f"  Pil Sagligi (SoH):      %{sonuc.soh:.2f}  [{sonuc.soh_label}]")
        print(f"  Kalan Omur (RUL):       {sonuc.rul:.0f} dongu  [{sonuc.rul_label}]")
        print(f"  Teknik Uygunluk (TUS):  {sonuc.tus:.2f}/100  [{sonuc.tus_label}]")
        
        print(f"\n💰 EKONOMIK METRIKLER:")
        print(f"  Gelir:                  ${sonuc.revenue:,.2f}")
        print(f"  Net Kazanc:             ${sonuc.net_gain:,.2f}")
        print(f"  ROI:                    %{sonuc.roi:.2f}")
        if sonuc.payback_period_years:
            print(f"  Geri Odeme Suresi:      {sonuc.payback_period_years:.1f} yil")
        print(f"  Ekonomik Uygunluk(EUS): {sonuc.eus:.2f}/100  [{sonuc.eus_label}]")
        
        print(f"\n⭐ GENEL DEGERLENDIRME:")
        print(f"  Skor:                   {sonuc.general_score:.2f}/100  [{sonuc.score_label}]")
        print(f"  Renk Kodu:              {sonuc.score_color}")
        
        print(f"\n🔬 KIMYA PROFILI:")
        print(f"  Kimya:                  {sonuc.chemistry_info.name}")
        print(f"  Bozunma katsayisi (k):  {sonuc.chemistry_info.k}")
        print(f"  Esik SoH:               %{sonuc.chemistry_info.threshold_soh}")
        
        print(f"\n📈 BOZUNMA EGRISI: {len(sonuc.degradation_curve)} veri noktasi uretildi")
        print(f"  Ilk nokta:  Dongu {sonuc.degradation_curve[0].cycle} -> %{sonuc.degradation_curve[0].soh_percent} SoH")
        print(f"  Son nokta:  Dongu {sonuc.degradation_curve[-1].cycle} -> %{sonuc.degradation_curve[-1].soh_percent} SoH")
        
        if sonuc.warnings:
            print(f"\n⚠️  UYARILAR ({len(sonuc.warnings)}):")
            for w in sonuc.warnings:
                print(f"   - {w}")
                
    except ValidationError as e:
        print(f"\n❌ DOGRULAMA HATASI:")
        for error in e.errors():
            print(f"   - {error['msg']} (Alan: {error['loc'][0]})")
    except Exception as e:
        print(f"\n❌ HATA: {e}")

print("="*60)
print("  ReLiOn Analiz Motoru — Kapsamli Demo")
print("="*60)

# 1. Ideal LFP — BESS
run_scenario("1. Ideal LFP Batarya — BESS Projesi", {
    "chemistry_type": ChemistryType.LFP,
    "nominal_capacity": 100.0,
    "measured_capacity": 95.0,
    "cycle_count": 500,
    "internal_resistance": 0.015,
    "age": 2.0,
    "usage_scenario": UsageScenario.BESS,
    "expected_lifetime_years": 10.0
}, {
    "total_energy_kwh": 80000.0,
    "energy_price_per_kwh": 0.20,
    "total_cost": 3000.0,
    "investment_cost": 1500.0,
    "project_lifetime_years": 10.0
})

# 2. Orta NMC — Ev Tipi
run_scenario("2. Orta Durumda NMC — Ev Tipi Depolama", {
    "chemistry_type": ChemistryType.NMC,
    "nominal_capacity": 50.0,
    "measured_capacity": 40.0,
    "cycle_count": 1800,
    "internal_resistance": 0.035,
    "age": 5.0,
    "usage_scenario": UsageScenario.HOME,
    "target_location": "Istanbul",
    "expected_lifetime_years": 7.0
}, {
    "total_energy_kwh": 25000.0,
    "energy_price_per_kwh": 0.18,
    "total_cost": 1800.0,
    "investment_cost": 1200.0,
    "project_lifetime_years": 7.0
})

# 3. Omrunu tamamlamis NCA — Mikro Sebeke
run_scenario("3. Omrunu Tamamlamis NCA — Mikro Sebeke", {
    "chemistry_type": ChemistryType.NCA,
    "nominal_capacity": 60.0,
    "measured_capacity": 38.0,
    "cycle_count": 3000,
    "internal_resistance": 0.08,
    "age": 7.0,
    "usage_scenario": UsageScenario.MICROGRID,
    "expected_lifetime_years": 3.0
}, {
    "total_energy_kwh": 8000.0,
    "energy_price_per_kwh": 0.12,
    "total_cost": 2000.0,
    "investment_cost": 1500.0,
    "project_lifetime_years": 3.0
})

# 4. Zarar eden proje
run_scenario("4. Ekonomik Zarar — Dusuk Enerji Uretimi", {
    "chemistry_type": ChemistryType.LFP,
    "nominal_capacity": 100.0,
    "measured_capacity": 82.0,
    "cycle_count": 1200,
    "internal_resistance": 0.025,
    "age": 4.0,
    "usage_scenario": UsageScenario.BESS
}, {
    "total_energy_kwh": 5000.0,
    "energy_price_per_kwh": 0.08,
    "total_cost": 3000.0,
    "investment_cost": 2000.0,
    "project_lifetime_years": 5.0
})

# 5. Hatali veri girisi
run_scenario("5. Hatali Veri (Sistem Reddedecek)", {
    "chemistry_type": ChemistryType.LFP,
    "nominal_capacity": 100.0,
    "measured_capacity": 150.0,
    "cycle_count": -50,
    "internal_resistance": 0,
    "age": 1.0
}, {
    "total_energy_kwh": 10000.0,
    "energy_price_per_kwh": 0.15,
    "total_cost": 1000.0,
    "investment_cost": 500.0
})

# 6. API'ye gidecek JSON ciktisi ornegi
print(f"\n{'='*60}")
print("BONUS: API/Frontend icin JSON cikti ornegi")
print(f"{'='*60}")
battery = BatteryInput(
    chemistry_type=ChemistryType.LFP,
    nominal_capacity=100.0, measured_capacity=88.0,
    cycle_count=900, internal_resistance=0.02,
    usage_scenario=UsageScenario.BESS
)
economic = EconomicInput(
    total_energy_kwh=60000.0, energy_price_per_kwh=0.16,
    total_cost=2000.0, investment_cost=1000.0
)
result = analyze(battery, economic)
# Sadece ilk 3 bozunma noktasini goster
result_dict = result.model_dump()
result_dict["degradation_curve"] = result_dict["degradation_curve"][:3]
print(json.dumps(result_dict, indent=2, ensure_ascii=False))
