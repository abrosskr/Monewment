import re
import json
import os
from typing import Optional, List, Dict
from app.models.ingredient_std import StandardizedIngredient
print("DEBUG: Loaded NormalizationEngine with Dict")
from app.engines.product_standard.parser import ProductDataParser

class NormalizationEngine:
    """
    [The PIM Transformer]
    Decomposes raw strings into structured PIM attributes.
    Supports Dynamic Learning via residue capture and Layered Ontology.
    """
    CORE_ONTOLOGY = os.path.join(os.getcwd(), "backend", "data", "ontology_core.json")
    EVOLVED_ONTOLOGY = os.path.join(os.getcwd(), "backend", "data", "ontology_evolved.json")
    
    @classmethod
    def _load_ontology(cls) -> Dict:
        # 1. Load Core (Baseline)
        ontology = {"origins": [], "states": [], "details": [], "main_categories": {}}
        if os.path.exists(cls.CORE_ONTOLOGY):
             with open(cls.CORE_ONTOLOGY, "r", encoding="utf-8") as f:
                 ontology = json.load(f)
        
        # 2. Layered evolution is deprecated in favor of Expert Ratification
        # Constitution Section 4: Only Core Ontology (Law) is trusted.
        pass
                 
        return ontology

    @classmethod
    def parse_multilingual_group(cls, raw_text: str, raw_qty: str = "") -> List[StandardizedIngredient]:
        """
        Decomposes complex strings like "Salt and Pepper" or "Sugar & Cinnamon".
        Uses multilingual conjunctions to split.
        """
        # Multilingual Conjunctions
        conjunctions = [r'\band\b', r'\bet\b', r'&', r'\+', r'\b와\b', r'\b과\b', r'\b및\b', r'\bと\b']
        pattern = '|'.join(conjunctions)
        
        # Check if we need to split
        if re.search(pattern, raw_text, re.IGNORECASE):
            parts = re.split(pattern, raw_text, flags=re.IGNORECASE)
            results = []
            for p in parts:
                p = p.strip()
                if p:
                    # If quantity is shared, apply it to all parts
                    results.append(cls.parse_to_pim(p, raw_qty))
            return results
        
        return [cls.parse_to_pim(raw_text, raw_qty)]

    @classmethod
    def parse_to_pim(cls, raw_text: str, raw_qty: str = "") -> StandardizedIngredient:
        """
        Main parsing logic.
        Example: "한돈 암 돼지 안심 생 1kg" -> StandardizedIngredient
        Example: "1.5 cups Flour" -> StandardizedIngredient
        """
        text = raw_text.strip()
        combined_text = text if not raw_qty else f"{text} {raw_qty}"
        
        # 1. 중량 추출 (개선된 글로벌 파서 활용)
        mass, unit = ProductDataParser.parse_weight(combined_text)
        
        # 2. 텍스트 정규화 (글로벌 단위 확장)
        # 다양한 언어의 단위를 포함하여 정규화
        unit_regex = r'(kg|g|lb|lbs|oz|ml|l|unit|개|포기|군|봉|T|t|컵|ml|L|팩|장|쪽|大さじ|小さじ|少々|pinch|cup|clove|count|unit|oignons)'
        clean_text = re.sub(r'[0-9./]+' + unit_regex, '', combined_text, flags=re.IGNORECASE)
        # 수량만 있는 경우(단위 생략)도 처리
        clean_text = re.sub(r'^[0-9./]+\s+', '', clean_text) 
        clean_text = re.sub(r'[()\[\]]', ' ', clean_text).strip()
        
        # Defensive: If clean_text is empty but we have a quantity, it might be a split error
        if not clean_text and combined_text:
            # If everything was stripped, the 'main ingredient' might have been part of the unit or misspelled
            # Fallback to residues
            pass
        
        if not clean_text:
             return StandardizedIngredient(main_category="Unknown", mass_g=mass)
        
        ontology = cls._load_ontology()
        origins = ontology.get("origins", [])
        states = ontology.get("states", [])
        details = ontology.get("details", [])
        main_categories = ontology.get("main_categories", {})

        origin = None
        detail = None
        main_cat = "기타"
        sub_cat = None
        state = "생"
        residues = []
        confidence_penalties = 0.0
        
        # 3. 속성 매핑 로직
        parts = re.split(r'[\s,]+', clean_text)
        for part in parts:
            part = part.strip()
            if not part: continue
            
            matched = False
            part_lower = part.lower()
            
            # Origin Check (Partial match penalty: -0.05)
            if any(o.lower() in part_lower for o in origins):
                origin = part
                matched = True
                if not any(o.lower() == part_lower for o in origins):
                    confidence_penalties += 0.05
                
            # State Check
            if any(s.lower() == part_lower for s in states):
                state = part
                matched = True

            # Detail Check
            if any(d.lower() in part_lower for d in details):
                detail = part
                matched = True
            
            # Category & Sub-Category Logic
            found_cat = False
            for cat, info in main_categories.items():
                # Exact Match (1.0)
                if cat.lower() == part_lower:
                    main_cat = cat
                    found_cat = True
                    matched = True
                    break
                # Synonym Match (Penalty: -0.1)
                elif any(syn.lower() in part_lower for syn in info.get("synonyms", [])):
                    main_cat = cat
                    found_cat = True
                    matched = True
                    confidence_penalties += 0.1
                    # Sub-category check
                    for sub in info.get("sub", []):
                        if sub.lower() in part_lower:
                            sub_cat = sub
                    break
            
            if not found_cat and main_cat != "기타":
                info = main_categories.get(main_cat, {})
                for sub in info.get("sub", []):
                    if sub.lower() in part_lower:
                        sub_cat = sub
                        matched = True

            if not matched:
                residues.append(part)
                confidence_penalties += 0.1 # Each residue reduces confidence
        
        # 4. Fallback & Intelligence Layer
        confidence = max(0.1, 1.0 - confidence_penalties)
        
        if main_cat == "기타" and residues:
             # Constitution Section 4: Propose residues as Hypotheses (Untrusted)
             from app.services.ontology_governance import OntologyGovernanceService
             # We pass the first residue or full string as reference
             res_str = " ".join(residues)
             OntologyGovernanceService.propose_hypothesis(
                 residue=res_str, 
                 context_url="INTERNAL_PARSER", 
                 confidence_score=confidence
             )
             confidence = min(confidence, 0.4) # Hypothesis grade is limited

        return StandardizedIngredient(
            origin=origin,
            detail=detail,
            main_category=main_cat,
            sub_category=sub_cat,
            storage_state=state,
            mass_g=mass,
            confidence=round(confidence, 2),
            residue=" ".join(residues) if residues else None
        )
