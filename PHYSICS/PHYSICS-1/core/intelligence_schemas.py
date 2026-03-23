from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

# [내부 지능] AREUM 추출 규격 (현장 감각)
class Essence(BaseModel):
    """AREUM이 추출하는 도메인별 핵심 정보 (Sensory Unit)"""
    target_subject: str = Field(..., description="분석 대상의 핵심 주제")
    sentiment_score: float = Field(..., description="정서적 상태 (-1.0 to 1.0)")
    key_facts: List[str] = Field(..., description="도메인 특화 핵심 사실 리스트")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="위험 수준")
    confidence: float = Field(..., description="분석 신뢰도")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="원본 데이터 참조 및 추가 메타데이터")

# [외부 지능] QUEEN-ORACLE 중재 규격 (외교 및 라우팅)
class AIRequest(BaseModel):
    """QUEEN-ORACLE에 전달되는 지능 요청 (Governor Unit)"""
    stratum_id: str = Field(..., description="요청 영토 UUID")
    intent: Literal["SEARCH", "IMAGE", "REASONING", "SIMPLE"] = Field(..., description="요청 의도")
    user_context: Dict[str, Any] = Field(default_factory=dict, description="사용자 Key 및 컨텍스트")
    payload: Dict[str, Any] = Field(..., description="데이터 본문")

class AIUsage(BaseModel):
    """지능 사용량 및 비용 추적 규격 (Registry)"""
    stratum_id: str
    model_name: str
    tokens_used: int
    estimated_cost: float # 사용자가 지출한 비용 추정치

class GlobalStrategy(BaseModel):
    """REX가 수립하는 제국 전체 전략 (Cortex Unit)"""
    strategic_directive: str = Field(..., description="전략적 지시사항")
    focus_sector: str = Field(..., description="집중 관리 분야")
    current_trend: Optional[str] = Field(None, description="현재 트렌드")
    anomalies: List[str] = Field(default_factory=list, description="이상 징후")
    correlations: List[str] = Field(default_factory=list, description="교차 도메인 상관관계")
    source_ref_ids: List[str] = Field(default_factory=list, description="합성에 사용된 원천 보고서 ID 리스트")
