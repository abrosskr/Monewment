import os
import shutil
import subprocess
import re
import json
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
from datetime import datetime
from sqlalchemy.orm import Session

# [모듈 임포트]
from src.config import settings
from src.database import engine, SessionLocal
from src.models import Base, User, Organization, Project
from src.logger import setup_logger
from src.routers import tools
from src.collector import collector # [신규] 시스템 정보 수집기 장착

logger = setup_logger()
running_processes = {}

# --- [DTO: 데이터 전송 객체 정의] ---
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateProjectRequest(BaseModel):
    user_id: int
    project_name: str
    organization_name: str 

class ApiKeyUpdate(BaseModel):
    service_name: str
    api_key: str

class ChatRequest(BaseModel):
    project_name: str
    message: str

class InstallRequest(BaseModel):
    project_name: str
    admin_id: str
    password: str
    organization_id: int = 1
    features: list[str] = ["logs"]
    
class EnvUpdateRequest(BaseModel):
    content: str

# --- [DB 세션 관리] ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# [수정됨] 동기식 엔진에 맞게 테이블 생성 로직 변경
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up... Checking Database Schema...")
    
    # [변경] 비동기(async with) -> 동기식 호출
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database Tables Created (Sync Mode).")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # [신규] 수집기에 앱 인스턴스 주입 (API 라우트 스캔을 위해 필수)
    collector.set_app(app)
    logger.info("✅ System Collector Attached.")

    yield
    
    for name, proc in running_processes.items():
        proc.terminate()
    logger.info("🛑 Shutting down...")

app = FastAPI(title="Monewment Platform", version="4.7-Collector", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"system": "Monewment Cluster", "status": "active", "mode": "B2B SaaS"}

# =========================================================
# [System Collector APIs] 시스템 정보 자동 수집 (신규 추가)
# =========================================================
@app.get("/api/admin/schema")
def get_real_db_schema():
    """[최적화] DB Inspector를 통해 실제 테이블 구조 반환"""
    # 기존 정규식 파싱 로직을 제거하고, 실제 DB 메타데이터를 조회합니다.
    return {"schema": collector.collect_db_schema()}

@app.get("/api/admin/endpoints")
def get_real_api_endpoints():
    """[신규] FastAPI 라우트 실시간 추출 반환"""
    return {"endpoints": collector.collect_api_endpoints()}

@app.get("/api/projects/{project_name}/structure")
def get_project_tree(project_name: str):
    """[신규] 프로젝트 폴더 구조 트리 반환"""
    return {"structure": collector.collect_project_structure(project_name)}

# =========================================================
# [Scenario 4] 회원가입 및 로그인 (Auth)
# =========================================================
@app.post("/api/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    new_user = User(email=req.email, hashed_password=req.password, role="OWNER")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id, "message": "가입이 완료되었습니다."}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email, User.hashed_password == req.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")
    return {"status": "success", "user_id": user.id, "name": user.email.split("@")[0], "token": "access-granted"}

