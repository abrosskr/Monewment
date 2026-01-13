import os
import shutil
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.dependencies import get_db
from src.models import Organization, Project
from src.schemas import CreateProjectRequest
from src.core.security import validate_project_path
from src.core.logger import setup_logger
from src.collector import collector

logger = setup_logger()
router = APIRouter()

@router.get("/{project_name}/structure")
def get_project_tree(project_name: str):
    """[신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다."""
    return {"structure": collector.collect_project_structure(project_name)}

@router.post("/create")
async def create_project_saas(req: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    """새로운 프로젝트 엔진을 개설하고 폴더 구조 및 템플릿을 배포합니다."""
    # [보안] Path Traversal 방어 적용
    target_path = validate_project_path(req.project_name)
    template_path = settings.TEMPLATES_DIR
    
    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="이미 존재하는 프로젝트 폴더입니다.")
        
    try:
        # [Phase 3] 트랜잭션 개선: 파일 작업 먼저 수행
        # 1. 템플릿 검증
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="Standard 템플릿이 없습니다.")
        
        # 2. DB: 법인 확인/생성
        result = await db.execute(select(Organization).where(Organization.name == req.organization_name))
        org = result.scalars().first()
        
        if not org:
            org = Organization(name=req.organization_name, plan_type="free")
            db.add(org)
            await db.flush()  # ID 생성을 위해 flush (commit 아님)
            
        # 3. 프로젝트 객체 생성 (아직 커밋 안 함)
        new_project = Project(name=req.project_name, org_id=org.id, installed_features=["logs"])
        db.add(new_project)
        await db.flush()  # ID 생성
        
        # 4. File: 템플릿 복사 (실패 가능성이 높은 작업)
        try:
            shutil.copytree(template_path, target_path)
        except Exception as file_error:
            # 파일 작업 실패 시 DB 롤백
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"파일 복사 실패: {str(file_error)}")
        
        # 5. File: config.json 생성
        try:
            config = {
                "project_id": new_project.id,
                "organization_id": org.id,
                "owner_id": req.user_id,
                "features": ["logs"],
                "created_at": str(datetime.now())
            }
            with open(os.path.join(target_path, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as config_error:
            # config.json 생성 실패 시 폴더 삭제 및 DB 롤백
            shutil.rmtree(target_path, ignore_errors=True)
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"설정 파일 생성 실패: {str(config_error)}")
            
        # 6. File: 로그 초기화
        try:
            with open(os.path.join(target_path, "main.log"), "w", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Project '{req.project_name}' initialized for '{req.organization_name}'.\n")
        except Exception as log_error:
            # 로그 파일 실패는 치명적이지 않으므로 경고만
            logger.warning(f"로그 파일 초기화 실패: {log_error}")
        
        # 7. 모든 파일 작업 성공 시 DB 커밋
        await db.commit()

        return {"status": "success", "message": f"프로젝트 '{req.project_name}'가 성공적으로 개설되었습니다."}
        
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except Exception as e:
        # 예상치 못한 에러 발생 시
        logger.error(f"Create Project Error: {str(e)}")
        
        # 생성된 폴더가 있다면 삭제
        if os.path.exists(target_path):
            try:
                shutil.rmtree(target_path)
            except Exception as cleanup_error:
                logger.error(f"폴더 정리 실패: {cleanup_error}")
        
        # DB 롤백
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
