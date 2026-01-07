import pytest
from src.core.redis_client import RedisManager

@pytest.mark.asyncio
async def test_redis_connection():
    manager = RedisManager.get_instance()
    await manager.connect()
    
    redis = manager.get_client()
    assert redis is not None
    
    # Test specific key
    await redis.set("test_key", "hello_monewment")
    val = await redis.get("test_key")
    assert val == "hello_monewment"
    
    await manager.close()
