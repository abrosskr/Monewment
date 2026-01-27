import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load env to get API Key
load_dotenv()

class LLMClassifier:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash') # Recommended model for production
        
    def classify(self, recipe_name: str, ingredients: list):
        """
        Input: 
            recipe_name: "목살 김치찜"
            ingredients: ["돼지고기 목살", "묵은지", "양파", ...]
            
        Output (JSON):
            {
                "food_type_name": "Jjim", 
                "base_material": "Broth (Minimal)",
                "default_method": "Braise/Steam", 
                "protein_modifier": "Pork (Neck)",
                "primary_modifier": "Kimchi",
                "reasoning": "Standard Jjim structure with Pork and Kimchi."
            }
        """
        
        prompt = f"""
        You are an expert Food Ontologist for the BIPS V3 System.
        Your goal is to analyze a recipe and deconstruct it into its structural DNA (Schema V3).
        
        ### The V3 Schema Logic
        1. **FoodType (The Noun)**: The immutable template. Definitions:
           - **Burger**: Base=Bread, Method=Assemble
           - **Jjigae**: Base=Broth, Method=Boil (Soup-like)
           - **Jjim**: Base=Sauce/Broth(Minimal), Method=Braise/Steam (Thick sauce)
           - **RiceBowl**: Base=Rice, Method=Top/Mix (e.g., Bibimbap, Deopbap)
           - **NoodleSoup**: Base=Noodle+Broth, Method=Boil
           - **Gui**: Base=Raw Ingredient, Method=Grill/Roast
        
        2. **StandardRecipe (The Adjective)**: The variable instance.
           - **Protein Modifier**: The main protein source (e.g., Pork, Beef, Seafood, Tofu).
           - **Primary Modifier**: Another Defining ingredient (e.g., Kimchi in Kimchi Jjigae).

        ### Input Data
        - **Menu Name**: {recipe_name}
        - **Ingredients**: {", ".join([i['item'] for i in ingredients])}

        ### Task
        Analyze the input and output a JSON object with the following keys:
        - `food_type_name`: Best fitting global category (English, Capitalized).
        - `base_material`: The foundation (e.g., Rice, Bread, Broth, Noodle).
        - `default_method`: The cooking technique.
        - `protein_modifier`: Extracted Protein (English). If none, "None".
        - `primary_modifier`: Key flavor/ingredient modifier (English).
        - `reasoning`: Brief explanation of why you classified it this way.

        Return ONLY the JSON. No markdown formatting.
        """
        
        import time
        import random
        
        max_retries = 3
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                # Cleanup markdown if present
                if text.startswith("```json"):
                    text = text[7:-3]
                return json.loads(text)
            except Exception as e:
                print(f"LLM Error (Attempt {attempt+1}/{max_retries}): {e}")
                if "429" in str(e) or "Quota" in str(e) or "ResourceExhausted" in str(e):
                    sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"  ⏳ Waiting {sleep_time:.1f}s before retry...")
                    time.sleep(sleep_time)
                else:
                    break # Don't retry on other errors
        
        return None

