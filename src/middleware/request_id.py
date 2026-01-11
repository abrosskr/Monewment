"""
요청 추적 ID 미들웨어
모든 HTTP 요청에 고유한 request_id를 부여하여 분산 시스템에서 추적 가능하게 합니다.
"""
import uuid
from fastapi import Request
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    모든 요청에 고유한 request_id를 추가하는 미들웨어
    """
    
    async def dispatch(self, request: Request, call_next):
        # 클라이언트가 제공한 request_id가 있으면 사용, 없으면 생성
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # 요청 상태에 저장
        request.state.request_id = request_id
        
        # structlog 컨텍스트에 바인딩 (모든 로그에 자동 포함)
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 헤더에 request_id 추가
            response.headers["X-Request-ID"] = request_id
            
            # 요청 완료 로그
            logger = structlog.get_logger()
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=None  # 필요시 타이머 추가
            )
            
            return response
            
        finally:
            # 컨텍스트 정리
            structlog.contextvars.clear_contextvars()
