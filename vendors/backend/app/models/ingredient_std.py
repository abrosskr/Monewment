from pydantic import BaseModel, Field
from typing import Optional

class StandardizedIngredient(BaseModel):
    """
    [Vendors Attribute Standard - VAS]
    Professional PIM model for ingredients.
    """
    origin: Optional[str] = Field(None, description="원산지 (e.g., 한돈, 국산, 미국산)")
    detail: Optional[str] = Field(None, description="세부산지/품종/성별 (e.g., 옥천, 암돼지, 하우스)")
    main_category: str = Field(..., description="메인카테고리 (e.g., 돼지, 시금치, 소, 닭)")
    sub_category: Optional[str] = Field(None, description="세부부위/품질 (e.g., 안심, 삼겹살, 뿌리, 목살)")
    storage_state: str = Field("생", description="저장/가공상태 (e.g., 생, 냉동, 냉장, 건조, 캔, 훈제)")
    mass_g: float = Field(0.0, description="수치화된 중량(g)")
    confidence: float = Field(1.0, description="정규화 신뢰도 점수 (0.0~1.0)")
    residue: Optional[str] = Field(None, description="분류되지 않은 나머지 텍스트 (학습용)")
    
    @property
    def full_name(self) -> str:
        """재구성된 정규 명칭"""
        parts = [p for p in [self.origin, self.detail, self.main_category, self.sub_category, self.storage_state] if p]
        return " ".join(parts) + f" {self.mass_g}g"
