# 📡 Communication & API Specification


## 📄 Router: `devtools.py`
- `[GET]` **/analyze/schema**
  - **기능: [유료 기능] 현재 프로젝트의 DB 스키마를 분석해서 JSON으로 반환합니다.**
  - Handler: `get_current_schema`
  - Params (Protocol): (No params)

## 📄 Router: `tools.py`
- `[POST]` **/generate-tree**
  - **기능: 파일 경로 리스트를 받아서 마크다운 트리로 변환**
  - Handler: `generate_tree_api`
  - Params (Protocol): file_paths


## 📄 Core: `main.py`
- `[GET]` **/**
  - **기능: 시스템 헬스 체크 및 현재 가동 모드를 확인합니다.**
  - Handler: `read_root`
  - Params (Protocol): (No params)
- `[GET]` **/api/admin/schema**
  - **기능: [최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다.**
  - Handler: `get_real_db_schema`
  - Params (Protocol): (No params)
- `[GET]` **/api/admin/endpoints**
  - **기능: [신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다.**
  - Handler: `get_real_api_endpoints`
  - Params (Protocol): (No params)
- `[GET]` **/api/projects/{project_name}/structure**
  - **기능: [신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다.**
  - Handler: `get_project_tree`
  - Params (Protocol): project_name
- `[POST]` **/api/auth/signup**
  - **기능: 새로운 사용자를 등록하고 OWNER 권한을 부여합니다.**
  - Handler: `signup`
  - Params (Protocol): req, db
- `[POST]` **/api/auth/login**
  - **기능: 이메일과 비밀번호를 검증하고 액세스 권한을 부여합니다.**
  - Handler: `login`
  - Params (Protocol): req, db
- `[POST]` **/api/projects/create**
  - **기능: 새로운 프로젝트 엔진을 개설하고 폴더 구조 및 템플릿을 배포합니다.**
  - Handler: `create_project_saas`
  - Params (Protocol): req, db
- `[GET]` **/api/services/list**
  - **기능: 플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다.**
  - Handler: `get_services_list`
  - Params (Protocol): (No params)
- `[POST]` **/api/services/keys**
  - **기능: Gemini 또는 OpenAI의 API 키를 .env 파일에 안전하게 업데이트합니다.**
  - Handler: `update_api_key`
  - Params (Protocol): req