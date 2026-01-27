# app/core/prompts.py

def get_classifier_prompt(recipe_name: str, ingredient_text: str, examples_context: str = "") -> str:
    """
    Generates the prompt for the Food Ontology Classifier (V3 Schema).
    """
    return f"""
        You are an expert Food Ontologist for the BIPS V3 System.
        Analyze the recipe based on the V3 Schema.
        
        {examples_context}

        ### The V3 Schema Logic (EXTREMELY IMPORTANT)
        1. FoodType (The Noun): Immutable template.
           - Jjigae: Base=Broth, Method=Boil
           - Muchim: Base=Raw/Blanched, Method=Muchim/Season (Mixed with sauce)
           - Jjim: Base=Sauce/Broth(Minimal), Method=Braise/Steam
           - RiceBowl: Base=Rice, Method=Top/Mix
           - Gui: Base=Raw Ingredient, Method=Grill/Roast
           ... (Generalize from examples)
        
        2. Standardized Naming Convention:
           - Use strictly ENGLISH for protein_modifier and primary_modifier.
           - Pork, Beef, Chicken, Shrimp, Scallop, etc.
           - If it is fermented kimchi, use "Kimchi (Fermented)".
           
        3. Noise Filtering:
           - IGNORE kitchenware or tools (Bowl, Pot, Knife, etc.) if they appear in ingredients.

        ### Input Data
        - Menu Name: {recipe_name}
        - Ingredients: {ingredient_text}

        ### Task
        Return a JSON object with keys:
        - food_type_name (Jjigae, Guk, Bokkeum, Gui, Muchim, etc.)
        - base_material (Broth, Rice, Noodle, Raw, Sauce, etc.)
        - default_method (Boil, Stir-fry, Grill, Steam, Muchim, etc.)
        - protein_modifier (Primary protein in English)
        - protein_part (Specific cut/part in English or "Whole")
        - primary_modifier (Primary flavor/veg in English)
        - reasoning (Short explanation in English)

        Respond ONLY with the JSON object.
    """
