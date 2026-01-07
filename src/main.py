import os
import shutil
import subprocess
import re
import json
import requests
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
from datetime import datetime
# [모듈 임포트]
from src.config import settings
from src.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.models import Base, User, Organization, Project, VMInstance, VMFlavor, VMUsage, AIModel, Cluster
from src.core.logger import setup_logger
from src.core.redis_client import RedisManager
from src.core.redis_client import RedisManager
from src.core.protocol import JobRequest, JobResult, JobStatus, JobType
from src.core.scheduler import Scheduler
from src.core.ant_security import AntSecurity
# [수정] ui_factory 라우터 추가
from src.routers import tools, ui_factory 
from src.collector import collector
from src.core.security import hash_password, verify_password, create_access_token, get_current_user, validate_project_path

logger = setup_logger()
logger = setup_logger()
running_processes = {}
background_tasks = {} # To hold references to background tasks
background_tasks = {} # To hold references to background tasks
# active_ant_sockets: dict[str, WebSocket] = {} # REPLACED by SocketManager
scheduler = Scheduler()
scheduler = Scheduler()

async def background_task_saver():
    """
    [Write-Behind] Redis에 쌓인 Heartbeat 정보를 1분마다 DB에 일괄 반영합니다.
    """
    logger.info("💾 Write-Behind Task Started.")
    try:
        while True:
            await asyncio.sleep(60) # 1분 대기
            
            redis = RedisManager.get_instance().get_client()
            if not redis: continue
            
            # Scan keys: ant:heartbeat:{client_id}
            # Note: In production with millions of keys, use SCAN iter. 
            # For 10k connections, keys() is acceptable but SCAN is safer.
            keys = await redis.keys("ant:heartbeat:*")
            if not keys: continue
            
            updates = {} # client_id -> timestamp (str)
            for key in keys:
                ts = await redis.get(key)
                if ts:
                    client_id = key.split(":")[-1] 
                    updates[client_id] = datetime.fromisoformat(ts)
            
            if updates:
                # Bulk Update DB
                # We need a new session context
                session_gen = get_db()
                db = await anext(session_gen)
                try:
                    # Update each VMInstance last_seen
                    # Optimization: Use bulk_update_mappings if possible, but async session requires execute
                    for cid, timestamp in updates.items():
                        # Assuming client_id matches VM Name or ID. 
                        # Ideally Client ID matches VM Name for simplicity here.
                        # If using ID, cast to int.
                        await db.execute(
                            VMInstance.__table__.update()
                            .where(VMInstance.name == cid)
                            .values(last_seen=timestamp)
                        )
                    await db.commit()
                    logger.info(f"💾 Saved {len(updates)} heartbeats to DB.")
                except Exception as e:
                    logger.error(f"Write-Behind Error: {e}")
                    await db.rollback()
                finally:
                    await db.close()

    except asyncio.CancelledError:
        logger.info("💾 Write-Behind Task Cancelled.")


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

class PricingUpdateRequest(BaseModel):
    hourly_rate: float

class ClusterCreateRequest(BaseModel):
    name: str
    region: str = "kr-seoul-1"
    cpu_capacity: int = 100
    ram_capacity_gb: int = 512
    gpu_capacity: int = 8

class OrgApproveRequest(BaseModel):
    org_id: int
    cluster_id: int
    quota_cpu: int
    quota_ram_gb: int
    quota_gpu: int

class ProjectExpandRequest(BaseModel):
    org_id: int
    project_name: str
    # Top-Down 방식이므로 템플릿 선택 등 추가 가능

# [DB 세션 관리] - Moved to dependencies.py
from src.dependencies import get_db

