import os
from fastapi import APIRouter, HTTPException
from src.schemas import ApiKeyUpdate
from src.config import settings

router = APIRouter()

@router.get("/list")
def get_services_list():
    """플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다."""
    return {
        "installed": [
            {"id": "logs", "name": "실시간 로그 스트리밍", "type": "basic", "status": "active"}
        ],
        "available": [
            {"id": "auto-doc", "name": "AI 자동 문서화", "price": 0, "desc": "DB 구조 및 폴더 트리 자동 분석"},
            {"id": "mcp-bot", "name": "AI 코드 수정 봇", "price": 49000, "desc": "에러 발생 시 AI가 코드를 직접 수정"},
            {"id": "ui-factory", "name": "UI 자동 생성 공장", "price": 59000, "desc": "명세서를 UI 코드로 자동 변환 (SaaS)"}, 
            {"id": "api-analyzer", "name": "API 트래픽 분석기", "price": 29000, "desc": "API 호출량 및 상태 시각화"}
        ]
    }

@router.post("/keys")
def update_api_key(req: ApiKeyUpdate):
    """Gemini 또는 OpenAI의 API 키를 .env 파일에 안전하게 업데이트합니다."""
    env_path = settings.ENV_FILE_PATH
    target_key = "GEMINI_API_KEY" if req.service_name == "gemini" else "OPENAI_API_KEY"
    
    try:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{target_key}="):
                new_lines.append(f"{target_key}='{req.api_key}'\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"\n{target_key}='{req.api_key}'\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        return {"status": "success", "message": "API Key secure updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
