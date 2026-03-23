import os
import asyncio
import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import asyncpg
from core.logger import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
_db_pool = None

async def get_fencing_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _db_pool

async def fencing_guard_middleware(request: Request, call_next):
    if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
        return await call_next(request)

    legacy_bypass = request.headers.get("X-Legacy-Bypass")
    if legacy_bypass == "True":
        expiry_date = datetime.datetime(2026, 3, 11, 0, 0, 0, tzinfo=datetime.timezone.utc)
        if datetime.datetime.now(datetime.timezone.utc) > expiry_date:
            return JSONResponse(status_code=401, content={"detail": "Legacy Bypass Expired"})
        logger.warning("LEGACY BYPASS USED")
        return await call_next(request)

    fencing_token = request.headers.get("X-Fencing-Token")
    entity_id = request.headers.get("X-Entity-ID")
    entity_type = request.headers.get("X-Entity-Type")

    if not fencing_token or not entity_id or not entity_type:
        return JSONResponse(status_code=401, content={"detail": "Missing Fencing Headers"})

    try:
        fencing_token = int(fencing_token)
    except ValueError:
        return JSONResponse(status_code=401, content={"detail": "Invalid Fencing Token"})

    try:
        async with asyncio.timeout(2.0):
            cache_key = f"fencing:{entity_type}:{entity_id}"
            cached_token = await redis_client.get(cache_key)

            if cached_token is not None:
                latest_token = int(cached_token)
            else:
                pool = await get_fencing_pool()
                async with pool.acquire() as conn:
                    table_map = {"AREUM": "areums", "QUEEN": "queens", "ANT": "ants"}
                    id_col_map = {"AREUM": "areum_id", "QUEEN": "queen_id", "ANT": "ant_id"}
                    
                    table_name = table_map.get(entity_type)
                    id_col = id_col_map.get(entity_type)
                    
                    if not table_name:
                        return JSONResponse(status_code=401, content={"detail": "Invalid Entity Type"})

                    query = f"SELECT fencing_token FROM schema_registry.{table_name} WHERE {id_col} = $1"
                    row = await conn.fetchrow(query, entity_id)
                    
                    if row:
                        latest_token = row["fencing_token"]
                        await redis_client.setex(cache_key, 60, str(latest_token))
                    else:
                        return JSONResponse(status_code=401, content={"detail": "Entity Not Found"})

            if fencing_token < latest_token:
                return JSONResponse(status_code=409, content={"detail": "Zombie Fencing Detected"})

    except asyncio.TimeoutError:
        return JSONResponse(status_code=503, content={"detail": "Fencing Validation Timeout"})
    except Exception as e:
        return JSONResponse(status_code=503, content={"detail": "Fencing Validation Error"})

    return await call_next(request)
