import re

class IngredientNormalizer:
    def __init__(self):
        # 1. Synonym Dictionary (Mapping raw terms to Standard ID/Name)
        # In a real system, this would be loaded from DB or a large JSON file.
        self.synonyms = {
            # Base
            "달걀": "Egg", "계란": "Egg",
            "양파": "Onion", "적양파": "Onion",
            "마늘": "Garlic", "다진마늘": "Garlic", "통마늘": "Garlic",
            "대파": "Green Onion", "파": "Green Onion", "쪽파": "Green Onion",
            "고추": "Chili", "청양고추": "Chili", "홍고추": "Chili",
            "당근": "Carrot",
            "감자": "Potato",
            "버섯": "Mushroom", "표고버섯": "Mushroom", "팽이버섯": "Mushroom", "새송이버섯": "Mushroom",
            
            # Meat
            "돼지고기": "Pork", "목살": "Pork (Neck)", "삼겹살": "Pork (Belly)", "앞다리살": "Pork (Leg)",
            "소고기": "Beef", "불고기": "Beef (Bulgogi)", "차돌박이": "Beef (Brisket)",
            "닭": "Chicken", "닭고기": "Chicken", "닭가슴살": "Chicken (Breast)",
            
            # Grain
            "밥": "Rice", "쌀": "Rice", "햇반": "Rice",
            "면": "Noodle", "국수": "Noodle", "라면": "Noodle (Ramen)", "당면": "Noodle (Glass)",
            
            # Sauce/Seasoning (Keeping them distinguishable)
            "소금": "Salt", "맛소금": "Salt",
            "설탕": "Sugar",
            "간장": "Soy Sauce", "진간장": "Soy Sauce", "국간장": "Soy Sauce",
            "고춧가루": "Chili Powder",
            "고추장": "Gochujang",
            "된장": "Doenjang",
            "후추": "Pepper",
            "참기름": "Sesame Oil",
            "물": "Water",
            "육수": "Broth",
            "김치": "Kimchi", "묵은지": "Kimchi",
        }
        
        # 2. Stopwords (Prefixes/Suffixes to remove)
        self.stop_words = [
            "다진", "채썬", "갈은", "으깬", "볶은", "구운", "삶은", "데친", "송송썬", "어슷썬",
            "약간", "조금", "적당량", "반개", "1개", "한줌"
        ]

    def normalize(self, raw_text):
        """
        Input: "다진 마늘 1큰술"
        Output: "Garlic"
        """
        if not raw_text:
            return None
            
        original = raw_text
        text = raw_text

        # A. Remove specifics inside parenthesis e.g. "파(쪽파)" -> "파"
        text = re.sub(r'\(.*?\)', '', text) 
        text = re.sub(r'\[.*?\]', '', text)
        
        # B. Clean non-hangul/non-alpha except spaces? 
        # Actually we should keep numbers to remove units next, or remove them now.
        
        # C. Remove common units and numbers using Regex
        # Matches: Digits followed by optional units
        # e.g., 100g, 1T, 1큰술, 1/2개
        text = re.sub(r'\d+(/\d+)?\s*[gkgmlL개컵Tts스푼큰술작은술]+', '', text)
        text = re.sub(r'\d+', '', text) # Remove remaining digits
        
        # D. Remove stopwords
        for word in self.stop_words:
            text = text.replace(word, '')
            
        text = text.strip()
        
        # E. Dictionary Lookup (Greedy match? or Exact?)
        # Strategy: Iterate through dictionary and scan text. 
        # Priority: Longer keys first? (e.g. "새송이버섯" > "버섯")
        
        found_key = None
        found_val = None
        max_len = 0
        
        for key, val in self.synonyms.items():
            if key in text:
                if len(key) > max_len:
                    max_len = len(key)
                    found_key = key
                    found_val = val
        
        if found_val:
            return found_val
            
        # F. Fallback: Return Cleaned Text if no match
        # (This helps us identify what missing synonyms to add)
        return f"Unknown ({text})"

if __name__ == "__main__":
    # Simple Unit Test
    norm = IngredientNormalizer()
    samples = [
        "다진마늘 1큰술",
        "양파 1/2개",
        "돼지고기 목살 300g",
        "채썬 당근 약간",
        "후추 톡톡",
        "와플믹스"
    ]
    for s in samples:
        print(f"'{s}' -> {norm.normalize(s)}")
