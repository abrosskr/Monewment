import os
import uvicorn
import asyncio
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from mcp import ClientSession
from mcp.client.sse import sse_client
from fastapi.middleware.cors import CORSMiddleware
import sys

# [기반 설정] 
# 한글 출력은 실행 시 환경변수($env:PYTHONIOENCODING="utf-8")를 통해 해결합니다.
# 시스템 충돌을 방지하기 위해 sys.stdout.detach 관련 코드는 포함하지 않았습니다.

# 1. 환경 설정
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: API Key가 없습니다.")

genai.configure(api_key=API_KEY)

# FastAPI 앱 생성
app = FastAPI(title="Monewment API", version="Final-Integrated-Failover")

# 웹 브라우저 접속 허용 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP 서버 주소
MCP_SERVER_URL = "http://localhost:8080/sse"

# ==========================================
# 🧠 [Brain] 지능형 라우팅 및 자동 스위칭 전략
# ==========================================
# 해선님의 비전: 최신 모델 우선 시도 -> 실패 시 안정적 모델로 자동 전환
# [정정 사항] 실제 호출 가능한 정확한 모델명으로 업데이트하여 Failover가 실질적으로 작동하게 함
TASK_ROUTING = {
    "ARCHITECT": {
        "keywords": ["알고리즘", "설계", "구조", "분석", "최적화", "비효율", "원인", "복잡", "Architecture", "계획"],
        "models": ["gemini-2.0-pro-exp-02-05", "gemini-1.5-pro", "gemini-1.5-flash"] 
    },
    "DATA_ANALYST": {
        "keywords": ["DB", "데이터", "스키마", "조회", "분석", "로그", "SQL", "Record", "json", "읽어"],
        "models": ["gemini-2.0-flash-thinking-exp-01-21", "gemini-1.5-pro", "gemini-1.5-flash"]
    },
    "CODER": {
        "keywords": ["작성해", "만들어", "코드", "수정", "Next.js", "React", "페이지", "컴포넌트", "UI", "함수"],
        "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"]
    }
}
# 기본 모델 (일반 대화용)
DEFAULT_MODELS = ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"]

# [표준] 요청 데이터 구조
class ChatRequest(BaseModel):
    query: str
    project_path: str = "."  # 작업할 대상 프로젝트 경로

# ==========================================
# 🛠️ 도구 정의 (기존 로직 유지)
# ==========================================
def local_write_file(base_path: str, file_rel_path: str, content: str):
    try:
        full_path = os.path.join(base_path, file_rel_path)
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 파일 작성 완료: {full_path}"
    except Exception as e:
        return f"❌ 파일 작성 실패: {str(e)}"

def local_get_db_schema():
    return """[Table: universal_records] (id, data(JSONB), created_at, updated_at)"""

async def fetch_remote_tools_desc():
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools
    except:
        return []

async def execute_remote_tool(tool_name, tool_args):
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=tool_args)
                return result.content[0].text if result.content else "성공"
    except Exception as e:
        return f"Error: {e}"

# ==========================================
# 🚀 API 엔드포인트 (지능형 Failover 엔진)
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_query = request.query
    project_root = request.project_path
    
    print(f"🚀 [API] 요청 수신: {user_query} (Path: {project_root})")

    # 1. 라우팅 (의도 파악)
    current_models = DEFAULT_MODELS
    query_lower = user_query.lower()
    for task, info in TASK_ROUTING.items():
        for kw in info["keywords"]:
            if kw in query_lower:
                print(f"🎯 [라우터] {task} 팀 투입")
                current_models = info["models"]
                break

    # 2. 도구 준비
    remote_tools = await fetch_remote_tools_desc()
    remote_names = {t.name for t in remote_tools}
    tool_desc = "\n".join([f"- [Remote] {t.name}" for t in remote_tools])
    tool_desc += "\n- [Local] write_file: 파일 작성 (args: file_path, content)"
    tool_desc += "\n- [Local] get_db_schema: DB 조회"

    # 3. 모델 실행 및 Failover (핵심 지능)
    current_model_idx = 0
    while True:
        model_name = current_models[current_model_idx]
        print(f"🤖 [엔진] 모델 투입: {model_name}")
        
        try:
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat()
            
            prompt = f"""
            당신은 Monewment 수석 개발자입니다. 작업 경로: {project_root}
            [도구] {tool_desc}
            [요청] {user_query}
            [규칙] 
            1. 파일 작성 시 경로는 상대경로(예: src/test.txt) 사용.
            2. 도구 사용: {{"tool": "이름", "args": {{...}}}} JSON 포맷.
            3. 완료 시: "작업 완료" 텍스트 포함.
            """

            response = await asyncio.to_thread(chat.send_message, prompt)
            answer = response.text.strip()
            
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match and "tool" in answer:
                tool_req = json.loads(json_match.group())
                t_name = tool_req["tool"]
                t_args = tool_req.get("args", {})
                
                res_text = ""
                if t_name == "write_file":
                    res_text = local_write_file(project_root, t_args.get("file_path"), t_args.get("content"))
                elif t_name == "get_db_schema":
                    res_text = local_get_db_schema()
                elif t_name in remote_names:
                    res_text = await execute_remote_tool(t_name, t_args)
                else:
                    res_text = "알 수 없는 도구"
                
                return {
                    "status": "success",
                    "model": model_name,
                    "answer": f"도구 실행됨: {t_name}",
                    "tool_result": res_text
                }
            else:
                return {"status": "success", "model": model_name, "answer": answer}

        except Exception as e:
            error_str = str(e).lower()
            print(f"🛑 [오류 감지] {model_name} 실패: {error_str[:50]}...")
            
            # 모델 없음(404), 한도 초과(429) 등의 경우 다음 모델로 즉시 스위칭
            if "429" in error_str or "quota" in error_str or "404" in error_str or "not found" in error_str:
                if current_model_idx < len(current_models) - 1:
                    print(f"🔄 [자동 전환] 다음 순위 모델({current_models[current_model_idx + 1]})로 작업을 위임합니다.")
                    current_model_idx += 1
                    continue 
                else:
                    return {"status": "error", "message": "모든 가용 모델이 실패했습니다."}
            else:
                return {"status": "error", "message": f"API Error: {error_str}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)