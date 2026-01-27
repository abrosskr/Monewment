import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor

def test_steak_searing_transition():
    print("\n🥩 Testing Steak Searing: Surface Water Depletion to High Heat...")
    
    # Simulate a steak with a bit of surface moisture (5g water)
    reactor = PhysicsReactor(
        ingredients={"beef": 200.0, "water": 5.0},
        current_temp=80.0,
        cooking_method="STIR_FRY"
    )
    
    dt = 1.0 # 1s precision
    
    print(f"   {'Time (s)':<10} | {'Temp (C)':<10} | {'Water (g)':<10} | {'Mode':<15}")
    print("-" * 55)
    
    for s in range(1, 101):
        reactor = FisPhysics.step_simulation(reactor, dt, power_watts=2000)
        
        mode = "Boiling Lock" if reactor.current_temp <= 100.1 and reactor.ingredients.get("water", 0) > 0.1 else "Searing (Surge)"
        
        if s % 10 == 0:
            print(f"   {s:<10} | {reactor.current_temp:<10.2f} | {reactor.ingredients.get('water', 0):<10.2f} | {mode}")

    assert reactor.current_temp > 150.0
    assert reactor.ingredients.get("water", 0) < 1.0
    print("\n   ✅ Searing Transition Confirmed: Temp surged after surface water evaporated.")

def test_deep_frying_speed():
    print("\n🍟 Testing Deep Frying: Low Specific Heat of Oil vs Water...")
    
    # 500g Oil vs 500g Water
    oil_reactor = PhysicsReactor(ingredients={"olive_oil": 500.0}, current_temp=25.0)
    water_reactor = PhysicsReactor(ingredients={"water": 500.0}, current_temp=25.0)
    
    # Sim for 60s
    for _ in range(60):
        oil_reactor = FisPhysics.step_simulation(oil_reactor, 1.0, power_watts=1500)
        water_reactor = FisPhysics.step_simulation(water_reactor, 1.0, power_watts=1500)
        
    print(f"   60s Heating Results (1500W):")
    print(f"   - Oil Temp: {oil_reactor.current_temp:.2f}C")
    print(f"   - Water Temp: {water_reactor.current_temp:.2f}C")
    
    ratio = (oil_reactor.current_temp - 25) / (water_reactor.current_temp - 25)
    print(f"   - Heating Speed Ratio: {ratio:.2f}x (Oil should be ~2x faster)")
    
    assert oil_reactor.current_temp > water_reactor.current_temp
    print("\n   ✅ Deep Frying Physics Confirmed: Oil heats significantly faster.")

if __name__ == "__main__":
    test_steak_searing_transition()
    test_deep_frying_speed()
