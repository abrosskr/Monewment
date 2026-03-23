# MONEWMENT-0/core/security.py
import time
from sqlalchemy import text
from .logger import logger

class SystemStatusCache:
    """
    [FORTIFICATION] Global Kill Switch with Caching.
    Prevents repeated DB hits by caching the status for 5 seconds.
    """
    _cached_status: bool = False
    _last_updated: float = 0.0
    _TTL: float = 5.0

    @classmethod
    async def get_status(cls, session_factory) -> bool:
        now = time.time()
        if now - cls._last_updated < cls._TTL:
            return cls._cached_status

        try:
            async with session_factory() as session:
                # Query DB table system_config (column is_emergency_shutdown)
                result = await session.execute(
                    text("SELECT is_emergency_shutdown FROM schema_system.system_config LIMIT 1")
                )
                status = result.scalar()
                # Ensure it's a bool (DB might return None or int)
                status = bool(status) if status is not None else False
                cls._cached_status = status
                cls._last_updated = now
                return status
        except Exception as e:
            logger.error(f"[SECURITY] Critical: Failed to query kill-switch status: {e}")
            # Safety Fallback: Return cached value (Architect preference)
            return cls._cached_status

system_cache = SystemStatusCache()
