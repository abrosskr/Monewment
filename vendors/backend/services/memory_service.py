import os
import json
import numpy as np
import requests
from .flavor_service import FlavorService
from ..config import settings

class MemoryService:
    def __init__(self, db_path=None, embedding_model=None):
        self.db_path = db_path or settings.KNOWLEDGE_BASE_PATH
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL
        self.api_url = settings.OLLAMA_API_URL
        self.memory = self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_db(self):
        # Atomic Write Pattern with Windows Retry Logic
        temp_path = f"{self.db_path}.tmp"
        import time
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(self.memory, f, ensure_ascii=False, indent=2)
                
                # Check for existing file and try replace
                if os.path.exists(self.db_path):
                    # Windows often locks files; try a few times
                    try:
                        os.replace(temp_path, self.db_path)
                    except PermissionError:
                        if attempt < max_retries - 1:
                            time.sleep(1.0 * (attempt + 1))
                            continue
                        else: raise
                else:
                    os.rename(temp_path, self.db_path)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ Save Failed after {max_retries} attempts: {e}")
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except: pass
                time.sleep(0.5)

    def _get_embedding(self, text):
        try:
            payload = {
                "model": self.embedding_model,
                "prompt": text
            }
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Embedding Error: {e}")
            return None

    def add_memory(self, text, classification_data):
        """
        Saves a 'Golden Record'.
        text: "목살김치찜 (Ing: ...)"
        classification_data: The correct JSON output (Type, Protein, etc.)
        """
        vector = self._get_embedding(text)
        if vector:
            # [ML Integration] Real-time Flavor Vectorization
            primary_modifier = classification_data.get("primary_modifier", "")
            if primary_modifier:
                flavor_ratios = FlavorService.parse_ingredient_string(primary_modifier)
                if flavor_ratios:
                    classification_data["flavor_ratios"] = flavor_ratios
                    flavor_vector = FlavorService.compute_flavor_vector(flavor_ratios)
                    if flavor_vector:
                         classification_data["flavor_vector"] = flavor_vector
                         print(f"🧪 Flavor Vectorized: {len(flavor_vector)} axes")

            record = {
                "text": text,
                "vector": vector,
                "classification": classification_data
            }
            self.memory.append(record)
            self._save_db()
            print(f"✅ Memory Saved: {text[:20]}...")
            return True
        return False

    def recall_similar(self, query_text, k=3):
        """
        Finds k most similar recipes.
        Returns: List of classification dicts.
        """
        if not self.memory:
            return []

        query_vec = self._get_embedding(query_text)
        if not query_vec:
            return []

        q_vec = np.array(query_vec)
        
        scores = []
        for idx, item in enumerate(self.memory):
            if "vector" not in item: continue
            mem_vec = np.array(item["vector"])
            
            dot_product = np.dot(q_vec, mem_vec)
            norm_a = np.linalg.norm(q_vec)
            norm_b = np.linalg.norm(mem_vec)
            
            similarity = dot_product / (norm_a * norm_b) if norm_b > 0 else 0
            scores.append((similarity, idx))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        
        top_k = scores[:k]
        results = []
        for score, idx in top_k:
            results.append({
                "similarity": float(score),
                "example": self.memory[idx]
            })
            
        return results

    def search_by_ingredients(self, ingredients: list, k=3):
        """
        [Intelligent Feature] Search recipes by available ingredients.
        Input: ["pork", "kimchi"]
        Internal: Embeds "pork, kimchi" and searches semantic matches.
        """
        query_text = ", ".join(ingredients)
        print(f"🧠 AI Embedding Search for ingredients: '{query_text}'")
        return self.recall_similar(query_text, k)

    def search_by_taste_profile(self, target_vector: list, k=3):
        """
        Search recipes based on Flavor Vectors (Stoichiometry).
        target_vector: [{'axis': 'Soy Sauce', 'magnitude': 15.0}, ...]
        Uses simple overlap or vector cosine if aligned.
        Here we implement a "Ingredient Magnitude Match".
        """
        # Simplify: Convert target to dict {axis: magnitude}
        target_map = {item['axis']: item['magnitude'] for item in target_vector}
        
        scores = []
        for idx, item in enumerate(self.memory):
            mem_class = item.get("classification", {})
            mem_flavor = mem_class.get("flavor_vector", [])
            
            if not mem_flavor:
                continue
                
            # Score based on overlap of axes and closeness of magnitude
            # Score = Sum(1 - abs(log(target/mem))) for matching axes?
            # Or simple Cosine on the sparse vector
            
            # Sparse Cosine Implementation
            mem_map = {m['axis']: m['magnitude'] for m in mem_flavor}
            
            dot_product = 0.0
            mag_a = 0.0
            mag_b = 0.0
            
            all_keys = set(target_map.keys()) | set(mem_map.keys())
            
            for key in all_keys:
                val_a = target_map.get(key, 0.0)
                val_b = mem_map.get(key, 0.0)
                dot_product += val_a * val_b
                mag_a += val_a ** 2
                mag_b += val_b ** 2
            
            if mag_a > 0 and mag_b > 0:
                similarity = dot_product / (np.sqrt(mag_a) * np.sqrt(mag_b))
                scores.append((similarity, idx))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        return [self.memory[i]['classification'] for s, i in scores[:k]]

if __name__ == "__main__":
    # Test
    mem = MemoryService()
    
    # ... (Test code can remain or be updated)

