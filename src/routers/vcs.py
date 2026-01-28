from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from src.dependencies import get_db
from src.services.vcs_service import vcs_service
from src.models import User
from src.core.security import get_current_user # Assuming this exists based on common pattern

router = APIRouter()

@router.post("/commit", response_model=Dict)
async def create_commit(
    project_id: int,
    message: str,
    files: List[Dict[str, str]],
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Disabled security for now for easier testing, but can be enabled later
):
    """Create a new commit snapshot for a project."""
    # Dummy user_id if security is disabled
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
