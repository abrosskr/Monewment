from fastapi import APIRouter, Depends, UploadFile, File
from typing import Dict
from src.core.security import get_api_key_user
from src.models import User

router = APIRouter()

# Router for DeepVault (Storage)
# The actual logic is distributed across 'manager' (Control Plane) and 'tracker' (P2P Plane).


# Include Tracker API
from src.api.v1.vault import tracker
router.include_router(tracker.router, tags=["DeepVault P2P Tracker"])

# Include Manager API
from src.api.v1.vault import manager
router.include_router(manager.router, tags=["DeepVault Manager"])
