from typing import List, Dict, Any, Optional

class ContextService:
    """
    [The Concierge Service]
    Adjusts recipe scores based on External Context (Weather, Bio-Data).
    """
    
    # 🌧️ Weather Boosters
    WEATHER_BOOSTS = {
        "RAINY": ["pancake", "fry", "soup", "stew", "noodle"],
        "HOT": ["cold", "salad", "ice", "cool"],
        "COLD": ["soup", "stew", "warm", "hot pot"],
    }

    # ❤️ Bio Boosters
    BIO_BOOSTS = {
        "STRESSED": ["spicy", "sweet", "capsaicin", "sugar"],
        "TIRED": ["protein", "meat", "vitamin"],
        "DIET": ["salad", "chicken breast", "low carb", "vegetable"],
    }

    @classmethod
    def calculate_context_score(cls, recipe_name: str, ingredients: List[str], context: Dict[str, str]) -> float:
        """
        Returns a multiplier (e.g., 1.2 for +20% boost).
        Base is 1.0.
        """
        multiplier = 1.0
        name_lower = recipe_name.lower()
        ing_str = " ".join(ingredients).lower()
        
        # 1. Weather Logic
        weather = context.get("weather", "").upper()
        if weather in cls.WEATHER_BOOSTS:
            targets = cls.WEATHER_BOOSTS[weather]
            if any(t in name_lower for t in targets) or any(t in ing_str for t in targets):
                multiplier += 0.2 # +20% Boost
        
        # 2. Bio/Mood Logic
        mood = context.get("mood", "").upper()
        if mood in cls.BIO_BOOSTS:
            targets = cls.BIO_BOOSTS[mood]
             # For mock logic, we check name/ingredients. 
             # In real logic, we check ChemicalVector (e.g., Capsaicin > 0.5)
            if any(t in name_lower for t in targets):
                 multiplier += 0.15 # +15% Boost

        return multiplier
