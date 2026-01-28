# Next Actions: VCS Integration & Visualization

## Phase 7: UI & Visualization (Timeline)
- [ ] **[Frontend]** VCS 타임라인 UI 구현 (`gui/app/...`)
    - 커밋 이력 카드 형 리스트 뷰
    - 커밋별 변경 파일 목록 및 내용(Content) 미리보기
- [ ] **[Backend]** 롤백(Rollback) 실구현
    - 특정 커밋 해시 기반으로 현재 워킹 디렉토리 파일 복원 로직 (`vcs_service.py`)
- [ ] **[Integration]** 사용자 작업(Save) 시 자동 커밋 연동 트리거

## Operational Tasks
- [ ] **[Infrastructure]** PostgreSQL 포트(`5433`) 충돌 해결 및 DB 마이그레이션 (SQLite -> Postgres)
- [ ] **[CI/CD]** VESS Check를 GitHub Actions 단계에 통합하여 환경 드리프트 사전 차단
- [ ] **[Security]** VCS API 권한 검증 미들웨어 활성화

## Production Readiness Checklist (상용화 필구 과제)

> [!IMPORTANT]
> 인프라 탄력성 및 데이터 영속성 확보가 최우선 과제입니다.

### 🔴 High Priority (인프라 및 탄력성)
- [ ] **[Infrastructure] Database Migration (SQLite -> PostgreSQL)**: 
    - 현재의 SQLite 개발 모드를 중단하고, Enterprise급 고가용성 DB(PostgreSQL)로 실데이터 마이그레이션 완성.
- [ ] **[VESS] Automated Healing Protocol**:
    - `vess.ps1`의 `heal` 기능을 실구현하여 환경 불일치 발생 시 원클릭 혹은 자동 복구 체계 구축. (Zero-Drift Enforcement)
- [ ] **[Security] Advanced API Key Caching**:
    - 매 요청마다 발생하는 DB 조회를 방지하기 위해 Redis 캐싱 레이어 도입. (성능 및 보안 가용성 확보)

### 🟡 Medium Priority (보안 및 관측성)
- [ ] **[Security] Granular Rate Limiting (Quota)**:
    - 사용자별, 프로젝트별 리소스 사용량(Quota) 제어 로직을 `AutoDeployer` 및 `VCSService`에 통합.
- [ ] **[Observability] Audit Logging & Identity Tracking**:
    - 시스템의 모든 쓰기(Write) 작업에 대한 행위자(User) 추적 로그 및 감사 이력(Audit Trail) 저장 시스템 구축.
- [ ] **[Security] API 권한 미들웨어 고도화**:
    - 각 엔드포인트별 Role-Based Access Control (RBAC) 적용 및 JWT 검증 로직 강화.

### 🟢 Low Priority (최적화 및 확장성)
- [ ] **[Performance] P2P Node Load Testing**:
    - 다수의 Ant 노드 가동 시 대용량 에셋 전송 병목 현상 측정 및 대역폭 최적화.
- [ ] **[Scale] Cluster Auto-Scaling Logic**:
    - 연산 수요에 따른 클러스터 자원 자동 증설 및 회수 로직 시뮬레이션 및 검증.
