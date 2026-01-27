# app/services/local_llm_classifier.py
import requests
import json
from .memory_service import MemoryService
from app.core.prompts import get_classifier_prompt

class LocalLLMClassifier:
    def __init__(self, model_name="llama3:latest"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        self.memory = MemoryService()
        
    def classify(self, recipe_name: str, ingredients: list):
        """
        Uses RAG (Retrieval) + Generation to classify.
        """
        from .ontology_normalization import OntologyService
        
        # 0. FILTER out tools/kitchenware
        ingredients = OntologyService.filter_ingredients(ingredients)
        
        ingredient_text = ", ".join([i['item'] for i in ingredients])
        full_text = f"{recipe_name} ({ingredient_text})"
        
        # 1. RETRIEVE from Memory (RAG)
        similar_examples = self.memory.recall_similar(full_text, k=3)
        
        examples_context = ""
        if similar_examples:
            examples_context = "### Reference Examples (Learn from these):\n"
            for ex in similar_examples:
                data = ex["example"]
                examples_context += f"- Input: {data['text']}\n"
                examples_context += f"  Output: {json.dumps(data['classification'], ensure_ascii=False)}\n"

        # 2. GENERATE Prompt
        prompt = get_classifier_prompt(recipe_name, ingredient_text, examples_context)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" 
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            if response.status_code != 200:
                error_msg = f"Local LLM API Error: {response.status_code} - {response.text}"
                print(error_msg)
                raise Exception(error_msg)
            
            response.raise_for_status()
            
            result = response.json()
            raw_response = result.get("response", "")
            
            # Clean up potential markdown
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:-3]
                
            result_json = json.loads(cleaned_response)
            
            # 2. APPLY Ontology Normalization (Double Check)
            from .ontology_normalization import OntologyService
            for key in ["protein_modifier", "protein_part", "primary_modifier", "default_method"]:
                if key in result_json:
                    result_json[key] = OntologyService.normalize(result_json[key])
            
            return result_json
            
        except Exception as e:
            print(f"Local LLM Error: {e}")
            raise # Re-raise exception to let the caller handle it or at least be aware
