import os
import requests
from fastapi import APIRouter, Request, Depends
from src.schemas import ChatRequest
from src.config import settings
from src.core.security import validate_project_path
from src.core.limiter import limiter

router = APIRouter()

@router.post("/")
@limiter.limit("10/minute") 
async def chat_with_agent(request: Request, chat_request: ChatRequest):
    """실시간 로그를 컨텍스트로 사용하여 AI 에이전트와 대화하고 해결책을 구합니다."""
    env_path = settings.ENV_FILE_PATH
    api_key = None
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    
    if not api_key:
        return {"response": "⚠️ API 키가 설정되지 않았습니다. [설정] 탭에서 키를 입력해주세요."}

    # [보안] Path Traversal 방어 적용
    project_path = validate_project_path(chat_request.project_name)
    log_path = project_path / "main.log"
    context = "로그 없음"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            context = "\n".join(f.read().splitlines()[-30:])

    prompt = f"당신은 AI DevOps 봇입니다.\n[로그]\n{context}\n[질문]\n{chat_request.message}\n\n해결책을 제시해주세요."
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if res.status_code == 200:
            return {"response": res.json()['candidates'][0]['content']['parts'][0]['text']}
        return {"response": f"AI Error: {res.text}"}
    except Exception as e:
        return {"response": f"Network Error: {str(e)}"}
