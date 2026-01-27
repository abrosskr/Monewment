# app/services/scraper_service.py
import json
import re
import time
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class ScraperService:
    """
    [The Collector]
    Fetches raw data from the web.
    Focuses on 'Schema.org/Recipe' which is the Global Standard.
    
    🛡️ Stealth Mode Enabled:
    - Random User-Agents
    - Human-like Jitter (Delays)
    - Exponential Backoff
    """

    # 🎭 Masking Tools
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]

    @classmethod
    def fetch_with_stealth(cls, url: str, retries: int = 3) -> Optional[str]:
        """
        [The Sneak]
        Fetches URL HTML with human-like behavior.
        "Slow is Smooth, Smooth is Fast."
        """
        for attempt in range(retries):
            try:
                # 1. 🐢 Human Delay (Random 2s ~ 5s)
                # We are not in a hurry. Stability > Speed.
                sleep_time = random.uniform(2.0, 5.0)
                time.sleep(sleep_time)

                # 2. 🎭 Mimic Browser Headers
                headers = {
                    "User-Agent": random.choice(cls.USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.google.com/"
                }

                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8')

            except urllib.error.HTTPError as e:
                print(f"   ⚠️ [Attempt {attempt+1}] Error {e.code}: {e.reason}")
                if e.code in [429, 503]: # Rate Limited or Busy
                    wait = (2 ** attempt) * 5 # Exponential Backoff (5s, 10s, 20s)
                    print(f"      Unknown human factor. Sleeping {wait}s...")
                    time.sleep(wait)
                else:
                    break # Fatal error (404, etc)
            except Exception as e:
                print(f"   ⚠️ [Attempt {attempt+1}] Connection Error: {e}")
                
        print("   ❌ Failed to fetch after retries.")
        return None

    @staticmethod
    def parse_json_ld(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses structured JSON-LD data (Standard Web Format).
        """
        if "@type" not in json_data or "Recipe" not in json_data["@type"]:
            raise ValueError("Not a valid Recipe JSON-LD")

        # Extract Core Fields
        return {
            "title": json_data.get("name", "Unknown Recipe"),
            "description": json_data.get("description", ""),
            "ingredients": json_data.get("recipeIngredient", []),
            "instructions": ScraperService._parse_instructions(json_data.get("recipeInstructions", [])),
            "image": json_data.get("image", ""),
            "author": json_data.get("author", {}).get("name", "Unknown"),
            "source_type": "SCHEMA_ORG"
        }

    @staticmethod
    def _parse_instructions(instructions: Any) -> List[str]:
        """
        Handles various Schema.org instruction formats (List[str] vs List[Dict]).
        """
        steps = []
        if isinstance(instructions, list):
            for item in instructions:
                if isinstance(item, str):
                    steps.append(item)
                elif isinstance(item, dict) and "text" in item:
                    steps.append(item["text"])
        return steps

    @staticmethod
    def clean_text(text_list: List[str]) -> Dict[str, float]:
        """
        Converts raw ingredient strings into structured Dict.
        Input: ["1 lb Pork", "2 tsp Salt"]
        Output: {"Pork": 450.0, "Salt": 10.0} (Mock Regex Logic)
        """
        cleaned = {}
        for raw in text_list:
            # 1. Regex to separate Qty / Unit / Name
            try:
                parts = raw.split(" ", 2)
                qty = float(parts[0])
                unit = parts[1].lower()
                name = parts[2] if len(parts) > 2 else "Unknown"
                
                # Normalize Mass to Grams (Simple logic)
                if unit in ["g", "gram", "grams"]: mass = qty
                elif unit in ["kg", "kilogram"]: mass = qty * 1000
                elif unit in ["lb", "pound"]: mass = qty * 453.59
                elif unit in ["oz", "ounce"]: mass = qty * 28.35
                elif unit in ["tsp", "teaspoon"]: mass = qty * 5.0 
                elif unit in ["tbsp", "tablespoon"]: mass = qty * 15.0
                else: mass = qty 
                    
                cleaned[name.strip()] = round(mass, 2)
            except Exception:
                pass
                
        return cleaned
