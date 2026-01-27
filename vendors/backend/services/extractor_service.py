import requests
import json
import logging
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class ExtractorService:
    """
    [The Ear Service]
    Uses Local LLM (Ollama) or Remote Gemini to parse natural language into structured data.
    """
    def __init__(self, use_gemini: bool = False):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = settings.LLM_MODEL
        self.use_gemini = use_gemini and settings.GOOGLE_API_KEY != ""

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Parses raw text into structured JSON.
        """
        prompt = f"""
        Extract ingredients, amounts, and units from the following recipe text.
        Also identify the primary cooking method (e.g., Boiling, Stir-Frying, Roasting).
        Return ONLY valid JSON in the following format:
        {{
            "method": "string",
            "ingredients": [
                {{"name": "string", "amount": number, "unit": "string"}}
            ]
        }}
        If amount is missing, use null. Convert volume units to grams if obvious (e.g. 1 cup water -> 240g).

        Text: "{text}"
        """
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            logger.info(f"📡 Sending extraction request to AI ({self.model})...")
            
            # Simple Ollama implementation
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ AI Engine returned error: {response.status_code}")
                return self._fallback_logic(text)
                
            result = response.json()
            raw_response = result.get('response', '')
            
            try:
                data = json.loads(raw_response)
                logger.info(f"📩 AI Extraction successful: {data.get('method')}")
                return data
            except json.JSONDecodeError:
                logger.warning("⚠️ AI failed to return valid JSON. Using fallback.")
                return self._fallback_logic(text)
            
        except Exception as e:
            logger.error(f"Extraction service error: {str(e)}")
            return self._fallback_logic(text)

    def _fallback_logic(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based fallback logic.
        """
        words = text.lower().split()
        method = "General"
        if "boil" in text.lower(): method = "Boiling"
        if "fry" in text.lower(): method = "Frying"
        if "sear" in text.lower(): method = "Searing"
        
        return {
            "method": method,
            "ingredients": [{"name": word, "amount": None, "unit": None} for word in words if len(word) > 4]
        }
