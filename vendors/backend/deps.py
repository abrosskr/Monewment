from app.core.security import get_api_key
from app.services.fis_service import FisService
from app.services.extractor_service import ExtractorService
from app.services.memory_service import MemoryService
from app.core.config import settings

def get_fis_service() -> FisService:
    return FisService()

def get_extractor_service() -> ExtractorService:
    return ExtractorService()

def get_memory_service() -> MemoryService:
    return MemoryService()

# Export common dependencies
__all__ = [
    "get_api_key",
    "get_fis_service",
    "get_extractor_service",
    "get_memory_service",
    "settings"
]
