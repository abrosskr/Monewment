import re

# Unit Conversion Table (Standardized to mL)
UNIT_MAP = {
    "큰술": 15.0, "스푼": 15.0, "숟가락": 15.0,
    "작은술": 5.0, "티스푼": 5.0,
    "컵": 200.0, "종이컵": 180.0,
    "T": 15.0, "t": 5.0,
    "ml": 1.0, "l": 1000.0,
    "g": 1.0, "kg": 1000.0,
    "약간": 0.5, "적당량": 1.0,
    "개": 0.0, "봉": 0.0, "대": 0.0, "쪽": 0.0, "톨": 0.0
}

# Regex for Ingredient Parsing
PARSE_REGEX = r'([가-힣a-zA-Z\s]+?)\s*(\d+(?:\.\d+)?(?:/\d+)?)\s*(스푼|큰술|작은술|컵|g|ml|kg|l|개|마리|봉|봉지|모|단|줌|쪽|톨|방울|약간|적당량|T|t)'

class FlavorService:
    @staticmethod
    def parse_ingredient_string(text):
        """
        Parses "간장 1스푼, 설탕 2큰술" into structured list.
        """
        if not text:
            return []
        
        # Pre-clean
        text = re.sub(r'\(.*?\)', '', text)
        raw_items = re.split(r'[,\n]+', text)
        structured_data = []
        
        for item in raw_items:
            item = item.strip()
            if not item: continue
            
            match = re.search(PARSE_REGEX, item)
            if match:
                name, quantity, unit = match.groups()
                try:
                    val = float(quantity)
                except:
                    val = 1.0
                
                structured_data.append({
                    "item": name.strip(),
                    "quantity": val,
                    "unit": unit
                })
            else:
                structured_data.append({
                    "item": item,
                    "quantity": None,
                    "unit": None
                })
        return structured_data

    @staticmethod
    def standardize_quantity(quantity, unit):
        if quantity is None: quantity = 1.0
        if not unit: return 0.0
        
        unit = unit.strip().lower()
        if unit in UNIT_MAP:
            return quantity * UNIT_MAP[unit]
        
        for key, conversion in UNIT_MAP.items():
            if key in unit:
                return quantity * conversion
        return 0.0

    @classmethod
    def compute_flavor_vector(cls, flavor_ratios):
        """
        Converts ratios -> [{axis: 'Soy Sauce', magnitude: 45.0}, ...]
        """
        vector_data = []
        for ratio in flavor_ratios:
            item_name = ratio.get("item")
            qty = ratio.get("quantity")
            unit = ratio.get("unit")
            
            ml_value = cls.standardize_quantity(qty, unit)
            if ml_value > 0:
                vector_data.append({
                    "axis": item_name,
                    "magnitude": ml_value
                })
        return vector_data
