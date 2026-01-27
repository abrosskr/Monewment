import os
import requests
from fastapi import HTTPException

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # Fallback: Check vendors-k8s.yaml if env var is missing
        if not self.api_key:
            import re
            k8s_path = os.path.join(os.getcwd(), "vendors-k8s.yaml")
            if os.path.exists(k8s_path):
                try:
                    with open(k8s_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        match = re.search(r'name:\s*GOOGLE_API_KEY\s*\n\s*value:\s*"([^"]+)"', content)
                        if match:
                            self.api_key = match.group(1)
                            print(f"[GeminiService] Loaded Key from K8s Manifest.")
                except Exception as e:
                    print(f"[GeminiService] Failed to read K8s: {e}")
                    
        if not self.api_key:
            print("[GeminiService] Warning: No API Key found.")

    def generate_content(self, prompt: str) -> str:
        """
        Generic generation method.
        """
        if not self.api_key:
             # Return valid JSON error or empty for fallback
             return "{}"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "{}"

    def analyze_items(self, items: list[str]) -> str:
        # Legacy wrapper
        prompt = f"당신은 B2B 식자재 전문가입니다. 다음 품목의 마진을 분석해서 JSON으로 응답하세요: {items}"
        try:
            return self.generate_content(prompt)
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"AI Error: {e}")

gemini_service = GeminiService()
