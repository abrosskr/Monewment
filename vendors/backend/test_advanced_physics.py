import sys
import os
import math

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics

def test_evaporation_and_concentration():
    print("\n💨 Testing Evaporation & Concentration Dynamics...")
    
    ingredients = {
        "water": 500.0,
        "soy_sauce": 50.0 
    }
    
    # Scene 1: Before cooking
    initial = FisPhysics.estimate_composite_properties(ingredients, cooking_duration=0)
    print(f"   [Initial] pH: {initial['composite_ph']}, Viscosity: {initial['composite_viscosity_cp']}cp")
    
    # Scene 2: After 10 mins (600s) boiling
    boiled = FisPhysics.estimate_composite_properties(ingredients, cooking_duration=600, cooking_method="BOILING")
    print(f"   [After Boiling 10m] Final Mass: {boiled['final_mass_g']}g, Factor: {boiled['concentration_factor']}x")
    print(f"   => New pH: {boiled['composite_ph']}")
    print(f"   => New Viscosity: {boiled['composite_viscosity_cp']}cp")
    
    assert boiled['final_mass_g'] < 550.0
    assert boiled['composite_viscosity_cp'] > initial['composite_viscosity_cp']

def test_arrhenius_kinetics():
    print("\n🧪 Testing Arrhenius Reaction Kinetics...")
    low_expo = FisPhysics.calculate_reaction_intensity(154, 30, "MAILLARD") 
    high_expo = FisPhysics.calculate_reaction_intensity(154, 180, "MAILLARD")
    print(f"   Maillard Intensity (154C, 30s): {low_expo}")
    print(f"   Maillard Intensity (154C, 180s): {high_expo}")
    assert high_expo > low_expo

def test_thermal_dynamics():
    print("\n🔥 Testing Thermal Dynamics (Efficiency Logic)...")
    small_time = FisPhysics.calculate_cooking_duration(200, 4.18, 80) 
    large_time = FisPhysics.calculate_cooking_duration(2000, 4.18, 80) 
    print(f"   Time to boil 200g: {small_time}s")
    print(f"   Time to boil 2kg: {large_time}s")
    assert large_time > small_time * 10 

def test_ambience_and_inertia():
    print("\n🌍 Testing Ambience & Thermal Inertia...")
    dry = FisPhysics.estimate_composite_properties({"water": 100}, cooking_duration=600, cooking_method="BOILING", amb_humidity=0.1) 
    humid = FisPhysics.estimate_composite_properties({"water": 100}, cooking_duration=600, cooking_method="BOILING", amb_humidity=0.9) 
    print(f"   Evap Impact (10% Humid): {dry['ambience_evap_impact']}x")
    print(f"   Evap Impact (90% Humid): {humid['ambience_evap_impact']}x")
    assert dry['ambience_evap_impact'] > humid['ambience_evap_impact']

    long_cook = FisPhysics.calculate_thermal_inertia(100, 100, 600) 
    short_cook = FisPhysics.calculate_thermal_inertia(100, 100, 60)  
    print(f"   Core Temp (10m): {long_cook['core_temp_estimate']}C")
    print(f"   Core Temp (1m): {short_cook['core_temp_estimate']}C")
    assert long_cook['core_temp_estimate'] > short_cook['core_temp_estimate']

if __name__ == "__main__":
    try:
        test_evaporation_and_concentration()
        test_arrhenius_kinetics()
        test_thermal_dynamics()
        test_ambience_and_inertia()
        print("\n✅ ALL AMBIENCE & INERTIA TESTS PASSED.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