# [수정됨] 동기식 엔진에 맞게 테이블 생성 로직 변경
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up... Checking Database Schema...")
    
    # [변경] Async Engine 사용 테이블 생성
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database Tables Verified (Async Mode).")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # [신규] 수집기에 앱 인스턴스 주입 (API 라우트 스캔을 위해 필수)
    collector.set_app(app)
    logger.info("✅ System Collector Attached.")

    await RedisManager.get_instance().connect()
    logger.info("✅ Redis Connected.")

    # [신규] Write-Behind Task Start
    task = asyncio.create_task(background_task_saver())
    background_tasks["saver"] = task

    yield
    
    # [신규] Cancel Background Task
    if "saver" in background_tasks:
        background_tasks["saver"].cancel()
        try:
            await background_tasks["saver"]
        except asyncio.CancelledError:
            pass


    # [신규] Redis Disconnection
    await RedisManager.get_instance().close()
    logger.info("🛑 Redis Connection Closed.")
    
    for name, proc in running_processes.items():
        proc.terminate()
    logger.info("🛑 Shutting down...")

app = FastAPI(title="Monewment Platform", version="4.8-UIFactory", lifespan=lifespan)

@app.get("/ping")
async def ping():
    print("DEBUG: Ping Request Received")
    return {"status": "pong"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [라우터 등록]
app.include_router(tools.router, prefix=settings.API_V1_STR)
# [신규] UI Factory (자동 코딩 머신) API 등록
app.include_router(ui_factory.router)

# [Legacy DeepSync Endpoint Removed]
# Functionality migrated to src/api/v1/sync/router.py


# [Phase 5-2] Admin Monitoring
# [Phase 5-2] Admin Monitoring (Updated path)
from src.api.v1.admin import monitoring
app.include_router(monitoring.router, prefix="/api/admin/ants", tags=["Admin Monitoring"])

# [Phase 4] VM Management Router
from src.api.v1.endpoints import vm
app.include_router(vm.router, prefix="/api/vm", tags=["Virtual Machines"])

# [Phase 6-2] Modular B2B API Routers
from src.api.v1.sync import router as sync_router
app.include_router(sync_router.router, prefix="/api/v1/sync", tags=["DeepSync (GenAI)"])

from src.api.v1.vault import router as vault_router
app.include_router(vault_router.router, prefix="/api/v1/vault", tags=["DeepVault (Storage)"])

from src.api.v1.render import router as render_router
app.include_router(render_router.router, prefix="/api/v1/render", tags=["DeepRender (Rendering)"])

@app.get("/")
def read_root():
    """시스템 헬스 체크 및 현재 가동 모드를 확인합니다."""
    return {"system": "Monewment Cluster", "status": "active", "mode": "B2B SaaS with UI Factory"}

# =========================================================
# [System Collector APIs] 시스템 정보 자동 수집
# =========================================================
@app.get("/api/admin/schema")
def get_real_db_schema():
    """[최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다."""
    return {"schema": collector.collect_db_schema()}

@app.get("/api/admin/endpoints")
def get_real_api_endpoints():
    """[신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다."""
    return {"endpoints": collector.collect_api_endpoints()}

@app.get("/api/projects/{project_name}/structure")
def get_project_tree(project_name: str):
    """[신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다."""
    return {"structure": collector.collect_project_structure(project_name)}

# ---------------------------------------------------------
# [Admin Dashboard APIs]
# ---------------------------------------------------------
@app.get("/api/admin/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """관리자용 대시보드 통계 정보를 반환합니다."""
    total_users = await db.scalar(select(func.count(User.id)))
    total_projects = await db.scalar(select(func.count(Project.id)))
    active_vms = await db.scalar(select(func.count(VMInstance.id)).where(VMInstance.status == "RUNNING"))
    
    # 총 매출 계산 (단순 합계)
    total_revenue = await db.scalar(select(func.sum(VMUsage.total_cost))) or 0
    
    return {
        "users": total_users,
        "projects": total_projects,
        "active_vms": active_vms,
        "revenue": float(total_revenue)
    }

@app.get("/api/admin/vms")
async def get_all_vms(db: AsyncSession = Depends(get_db)):
    """모든 프로젝트에서 실행 중인 VM 리스트를 반환합니다."""
    result = await db.execute(select(VMInstance))
    vms = result.scalars().all()
    
    result_list = []
    for vm in vms:
        result_list.append({
            "id": vm.id,
            "name": vm.name,
            "status": vm.status,
            "project_id": vm.project_id,
            "flavor": vm.flavor_id,
            "created_at": vm.created_at
        })
    return {"vms": result_list}

@app.get("/api/admin/pricing/flavors")
async def get_flavors(db: AsyncSession = Depends(get_db)):
    """현재 등록된 VM 등급별 시간당 요금을 조회합니다."""
    result = await db.execute(select(VMFlavor))
    flavors = result.scalars().all()
    return {"flavors": [{"id": f.id, "name": f.name, "hourly_rate": float(f.hourly_rate)} for f in flavors]}

@app.patch("/api/admin/pricing/flavors/{flavor_id}")
async def update_flavor_rate(flavor_id: int, req: PricingUpdateRequest, db: AsyncSession = Depends(get_db)):
    """특정 VM 등급의 시간당 요금을 실시간으로 업데이트합니다."""
    result = await db.execute(select(VMFlavor).where(VMFlavor.id == flavor_id))
    flavor = result.scalars().first()
    
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")
    
    flavor.hourly_rate = req.hourly_rate
    await db.commit()
    return {"status": "success", "new_rate": float(flavor.hourly_rate)}

@app.get("/api/admin/hierarchy")
async def get_system_hierarchy(db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 시스템 전체 계층 구조(Cluster -> Org -> Project)를 조회합니다."""
    try:
        stmt = select(Cluster).options(
            selectinload(Cluster.organizations).selectinload(Organization.projects)
        )
        result = await db.execute(stmt)
        clusters = result.scalars().all()
        
        cluster_list = []
        for c in clusters:
            orgs = []
            for org in c.organizations:
                projs = [{"id": p.id, "name": p.name, "status": p.status} for p in org.projects]
                orgs.append({
                    "id": org.id,
                    "name": org.name,
                    "status": org.status,
                    "projects": projs,
                    "quota": {"cpu": org.quota_cpu, "ram": org.quota_ram_gb, "gpu": org.quota_gpu}
                })
            cluster_list.append({
                "id": c.id,
                "name": c.name,
                "region": c.region,
                "status": c.status,
                "organizations": orgs
            })
        return {"hierarchy": cluster_list}
    except Exception as e:
        logger.error(f"Hierarchy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/clusters")
async def create_cluster(req: ClusterCreateRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 새 클러스터를 시스템에 등록합니다."""
    new_cluster = Cluster(
        name=req.name, 
        region=req.region, 
        cpu_capacity=req.cpu_capacity,
        ram_capacity_gb=req.ram_capacity_gb,
        gpu_capacity=req.gpu_capacity
    )
    db.add(new_cluster)
    await db.commit()
    return {"status": "success", "cluster_id": new_cluster.id}

@app.post("/api/admin/organizations/approve")
async def approve_organization(req: OrgApproveRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 입점 신청한 Organization을 승인하고 자원을 할당합니다."""
    result = await db.execute(select(Organization).where(Organization.id == req.org_id))
    org = result.scalars().first()
    
    if not org: raise HTTPException(status_code=404, detail="Org not found")
    
    org.cluster_id = req.cluster_id
    org.quota_cpu = req.quota_cpu
    org.quota_ram_gb = req.quota_ram_gb
    org.quota_gpu = req.quota_gpu
    org.status = "ACTIVE"
    
    await db.commit()
    return {"status": "success"}

@app.post("/api/admin/projects/expand")
async def expand_project_topdown(req: ProjectExpandRequest, db: AsyncSession = Depends(get_db)):
    """[최상위 관리자] 특정 Organization 하위에 프로젝트를 Top-Down 방식으로 직접 배포합니다."""
    # 1. 대상 Org 확인
    result = await db.execute(select(Organization).where(Organization.id == req.org_id))
    org = result.scalars().first()
    
    if not org: raise HTTPException(status_code=404, detail="Organization not found")
    
    # 2. 프로젝트 생성 (보안 검증 포함)
    target_path = validate_project_path(req.project_name)
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 폴더입니다.")
        
    # 물리 폴더 생성
    os.makedirs(target_path, exist_ok=True)
    
    # DB 기록
    new_project = Project(name=req.project_name, org_id=req.org_id, status="ACTIVE")
    db.add(new_project)
    await db.commit()
    
    return {"status": "success", "project_id": new_project.id, "path": str(target_path)}

# =========================================================
# [Scenario 4] 회원가입 및 로그인 (Auth)
# =========================================================
@app.post("/api/auth/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    """새로운 사용자를 등록하고 OWNER 권한을 부여합니다."""
    result = await db.execute(select(User).where(User.email == req.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    hashed = hash_password(req.password)
    new_user = User(email=req.email, hashed_password=hashed, role="OWNER")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id, "message": "가입이 완료되었습니다."}

@app.post("/api/auth/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    print(f"DEBUG: Login Request for {req.email}")
    """이메일과 비밀번호를 검증하고 액세스 권한을 부여합니다."""
    try:
        result = await db.execute(select(User).where(User.email == req.email))
        user = result.scalars().first()
        
        if not user or not verify_password(req.password, user.hashed_password):
            print("DEBUG: Auth Failed")
            raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")
        
        print("DEBUG: Auth Success, Generating Token...")
        # Generate JWT Token
        access_token = create_access_token(data={"sub": user.email})
        print(f"DEBUG: Token Generated: {access_token[:10]}...")
        
        return {
            "status": "success", 
            "user_id": user.id, 
            "name": user.email.split("@")[0], 
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(f"DEBUG: Login Endpoint Error: {e}")
        import traceback
        traceback.print_exc()
        raise e

@app.get("/api/auth/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자의 정보를 반환합니다 (JWT 검증)."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }

# =========================================================
# [Scenario 5] 프로젝트(법인/팀) 생성 및 폴더 배포
# =========================================================
@app.post("/api/projects/create")
async def create_project_saas(req: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    """새로운 프로젝트 엔진을 개설하고 폴더 구조 및 템플릿을 배포합니다."""
    # [보안] Path Traversal 방어 적용
    target_path = validate_project_path(req.project_name)
    template_path = settings.TEMPLATES_DIR
    
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 폴더입니다.")
        
    try:
        # 1. DB: 법인 확인/생성
        result = await db.execute(select(Organization).where(Organization.name == req.organization_name))
        org = result.scalars().first()
        
        if not org:
            org = Organization(name=req.organization_name, plan_type="free")
            db.add(org)
            await db.commit()
            await db.refresh(org)
            
        # 2. DB: 프로젝트 생성
        new_project = Project(name=req.project_name, org_id=org.id, installed_features=["logs"])
        db.add(new_project)
        await db.commit()
        
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
    """플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다."""
    return {
        "installed": [
            {"id": "logs", "name": "실시간 로그 스트리밍", "type": "basic", "status": "active"}
        ],
        "available": [
            {"id": "auto-doc", "name": "AI 자동 문서화", "price": 0, "desc": "DB 구조 및 폴더 트리 자동 분석"},
            {"id": "mcp-bot", "name": "AI 코드 수정 봇", "price": 49000, "desc": "에러 발생 시 AI가 코드를 직접 수정"},
            {"id": "ui-factory", "name": "UI 자동 생성 공장", "price": 59000, "desc": "명세서를 UI 코드로 자동 변환 (SaaS)"}, # [업데이트]
            {"id": "api-analyzer", "name": "API 트래픽 분석기", "price": 29000, "desc": "API 호출량 및 상태 시각화"}
        ]
    }

# =========================================================
# [Phase 4] OTA Update API
# =========================================================
@app.get("/api/client/version")
def get_client_version():
    """Ant Client가 최신 버전인지 확인합니다."""
    # In production, this would read from a release DB or tag
    return {
        "version": "1.0.0", 
        "download_url": "https://download.monewment.com/installer.exe",
        "hash": "sha256:dummy_hash_for_testing_integrity",
        "force_update": False
    }

# =========================================================
# [Scenario 8] API Key 관리
# =========================================================
@app.post("/api/services/keys")
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

# =========================================================
# [AI Brain] 채팅 에이전트
# =========================================================
@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
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
    project_path = validate_project_path(request.project_name)
    log_path = project_path / "main.log"
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
# [Phase 3] Ant Client Connection (WebSocket)
# =========================================================
# =========================================================
# [Phase 3] Ant Client Connection (WebSocket)
# =========================================================
from src.core.socket_manager import SocketManager

@app.websocket("/ws/ant/{client_id}")
async def ant_websocket_endpoint(websocket: WebSocket, client_id: str):
    manager = SocketManager.get_instance()
    await manager.connect(client_id, websocket)
    
    # [Phase 10] Push existing token from Redis if available (Silent Start support)
    try:
        redis = RedisManager.get_instance().get_client()
        token = await redis.get(f"ant:token:{client_id}")
        if token:
            logger.info(f"✨ Pushing cached token to {client_id}")
            await manager.send_message(client_id, json.dumps({"type": "token_sync", "token": token}))
    except Exception as e:
        logger.error(f"Failed to push initial token to {client_id}: {e}")

    # [Security] Initialize Decryptor
    # In production, fetch specific shared key for this client_id from DB/Vault
    # For now, we use the default hardcoded key in AntSecurity (or env var)
    security = AntSecurity() 
    
    try:
        redis = RedisManager.get_instance().get_client()
        while True:
            # Client sends encrypted token: "v1|nonce|ciphertext"
            encrypted_data = await websocket.receive_text()
            
            try:
                payload = security.decrypt_payload(encrypted_data)
                print(f"DEBUG: Decrypted from {client_id}: {payload.get('type')}") # DEBUG

                # 2. Validate Payload
                if payload.get("client_id") != client_id:
                    print(f"DEBUG: Client ID Mismatch") # DEBUG
                    logger.warning(f"⚠️ Security Alert: Client ID Mismatch")
                    await websocket.close(code=4003)
                    return
                    
                msg_type = payload.get("type")
                
                if msg_type == "job_result":
                    data = payload.get("data")
                    print(f"DEBUG: Job Result: {data}") # DEBUG
                    logger.info(f"🎨 Job Completed: {data.get('job_id')} by {client_id}")
                    
                    # [Phase 7] Save Result for UI
                    from src.api.v1.render.router import JobDatabase
                    from src.core.protocol import JobResult
                    
                    try:
                        res = JobResult(**data)
                        JobDatabase.add_result(res)
                    except Exception as e:
                        print(f"DEBUG: JobResult Parse Error: {e}") # DEBUG
                        logger.error(f"Failed to parse JobResult: {e}")
                        
                elif msg_type == "heartbeat":
                    # Update status in Redis
                    status = payload.get("status", "ONLINE")
                    if redis:
                        await redis.set(f"ant:heartbeat:{client_id}", str(datetime.now()), ex=60)
                        print(f"DEBUG: Saved Heartbeat {client_id}") # DEBUG
                        info = {
                            "status": status,
                            "gpu": "RTX_4090", 
                            "last_seen": str(datetime.now())
                        }
                        await redis.set(f"ant:info:{client_id}", json.dumps(info))
                    else:
                        print("DEBUG: Redis is None!") # DEBUG
                        
                elif msg_type == "RELAY":
                    # [Phase 14] NAT Traversal Relay Handler
                    # Format: { "type": "RELAY", "target_id": "...", "payload": "..." }
                    target_id = payload.get("target_id")
                    inner_payload = payload.get("payload") # Encrypted blob or P2P packet
                    
                    if target_id and inner_payload:
                        # Forward to Target
                        # We wrap it back in a "RELAY" envelope so the recipient knows it came via Queen
                        relay_msg = json.dumps({
                           "type": "RELAY",
                           "sender_id": client_id,
                           "payload": inner_payload
                        })
                        
                        sent = await manager.send_message(target_id, relay_msg)
                        if sent:
                            logger.debug(f"📡 Relayed {len(inner_payload)} bytes: {client_id} -> {target_id}")
                        else:
                            logger.warning(f"🚫 Relay Failed: Target {target_id} not connected.")
                            # Optional: Send 'Relay Failed' Ack back to sender

                # For speed, Ack implies 'Received & Verified'
                await websocket.send_text(json.dumps({"type": "ack", "status": "verified"}))
                
            except Exception as e:
                logger.error(f"🔐 Decryption Failed from {client_id}: {e}")
                # Don't close immediately to avoid DoS on simple error, but in high security mode, yes.
                await websocket.send_text(json.dumps({"type": "error", "message": "Encryption Error"}))
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
            
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(client_id)
        try:
            await websocket.close()
        except:
            pass

# =========================================================
# [Legacy / Admin]
# =========================================================
@app.get("/api/admin/env")
async def get_env_raw():
    """.env 파일의 원본 내용을 읽어옵니다."""
    env_path = settings.ENV_FILE_PATH
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f: return {"content": f.read()}
    return {"content": ""}

@app.post("/api/admin/env")
async def save_env_raw(req: EnvUpdateRequest):
    """.env 파일의 내용을 직접 수정하고 저장합니다."""
    with open(settings.ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(req.content)
    return {"status": "success"}

@app.get("/projects")
async def list_projects():
    """현재 가동 중인 모든 프로젝트 디렉토리 목록을 반환합니다."""
    projects_dir = settings.PROJECTS_DIR
    if not os.path.exists(projects_dir): return {"projects": []}
    return {"projects": [f for f in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, f))]}

@app.get("/projects/{project_name}/logs")
async def get_logs(project_name: str):
    """지정된 프로젝트의 main.log 파일 내용을 읽어옵니다."""
    # [보안] Path Traversal 방어 적용
    project_path = validate_project_path(project_name)
    log_path = project_path / "main.log"
    
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f: return {"logs": f.read()}
    return {"logs": ""}

@app.post("/projects/{project_name}/start")
async def start_project(project_name: str):
    """지정된 프로젝트의 엔진(main.py)을 독립 프로세스로 실행합니다."""
    if project_name in running_processes: return {"status": "info", "message": "Already running"}
    
    # [보안] Path Traversal 방어 적용
    project_path = validate_project_path(project_name)
    running_processes[project_name] = subprocess.Popen(["python", "main.py"], cwd=str(project_path))
    return {"status": "success"}

@app.post("/projects/{project_name}/stop")
async def stop_project(project_name: str):
    """지정된 프로젝트에서 실행 중인 엔진 프로세스를 강제 종료합니다."""
    if project_name in running_processes:
        running_processes.pop(project_name).terminate()
        return {"status": "success"}
    return {"status": "info"}

@app.post("/install")
async def install_legacy(req: InstallRequest):
    """[Legacy] 이전 방식의 프로젝트 설치 요청을 새로운 SaaS 로직으로 연결합니다."""
    gen_db = get_db()
    db = await anext(gen_db)
    try:
        return await create_project_saas(CreateProjectRequest(
            user_id=1, project_name=req.project_name, organization_name="LegacyOrg"
        ), db)
    finally:
        await db.close()
