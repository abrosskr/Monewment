import os
from sqlalchemy import inspect as sqlalchemy_inspect
from fastapi.routing import APIRoute
from src.database import engine
from src.config import settings
from src.core.security import validate_project_path

class SystemCollector:
    def __init__(self, app_instance=None):
        self.app = app_instance

    def set_app(self, app):
        """메인 앱 인스턴스 연결 (API 스캔용)"""
        self.app = app

    def collect_db_schema(self):
        """
        [DB 스키마 정밀 분석]
        실제 DB 엔진에 접속하여 테이블과 컬럼의 상세 스펙을 긁어옵니다.
        """
        try:
            inspector = sqlalchemy_inspect(engine)
            schema_info = []
            
            for table_name in inspector.get_table_names():
                columns = []
                for col in inspector.get_columns(table_name):
                    columns.append({
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "primary_key": col.get("primary_key", False)
                    })
                schema_info.append({
                    "table_name": table_name,
                    "columns": columns
                })
            return schema_info
        except Exception as e:
            return [{"error": f"DB 접속 실패: {str(e)}"}]

    def collect_api_endpoints(self):
        """
        [API 라우트 자동 수집]
        FastAPI에 등록된 모든 URL, 메서드, 함수명을 추출합니다.
        """
        if not self.app: return []
        
        api_list = []
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                api_list.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name,
                    "description": route.description or "설명 없음",
                    "tags": route.tags
                })
        return api_list

    def collect_project_structure(self, project_name: str):
        """
        [폴더 구조 트리 매핑]
        특정 프로젝트의 폴더 구조를 재귀적으로 스캔하여 JSON 트리로 반환합니다.
        """
        # [보안] Path Traversal 방어 적용
        root_dir = validate_project_path(project_name)
        if not os.path.exists(root_dir): return {"error": "Project not found", "path": str(root_dir)}

        def scan_dir(path):
            tree = {"name": os.path.basename(path), "type": "folder", "children": []}
            try:
                for entry in os.scandir(path):
                    if entry.is_dir():
                        if entry.name not in ["__pycache__", ".git", ".next", "node_modules"]:
                            tree["children"].append(scan_dir(entry.path))
                    elif entry.is_file():
                        tree["children"].append({"name": entry.name, "type": "file"})
            except PermissionError:
                pass
            return tree

        return scan_dir(root_dir)

# 전역 콜렉터 인스턴스 생성
collector = SystemCollector()
