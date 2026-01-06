# 📡 Monewment API Reference

> **Last Updated:** 2026-01-07 00:57:04\n\n> **Base URL:** `http://localhost:8001`\n\n> **Total Endpoints:** 26\n\n---\n\n## 🔐 Authentication\n\nMost endpoints require JWT authentication. Include the token in the Authorization header:\n\n```http\nAuthorization: Bearer <your_jwt_token>\n```\n\n### Obtaining a Token\n\n```http\nPOST /api/auth/login\nContent-Type: application/json\n\n{\n  "email": "user@example.com",\n  "password": "your_password"\n}\n```\n\n---\n\n## 📂 Admin\n\n### `GET /api/admin/schema`\n\n**Description:** [최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다.\n\n**Function:** `get_real_db_schema()`\n\n**Request Example:**\n\n```http\nGET /api/admin/schema HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/endpoints`\n\n**Description:** [신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다.\n\n**Function:** `get_real_api_endpoints()`\n\n**Request Example:**\n\n```http\nGET /api/admin/endpoints HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/stats`\n\n**Description:** Get Admin Stats\n\n**Function:** `get_admin_stats()`\n\n**Request Example:**\n\n```http\nGET /api/admin/stats HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/vms`\n\n**Description:** Get All Vms\n\n**Function:** `get_all_vms()`\n\n**Request Example:**\n\n```http\nGET /api/admin/vms HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/pricing/flavors`\n\n**Description:** Get Flavors\n\n**Function:** `get_flavors()`\n\n**Request Example:**\n\n```http\nGET /api/admin/pricing/flavors HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `PATCH /api/admin/pricing/flavors/{flavor_id}`\n\n**Description:** Update Flavor Rate\n\n**Function:** `update_flavor_rate()`\n\n**Request Example:**\n\n```http\nPATCH /api/admin/pricing/flavors/{flavor_id} HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/hierarchy`\n\n**Description:** Get System Hierarchy\n\n**Function:** `get_system_hierarchy()`\n\n**Request Example:**\n\n```http\nGET /api/admin/hierarchy HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "hierarchy": [
    {
      "id": 1,
      "name": "Seoul-Cluster-1",
      "region": "kr-seoul-1",
      "status": "ACTIVE",
      "organizations": [
        {
          "id": 1,
          "name": "Example Corp",
          "quota_cpu": 20,
          "quota_ram_gb": 64,
          "quota_gpu": 2,
          "projects": [...]
        }
      ]
    }
  ]
}```\n\n---\n\n### `POST /api/admin/clusters`\n\n**Description:** Create Cluster\n\n**Function:** `create_cluster()`\n\n**Request Example:**\n\n```http\nPOST /api/admin/clusters HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{
  "name": "Seoul-Cluster-1",
  "region": "kr-seoul-1",
  "cpu_capacity": 1000,
  "ram_capacity_gb": 4096,
  "gpu_capacity": 64
}```\n\n**Response Example:**\n\n```json\n{
  "message": "Cluster created successfully",
  "cluster": {
    "id": 1,
    "name": "Seoul-Cluster-1",
    "region": "kr-seoul-1",
    "status": "ACTIVE"
  }
}```\n\n---\n\n### `POST /api/admin/organizations/approve`\n\n**Description:** Approve Organization\n\n**Function:** `approve_organization()`\n\n**Request Example:**\n\n```http\nPOST /api/admin/organizations/approve HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{
  "org_id": 1,
  "cluster_id": 1,
  "quota_cpu": 20,
  "quota_ram_gb": 64,
  "quota_gpu": 2
}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/admin/projects/expand`\n\n**Description:** Expand Project Topdown\n\n**Function:** `expand_project_topdown()`\n\n**Request Example:**\n\n```http\nPOST /api/admin/projects/expand HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{
  "org_id": 1,
  "project_name": "MyProject"
}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/admin/env`\n\n**Description:** .env 파일의 원본 내용을 읽어옵니다.\n\n**Function:** `get_env_raw()`\n\n**Request Example:**\n\n```http\nGET /api/admin/env HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/admin/env`\n\n**Description:** .env 파일의 내용을 직접 수정하고 저장합니다.\n\n**Function:** `save_env_raw()`\n\n**Request Example:**\n\n```http\nPOST /api/admin/env HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n## 📂 Authentication\n\n### `POST /api/auth/signup`\n\n**Description:** Signup\n\n**Function:** `signup()`\n\n**Request Example:**\n\n```http\nPOST /api/auth/signup HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\n\n{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name"
}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/auth/login`\n\n**Description:** Login\n\n**Function:** `login()`\n\n**Request Example:**\n\n```http\nPOST /api/auth/login HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\n\n{
  "email": "admin@example.com",
  "password": "secure_password"
}```\n\n**Response Example:**\n\n```json\n{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "role": "ADMIN"
  }
}```\n\n---\n\n### `GET /api/auth/me`\n\n**Description:** Read Users Me\n\n**Function:** `read_users_me()`\n\n**Request Example:**\n\n```http\nGET /api/auth/me HTTP/1.1\nHost: localhost:8001\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n## 📂 General\n\n### `GET /`\n\n**Description:** 시스템 헬스 체크 및 현재 가동 모드를 확인합니다.\n\n**Function:** `read_root()`\n\n**Request Example:**\n\n```http\nGET / HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /api/services/list`\n\n**Description:** 플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다.\n\n**Function:** `get_services_list()`\n\n**Request Example:**\n\n```http\nGET /api/services/list HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/services/keys`\n\n**Description:** Gemini 또는 OpenAI의 API 키를 .env 파일에 안전하게 업데이트합니다.\n\n**Function:** `update_api_key()`\n\n**Request Example:**\n\n```http\nPOST /api/services/keys HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/chat`\n\n**Description:** 실시간 로그를 컨텍스트로 사용하여 AI 에이전트와 대화하고 해결책을 구합니다.\n\n**Function:** `chat_with_agent()`\n\n**Request Example:**\n\n```http\nPOST /api/chat HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /projects`\n\n**Description:** 현재 가동 중인 모든 프로젝트 디렉토리 목록을 반환합니다.\n\n**Function:** `list_projects()`\n\n**Request Example:**\n\n```http\nGET /projects HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `GET /projects/{project_name}/logs`\n\n**Description:** 지정된 프로젝트의 main.log 파일 내용을 읽어옵니다.\n\n**Function:** `get_logs()`\n\n**Request Example:**\n\n```http\nGET /projects/{project_name}/logs HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /projects/{project_name}/start`\n\n**Description:** 지정된 프로젝트의 엔진(main.py)을 독립 프로세스로 실행합니다.\n\n**Function:** `start_project()`\n\n**Request Example:**\n\n```http\nPOST /projects/{project_name}/start HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /projects/{project_name}/stop`\n\n**Description:** 지정된 프로젝트에서 실행 중인 엔진 프로세스를 강제 종료합니다.\n\n**Function:** `stop_project()`\n\n**Request Example:**\n\n```http\nPOST /projects/{project_name}/stop HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /install`\n\n**Description:** [Legacy] 이전 방식의 프로젝트 설치 요청을 새로운 SaaS 로직으로 연결합니다.\n\n**Function:** `install_legacy()`\n\n**Request Example:**\n\n```http\nPOST /install HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n## 📂 Projects\n\n### `GET /api/projects/{project_name}/structure`\n\n**Description:** [신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다.\n\n**Function:** `get_project_tree()`\n\n**Request Example:**\n\n```http\nGET /api/projects/{project_name}/structure HTTP/1.1\nHost: localhost:8001\nAuthorization: Bearer <token>\n```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n### `POST /api/projects/create`\n\n**Description:** Create Project Saas\n\n**Function:** `create_project_saas()`\n\n**Request Example:**\n\n```http\nPOST /api/projects/create HTTP/1.1\nHost: localhost:8001\nContent-Type: application/json\nAuthorization: Bearer <token>\n\n{}```\n\n**Response Example:**\n\n```json\n{
  "message": "Success",
  "data": {}
}```\n\n---\n\n## ⚠️ Error Codes\n\n| Code | Description |\n|------|-------------|\n| 200 | Success |\n| 201 | Created |\n| 400 | Bad Request |\n| 401 | Unauthorized |\n| 403 | Forbidden |\n| 404 | Not Found |\n| 500 | Internal Server Error |\n\n---\n\n*Generated by Monewment Auto-Doc System v4.0*\n