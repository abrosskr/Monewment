import sys
import re
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header
from src.core.config import settings
from src.middleware.dispatch import TenantMiddleware
from src.core.context import get_tenant_id
from src.core.provisioner import Provisioner
from src.core.migrator import GlobalMigrator
from src.core.onboarder import TenantOnboarder # 입주 엔진 임포트

# [1] 마스킹 시스템 (로그 보안 강화)
class MaskedStream:
    def __init__(self, original_stream):
        self.original_stream = original_stream
    def mask_text(self, text):
        if not isinstance(text, str): return text
        text = re.sub(r"(://[^:]+):(.+)(@)", r"\1:****\3", text)
        text = re.sub(r'(?i)(password|pwd|secret|token|api_key|key)["\s:]+=[ "\']?([^ "\',}]+)[ "\']?', r'\1=****', text)
        return text
    def write(self, data):
        self.original_stream.write(self.mask_text(data))
    def flush(self):
        self.original_stream.flush()
    def __getattr__(self, name):
        return getattr(self.original_stream, name)

sys.stdout = MaskedStream(sys.stdout)
sys.stderr = MaskedStream(sys.stderr)

# [2] 앱 초기화
app = FastAPI(title=settings.PROJECT_NAME)

# [3] 글로벌 미들웨어 등록
app.add_middleware(TenantMiddleware)

# [4] 데이터 규격 (입주용)
class BulkOnboardRequest(BaseModel):
    queen_id: str
    members: List[Dict[str, Optional[str]]]

# [5] 모듈형 라우터 조립
from src.rooms.members.router import router as members_router
app.include_router(members_router)

# [6] 엔드포인트: 공통 인프라 및 관리
@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "Monewment V3 Modular"}

@app.get("/test-tenant")
def test_tenant(x_queen_id: str = Header(..., alias="X-Queen-ID")):
    """컨텍스트에 테넌트 ID가 정상적으로 주입되었는지 확인합니다."""
    return {"current_queen_id": get_tenant_id()}

@app.post("/admin/provision/{queen_id}", tags=["Admin"])
async def provision_queen_room(queen_id: str):
    """새로운 테넌트 영토(Schema)와 전용 권한(Role)을 생성합니다."""
    await Provisioner.provision_queen_room(queen_id)
    return {"status": "success", "room": queen_id}

# [7] Global Migration Protocol (GMP)
@app.post("/admin/migrate/ensure-latest", tags=["Admin"])
async def migrate_ensure_latest():
    """모든 테넌트의 방을 스캔하여 최신 버전(V1, V2...)으로 일괄 진화시킵니다."""
    report = await GlobalMigrator.upgrade_all()
    return {
        "status": "Global Migration Protocol Executed",
        "timestamp": "2026-02-19T22:30:00Z",
        "report": report
    }

# [8] Tenant Onboarding System (입주 자동화)
@app.post("/admin/onboard", tags=["Admin"])
async def onboard_new_tenant(payload: BulkOnboardRequest):
    """
    [내일 실전용] 새로운 테넌트 입주 시스템
    - 방 생성 -> 최신 스키마 적용 -> 대량 데이터 적재를 원클릭으로 처리합니다.
    """
    result = await TenantOnboarder.onboard_tenant(payload.queen_id, payload.members)
    return {
        "status": "Onboarding Process Completed",
        "queen_id": payload.queen_id,
        "details": result
    }