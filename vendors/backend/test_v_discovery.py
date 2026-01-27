import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.v_discovery.core import VDiscoveryEngine, OptimizationGoal
from app.engines.v_vpt.core.simulator import VPTScenario, TimelineEvent

async def test_v_discovery():
    print("\n🧠 Testing V-Discovery: Generative Physics Recipe Optimization")
    print("-" * 85)

    # 1. Base Scenario: Cooking beef without a strategy
    base_scenario = VPTScenario(
        name="Discovery Base: Beef Stew",
        hardware_id="induction_pro",
        initial_ingredients={"beef": 500.0, "water": 10.0},
        timeline=[], # Start empty to let Discovery build it
        max_duration_s=600
    )

    # 2. Setup Optimizer
    engine = VDiscoveryEngine(base_scenario)
    goal = OptimizationGoal(target_maillard=0.1, priority="TASTE")

    # 3. Discover!
    print("   Action: Running 50 virtual simulations to find the 'Ultimate Rhythm'...")
    discovery_result = await engine.discover_optimal_path(goal, iterations=50)

    print(f"\n   ✅ Discovery Complete!")
    print(f"      - Best Taste Score Found: {discovery_result['best_score']:.2f}")
    print(f"      - Final Maillard: {discovery_result['estimated_metrics']['maillard']*100:.2f}%")
    print(f"      - Final Moisture: {discovery_result['estimated_metrics']['moisture']*100:.2f}%")
    
    print("\n   [Discovered Optimal Timeline]")
    for event in discovery_result['optimal_timeline']:
        val = event['value']
        print(f"      T+{event['time_s']:05.1f}s | {event['action']:15} | {val}")

    # Validation: Score should be positive
    assert discovery_result['best_score'] > 0
    print("\n   ✅ SUCCESS: V-Discovery invented a new cooking sequence based on pure physics.")

if __name__ == "__main__":
    asyncio.run(test_v_discovery())
