import asyncio
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import setup_logger
from src.core.redis_client import RedisManager
from src.dependencies import get_db
from src.models import VMInstance

logger = setup_logger()

async def background_task_saver():
    """
    [Write-Behind] Redis에 쌓인 Heartbeat 정보를 1분마다 DB에 일괄 반영합니다.
    """
    logger.info("💾 Write-Behind Task Started.")
    try:
        while True:
            await asyncio.sleep(60) # 1분 대기
            
            redis = RedisManager.get_instance().get_client()
            if not redis: continue
            
            # Scan keys: ant:heartbeat:{client_id}
            # [Optimized] Use SCAN instead of KEYS to prevent blocking Redis
            
            updates = {} # client_id -> timestamp (str)
            
            async for key in redis.scan_iter("ant:heartbeat:*"):
                ts = await redis.get(key)
                if ts:
                    client_id = key.split(":")[-1] 
                    updates[client_id] = datetime.fromisoformat(ts)
            
            if updates:
                # Bulk Update DB
                # We need a new session context
                session_gen = get_db()
                db = await anext(session_gen)
                try:
                    # Update each VMInstance last_seen
                    for cid, timestamp in updates.items():
                        await db.execute(
                            update(VMInstance)
                            .where(VMInstance.name == cid)
                            .values(last_seen=timestamp)
                        )
                    await db.commit()
                    logger.info(f"💾 Saved {len(updates)} heartbeats to DB.")
                except Exception as e:
                    logger.error(f"Write-Behind Error: {e}")
                    await db.rollback()
                finally:
                    await db.close()

    except asyncio.CancelledError:
        logger.info("💾 Write-Behind Task Cancelled.")
