import redis.asyncio as redis
from typing import Optional
from src.config import settings

class RedisManager:
    _instance: Optional['RedisManager'] = None
    
    def __init__(self):
        self.redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        self.redis: Optional[redis.Redis] = None

    @classmethod
    def get_instance(cls) -> 'RedisManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def connect(self):
        if not self.redis:
            self.redis = redis.from_url(
                self.redis_url, 
                encoding="utf-8", 
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    def get_client(self) -> Optional[redis.Redis]:
        """
        Redis 클라이언트 반환. 연결되지 않은 경우 None 반환.
        """
        if not self.redis:
            from src.core.logger import setup_logger
            logger = setup_logger()
            logger.warning("Redis not connected. Some features may be unavailable.")
            return None
        return self.redis


# Dependency for FastAPI
async def get_redis() -> Optional[redis.Redis]:
    """FastAPI 의존성으로 사용. Redis 연결 실패 시 None 반환."""
    manager = RedisManager.get_instance()
    return manager.get_client()

