from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel
from app.models.matter import IngredientModel, FlavorProfile, PhysicalProperties, ReactionPotential

class TasteDNA:
    """
    [The Engine Core: Taste DNA]
    Pure logic module for Taste Vectorization and Classification.
    Uses 'Matter' (IngredientModel) for high-fidelity physics.
    """

    # ⚓️ Culinary Anchors (Identity vs. Support)
    # SOUL: Must match the dish name prefix (e.g., 'Kimchi' in 'Kimchi Fried Rice')
    # SUPPORT: Aromatics that vary by preference but don't define the name.
    CULINARY_ANCHORS = {
        "볶음밥": {
            "aliases": ["Fried Rice", "Bokkeumbap"],
            "soul_required": True,
            "structure": ["참기름", "들기름", "식용유", "oil", "butter"],
            "optional_aromatics": ["마늘", "파", "양파", "생강", "garlic", "onion", "scallion", "ginger"]
        },
        "찌개": {
            "aliases": ["Stew", "Jjigae"],
            "soul_required": True,
            "structure": ["된장", "고추장", "김치", "doenjang", "gochujang", "kimchi"],
            "optional_aromatics": ["마늘", "파", "고추", "garlic", "chili", "pepper"]
        },
        "비빔밥": {
            "aliases": ["Bibimbap"],
            "soul_required": True,
            "structure": ["고추장", "참기름", "gochujang", "sesame oil"],
            "optional_aromatics": ["계란", "egg", "깨", "sesame seeds"]
        },
        "국/탕": {
            "aliases": ["Soup", "Guk", "Tang", "Broth"],
            "soul_required": False, # relaxed
            "structure": ["물", "water", "broth", "stock", "육수"],
            "optional_aromatics": ["파", "마늘", "무", "radish", "onion"]
        },
        "볶음/구이": {
             "aliases": ["Stir-fry", "Roast", "Bokkeum", "Gui", "Grilled"],
             "soul_required": False,
             "structure": ["oil", "식용유", "간장", "soy sauce", "gochujang"],
             "optional_aromatics": ["마늘", "파", "깨"]
        },
        "면요리": {
            "aliases": ["Noodle", "Pasta", "Spaghetti", "Ramen", "Udon", "Guksu"],
            "soul_required": False,
            "structure": ["면", "noodle", "pasta", "spaghetti", "water", "oil"],
            "optional_aromatics": ["양파", "onion", "garlic"]
        },
        "커리": {
            "aliases": ["Curry", "Kare"],
            "soul_required": True,
            "structure": ["카레", "curry", "turmeric"],
            "optional_aromatics": ["potato", "onion", "carrot"]
        },
        "샐러드": {
            "aliases": ["Salad", "Muchim"],
            "soul_required": False,
            "structure": ["oil", "vinegar", "lemon", "mayo", "ssamjang"],
            "optional_aromatics": ["vegetable", "lettuce"]
        }
    }

    # 🔭 Cultural Markers
    CULTURE_MARKERS = {
        "KOREAN": ["kimchi", "gochujang", "doenjang", "soy sauce", "garlic", "sesame"],
        "ITALIAN": ["tomato", "basil", "olive oil", "pasta", "cheese", "oregano"],
        "JAPANESE": ["miso", "dashi", "mirin", "sake", "soy sauce"],
        "WESTERN": ["butter", "cream", "thyme", "rosemary", "steak"],
    }

    # 🧪 Flavor Vector Database (Legacy Support for AutoLabeler)
    INGREDIENT_VECTORS: Dict[str, Dict[str, float]] = {
        "salt": {"salt": 1.0},
        "sugar": {"sugar": 1.0},
        "vinegar": {"acid": 0.9},
        "lemon": {"acid": 0.8},
        "lime": {"acid": 0.8},
        "oil": {"lipid": 1.0},
        "butter": {"lipid": 0.9, "sugar": 0.1},
        "cream": {"lipid": 0.8, "sugar": 0.1},
        "cheese": {"lipid": 0.6, "glutamate": 0.4, "salt": 0.3},
        "bacon": {"lipid": 0.7, "salt": 0.5, "glutamate": 0.4},
        "pork": {"lipid": 0.6, "glutamate": 0.3},
        "beef": {"lipid": 0.5, "glutamate": 0.5},
        "chicken": {"glutamate": 0.4, "lipid": 0.3},
        "fish": {"glutamate": 0.6, "lipid": 0.2},
        "soy sauce": {"salt": 0.6, "glutamate": 0.7},
        "miso": {"salt": 0.5, "glutamate": 0.6},
        "doenjang": {"salt": 0.5, "glutamate": 0.7},
        "gochujang": {"spiciness": 0.7, "sugar": 0.3, "glutamate": 0.5},
        "kimchi": {"acid": 0.4, "spiciness": 0.5, "glutamate": 0.4},
        "tomato": {"acid": 0.3, "glutamate": 0.4, "sugar": 0.3},
        "onion": {"sugar": 0.4, "glutamate": 0.2},
        "garlic": {"spiciness": 0.2, "glutamate": 0.3},
        "chili": {"capsaicin": 0.9},
        "pepper": {"capsaicin": 0.6},
        "msg": {"glutamate": 1.0},
        "mushroom": {"glutamate": 0.5},
        "anchovy": {"glutamate": 0.8, "salt": 0.4},
        "kelp": {"glutamate": 0.6}
    }

    # 🧪 Matter Database (v2.0 - High Fidelity)
    # This serves as the internal cache until we connect to a real DB.
    MATTER_DB: Dict[str, IngredientModel] = {
        # Proteins
        "돼지": IngredientModel(
            id="pork_std", name="Pork (Generic)", 
            flavor=FlavorProfile(lipid=0.8, umami=0.6),
            physical=PhysicalProperties(water_activity=0.9, fat_content_percent=20),
            reaction=ReactionPotential(maillard_score=0.9)
        ),
        "소": IngredientModel(
            id="beef_std", name="Beef (Generic)", 
            flavor=FlavorProfile(lipid=0.6, umami=0.8),
            physical=PhysicalProperties(water_activity=0.85, fat_content_percent=15, protein_denaturation_temp_c=55),
            reaction=ReactionPotential(maillard_score=0.95)
        ),
        
        # Veggies
        "김치": IngredientModel(
            id="kimchi_std", name="Kimchi", 
            flavor=FlavorProfile(salt=0.5, acid=0.6, spiciness=0.7, umami=0.4),
            physical=PhysicalProperties(water_activity=0.95, viscosity_cp=1000), 
            reaction=ReactionPotential(fermentation_affinity=0.0) # Already fermented
        ),
        "마늘": IngredientModel(
            id="garlic_std", name="Garlic", 
            flavor=FlavorProfile(spiciness=0.2, umami=0.3, aroma=0.9),
            physical=PhysicalProperties(water_activity=0.7),
            reaction=ReactionPotential(caramelization_score=0.7)
        ),
        "양파": IngredientModel(
            id="onion_std", name="Onion", 
            flavor=FlavorProfile(sugar=0.3, umami=0.1, aroma=0.6),
            physical=PhysicalProperties(water_activity=0.9),
            reaction=ReactionPotential(caramelization_score=0.95, maillard_score=0.6)
        ),
        
        # Seasonings
        "설탕": IngredientModel(
            id="sugar_white", name="White Sugar", 
            flavor=FlavorProfile(sugar=1.0),
            physical=PhysicalProperties(water_activity=0.2, melting_point_c=186),
            reaction=ReactionPotential(caramelization_score=1.0)
        ),
        "소금": IngredientModel(
            id="salt_std", name="Salt", 
            flavor=FlavorProfile(salt=1.0),
            physical=PhysicalProperties(water_activity=0.1),
            reaction=ReactionPotential()
        ),
        "물": IngredientModel(
            id="water_h2o", name="Water", 
            flavor=FlavorProfile(), 
            physical=PhysicalProperties(water_activity=1.0, boiling_point_c=100, viscosity_cp=1.0),
            reaction=ReactionPotential()
        )
    }

    @classmethod
    def classify_role(cls, name: str, ratio: float) -> str:
        """
        Determines if ingredient is Main or Seasoning based on mass ratio.
        """
        name_lower = name.lower()
        
        # Aromatic/Seasoning Exclusion (Should NOT be Main Ingredients)
        aromatics = ["마늘", "생강", "파", "고추", "sauce", "salt", "spice", "powder", "oil", "garlic", "ginger"]
        if any(a in name_lower for a in aromatics):
            return "SEASONING"

        # Protein Rule
        if any(p in name_lower for p in ["meat", "pork", "beef", "chicken", "fish", "돼지", "소", "닭"]):
            return "MAIN_INGREDIENT"

        # Ratio Rule
        if ratio > 0.20:
            return "MAIN_INGREDIENT"
        else:
            return "SUB_INGREDIENT"

    @classmethod
    def predict_culture(cls, ingredient_names: List[str]) -> str:
        """
        Scoring system for culture prediction.
        """
        scores = {k: 0 for k in cls.CULTURE_MARKERS.keys()}
        
        for ing in ingredient_names:
            ing = ing.lower()
            for culture, markers in cls.CULTURE_MARKERS.items():
                if any(m in ing for m in markers):
                    scores[culture] += 1
        
        best_match = max(scores, key=scores.get)
        return best_match if scores[best_match] > 0 else "GLOBAL"

    @classmethod
    def get_matter(cls, name: str) -> IngredientModel:
        """
        Retrieves the full physical model of an ingredient.
        """
        # Simple lookup for now
        return cls.MATTER_DB.get(name.lower(), cls.MATTER_DB["물"]) # Default to Water if unknown

    @classmethod
    def get_chemical_vector(cls, name: str) -> FlavorProfile:
        """
        Backward compatibility wrapper.
        """
        matter = cls.get_matter(name)
        return matter.flavor
