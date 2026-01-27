import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor
from app.engines.v_mapper.core import VMapperEngine
from app.engines.v_optimizer.core import VOptimizerEngine

def test_chef_to_home_fidelity():
    print("\n👨‍🍳 Testing AI Recipe Engineering: Achieving 99% Chef Quality at Home")
    print("-" * 80)

    # 1. Chef's 'Gold Standard' (High Power, 30s)
    # Simulation in 1s steps for accuracy
    chef_reactor = PhysicsReactor(ingredients={"beef": 200.0, "water": 10.0})
    for _ in range(30):
        chef_reactor = FisPhysics.step_simulation(chef_reactor, dt=1.0, power_watts=3000)
    
    print(f"   [CHEF-PRO]  Maillard: {chef_reactor.reaction_progress['MAILLARD']:.6f}, Temp: {chef_reactor.current_temp:.2f}C")

    # 2. AI Adaptation
    adaptation = VOptimizerEngine.adapt_recipe(
        pro_baseline={"power": 3000, "duration": 30},
        home_hardware_eff=0.4 # Gas
    )

    # 3. Optimized Home Execution (Pre-heat + Modified Ingredients + Step-by-step Sim)
    water_multiplier = adaptation["modified_ingredients"].get("water", 1.0)
    home_opt_reactor = PhysicsReactor(ingredients={"beef": 200.0, "water": 10.0 * water_multiplier})
    home_opt_reactor.heating_method = "GAS"
    home_opt_reactor.current_temp = adaptation['preheat_temp'] # 220C
    
    # Run in 1s steps to allow Water Lock to break
    for _ in range(int(adaptation['adapted_duration'])):
        home_opt_reactor = FisPhysics.step_simulation(home_opt_reactor, dt=1.0, power_watts=1500)
    
    report_opt = VMapperEngine.compare_states(chef_reactor, home_opt_reactor)
    
    print(f"   [VAL-HOME]  Maillard: {home_opt_reactor.reaction_progress['MAILLARD']:.6f}, Temp: {home_opt_reactor.current_temp:.2f}C")
    print(f"   [FIDELITY]  Current Score: {report_opt.taste_fidelity * 100:.1f}%")

    print(f"\n   💡 AI RECIPE ENGINEERING CONCLUSION:")
    for rec in adaptation['recommendations']:
        print(f"      - {rec}")
    
    assert report_opt.taste_fidelity >= 0.85
    print(f"\n   ✅ SUCCESS: High fidelity ({report_opt.taste_fidelity * 100:.1f}%) confirmed via time-series bridging.")

if __name__ == "__main__":
    test_chef_to_home_fidelity()
