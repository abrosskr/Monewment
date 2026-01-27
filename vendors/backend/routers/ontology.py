from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from ..config import settings

router = APIRouter()

@router.get("/ontology", tags=["Ontology"])
async def get_ontology():
    """
    Returns the Single Source of Truth text/json for frontend.
    """
    file_path = settings.ONTOLOGY_FILE_PATH
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Ontology data not found")
    return FileResponse(file_path)
