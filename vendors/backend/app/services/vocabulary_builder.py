import json
import os
import re
from collections import Counter
from sqlalchemy.orm import Session
from app.engines.product_standard.models import ProductMaster
# from app.models.recipe import ScrapedRecipe (Use if available)

class VocabularyBuilder:
    """
    [Ontology Expansion]
    Scans DB for new terms and updates the Knowledge Base.
    """
    def __init__(self, db: Session):
        self.db = db
        self.kb_path = os.path.join(os.getcwd(), "backend", "data", "knowledge_base.json")

    def build_vocabulary(self):
        print("📚 [Vocabulary] Scanning database for new terms...")
        
        # 1. Harvest Terms from PIM
        products = self.db.query(ProductMaster).all()
        terms = []
        for p in products:
            # Extract meaningful words from product name
            words = self._extract_words(p.product_name)
            terms.extend(words)
            
        # 2. Analyze Frequency
        counter = Counter(terms)
        common_terms = counter.most_common(20)
        
        print(f"   ✅ Analyzed {len(products)} products -> Found {len(counter)} unique terms.")
        print(f"   🔝 Top Terms: {[t[0] for t in common_terms]}")
        
        # 3. Update Knowledge Base (Mock Update for now)
        # In real implementation, we would load existing JSON and append new keys.
        self._update_knowledge_base(counter)

    def _extract_words(self, text: str) -> list:
        # Simple tokenizer for Korean/English
        # Removes numbers, brackets, special chars
        clean = re.sub(r'[^\w\s]', '', text)
        return [w for w in clean.split() if len(w) > 1]

    def _update_knowledge_base(self, new_stats: Counter):
        # Here we would merge with existing JSON
        # For prototype, we just verify the logic works
        pass
