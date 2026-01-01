# scripts/check_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ API Key가 없습니다.")
else:
    genai.configure(api_key=API_KEY)
    print(f"🔑 API Key 확인됨. 사용 가능한 모델 목록을 조회합니다...\n")
    
    try:
        # 사용 가능한 모델 리스트를 서버에서 가져옵니다.
        models = genai.list_models()
        found = False
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found = True
        
        if not found:
            print("⚠️ 'generateContent'를 지원하는 모델이 하나도 없습니다.")
            
    except Exception as e:
        print(f"❌ 목록 조회 실패: {e}")