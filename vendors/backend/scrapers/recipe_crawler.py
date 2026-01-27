from typing import List, Dict, Optional
import time
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.engines.compiler import CompilerEngine, CompilationResult
from app.models.matter import TrustTier
from app.models.fis_protocol import FisFile

class RecipeCrawler:
    """
    [Phase 6: The Quality Gate]
    Crawls recipes but REJECTS vague/historical texts.
    Only allows 'Modern Structured' recipes into the FIS Repo.
    """
    
    def __init__(self):
        pass
        
    def check_feasibility(self, instructions: List[str]) -> bool:
        """
        The Bouncer: Rejects recipes that lack physics indicators.
        """
        full_text = " ".join(instructions).lower()
        
        # 1. Physics Keyword Check
        keywords = ["minute", "min", "hour", "degree", "heat", "boil", "fry", "bake", "c"]
        score = sum(1 for k in keywords if k in full_text)
        
        # Threshold: At least 2 physics keywords required
        if score < 2:
            return False
            
        # 2. Vague Term Check (Gutenberg Style)
        vague_terms = ["cook until done", "moderate fire", "slow oven"]
        if any(v in full_text for v in vague_terms):
            # Penalize
            return False
            
        return True

    def assign_tier(self, result: CompilationResult) -> TrustTier:
        """
        Assigns Trust Tier based on Compilation Confidence.
        """
        if result.status == "FAILED":
            return TrustTier.U
            
        # Inspect Metadata from Compiler
        # If compiler engine had access to "Hybrid Verified" params -> Tier B
        # If mostly "LLM Inferred" -> Tier C
        
        # Simplified Logic for Prototype:
        # Check logs for "Conf: HIGH"
        high_conf_count = sum(1 for log in result.logs if "Conf: HIGH" in log)
        total_steps = len(result.fis_file.timeline) if result.fis_file else 1
        
        ratio = high_conf_count / max(total_steps, 1)
        
        if ratio > 0.8:
            return TrustTier.B # Text Explicit
        elif ratio > 0.4:
            return TrustTier.C # Hybrid / Partial
        else:
            return TrustTier.D # Heuristic

    def process_recipe(self, title: str, ingredients: List[str], instructions: List[str]) -> Optional[FisFile]:
        """
        Pipeline: Feasibility -> Compile -> Tier -> Save
        """
        print(f"Crawler: Processing '{title}'...")
        
        # 1. Quality Gate
        if not self.check_feasibility(instructions):
            print(f"  REJECTED: Low Feasibility (Vague Structure).")
            return None
            
        # 2. Compile
        result = CompilerEngine.compile_recipe(title, ingredients, instructions)
        
        if result.status == "FAILED":
            print(f"  COMPILATION FAILED: {result.issues}")
            return None
            
        # 3. Assign Tier
        tier = self.assign_tier(result)
        result.fis_file.metadata.data_quality = tier # inject tier into quality field or custom
        result.fis_file.metadata.extra_info["trust_tier"] = tier.value
        
        print(f"  ACCEPTED: Tier {tier.value} (Conf Ratio: {result.status})")
        return result.fis_file

if __name__ == "__main__":
    # Test
    crawler = RecipeCrawler()
    
    # Bad Recipe (Gutenberg)
    crawler.process_recipe(
        "Old Porridge", 
        ["Oats", "Water"], 
        ["Cook until done on a moderate fire."]
    )
    
    # Good Recipe (Modern)
    crawler.process_recipe(
        "Modern Oatmeal", 
        ["Oats", "Water"], 
        ["Boil water.", "Add oats and simmer for 5 minutes."]
    )
