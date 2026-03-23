from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from uuid import UUID
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = 'PENDING'
    CRAWLED = 'CRAWLED'
    AREUM_PROCESSING = 'AREUM_PROCESSING'   # AREUM이 로컬 AI 분석 중
    AREUM_DONE = 'AREUM_DONE'               # AREUM 분석 완료, REX 전송 대기
    REX_CONSUMED = 'REX_CONSUMED'           # REX가 수신 및 메타 분석 반영 완료
    API_COMPLETED = 'API_COMPLETED'
    FAILED = 'FAILED'

class PipelineTask(BaseModel):
    task_id: str
    stratum_id: str
    target_url: str
    status: TaskStatus
    payload_locator: str | None = None
    cost_cents: float = 0.0
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AreumReport(BaseModel):
    """
    AREUM이 로컬 Ollama 분석 후 schema_pipeline.cross_reports 에 적재하는 데이터.
    REX는 이 객체를 유일한 인풋으로 사용하여 메타 트렌드를 융합한다.
    """
    areum_id: str
    stratum_id: str
    source_asset_id: str | None = None
    ollama_model: str = "gemma3:4b"
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    keywords: list[str] = Field(default_factory=list)
    summary: str
    raw_essence: dict | None = None
    model_config = ConfigDict(from_attributes=True)

class CrossReport(BaseModel):
    """
    schema_pipeline.cross_reports 테이블의 데이터 계약 (REX가 읽는 형식).
    """
    report_id: str
    areum_id: str | None
    stratum_id: str
    source_asset_id: str | None
    confidence_score: float
    keywords: list[str]
    summary: str
    rex_consumed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
