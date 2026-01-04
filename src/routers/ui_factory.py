# 파일 위치: src/routers/ui_factory.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter(
    prefix="/api/v1/ui-factory",
    tags=["UI Factory (Monetization Core)"]
)

# 1. [상품 정의] 요청 받을 주문서 양식
class UIRequest(BaseModel):
    component_name: str
    spec_content: str
    api_key: str | None = None  # 나중에 유료화 시 여기서 인증 처리

# 2. [핵심 로직] UI 생성 엔진 (여기가 핵심 기술)
# 지금은 룰 기반이지만, 나중엔 LLM(Gemini/GPT)이 붙어서 고가 요금제로 팔리는 구간입니다.
def generate_react_code(name: str, spec: str) -> str:
    # (1) 명세서 파싱 (기초적인 AI 흉내)
    width = "w-full"
    bg_color = "#1A1A1A"
    
    w_match = re.search(r"너비.*(\d+px|full)", spec)
    if w_match: width = f"w-[{w_match.group(1)}]" if "px" in w_match.group(1) else "w-full"
    
    bg_match = re.search(r"배경색.*(#[0-9a-fA-F]+)", spec)
    if bg_match: bg_color = bg_match.group(1)

    # (2) 코드 템플릿 조립
    return f"""'use client';

export default function {name}() {{
  return (
    // [Powered by Monewment UI Factory API]
    // 이 코드는 유료 생성 엔진에 의해 작성되었습니다.
    <div className="{width} h-full bg-[{bg_color}] flex flex-col p-4 border border-[#262626] text-white shadow-xl">
      <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
        <h2 className="text-lg font-bold text-[#FFD700]">{name}</h2>
        <span className="text-xs text-gray-500">Auto-Generated</span>
      </div>
      
      {{/* Dynamic Content Area */}}
      <div className="flex-1 bg-black/20 rounded border border-dashed border-[#404040] flex items-center justify-center">
        <span className="text-sm text-[#808080]">
           UI Factory Area ({width} x {bg_color})
        </span>
      </div>
    </div>
  );
}}
"""

# 3. [판매 창구] API 엔드포인트
@router.post("/generate")
async def generate_ui(request: UIRequest):
    """
    [유료 API] 명세서를 보내면 React 코드를 반환합니다.
    """
    # TODO: 여기서 request.api_key를 검사해서 과금 처리를 합니다.
    print(f"💰 [UI Factory] 주문 접수됨: {request.component_name}")
    
    generated_code = generate_react_code(request.component_name, request.spec_content)
    
    return {
        "status": "success",
        "component_name": request.component_name,
        "code": generated_code,
        "credits_used": 1  # 과금 로그 예시
    }