from fastapi import APIRouter
from src.core.devtools.inspector import ProjectInspector
import os

router = APIRouter(prefix="/devtools", tags=["DevTools (Monetization)"])

# 이 API가 나중에 다른 개발자들에게 팔 기능입니다.
@router.get("/analyze/schema")
def get_current_schema():
    """
    [유료 기능] 현재 프로젝트의 DB 스키마를 분석해서 JSON으로 반환합니다.
    """
    root_dir = os.getcwd() # 실제 서비스에선 사용자 프로젝트 경로가 들어감
    inspector = ProjectInspector(root_dir)
    return {"schema": inspector.analyze_db_schema()}
