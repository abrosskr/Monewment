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

# 1. 환경 설정
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: API Key가 없습니다.")

genai.configure(api_key=API_KEY)

# FastAPI 앱 생성
app = FastAPI(title="Antigravity API", version="1.0")

# CORS 설정 (나중에 웹 채팅창 붙일 때 필수)
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
# 🧠 [Brain] 라우팅 전략 (ai_agent.py와 동일하게 유지)
# ==========================================
TASK_ROUTING = {
    "ARCHITECT": {
        "keywords": ["알고리즘", "설계", "구조", "분석", "최적화", "비효율", "원인", "복잡", "Architecture", "계획"],
        "models": ["gemini-pro-latest", "gemini-flash-latest"] 
    },
    "DATA_ANALYST": {
        "keywords": ["DB", "데이터", "스키마", "조회", "분석", "로그", "SQL", "Record", "json", "읽어"],
        "models": ["gemini-flash-latest", "gemini-2.0-flash-lite"]
    },
    "CODER": {
        "keywords": ["작성해", "만들어", "코드", "수정", "Next.js", "React", "페이지", "컴포넌트", "UI", "함수"],
        "models": ["gemini-2.0-flash-lite", "gemini-flash-latest"]
    }
}
DEFAULT_MODELS = ["gemini-2.0-flash-lite", "gemini-flash-latest"]

# 요청 데이터 구조 (웹에서 받을 데이터)
class ChatRequest(BaseModel):
    query: str
    project_path: str = "."  # 작업할 프로젝트 경로

# ==========================================
# 🛠️ 도구 정의 (서버용)
# ==========================================
def local_write_file(base_path: str, file_rel_path: str, content: str):
    """
    서버에서는 보안을 위해 base_path(프로젝트 경로) 안에만 파일을 씁니다.
    """
    try:
        # 경로 합치기
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
    return """
    [Table: universal_records]
    - id (BigInt): PK
    - data (JSONB): 실제 데이터
    - created_at, updated_at (Timestamp)
    """

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
# 🚀 API 엔드포인트 (핵심 로직)
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_query = request.query
    project_root = request.project_path
    
    print(f"🚀 [API] 요청 수신: {user_query}")

    # 1. 라우팅 (Intent Detection)
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

    # 3. 모델 실행 및 Failover (ai_agent.py의 로직과 동일)
    current_model_idx = 0
    
    while True:
        model_name = current_models[current_model_idx]
        print(f"🤖 모델 실행: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat()
        
        prompt = f"""
        당신은 Antigravity 수석 개발자입니다.
        현재 작업 경로: {project_root}
        
        [도구]
        {tool_desc}
        
        [요청] {user_query}
        
        [규칙]
        - 도구 사용: {{"tool": "이름", "args": {{...}}}} JSON 포맷.
        - 완료 시: "작업 완료"라고 말하세요.
        """

        try:
            response = await asyncio.to_thread(chat.send_message, prompt)
            answer = response.text.strip()
            
            # 도구 파싱
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
                
                # 결과 반환 (JSON)
                return {
                    "status": "success",
                    "model": model_name,
                    "answer": f"도구 실행: {t_name}",
                    "tool_result": res_text
                }
            
            else:
                # 일반 대화 반환
                return {
                    "status": "success", 
                    "model": model_name,
                    "answer": answer
                }

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota" in error_str:
                print(f"🛑 [한도 초과] {model_name}. 다음 모델로 전환합니다.")
                if current_model_idx < len(current_models) - 1:
                    current_model_idx += 1
                    continue # 다음 모델로 재시도
                else:
                    return {"status": "error", "message": "모든 모델 한도 초과 (잠시 후 다시 시도하세요)"}
            else:
                return {"status": "error", "message": f"API Error: {error_str}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)