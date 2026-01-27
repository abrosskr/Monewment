import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.fis_physics import FisPhysics, PhysicsReactor
from app.engines.v_surface.core import SurfaceState

def test_bad_pan_adhesion_penalty():
    print("\n🍳 Testing Hell Mode: Sticking Pan (Damaged Coating & No Oil)...")
    
    # 1. Good Pan (New Coating, Good Oil Film)
    good_reactor = PhysicsReactor(
        ingredients={"beef": 200.0},
        current_temp=154.0,
        surface=SurfaceState(coating_integrity=1.0, oil_film_density=1.0)
    )
    
    # 2. Bad Pan (Destroyed Coating, Dry)
    bad_reactor = PhysicsReactor(
        ingredients={"beef": 200.0},
        current_temp=154.0,
        surface=SurfaceState(coating_integrity=0.2, oil_film_density=0.1)
    )
    
    dt = 10.0
    good_reactor = FisPhysics.step_simulation(good_reactor, dt)
    bad_reactor = FisPhysics.step_simulation(bad_reactor, dt)
    
    print(f"   Good Pan Maillard Progress: {good_reactor.reaction_progress['MAILLARD']:.6f}")
    print(f"   Bad Pan Maillard Progress: {bad_reactor.reaction_progress['MAILLARD']:.6f}")
    
    # Bad pan should have lower progress because of the quality penalty/adhesion risk
    assert bad_reactor.reaction_progress['MAILLARD'] < good_reactor.reaction_progress['MAILLARD']
    print(f"   ✅ Adhesion Penalty Verified: Bad pan quality reduced by ~{(1 - bad_reactor.reaction_progress['MAILLARD']/good_reactor.reaction_progress['MAILLARD'])*100:.1f}%")

if __name__ == "__main__":
    test_bad_pan_adhesion_penalty()