# =========================================================
# [Scenario 5] 프로젝트(법인/팀) 생성 및 폴더 배포
# =========================================================
@app.post("/api/projects/create")
def create_project_saas(req: CreateProjectRequest, db: Session = Depends(get_db)):
    base_path = "D:\\projects\\Monewment"
    target_path = os.path.join(base_path, "projects", req.project_name)
    template_path = os.path.join(base_path, "templates", "standard")
    
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 폴더입니다.")
        
    try:
        # 1. DB: 법인 확인/생성
        org = db.query(Organization).filter(Organization.name == req.organization_name).first()
        if not org:
            org = Organization(name=req.organization_name, plan_type="free")
            db.add(org)
            db.commit()
            db.refresh(org)
            
        # 2. DB: 프로젝트 생성
        new_project = Project(name=req.project_name, org_id=org.id, installed_features=["logs"])
        db.add(new_project)
        db.commit()
        
        # 3. File: 템플릿 복사
        if not os.path.exists(template_path):
             raise HTTPException(status_code=500, detail="Standard 템플릿이 없습니다.")
        shutil.copytree(template_path, target_path)
        
        # 4. File: config.json 생성
        config = {
            "project_id": new_project.id,
            "organization_id": org.id,
            "owner_id": req.user_id,
            "features": ["logs"],
            "created_at": str(datetime.now())
        }
        with open(os.path.join(target_path, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
            
        # 5. File: 로그 초기화
        with open(os.path.join(target_path, "main.log"), "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Project '{req.project_name}' initialized for '{req.organization_name}'.\n")

        return {"status": "success", "message": f"프로젝트 '{req.project_name}'가 성공적으로 개설되었습니다."}
        
    except Exception as e:
        logger.error(f"Create Project Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# [Scenario 6, 7] 서비스 관리
# =========================================================
@app.get("/api/services/list")
def get_services_list():
    return {
        "installed": [
            {"id": "logs", "name": "실시간 로그 스트리밍", "type": "basic", "status": "active"}
        ],
        "available": [
            {"id": "auto-doc", "name": "AI 자동 문서화", "price": 0, "desc": "DB 구조 및 폴더 트리 자동 분석"},
            {"id": "mcp-bot", "name": "AI 코드 수정 봇", "price": 49000, "desc": "에러 발생 시 AI가 코드를 직접 수정"},
            {"id": "api-analyzer", "name": "API 트래픽 분석기", "price": 29000, "desc": "API 호출량 및 상태 시각화"}
        ]
    }

# =========================================================
# [Scenario 8] API Key 관리
# =========================================================
@app.post("/api/services/keys")
def update_api_key(req: ApiKeyUpdate):
    env_path = "D:\\projects\\Monewment\\.env"
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

# =========================================================
# [AI Brain] 채팅 에이전트
# =========================================================
@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    env_path = "D:\\projects\\Monewment\\.env"
    api_key = None
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    
    if not api_key:
        return {"response": "⚠️ API 키가 설정되지 않았습니다. [설정] 탭에서 키를 입력해주세요."}

    log_path = os.path.join("D:\\projects\\Monewment\\projects", request.project_name, "main.log")
    context = "로그 없음"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            context = "\n".join(f.read().splitlines()[-30:])

    prompt = f"당신은 AI DevOps 봇입니다.\n[로그]\n{context}\n[질문]\n{request.message}\n\n해결책을 제시해주세요."
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if res.status_code == 200:
            return {"response": res.json()['candidates'][0]['content']['parts'][0]['text']}
        return {"response": f"AI Error: {res.text}"}
    except Exception as e:
        return {"response": f"Network Error: {str(e)}"}

# =========================================================
# [Legacy / Admin]
# =========================================================
@app.get("/api/admin/env")
async def get_env_raw():
    env_path = "D:\\projects\\Monewment\\.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f: return {"content": f.read()}
    return {"content": ""}

@app.post("/api/admin/env")
async def save_env_raw(req: EnvUpdateRequest):
    with open("D:\\projects\\Monewment\\.env", "w", encoding="utf-8") as f:
        f.write(req.content)
    return {"status": "success"}

@app.get("/projects")
async def list_projects():
    projects_dir = "D:\\projects\\Monewment\\projects"
    if not os.path.exists(projects_dir): return {"projects": []}
    return {"projects": [f for f in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, f))]}

@app.get("/projects/{project_name}/logs")
async def get_logs(project_name: str):
    log_path = os.path.join("D:\\projects\\Monewment\\projects", project_name, "main.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f: return {"logs": f.read()}
    return {"logs": ""}

@app.post("/projects/{project_name}/start")
async def start_project(project_name: str):
    if project_name in running_processes: return {"status": "info", "message": "Already running"}
    path = os.path.join("D:\\projects\\Monewment\\projects", project_name)
    running_processes[project_name] = subprocess.Popen(["python", "main.py"], cwd=path)
    return {"status": "success"}

@app.post("/projects/{project_name}/stop")
async def stop_project(project_name: str):
    if project_name in running_processes:
        running_processes.pop(project_name).terminate()
        return {"status": "success"}
    return {"status": "info"}

@app.post("/install")
async def install_legacy(req: InstallRequest):
    return create_project_saas(CreateProjectRequest(
        user_id=1, project_name=req.project_name, organization_name="LegacyOrg"
    ), next(get_db()))