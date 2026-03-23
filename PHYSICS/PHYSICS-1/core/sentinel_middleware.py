import asyncio
import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.logger import logger

# Redis client import (Adjustable based on core.database spec)
try:
    from core.database import redis_client
except ImportError:
    redis_client = None


class SentinelMiddleware(BaseHTTPMiddleware):
    """
    [Phase 1: Local Sentinel]
    Extreme Fail-Open, Zero-Overhead Circuit Breaker Middleware.
    
    제국 헌법(물리적 방어선) 준수:
    1. Extreme Fail-Open: 모든 Redis I/O는 50ms 하드 타임아웃을 가지며, 실패 시 무시하고 넘어갑니다.
    2. Zero-Overhead: 정상 트래픽(HTTP 200 등)의 요청/응답 사이클에는 외부 I/O 대기시간이 발생하지 않도록 
       로컬 인메모리 캐싱과 백그라운드 태스킹을 활용합니다.
    """

    def __init__(self, app, redis=None, max_errors: int = 10, window_ttl: int = 60, blown_ttl: int = 300):
        super().__init__(app)
        self.redis = redis or redis_client
        self.max_errors = max_errors
        self.window_ttl = window_ttl
        self.blown_ttl = blown_ttl
        
        # [Zero-Overhead] 빠른 판단을 위한 로컬 인메모리 서킷 브레이커 캐시
        self._local_blown_cache = {}

    async def _safe_redis_call(self, coro):
        """[Extreme Fail-Open] 50ms 하드 타임아웃 래퍼"""
        if not self.redis:
            return None
        try:
            return await asyncio.wait_for(coro, timeout=0.05)
        except (asyncio.TimeoutError, Exception) as e:
            # 타임아웃 체제: 에러 로깅을 삼키고 비즈니스 로직(call_next) 보호
            # logger.debug(f"[SENTINEL] Fail-Open triggered: Redis I/O dropped ({e})")
            return None

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        now = time.time()

        # 1. 🚦 Zero-Overhead Local Pre-Check (Redis I/O 없음)
        cache_expiry = self._local_blown_cache.get(path, 0)
        if cache_expiry > now:
            return Response(
                content=json.dumps({"detail": "Circuit Breaker Open: The Imperial Panopticon has blocked this route."}),
                status_code=503,
                media_type="application/json"
            )

        # 2. ⚡ 비즈니스 로직 본연의 처리 (정상일 경우 여기서 끝남)
        try:
            response = await call_next(request)
        except Exception as e:
            # Unhandled Exception도 에러 트리거로 간주
            asyncio.create_task(self._record_error_metrics(path, 500))
            raise e

        # 3. 🛡️ 에러 감지 (백그라운드로 평가하여 응답 지연 0)
        if response.status_code in [409, 500, 502, 503, 504]:
            asyncio.create_task(self._record_error_metrics(path, response.status_code))

        return response

    async def _record_error_metrics(self, path: str, status_code: int):
        """에러 애그리게이션 및 서킷 브레이커 트리거 제어 로직 (백그라운드 비동기)"""
        error_key = f"panopticon:circuit:errors:{path}"
        blown_key = f"panopticon:circuit:blown:{path}"

        # 50ms Hard Timeout Redis I/O
        count = await self._safe_redis_call(self.redis.incr(error_key))
        if count == 1:
            await self._safe_redis_call(self.redis.expire(error_key, self.window_ttl))

        # 차단 임계치 초과 시 서킷 브레이커 발동
        if count and count >= self.max_errors:
            # Redis에 글로벌 블록 (50ms timeout)
            await self._safe_redis_call(self.redis.setex(blown_key, self.blown_ttl, "BLOWN"))
            
            # Local Worker 메모리에 글로벌 블록 동기화 (Zero-Overhead 판단용)
            self._local_blown_cache[path] = time.time() + self.blown_ttl
            logger.critical(f"[SENTINEL] CIRCUIT BLOWN for {path} after {count} consecutive errors.")

            # Incident Aggregation Payload
            incident_payload = {
                "path": path,
                "status_code": str(status_code),
                "timestamp": str(time.time()),
                "trigger": "MAX_ERRORS"
            }
            # Stream에 발행하여 Inquisitor가 볼 수 있도록 전송 (50ms timeout)
            await self._safe_redis_call(
                self.redis.xadd("panopticon:incidents", incident_payload)
            )

