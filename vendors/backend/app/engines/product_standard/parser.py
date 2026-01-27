import re
from typing import Tuple, Optional
from .codes import WeightUnit

class ProductDataParser:
    """
    [Logistics Normalizer]
    Converts global raw data into ProductStandard logic.
    """
    
    @staticmethod
    def normalize_gtin(code: str) -> str:
        """
        Pads UPC-A (12) or EAN-13 (13) to GTIN-14 standard.
        Strips whitespace and dashes.
        """
        clean_code = re.sub(r'[^0-9]', '', str(code))
        # Pad with leading zeros to 14 digits
        return clean_code.zfill(14)

    @staticmethod
    def parse_weight(raw_weight: str) -> Tuple[float, WeightUnit]:
        """
        Parses global strings into (value, MetricUnit).
        Handles: "1 lb", "453g", "10 oz", "대사지 1", "3 pincées"
        """
        raw = raw_weight.lower().strip().replace(",", ".")
        
        # 1. Define Unit Anchors for Robust Matching
        units_map = {
            "g": WeightUnit.G, "ml": WeightUnit.ML,
            "kg": WeightUnit.G, "l": WeightUnit.ML, "liter": WeightUnit.ML, "liters": WeightUnit.ML, "cl": WeightUnit.ML,
            "lb": WeightUnit.G, "lbs": WeightUnit.G, "pound": WeightUnit.G, "pounds": WeightUnit.G,
            "oz": WeightUnit.G, "ounce": WeightUnit.G, "ounces": WeightUnit.G,
            "floz": WeightUnit.ML, "folz": WeightUnit.ML,
            "cup": WeightUnit.ML, "cups": WeightUnit.ML, "컵": WeightUnit.ML,
            "tbsp": WeightUnit.G, "大さじ": WeightUnit.G, "큰술": WeightUnit.G, "t": WeightUnit.G, "tb": WeightUnit.G,
            "tsp": WeightUnit.G, "小さじ": WeightUnit.G, "작은술": WeightUnit.G, "ts": WeightUnit.G,
            "pinch": WeightUnit.G, "pincée": WeightUnit.G, "pincées": WeightUnit.G, "少々": WeightUnit.G,
            "pack": WeightUnit.G, "팩": WeightUnit.G, "봉": WeightUnit.G, "봉지": WeightUnit.G,
            "sheet": WeightUnit.G, "장": WeightUnit.G,
            "unit": WeightUnit.G, "개": WeightUnit.G, "count": WeightUnit.G, "個": WeightUnit.G, "oignons": WeightUnit.G,
            "egg": WeightUnit.G, "eggs": WeightUnit.G, "pcs": WeightUnit.G, "pce": WeightUnit.G,
            "clove": WeightUnit.G, "cloves": WeightUnit.G, "쪽": WeightUnit.G, "gousse": WeightUnit.G, "gousses": WeightUnit.G,
            "cm": WeightUnit.G, "모": WeightUnit.G, "줌": WeightUnit.G
        }
        
        # 2. Extract Value and Potential Unit
        # Look for number patterns (including fractions like 1/2, 1.5, 1 1/2)
        # Improved Regex: Captures "1 1/2", "1/2", "1.5", "1,5", "10"
        num_match = re.search(r"(\d+\s+\d+/\d+|\d+/\d+|\d+[.,]\d+|\d+)", raw)
        
        if not num_match:
            return (0.0, WeightUnit.G)
            
        val_str = num_match.group(1).replace(",", ".")
        remaining = raw.replace(num_match.group(0), "").replace(" ", "") # Use group(0) to remove exact match
        
        # Handle fractions
        try:
            val = 0.0
            if " " in val_str and "/" in val_str: # Mixed fraction "1 1/2"
                whole, frac = val_str.split()
                n, d = frac.split("/")
                val = float(whole) + (float(n) / float(d))
            elif "/" in val_str: # Simple fraction "1/2"
                n, d = val_str.split("/")
                val = float(n) / float(d)
            else:
                val = float(val_str)
        except:
            val = 0.0
            
        # 3. Best-match Unit
        found_unit = None
        # Try exact match first on remaining
        if remaining in units_map:
            found_unit = remaining
        else:
            # Try to find any unit anchor in the remaining string
            for u in sorted(units_map.keys(), key=len, reverse=True):
                if u in remaining:
                    found_unit = u
                    break
        
        if not found_unit:
            return (val, WeightUnit.G)
            
        # 4. Global Unit conversion logic
        unit_key = found_unit
        if unit_key in ["kg"]: return (val * 1000.0, WeightUnit.G)
        if unit_key in ["l", "liter", "liters"]: return (val * 1000.0, WeightUnit.ML)
        if unit_key in ["cl"]: return (val * 10.0, WeightUnit.ML)
        if unit_key in ["lb", "lbs", "pound", "pounds"]: return (val * 453.59, WeightUnit.G)
        if unit_key in ["oz", "ounce", "ounces"]: return (val * 28.35, WeightUnit.G)
        if unit_key in ["floz", "folz"]: return (val * 29.57, WeightUnit.ML)
        if unit_key in ["cup", "cups", "컵"]: return (val * 200.0, WeightUnit.ML)
        if unit_key in ["tbsp", "大さじ", "큰술", "tb", "t"]: return (val * 15.0, WeightUnit.G) # T or t often 15g in KR
        if unit_key in ["tsp", "小さじ", "작은술", "ts"]: return (val * 5.0, WeightUnit.G)
        if unit_key in ["pinch", "pincée", "pincées", "少々"]: return (val * 1.0, WeightUnit.G)
        if unit_key in ["pack", "팩", "봉", "봉지"]: return (val * 210.0, WeightUnit.G)
        if unit_key in ["sheet", "장"]: return (val * 15.0, WeightUnit.G)
        if unit_key in ["egg", "eggs"]: return (val * 60.0, WeightUnit.G)
        if unit_key in ["unit", "개", "count", "pcs", "pce"]: return (val * 60.0, WeightUnit.G)
        if unit_key in ["oignons"]: return (val * 150.0, WeightUnit.G)
        if unit_key in ["個"]: return (val * 200.0, WeightUnit.G)
        if unit_key in ["clove", "cloves", "쪽", "gousse", "gousses"]: return (val * 5.0, WeightUnit.G)
        if unit_key in ["cm"]: return (val * 20.0, WeightUnit.G)
        if unit_key in ["모"]: return (val * 300.0, WeightUnit.G)
        if unit_key in ["줌"]: return (val * 30.0, WeightUnit.G)
             
        return (val, units_map.get(unit_key, WeightUnit.G))
