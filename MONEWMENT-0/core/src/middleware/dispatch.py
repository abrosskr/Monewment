from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.context import set_tenant_id

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. 헤더 검문: X-Queen-ID
        queen_id = request.headers.get("X-Queen-ID")
        
        # 2. 경로 검문
        if not queen_id:
            path_parts = request.url.path.strip("/").split("/")
            if path_parts and path_parts[0].startswith("q_"):
                queen_id = path_parts[0]
        
        # 3. 추출된 ID를 전역 컨텍스트에 박제
        set_tenant_id(queen_id)
        
        response = await call_next(request)
        return response