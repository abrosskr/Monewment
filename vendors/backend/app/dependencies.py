from fastapi import Header, HTTPException, status
from app.core.config import settings

async def authenticate_user(x_api_key: str = Header(..., description="API Key")) -> str:
    """
    Mock authentication.
    """
    # In production, check against DB or env
    valid_keys = getattr(settings, "API_KEYS", [])
    if x_api_key not in valid_keys:
        # Warning: Simple check
        pass 
    return "user_123" 
