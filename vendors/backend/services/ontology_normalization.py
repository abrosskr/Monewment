import re

class OntologyService:
    """
    [Food IQ] Service to normalize ingredient names and food descriptors 
    to standard English ontology based on official naming conventions.
    """
    
    # Standard Mapping Dictionary
    MAP = {
        # Kitchenware / Tools (Priority Filter)
        "믹싱볼": "TOOL_IGNORE",
        "조리용나이프": "TOOL_IGNORE",
        "위생장갑": "TOOL_IGNORE",
        "키친타올": "TOOL_IGNORE",
        "전자레인지": "TOOL_IGNORE",
        "가스레인지": "TOOL_IGNORE",
        "계량스푼": "TOOL_IGNORE",
        "계량컵": "TOOL_IGNORE",
        "프라이팬": "TOOL_IGNORE",
        "후라이팬": "TOOL_IGNORE",
        "볼": "TOOL_IGNORE",
        "채반": "TOOL_IGNORE",
        "냄비": "TOOL_IGNORE",
        "도마": "TOOL_IGNORE",
        "칼": "TOOL_IGNORE",
        "나이프": "TOOL_IGNORE",
        "접시": "TOOL_IGNORE",
        "그릇": "TOOL_IGNORE",
        "웍": "TOOL_IGNORE",
        "가위": "TOOL_IGNORE",
        "집게": "TOOL_IGNORE",
        "국자": "TOOL_IGNORE",
        "수저": "TOOL_IGNORE",
        "숟가락": "TOOL_IGNORE",
        "젓가락": "TOOL_IGNORE",
        "믹서기": "TOOL_IGNORE",
        "오븐": "TOOL_IGNORE",
        "저울": "TOOL_IGNORE",
        "팬": "TOOL_IGNORE",
        
        # Proteins
        "돼지고기": "Pork",
        "돼지": "Pork",
        "돈육": "Pork",
        "소고기": "Beef",
        "소": "Beef",
        "우육": "Beef",
        "닭고기": "Chicken",
        "닭": "Chicken",
        "계육": "Chicken",
        "양고기": "Lamb",
        "오리고기": "Duck",
        "생선": "Fish",
        "새우": "Shrimp",
        "계란": "Egg",
        "달걀": "Egg",
        "키조개": "Scallop",
        "가리비": "Scallop",
        
        # Specific Parts (Cuts)
        "안심": "Tenderloin",
        "등심": "Loin",
        "삼겹살": "Belly",
        "목살": "Shoulder/Neck",
        "앞다리": "Foreleg/Picnic",
        "뒷다리": "Hindleg/Ham",
        "사태": "Shank",
        "양지": "Brisket",
        "차돌박이": "Brisket (Point)",
        "갈비": "Ribs",
        "항정살": "Jowl",
        "껍데기": "Skin",
        "가슴살": "Breast",
        "다리살": "Thigh",
        "날개": "Wing",
        "똥집": "Gizzard",
        "모래집": "Gizzard",
        "관자": "Adductor",
        "알": "Roe",
        "곤이": "Roe/Seminal",
        "이리": "Milt",
        "간": "Liver",
        "허파": "Lung",
        "곱창": "Small Intestine",
        "대창": "Large Intestine",
        "막창": "Abomasum",
        
        # Fermented / Specific Korean items
        "신김치": "Kimchi (Fermented)",
        "익은김치": "Kimchi (Fermented)",
        "묵은지": "Kimchi (Aged)",
        "김치": "Kimchi",
        "된장": "Doenjang (Soybean Paste)",
        "고추장": "Gochujang (Chili Paste)",
        "간장": "Soy Sauce",
        
        # Vegetables / Base
        "두부": "Tofu",
        "파": "Green Onion",
        "대파": "Green Onion",
        "양파": "Onion",
        "마늘": "Garlic",
        "감자": "Potato",
        "쌀": "Rice",
        "밥": "Rice",
        
        # Methods / Others
        "끓이기": "Boil",
        "찌기": "Steam",
        "굽기": "Grill",
        "볶기": "Stir-fry",
        "튀기기": "Deep-fry",
        "조리기": "Braise",
        "무침": "Muchim/Season",
        "데치기": "Blanch",
        "절임": "Pickle",
        "부침": "Pan-fry",
        "전": "Pan-fry",
        "회": "Raw",

        # Kitchenware / Tools (To be filtered out)
        "볼": "TOOL_IGNORE",
        "채반": "TOOL_IGNORE",
        "냄비": "TOOL_IGNORE",
        "도마": "TOOL_IGNORE",
        "칼": "TOOL_IGNORE",
        "나이프": "TOOL_IGNORE",
        "위생장갑": "TOOL_IGNORE",
        "키친타올": "TOOL_IGNORE",
        "접시": "TOOL_IGNORE",
        "그릇": "TOOL_IGNORE",
        "프라이팬": "TOOL_IGNORE",
        "후라이팬": "TOOL_IGNORE",
        "웍": "TOOL_IGNORE",
        "가위": "TOOL_IGNORE",
        "집게": "TOOL_IGNORE",
        "국자": "TOOL_IGNORE",
        "수저": "TOOL_IGNORE",
        "숟가락": "TOOL_IGNORE",
        "젓가락": "TOOL_IGNORE",
        "믹서기": "TOOL_IGNORE",
        "전자레인지": "TOOL_IGNORE",
        "오븐": "TOOL_IGNORE",
        "계량컵": "TOOL_IGNORE",
        "계량스푼": "TOOL_IGNORE",
        "저울": "TOOL_IGNORE"
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Normalize Korean text to English standard.
        """
        if not text:
            return ""
            
        # 1. Clean up brackets and romanization leftovers if any
        clean_text = re.sub(r'\(.*?\)', '', text).strip()
        
        # 2. Direct mapping check
        if clean_text in cls.MAP:
            return cls.MAP[clean_text]
            
        # 3. Partial match / Keyword fallback
        for ko, en in cls.MAP.items():
            if ko in clean_text:
                return en
                
        return clean_text

    @classmethod
    def is_seasoning(cls, name: str) -> bool:
        """Check if the ingredient is likely a seasoning/condiment."""
        seasonings = ["Salt", "Sugar", "Soy Sauce", "Vinegar", "Gochujang", "Doenjang", 
                      "Oil", "Sesame", "Pepper", "Garlic", "Ginger", "Sauce", "Water", "Broth"]
        norm = cls.normalize(name)
        # Check explicit list or keywords
        if norm in seasonings: return True
        if any(x in norm for x in ["Sauce", "Paste", "Powder", "Oil", "Syrup"]): return True
        return False

    @classmethod
    def filter_ingredients(cls, ingredients: list) -> list:
        """
        Filters out non-food items (tools) and enriches ingredients with metadata.
        Returns: List of dicts {item, quantity, normalized, is_seasoning}
        """
        if not ingredients: return []
        filtered = []
        try:
            for ing in ingredients:
                # Handle both dict and string
                original_item = ing.get("item", "") if isinstance(ing, dict) else str(ing)
                quantity = ing.get("quantity", "") if isinstance(ing, dict) else ""
                
                norm = cls.normalize(original_item)
                
                if norm == "TOOL_IGNORE":
                    continue
                
                # Enrich data
                enriched = {
                    "item": original_item,
                    "quantity": quantity,
                    "normalized": norm,
                    "is_seasoning": cls.is_seasoning(original_item)
                }
                filtered.append(enriched)
        except Exception as e:
            print(f"⚠️ [Ontology Filter Warning] {e}")
            return ingredients # Fallback to original if error
            
        return filtered

    @classmethod
    def get_supported_methods(cls):
        return ["Boil", "Steam", "Fry", "Grill", "Braise", "Stir-fry", "Muchim", "Blanch", "Pickle", "Raw"]

    @classmethod
    def get_food_types(cls):
        return ["Jjigae", "Guk/Tang", "Jjim", "Bokkeum", "Gui", "Muchim", "Twigim", "Jeon", "Salad", "Steak", "Pasta"]

    @classmethod
    def predict_main_ingredient(cls, menu_name: str, ingredients: list) -> str:
        """
        Heuristics to find the Main Ingredient (Protein Modifier).
        Priority:
        1. Explicit mention in Menu Name (e.g., "Kimchi Jjigae" -> Kimchi)
        2. High-priority protein found in Ingredient List (Pork, Beef > Tofu > Veg)
        """
        # Priority mapping for Heuristic
        # Keywords to look for in Menu Name -> Mapped Value
        NAME_PRIORITY = {
            "돼지": "Pork", "돈육": "Pork", "제육": "Pork", "삼겹": "Pork", "목살": "Pork",
            "소고기": "Beef", "우육": "Beef", "차돌": "Beef", "불고기": "Beef", "갈비": "Beef",
            "닭": "Chicken", "치킨": "Chicken",
            "김치": "Kimchi", "묵은지": "Kimchi",
            "참치": "Fish", "고등어": "Fish", "꽁치": "Fish", "동태": "Fish",
            "두부": "Tofu", "순두부": "Tofu",
            "계란": "Egg", "달걀": "Egg",
            "오징어": "Seafood", "새우": "Shrimp"
        }

        # 1. Check Menu Name
        for kw, val in NAME_PRIORITY.items():
            if kw in menu_name:
                return val
        
        # 2. Check Ingredients (Iterate list)
        # We look for high-value proteins in the ingredient list
        # Order matters!
        PRIORITY_LIST = ["Beef", "Pork", "Chicken", "Lamb", "Duck", "Fish", "Shrimp", "Scallop", "Tofu", "Egg", "Kimchi"]
        
        # Normalize ingredients first
        norm_ingredients = []
        for ing in ingredients:
            item_name = ing.get("item", "") if isinstance(ing, dict) else str(ing)
            norm = cls.normalize(item_name)
            norm_ingredients.append(norm)

        for p in PRIORITY_LIST:
            # Check if this protein or its cuts exist in normalized ingredients
            # Simple check: is the protein name itself there?
            if p in norm_ingredients:
                return p
            # Deep check: e.g., "Belly" implies "Pork"? (We need reverse mapping for that, skipping for simple heuristic now)
            
        # Fallback
        return ""

    @classmethod
    def predict_flavor(cls, menu_name: str, ingredients: list) -> str:
        """
        Simple heuristic for Primary Flavor.
        """
        normalized_ings = []
        for ing in ingredients:
            item_name = ing.get("item", "") if isinstance(ing, dict) else str(ing)
            normalized_ings.append(cls.normalize(item_name))

        # Check for strong flavor indicators
        if any("Kimchi" in i or "Gochujang" in i for i in normalized_ings):
            return "Spicy"
        if any("Sugar" in i or "Honey" in i or "Syrup" in i for i in normalized_ings):
            return "Sweet"
        if any("Vinegar" in i or "Lemon" in i for i in normalized_ings):
            return "Sour"
        if any("Soy Sauce" in i or "Salt" in i or "Doenjang" in i for i in normalized_ings):
            return "Salty"
            
        return "Umami" # Default fallback
