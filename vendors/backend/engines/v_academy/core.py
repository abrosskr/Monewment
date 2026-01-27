from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TechniqueCategory(str, Enum):
    THERMAL = "Thermal_Control"         # Pre-heating, Pulsing, Temperature steps
    HYDRATION = "Moisture_Management"   # Staged addition, reduction, deglazing
    SURFACE = "Surface_Tribology"       # Seasoning, scraping, vibrating
    CHEMICAL = "Reaction_Kinetics"      # Buffering pH, enzyme activation (rest)

class PhysicalPrimitive(BaseModel):
    """
    [The Atomic Unit of Cooking]
    A technique decoupled from specific recipes.
    Example: 'Staged Addition' can apply to Stew, Curry, or Sauce.
    """
    id: str
    category: TechniqueCategory
    name: str
    logic_pattern: str   # The "Why" (Physics)
    action_sequence: List[Dict[str, Any]] # The "How" (Events)
    context_tags: List[str] # ["Low_Power", "High_Protein", "Water_Base"]

class VAcademyEngine:
    """
    [V-Academy: The Universal Translator]
    1. Cross-Language Normalization: Converts global chef tips into Physics Primitives.
    2. Atomic Storage: Techniques are stored as industry-agnostic physical patterns.
    3. Cross-Dish Application: Decouples 'How to cook' from 'What to cook'.
    """
    
    # Universal Library of Physical Primitives
    PRIMITIVE_LIBRARY: Dict[str, PhysicalPrimitive] = {
        # --- HYDRATION (Moisture Management) ---
        "TECH_HYD_001": PhysicalPrimitive(id="TECH_HYD_001", category=TechniqueCategory.HYDRATION, name="Incremental Hydration", logic_pattern="Avoids temperature shock; maintains surface enthalpy.", action_sequence=[{"action": "SPLIT_INPUT"}], context_tags=["Water_Base", "Sauce", "Risotto"]),
        "TECH_HYD_002": PhysicalPrimitive(id="TECH_HYD_002", category=TechniqueCategory.HYDRATION, name="Deglazing", logic_pattern="Solubilizes fond (Maillard byproducts) into liquid phase.", action_sequence=[{"action": "ADD_LIQUID", "target": "HOT_SURFACE"}], context_tags=["Pan_Sauce", "Flavor_Recovery"]),
        "TECH_HYD_003": PhysicalPrimitive(id="TECH_HYD_003", category=TechniqueCategory.HYDRATION, name="Reduction", logic_pattern="Evaporates solvent to increase solute concentration (viscosity/flavor).", action_sequence=[{"action": "SIMMER", "lid": False}], context_tags=["Sauce", "Intensification"]),
        "TECH_HYD_004": PhysicalPrimitive(id="TECH_HYD_004", category=TechniqueCategory.HYDRATION, name="Osmotic Extraction", logic_pattern="Uses salt/sugar to draw cellular moisture via osmosis.", action_sequence=[{"action": "SALT_SURFACE", "wait": True}], context_tags=["Pre_Cooking", "Texture_Mod"]),
        
        # --- THERMAL (Heat Management) ---
        "TECH_THR_001": PhysicalPrimitive(id="TECH_THR_001", category=TechniqueCategory.THERMAL, name="Residual Heat Resting", logic_pattern="Equalizes internal pressure/temp gradients post-heating.", action_sequence=[{"action": "POWER_OFF", "wait": True}], context_tags=["Protein", "Steak", "Rice"]),
        "TECH_THR_002": PhysicalPrimitive(id="TECH_THR_002", category=TechniqueCategory.THERMAL, name="Leidenfrost Effect Searing", logic_pattern="High heat creates vapor barrier preventing sticking/steaming.", action_sequence=[{"action": "HEAT_PAN", "temp": "HIGH"}], context_tags=["Stainless_Steel", "Searing"]),
        "TECH_THR_003": PhysicalPrimitive(id="TECH_THR_003", category=TechniqueCategory.THERMAL, name="Carryover Cooking", logic_pattern="Internal conduction continues raising core temp after heat removal.", action_sequence=[{"action": "REMOVE_HEAT_EARLY"}], context_tags=["Precision", "Protein"]),
        "TECH_THR_004": PhysicalPrimitive(id="TECH_THR_004", category=TechniqueCategory.THERMAL, name="Blanching", logic_pattern="Deactivates enzymes rapidly then halts thermal momentum.", action_sequence=[{"action": "BOIL_SHORT"}, {"action": "ICE_BATH"}], context_tags=["Vegetable", "Color_Preservation"]),
        "TECH_THR_005": PhysicalPrimitive(id="TECH_THR_005", category=TechniqueCategory.THERMAL, name="Tempering", logic_pattern="Slowly equalizing temperatures to prevent coagulation shock.", action_sequence=[{"action": "MIX_HOT_INTO_COLD_SLOW"}], context_tags=["Eggs", "Dairy", "Chocolate"]),

        # --- SURFACE (Texture & Mechanical) ---
        "TECH_SUR_001": PhysicalPrimitive(id="TECH_SUR_001", category=TechniqueCategory.SURFACE, name="Maillard Reaction", logic_pattern="Reducing sugars + amino acids at >140°C create flavor compounds.", action_sequence=[{"action": "DRY_HEAT", "temp": ">140C"}], context_tags=["Browning", "Flavor_Dev"]),
        "TECH_SUR_002": PhysicalPrimitive(id="TECH_SUR_002", category=TechniqueCategory.SURFACE, name="Emulsification", logic_pattern="Dispersing hydrophobic liquid into hydrophilic via agitation.", action_sequence=[{"action": "WHISK_VIGOROUSLY", "add": "SLOW_OIL"}], context_tags=["Sauce", "Mayo", "Vinaigrette"]),
        "TECH_SUR_003": PhysicalPrimitive(id="TECH_SUR_003", category=TechniqueCategory.SURFACE, name="Aeration", logic_pattern="Trapping air bubbles in protein matrix for volume.", action_sequence=[{"action": "WHIP", "target": "PEAKS"}], context_tags=["Egg_Whites", "Cream", "Souffle"]),
        "TECH_SUR_004": PhysicalPrimitive(id="TECH_SUR_004", category=TechniqueCategory.SURFACE, name="Velvetting", logic_pattern="Alkaline/Starch coating protects protein fibers from seizing.", action_sequence=[{"action": "COAT_STARCH_OIL"}], context_tags=["Stir_Fry", "Tenderizing"]),
        
        # --- CHEMICAL (Reactions) ---
        "TECH_CHM_001": PhysicalPrimitive(id="TECH_CHM_001", category=TechniqueCategory.CHEMICAL, name="Acid Denaturation", logic_pattern="Low pH alters protein structure without heat.", action_sequence=[{"action": "SOAK_ACID"}], context_tags=["Ceviche", "Marinade"]),
        "TECH_CHM_002": PhysicalPrimitive(id="TECH_CHM_002", category=TechniqueCategory.CHEMICAL, name="Gelatinization", logic_pattern="Starch granules swell and burst absorbing water.", action_sequence=[{"action": "HEAT_STARCH_WATER"}], context_tags=["Thickening", "Roux", "Porridge"]),
        "TECH_CHM_003": PhysicalPrimitive(id="TECH_CHM_003", category=TechniqueCategory.CHEMICAL, name="Caramelization", logic_pattern="Oxidation of sugar at high temps (non-enzymatic browning).", action_sequence=[{"action": "HEAT_SUGAR"}], context_tags=["Onions", "Sugar", "Color"]),
    }

    # Cross-Language Semantic Bridge (Maps Native -> Physical Concept)
    LINGUISTIC_MAP = {
        "ko": {
            # Hydration
            "조금씩": "staged", "나눠서": "staged", "육즙": "hydration", "촉촉": "hydration",
            "졸여": "reduction", "자박하게": "reduction", "날려": "reduction", "수분": "moisture",
            # Thermal
            "뜸": "resting", "잔열": "resting", "식혀": "cooling", "달궈진": "preheated", "예열": "preheated",
            "데치": "blanching", "찬물에": "shocking", "불 끄고": "resid_heat",
            # Surface/Chem
            "노릇하게": "maillard", "바삭": "crisp", "태우듯이": "sear", "갈색": "brown", "마이야르": "maillard",
            "휘핑": "aeration", "거품": "aeration", "유화": "emulsification", "물과 기름": "emulsification",
            "재워": "osmosis", "밑간": "osmosis", "전분": "starch", "코팅": "velvet"
        },
        "en": {
            # Hydration
            "bit by bit": "staged", "slowly": "staged", "gradually": "staged", "deglaze": "deglazing",
            "scrape": "deglaze", "reduce": "reduction", "simmer down": "reduction", "thicken": "reduction",
            "draw out": "osmosis", "sweat": "osmosis",
            # Thermal
            "resting": "resting", "rest": "resting", "carryover": "carryover", "residual": "residual",
            "preheat": "preheated", "hot pan": "preheated", "smoking hot": "leidenfrost",
            "blanch": "blanching", "ice bath": "shocking", "temper": "tempering",
            # Surface/Chem
            "sear": "maillard", "brown": "maillard", "crust": "maillard", "golden": "maillard",
            "whisk": "emulsification", "emulsify": "emulsification", "drizzle": "emulsification",
            "whip": "aeration", "peaks": "aeration", "fold": "aeration",
            "marinate": "denaturation", "cure": "osmosis", "velveting": "velvetting"
        }
    }

    @classmethod
    def process_transcript(cls, transcript: str, language: str = "auto") -> List[PhysicalPrimitive]:
        """
        [The Distillation Algorithm]
        1. Language Normalization: Bridge native terms to Physical Concepts.
        2. Parameter Extraction: Regex hunt for numbers (Temp/Time).
        3. Category Filtering: Narrow down by tags.
        """
        extracted = []
        
        # 1. Broad Language Normalization (Simulated)
        detected_lang = "ko" if any(c in transcript for c in "가나다") else "en"
        semantics = cls.LINGUISTIC_MAP.get(detected_lang, {})
        
        normalized_content = transcript.lower()
        for native, concept in semantics.items():
            normalized_content = normalized_content.replace(native, concept)

        # 2. Physics Parameter Extraction (Hybrid: LLM + Regex Validation)
        # Architecture: LLM Hypothesizes -> Regex Validates -> Confidence System
        
        from app.services.gemini import gemini_service
        import json
        import re

        temp_c = None
        duration_s = None
        confidence = "LOW"
        source = "NONE"

        # A. LLM Hypothesis Generation
        prompt = f"""
        Extract cooking physics attributes from this text into JSON.
        Text: "{transcript}"
        
        Output Format:
        {{
            "temperature_c": float or null,
            "duration_sec": int or null,
            "action": string
        }}
        If implied (e.g. 'simmer' -> 95C), guess it.
        """
        
        try:
            llm_response = gemini_service.generate_content(prompt)
            print(f"DEBUG LLM RAW: {llm_response}") # DEBUG
            
            # Simple cleanup for JSON parsing
            clean_json = llm_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            hyp_temp = data.get("temperature_c")
            hyp_time = data.get("duration_sec")
            
            print(f"DEBUG EXTRACTED: Temp={hyp_temp}, Time={hyp_time}") # DEBUG
            
            # B. Traceability Check (Regex Validation)
            # Can we find these numbers in the source text?
            
            temp_valid = False
            time_valid = False
            
            if hyp_temp:
                # Check if the number (e.g. 200) appears in text
                if str(int(hyp_temp)) in transcript or str(float(hyp_temp)) in transcript:
                    temp_valid = True
            
            if hyp_time:
                # Check if number appears (complex due to unit conversion, simplified here)
                # If LLM says 600s (10m), we look for '10' or '600'
                if str(hyp_time) in transcript or str(hyp_time//60) in transcript:
                    time_valid = True
            
            # C. Confidence Assignment
            if temp_valid and time_valid:
                confidence = "HIGH"
                source = "HYBRID_VERIFIED"
            elif temp_valid or time_valid:
                confidence = "MEDIUM"
                source = "PARTIAL_VERIFIED"
            elif hyp_temp or hyp_time:
                confidence = "LOW" # LLM Hallucinated connection (e.g. "Simmer" -> 95C)
                source = "LLM_INFERRED"
            
            if hyp_temp: temp_c = hyp_temp
            if hyp_time: duration_s = hyp_time
                
        except Exception as e:
            print(f"Hybrid Inference Failed: {e}")
            # Fallback to pure Regex (implemented below as safety net?)
            # For Phase 5, we rely on Hybrid. if it fails, we get nothing.
            pass

        # 3. Match against Primitive Library
        for p_id, primitive in cls.PRIMITIVE_LIBRARY.items():
            # Keyword matching based on normalized semantic concepts
            
            # (A) Concept Match
            for concept in semantics.values():
                if concept in normalized_content:
                    is_match = False
                    
                    # Heuristic Mapping
                    if "staged" in concept and primitive.category == TechniqueCategory.HYDRATION: is_match = True
                    if "reduction" in concept and primitive.name == "Reduction": is_match = True
                    if "deglaze" in concept and primitive.name == "Deglazing": is_match = True
                    if "osmosis" in concept and primitive.name == "Osmotic Extraction": is_match = True
                    if "resting" in concept and primitive.name == "Residual Heat Resting": is_match = True
                    if "preheat" in concept and "preheated" in primitive.logic_pattern: is_match = True
                    if "leidenfrost" in concept and primitive.name == "Leidenfrost Effect Searing": is_match = True
                    if "blanch" in concept and primitive.name == "Blanching": is_match = True
                    if "temper" in concept and primitive.name == "Tempering": is_match = True
                    if "maillard" in concept and primitive.name == "Maillard Reaction": is_match = True
                    if "emulsification" in concept and primitive.name == "Emulsification": is_match = True
                    if "aeration" in concept and primitive.name == "Aeration": is_match = True
                    
                    if is_match and primitive not in extracted:
                        extracted.append(primitive)
            
            # (B) Direct Keyword Match
            if primitive.name.lower() in normalized_content:
                if primitive not in extracted:
                    extracted.append(primitive)
        
        # 4. Attach Extracted Parameters to Metadata
        # We inject the "Uncertainty Metadata" here.
        if temp_c or duration_s:
            for p in extracted:
                if temp_c: 
                    p.context_tags.append(f"PARAM_TEMP:{temp_c}")
                if duration_s: 
                    p.context_tags.append(f"PARAM_TIME:{duration_s}")
                
                # The Critical "Uncertainty" Metadata
                p.context_tags.append(f"META_CONFIDENCE:{confidence}")
                p.context_tags.append(f"META_SOURCE:{source}")
            
        return extracted

    @classmethod
    def get_or_create_primitive(cls, **kwargs) -> PhysicalPrimitive:
        p_id = kwargs["id"]
        if p_id not in cls.PRIMITIVE_LIBRARY:
            cls.PRIMITIVE_LIBRARY[p_id] = PhysicalPrimitive(**kwargs)
        return cls.PRIMITIVE_LIBRARY[p_id]
