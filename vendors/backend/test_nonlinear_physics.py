from app.core.fis_physics import FisPhysics
import json

def test_nonlinear():
    print("⚛️ Testing Nonlinear Physics Engine...\n")
    
    # Test 1: Logarithmic pH Mixing
    # Mix Honey (pH 3.9) and Milk (pH 6.7) - 50:50
    # Average pH is NOT (3.9+6.7)/2 = 5.3.
    # It should be closer to the acidic side because it's logarithmic.
    ingredients = {"honey": 100.0, "milk": 100.0}
    result = FisPhysics.estimate_composite_properties(ingredients)
    print(f"[pH Mix] Honey(3.9) + Milk(6.7) 1:1")
    print(f" -> Result pH: {result['composite_ph']} (Linear avg would be 5.3)")
    
    # Test 2: Nonlinear Viscosity
    # Mix Water (1cp) and Honey (10,000cp) - 50:50
    # Linear average would be 5000cp. Log mixing should be lower (~100cp).
    ingredients_visc = {"water": 100.0, "honey": 100.0}
    result_visc = FisPhysics.estimate_composite_properties(ingredients_visc)
    print(f"\n[Viscosity Mix] Water(1cp) + Honey(10,000cp) 1:1")
    print(f" -> Result Viscosity: {result_visc['composite_viscosity_cp']}cp (Linear avg would be 5000cp)")

    # Test 3: Reaction Probability (Sigmoid)
    # Maillard at threshold (154C) should be 0.5 (50%)
    # Maillard at 160C should be near 1.0 (100%)
    prob_mid = FisPhysics.calculate_reaction_probability(154.0, 154.0)
    prob_high = FisPhysics.calculate_reaction_probability(160.0, 154.0)
    prob_low = FisPhysics.calculate_reaction_probability(150.0, 154.0)
    print(f"\n[Reaction Prob] Maillard (Threshold 154°C)")
    print(f" -> 150°C: {prob_low*100}%")
    print(f" -> 154°C: {prob_mid*100}%")
    print(f" -> 160°C: {prob_high*100}%")

if __name__ == "__main__":
    test_nonlinear()
