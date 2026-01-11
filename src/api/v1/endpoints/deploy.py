from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.dependencies import get_db
from src.models import DeploymentConfig, ServiceEndpoint, EnvironmentVariable, BuildLog, Project
from src.core.deployer import AutoDeployer, DeploymentResult
from src.core.env_crypto import env_crypto
from src.core.logger import setup_logger

router = APIRouter()
logger = setup_logger()

# --- Request/Response Models ---

class AutoDeployRequest(BaseModel):
    project_id: int
    git_repo: str
    git_branch: str = "main"
    git_token: Optional[str] = None  # Private repo용
    port: int = 8080
    replicas: int = 1
    env_vars: Dict[str, str] = {}

class DeploymentStatusResponse(BaseModel):
    id: int
    project_id: int
    git_repo: str
    git_branch: str
    status: str
    url: Optional[str] = None
    last_deployed_at: Optional[str] = None
    last_commit_sha: Optional[str] = None

class BuildLogResponse(BaseModel):
    id: int
    commit_sha: Optional[str]
    status: str
    logs: str
    started_at: str
    completed_at: Optional[str]

# --- Endpoints ---

@router.post("/auto-deploy", response_model=DeploymentStatusResponse)
async def auto_deploy(req: AutoDeployRequest, db: AsyncSession = Depends(get_db)):
    """
    Git 저장소에서 자동으로 서비스 배포
    
    1. Git 클론
    2. Dockerfile 감지
    3. Docker 이미지 빌드
    4. Kubernetes Deployment 생성
    5. Service/Ingress 생성
    6. 도메인 할당
    """
    # 1. 프로젝트 확인
    result = await db.execute(select(Project).where(Project.id == req.project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 2. 기존 배포 설정 확인
    result = await db.execute(
        select(DeploymentConfig).where(DeploymentConfig.project_id == req.project_id)
    )
    deployment_config = result.scalars().first()
    
    if not deployment_config:
        # 새 배포 설정 생성
        deployment_config = DeploymentConfig(
            project_id=req.project_id,
            git_repo=req.git_repo,
            git_branch=req.git_branch,
            git_token_encrypted=env_crypto.encrypt(req.git_token) if req.git_token else None,
            port=req.port,
            replicas=req.replicas,
            status="BUILDING"
        )
        db.add(deployment_config)
        await db.flush()
    else:
        # 기존 설정 업데이트
        deployment_config.git_repo = req.git_repo
        deployment_config.git_branch = req.git_branch
        if req.git_token:
            deployment_config.git_token_encrypted = env_crypto.encrypt(req.git_token)
        deployment_config.port = req.port
        deployment_config.replicas = req.replicas
        deployment_config.status = "BUILDING"
    
    await db.commit()
    await db.refresh(deployment_config)
    
    # 3. 환경 변수 저장
    for key, value in req.env_vars.items():
        # 기존 환경 변수 확인
        result = await db.execute(
            select(EnvironmentVariable).where(
                EnvironmentVariable.deployment_id == deployment_config.id,
                EnvironmentVariable.key == key
            )
        )
        env_var = result.scalars().first()
        
        if env_var:
            env_var.value_encrypted = env_crypto.encrypt(value)
        else:
            env_var = EnvironmentVariable(
                deployment_id=deployment_config.id,
                key=key,
                value_encrypted=env_crypto.encrypt(value)
            )
            db.add(env_var)
    
    await db.commit()
    
    # 4. 빌드 로그 생성
    build_log = BuildLog(
        deployment_id=deployment_config.id,
        status="BUILDING"
    )
    db.add(build_log)
    await db.commit()
    await db.refresh(build_log)
    
    # 5. 자동 배포 실행
    deployer = AutoDeployer()
    
    # Git 토큰 복호화
    git_token = None
    if deployment_config.git_token_encrypted:
        git_token = env_crypto.decrypt(deployment_config.git_token_encrypted)
    
    # 환경 변수 복호화
    env_vars_decrypted = {}
    for env_var in deployment_config.env_vars:
        env_vars_decrypted[env_var.key] = env_crypto.decrypt(env_var.value_encrypted)
    
    result: DeploymentResult = await deployer.deploy_from_git(
        git_repo=req.git_repo,
        branch=req.git_branch,
        project_name=project.name,
        port=req.port,
        env_vars=env_vars_decrypted,
        git_token=git_token
    )
    
    # 6. 결과 저장
    build_log.status = result.status
    build_log.logs = result.build_logs
    build_log.image_tag = result.image_tag
    build_log.error_message = result.error
    build_log.completed_at = datetime.now(timezone.utc)
    
    deployment_config.status = "DEPLOYED" if result.status == "SUCCESS" else "FAILED"
    deployment_config.last_deployed_at = datetime.now(timezone.utc)
    
    # 7. 서비스 엔드포인트 생성/업데이트
    if result.status == "SUCCESS":
        result_endpoint = await db.execute(
            select(ServiceEndpoint).where(ServiceEndpoint.deployment_id == deployment_config.id)
        )
        endpoint = result_endpoint.scalars().first()
        
        if not endpoint:
            endpoint = ServiceEndpoint(
                deployment_id=deployment_config.id,
                internal_port=req.port,
                subdomain=f"{project.name}.monewment.io",
                status="ACTIVE",
                url=result.url
            )
            db.add(endpoint)
        else:
            endpoint.status = "ACTIVE"
            endpoint.url = result.url
    
    await db.commit()
    await db.refresh(deployment_config)
    
    logger.info("deployment_completed", 
        project_id=req.project_id,
        status=result.status,
        url=result.url
    )
    
    return DeploymentStatusResponse(
        id=deployment_config.id,
        project_id=deployment_config.project_id,
        git_repo=deployment_config.git_repo,
        git_branch=deployment_config.git_branch,
        status=deployment_config.status,
        url=result.url,
        last_deployed_at=deployment_config.last_deployed_at.isoformat() if deployment_config.last_deployed_at else None,
        last_commit_sha=deployment_config.last_commit_sha
    )

@router.get("/deployments/{project_id}", response_model=DeploymentStatusResponse)
async def get_deployment_status(project_id: int, db: AsyncSession = Depends(get_db)):
    """배포 상태 조회"""
    result = await db.execute(
        select(DeploymentConfig).where(DeploymentConfig.project_id == project_id)
    )
    deployment = result.scalars().first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # URL 조회
    url = None
    result_endpoint = await db.execute(
        select(ServiceEndpoint).where(ServiceEndpoint.deployment_id == deployment.id)
    )
    endpoint = result_endpoint.scalars().first()
    if endpoint:
        url = endpoint.url
    
    return DeploymentStatusResponse(
        id=deployment.id,
        project_id=deployment.project_id,
        git_repo=deployment.git_repo,
        git_branch=deployment.git_branch,
        status=deployment.status,
        url=url,
        last_deployed_at=deployment.last_deployed_at.isoformat() if deployment.last_deployed_at else None,
        last_commit_sha=deployment.last_commit_sha
    )

@router.get("/deployments/{project_id}/logs", response_model=List[BuildLogResponse])
async def get_build_logs(project_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """빌드 로그 조회"""
    # 배포 설정 확인
    result = await db.execute(
        select(DeploymentConfig).where(DeploymentConfig.project_id == project_id)
    )
    deployment = result.scalars().first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # 빌드 로그 조회
    result = await db.execute(
        select(BuildLog)
        .where(BuildLog.deployment_id == deployment.id)
        .order_by(desc(BuildLog.started_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return [
        BuildLogResponse(
            id=log.id,
            commit_sha=log.commit_sha,
            status=log.status,
            logs=log.logs or "",
            started_at=log.started_at.isoformat(),
            completed_at=log.completed_at.isoformat() if log.completed_at else None
        )
        for log in logs
    ]

@router.delete("/deployments/{project_id}")
async def delete_deployment(project_id: int, db: AsyncSession = Depends(get_db)):
    """배포 삭제"""
    result = await db.execute(
        select(DeploymentConfig).where(DeploymentConfig.project_id == project_id)
    )
    deployment = result.scalars().first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Kubernetes 리소스 삭제 (Stub)
    logger.info("deployment_delete", project_id=project_id, mode="STUB")
    
    # DB에서 삭제
    await db.delete(deployment)
    await db.commit()
    
    return {"status": "success", "message": f"Deployment for project {project_id} deleted"}
