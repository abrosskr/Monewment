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

    def get_client(self) -> redis.Redis:
        if not self.redis:
            raise ConnectionError("Redis is not initialized. Call connect() first.")
        return self.redis

# Dependency for FastAPI
async def get_redis() -> redis.Redis:
    manager = RedisManager.get_instance()
    try:
        return manager.get_client()
    except ConnectionError:
        # Fallback or auto-connect logic if needed, 
        # but usually connect() is called at startup.
        await manager.connect()
        return manager.get_client()
