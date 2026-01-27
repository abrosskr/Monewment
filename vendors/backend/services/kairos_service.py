# app/services/kairos_service.py
from typing import Dict, Any, List
import random
from app.services.graph_service import GraphService, RelationType

class KairosService:
    """
    [Smart Data Engine]
    Integrates Weather, Economics (KAMIS), and Graph Context to provide
    'Profit-Optimized Recommendations'.
    """

    # 🌦️ Mock Weather API
    @staticmethod
    def get_weather_forecast(location: str) -> Dict[str, Any]:
        """
        Simulates calling OpenWeatherMap or KMA.
        For demo, we force 'Rain' if location is 'Seoul'.
        """
        if location.lower() == "seoul":
            return {"condition": "Rain", "humidity": 90, "temp": 22}
        return {"condition": "Sunny", "humidity": 40, "temp": 28}

    # 💰 Mock KAMIS API (Agro-Food Info)
    @staticmethod
    def get_market_price(ingredient: str) -> Dict[str, Any]:
        """
        Simulates calling KAMIS API.
        Returns 'current_price' and 'trend' (vs avg year).
        """
        # Scenario: Green Onion is expensive, Chives are cheap.
        prices = {
            "Green_Onion": {"price": 15000, "trend": "Expensive (+30%)"},
            "Chives":      {"price": 4000,  "trend": "Cheap (-40%)"},
            "Seafood_Mix": {"price": 8000,  "trend": "Normal"},
            "Flour":       {"price": 2000,  "trend": "Stable"},
        }
        return prices.get(ingredient, {"price": 5000, "trend": "Normal"})

    @classmethod
    def analyze_opportunity(cls, location: str) -> Dict[str, Any]:
        """
        [The Kairos Logic]
        1. Check Weather
        2. If Rain -> Trigger 'Jeon Strategy'
        3. Analyze Cost (Green Onion vs Chives)
        4. Recommend Profit-Maximized Menu
        """
        weather = cls.get_weather_forecast(location)
        
        # 1. Trigger: Rain
        if weather['condition'] == "Rain":
            trigger_msg = "☔ Rain detected! High probability of craving 'Savory/Oily' foods."
            
            # 2. Target Menu: Jeon (Pancake)
            # Find ingredients for 'Seafood_Pajeon' from Graph
            # In a real app, we'd query Graph for dishes tagged 'Rainy_Day'
            target_dish = "Seafood_Pajeon"
            graph_context = GraphService.search_context(target_dish)
            
            # Ingredients: ['Green_Onion', 'Seafood_Mix', 'Flour_Batter'] (from mocked graph lines 53-55)
            # Note: search_context returns 'goes_well_with', etc. 
            # We need 'Contains' edges. GraphService.search_context currently does successors.
            # Let's assume we find "Green_Onion" is a key ingredient.
            
            # 3. Cost Analysis (Substitution)
            primary_ing = "Green_Onion"
            price_info = cls.get_market_price(primary_ing)
            
            recommendation = {
                "trigger": trigger_msg,
                "weather": weather,
                "strategy": "Standard",
                "menu": target_dish,
                "cost_analysis": f"{primary_ing} is {price_info['trend']}"
            }
            
            # 4. Profit Optimization logic (Swap Expensive -> Cheap)
            if "Expensive" in price_info['trend']:
                # Find substitute from Graph
                substitutes = GraphService.search_context(primary_ing).get("context", {}).get("can_be_replaced_by", [])
                
                best_sub = None
                best_margin = 0
                
                for sub in substitutes: # e.g., ['Chives']
                    sub_price = cls.get_market_price(sub)
                    if "Cheap" in sub_price['trend']:
                        best_sub = sub
                
                if best_sub:
                    recommendation["strategy"] = "Profit_Optimized"
                    recommendation["alert"] = f"🚨 {primary_ing} is too expensive! Use {best_sub} instead."
                    recommendation["modified_menu"] = target_dish.replace("Pajeon", f"{best_sub}_Jeon") # Mock naming
                    recommendation["margin_impact"] = "+15% Projected Margin"
                    
                    # 5. Cross-Sell (Pairing)
                    pairings = GraphService.search_context(target_dish).get("context", {}).get("goes_well_with", [])
                    recommendation["upsell_opportunity"] = pairings # e.g., ['Makgeolli']
            
            return recommendation

        return {"status": "No special events", "weather": weather}
