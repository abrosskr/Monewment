from app.services.gemini import GeminiService
import requests
import os
import json

class VisionService(GeminiService):
    def analyze_menu_image(self, image_b64: str, context: str = "") -> list[dict]:
        if not self.api_key:
             raise Exception("Google API Key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        prompt = f"""
        당신은 배달 음식 원가 분석 전문가입니다.
        제공된 메뉴판/음식 사진을 분석하여, 판매되고 있는 음식의 '식자재 리스트'를 추정해 주세요.
        
        컨텍스트: {context} (가게 이름 등)
        
        다음 JSON 형식으로만 응답하세요. (마크다운 없이 순수 JSON):
        [
            {{
                "item": "추정되는 메뉴명",
                "ingredients": [
                    {{"name": "재료명(예: 삼겹살)", "qty": "추정중량(예: 200g)", "count": 1}}
                ]
            }}
        ]
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64
                        }
                    }
                ]
            }]
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            try:
                text_content = data['candidates'][0]['content']['parts'][0]['text']
                # Clean markdown if present
                clean_json = text_content.replace('```json', '').replace('```', '').strip()
                return json.loads(clean_json)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"Vision Parse Error: {e}, Raw: {data}")
                return []
                
        except Exception as e:
            print(f"Vision API Error: {e}")
            return []

vision_service = VisionService()
