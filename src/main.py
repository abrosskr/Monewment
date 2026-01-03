import os
import shutil
import subprocess  # [신규 추가] 외부 파이썬 파일을 실행하기 위해 필요합니다.
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 

# 기존 경로 및 설정 유지 (원본 100% 보존)
from src.config import settings
from src.database import engine
from src.models import Base
from src.logger import setup_logger

# [기존 로직 유지] 라우터 가져오기
from src.routers import tools 

logger = setup_logger()

# [신규 추가] 실행 중인 프로젝트 프로세스들을 관리하는 저장소입니다.
running_processes = {}

# [기존 유지] 설치 기능용 데이터 형식
class InstallRequest(BaseModel):
    project_name: str
    admin_id: str
    password: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 DB 테이블 생성 로직 유지
    logger.info("🚀 Starting up... Creating DB tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ DB Tables created successfully.")
    yield
    # [신규 추가] 서버 종료 시 가동 중인 모든 AI 에이전트도 함께 안전하게 종료합니다.
    for name, proc in running_processes.items():
        proc.terminate()
    logger.info("🛑 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# [연결 설정] Next.js(3000번)와 통신하기 위해 필수입니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [기존 로직 유지] 라우터 등록
app.include_router(tools.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "system": "Monewment Cluster",
        "status": "active",
        "version": "4.1"
    }

# [기존 유지] 설치된 모든 프로젝트 목록을 반환하는 엔드포인트
@app.get("/projects")
async def list_projects():
    projects_dir = "D:\\projects\\Monewment\\projects"
    if not os.path.exists(projects_dir):
        return {"projects": []}
    try:
        folders = [f for f in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, f))]
        logger.info(f"📂 Found {len(folders)} projects in dashboard.")
        return {"projects": folders}
    except Exception as e:
        logger.error(f"❌ Failed to list projects: {str(e)}")
        raise HTTPException(status_code=500, detail="프로젝트 목록을 읽는 중 오류가 발생했습니다.")

# [기존 유지] 프로젝트 템플릿 설치(복사) 엔드포인트
@app.post("/install")
async def install_project(request: InstallRequest):
    base_path = "D:\\projects\\Monewment"
    template_path = os.path.join(base_path, "templates", "standard")
    target_path = os.path.join(base_path, "projects", request.project_name)
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="템플릿 폴더가 없습니다.")
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 이름입니다.")
    try:
        shutil.copytree(template_path, target_path)
        logger.info(f"✨ Project installed: {request.project_name}")
        return {"status": "success", "message": f"프로젝트 '{request.project_name}' 설치 완료!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"복사 실패: {str(e)}")

# [기존 유지] 프로젝트 삭제 기능
@app.delete("/projects/{project_name}")
async def delete_project(project_name: str):
    project_path = os.path.join("D:\\projects\\Monewment\\projects", project_name)
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="삭제할 프로젝트를 찾을 수 없습니다.")
    try:
        shutil.rmtree(project_path)
        logger.info(f"🗑️ Project deleted: {project_name}")
        return {"status": "success", "message": f"'{project_name}' 삭제 완료."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [기존 유지] 로그 파일 읽기 기능
@app.get("/projects/{project_name}/logs")
async def get_project_logs(project_name: str):
    log_path = os.path.join("D:\\projects\\Monewment\\projects", project_name, "main.log")
    if not os.path.exists(log_path):
        return {"logs": "아직 기록된 로그가 없습니다."}
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            return {"logs": "\n".join(content.splitlines()[-100:])}
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그 읽기 오류")

# ---------------------------------------------------------
# [신규 추가] AI 에이전트 가동 및 중지 제어 기능
# ---------------------------------------------------------
@app.post("/projects/{project_name}/start")
async def start_project(project_name: str):
    if project_name in running_processes:
        return {"status": "info", "message": "이미 가동 중입니다."}
    
    project_path = os.path.join("D:\\projects\\Monewment\\projects", project_name)
    main_script = os.path.join(project_path, "main.py")
    
    if not os.path.exists(main_script):
        raise HTTPException(status_code=404, detail="실행할 main.py가 없습니다.")

    # 백그라운드에서 독립적인 파이썬 프로세스로 실행합니다.
    process = subprocess.Popen(["python", "main.py"], cwd=project_path)
    running_processes[project_name] = process
    return {"status": "success", "message": f"'{project_name}' 가동 시작"}

@app.post("/projects/{project_name}/stop")
async def stop_project(project_name: str):
    if project_name not in running_processes:
        return {"status": "info", "message": "현재 가동 중이 아닙니다."}
    
    process = running_processes.pop(project_name)
    process.terminate() # 프로세스 종료 신호 전송
    return {"status": "success", "message": f"'{project_name}' 가동 중지 완료"}