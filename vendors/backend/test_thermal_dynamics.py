from app.services.normalizer_service import RecipeNormalizer

def test_thermodynamics():
    print("🔥 Testing Thermal Dynamics (Duration Prediction)...")
    
    # CASE A: Boiling water (1 ingredient)
    cmd_a = RecipeNormalizer.convert_to_fis_command("Boil the water", 1, ["water"])
    print(f"\n[Case A] 'Boil the water'")
    print(f" -> Duration: {cmd_a.params['duration']}s")
    
    # CASE B: Boiling massive soup (4 ingredients)
    # 4 ingredients = 1000g (in my simplified mock logic)
    cmd_b = RecipeNormalizer.convert_to_fis_command("Boil everything", 2, ["pork", "kimchi", "tofu", "water"])
    print(f"\n[Case B] 'Boil everything' (4 ingredients)")
    print(f" -> Duration: {cmd_b.params['duration']}s")
    
    # Verify B > A
    if cmd_b.params['duration'] > cmd_a.params['duration']:
        print("\n✅ Success! Duration increases with mass.")
    else:
        print("\n❌ Error: Duration did not scale correctly.")

if __name__ == "__main__":
    test_thermodynamics()
