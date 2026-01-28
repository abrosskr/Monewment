from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict
from src.dependencies import get_db
from src.services.vcs_service import vcs_service
from src.models import User, Project
from src.core.security import validate_project_path, get_current_user

router = APIRouter()

@router.post("/commit", response_model=Dict)
async def create_commit(
    project_id: int,
    message: str,
    files: List[Dict[str, str]],
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """Create a new commit snapshot for a project."""
    user_id = 1 
    
    try:
        commit_hash = await vcs_service.commit(
            db=db,
            project_id=project_id,
            author_id=user_id,
            message=message,
            files=files
        )
        return {"status": "success", "commit_hash": commit_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback", response_model=Dict)
async def rollback(
    project_id: int = Body(...),
    target_hash: str = Body(...),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """Roll back a project to a specific commit state."""
    user_id = 1
    
    # 1. Resolve Project Path
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # 2. Securely validate and get physical path
        project_root = validate_project_path(project.name)
        
        # 3. Execute Atomic Restore
        await vcs_service.rollback(
            db=db,
            project_id=project_id,
            executor_id=user_id,
            target_hash=target_hash,
            project_root_path=project_root
        )
        return {"status": "success", "message": f"Project restored to {target_hash}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{project_id}", response_model=List[Dict])
async def get_history(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the commit history for a project."""
    return await vcs_service.get_history(db, project_id)

@router.get("/content/{commit_hash}", response_model=List[Dict])
async def get_commit_content(
    commit_hash: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all files and their contents for a specific commit."""
    return await vcs_service.get_commit_content(db, commit_hash)
