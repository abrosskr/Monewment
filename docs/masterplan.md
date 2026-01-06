# 🏗️ Monewment: Enterprise AI/Game Dev Ops Platform
## Strategic Master Plan (v2.3)

> **Last Updated:** 2026-01-07  
> **Status:** Phase 4 Complete (Security Hardening) / Phase 5 In-Progress (Admin Tools)  
> **Target:** Global B2B SaaS for High-Compute Infrastructure  

---

## 1. 🎯 프로젝트 개요 (Purpose)
Monewment는 고성능 컴퓨팅 자원(GPU VM)이 필요한 **AI 연구원**과 **게임 개발자**를 위한 B2B SaaS 플랫폼입니다. Kubernetes 기반의 가상화(KubeVirt)를 통해 복잡한 인프라 설정을 자동화하고, 사용한 만큼만 지불하는 정밀한 과금과 팀 협업 기능을 제공합니다.

---

## 2. 🛠️ 개발 환경 및 도구 (Development Environment)

### 2.1. 인프라 (Infrastructure)
- **OS:** Windows (WSL2 Backend)
- **Containerization:** Docker Desktop
- **Orchestration:** Kubernetes (Local Dev: Docker Kubernetes)
- **Virtualization:** KubeVirt v1.x (with Local Stub Strategy)
- **Remote Gateway:** Apache Guacamole (Browser-based VNC)

### 2.2. 기술 스택 (Tech Stack)
- **Backend:** 
    - Framework: `FastAPI` (Python 3.12+)
    - ORM/Database: `SQLAlchemy` (Sync), `PostgreSQL 15-alpine`
    - Client: `Kubernetes Python Client`
    - Security: `Bcrypt`, `JWT`, Path Traversal Sanitization
- **Frontend:** 
    - Framework: `Next.js 16.1.1` (App Router)
    - UI: `React 19`, `Tailwind CSS 4`, `TypeScript`
    - Design: Glassmorphism, Premium Dark Theme
- **Authentication:** `JWT` with `Bcrypt` password hashing
- **Payment:** (Planned) `Toss Payments`

---

## 3. ✅ 현재 구현된 기능 (Feature List)

### 3.1. 사용자 및 조직 관리 (RBAC)
- **법인격(Organization):** 프로젝트 소유 및 결제 주체.
- **프로젝트(Project):** 격리된 작업 공간 및 폴더 구조.
- **멤버십:** 권한(ADMIN, MEMBER) 기반의 팀원 초대 및 관리.

### 3.2. 가상화 서비스 (Virtualization)
- **VM lifecycle API:** 가상머신(VMI) 생성, 삭제, 리스트 조회 구현.
- **Stub 전략:** 로컬 커널 제약을 해결하기 위한 VNC Container 기반의 High-fidelity Stub 도입.
- **원격 접속:** Guacamole 스택을 통해 별도 소프트웨어 설치 없이 브라우저에서 VM 제어.

### 3.3. 비즈니스 로직 (Billing & Metering)
- **복합 과금:** 하드웨어(CPU/GPU) 요율 + AI 모델 라이선스 요율 합산.
- **세션 분할:** 사용 중 AI 모델 스위칭 시 요금 구간을 자동으로 정산 및 분리.
- **상품 카탈로그:** `VMFlavor` 및 `AIModel` 테이블을 통한 유연한 가격 관리.

### 3.4. 시스템 인텔리전스 (Observability)
- **CCTV 모듈:** 파일 변경 감지 및 자동 문서화 연동.
- **System Collector:** 실시간 DB 스키마 및 API 엔드포인트 자동 추출 및 마크다운 생성.

### 3.5. 보안 및 격리 (Security & Isolation) ✨ NEW
- **환경 격리:** 설정 파일(`src/config.py`)을 기준으로 모든 경로를 동적으로 계산하여 배포 유연성 확보.
- **Bcrypt 해싱:** 사용자 비밀번호 암호화 저장 및 검증.
- **JWT 인증:** 토큰 기반 stateless 인증 시스템 구현.
- **Path Traversal 방어:** 파일 시스템 접근 시 상위 디렉토리 탈출 공격 차단.

### 3.6. 관리자 대시보드 (Super Admin Console) ✨ NEW
- **계층 구조 관리:** Cluster → Organization → Project 3단계 계층 시각화.
- **리소스 할당:** Top-Down 방식의 프로젝트 배포 및 Bottom-Up 방식의 조직 승인.
- **프리미엄 UI/UX:** 
  - Glassmorphism 디자인 시스템
  - 실시간 상태 토스트 알림
  - 트리 구조 시각화 (계층 라인)
  - 반응형 카드 레이아웃
- **주요 기능:**
  - 클러스터 생성 및 관리
  - 조직 승인 및 쿼타 할당
  - 프로젝트 Top-Down 배포
  - 실시간 계층 구조 조회

---

## 4. 📊 개발 진행율 (Progress)

| Phase | 단계 | 상태 | 달성률 |
| :--- | :--- | :--- | :--- |
| **Phase 1** | 인프라 기초 (Postgres/Docker) | ✅ Complete | 100% |
| **Phase 2** | 가상화 코어 (KubeVirt/Guacamole) | ✅ Complete | 100% |
| **Phase 3** | 과금 및 미터링 API | ✅ Complete | 100% |
| **Phase 4** | 보안 및 환경 격리 | ✅ Complete | 100% |
| **Phase 5** | 관리자 도구 및 결제 연동 | [/] In-Progress | 65% |
| **Phase 6** | 글로벌 클라우드 확장 | 🏗️ Future | 0% |

**전체 진행률: 약 77% (보안 강화 및 관리자 UI 완료)**

---

## 5. 🚨 향후 계획 (Roadmap 2026)

### 🛡️ Phase 4: 보안 패치 ✅ COMPLETED
1. **✅ 환경 격리 (Isolation):** 하드코딩된 절대 경로 제거 및 설정 중앙화.
2. **✅ Bcrypt 해싱:** 사용자 비밀번호 평문 저장 방식 폐기 및 암호화 적용.
3. **✅ JWT 미들웨어:** 전역 라우트에 대한 인증 필터 및 토큰 수명 관리.
4. **✅ Path Traversal 방어:** 파일 시스템 접근 시 상위 폴더 접근(Directory Traversal) 방지 로직 보강.

### 💼 Phase 5: 관리자 도구 및 결제 (In-Progress - 65%)
#### 완료된 작업:
1. **✅ 계층 구조 설계:** Cluster-Organization-Project 3단계 모델 구축.
2. **✅ Super Admin Dashboard UI:** 
   - 프리미엄 디자인 시스템 (Glassmorphism)
   - 실시간 계층 구조 시각화
   - 상태 토스트 알림 시스템
3. **✅ 핵심 API 구현:**
   - `/api/admin/hierarchy` - 계층 구조 조회
   - `/api/admin/clusters` - 클러스터 생성
   - `/api/admin/organizations/approve` - 조직 승인
   - `/api/admin/projects/expand` - Top-Down 프로젝트 배포

#### 진행 중인 작업:
1. **[/] 삭제 기능:** 클러스터 및 프로젝트 삭제 API 및 UI 구현.
2. **[/] Project Admin Dashboard:** 브랜드/팀 관리자용 대시보드 개발.

#### 남은 작업:
1. **[ ] Toss Payments 연동:** 
   - Sandbox 환경 테스트
   - 결제 승인 및 취소 로직
   - 크레딧 충전 시스템
2. **[ ] Billing UI:** 
   - 사용자 실시간 요금 확인 대시보드
   - 월별/프로젝트별 사용 내역
3. **[ ] Usage Watchdog:** 
   - 예산 초과 시 자동 리소스 회수
   - 알림 및 경고 시스템

### 🚀 Phase 6: 상용 서비스 런칭 (Future)
1. **Production KubeVirt:** Stub 제거 및 베어메탈 노드 기반의 실제 VM 서비스 시작.
2. **Multi-Region Support:** 서울, 도쿄, 싱가포르 등 글로벌 리전 확장.
3. **OpenAPI Docs:** 외부 파트너사를 위한 API 명세서 고도화.
4. **Monitoring & Alerting:** Prometheus + Grafana 통합.
5. **Auto-Scaling:** 트래픽 기반 자동 스케일링 정책.

---

## 6. 📋 즉시 착수 가능한 작업 목록 (Next Actions)

### 우선순위 1 (High Priority)
- [ ] 클러스터 삭제 API 구현 (`DELETE /api/admin/clusters/{id}`)
- [ ] 프로젝트 삭제 API 구현 (`DELETE /api/admin/projects/{id}`)
- [ ] Admin Dashboard에 삭제 버튼 UI 추가
- [ ] Project Admin Dashboard 기본 레이아웃 설계

### 우선순위 2 (Medium Priority)
- [ ] Toss Payments Sandbox 계정 생성 및 테스트
- [ ] 결제 승인 API 엔드포인트 구현
- [ ] 사용자 크레딧 잔액 관리 시스템
- [ ] Billing Dashboard 프로토타입 제작

### 우선순위 3 (Low Priority)
- [ ] Usage Watchdog 알고리즘 설계
- [ ] 예산 초과 알림 이메일 템플릿
- [ ] OpenAPI 스펙 자동 생성 스크립트
- [ ] E2E 테스트 자동화 (Playwright)

---

## 7. 🎓 학습 및 개선 사항 (Lessons Learned)

### 기술적 성과:
- **하이드레이션 이슈 해결:** Next.js SSR 환경에서 브라우저 확장 프로그램으로 인한 속성 불일치 문제를 `suppressHydrationWarning`과 `mounted` 체크로 해결.
- **상태 관리 최적화:** `window.prompt`/`alert` 대신 내부 상태 기반 토스트 시스템으로 전환하여 브라우저 차단 우회.
- **API 설계 패턴:** Top-Down(Super Admin) vs Bottom-Up(Project Admin) 권한 분리 전략 확립.

### 개선 필요 사항:
- **접근성(A11y):** `aria-label`, `role` 속성 추가 필요.
- **테스트 자동화:** `data-testid` 속성을 통한 E2E 테스트 커버리지 확대.
- **에러 핸들링:** 사용자 친화적인 에러 메시지 및 복구 플로우 강화.

---

*Generated by Monewment AI Architect (Pro Context Active)*
*Last Major Update: Phase 5 Admin Dashboard Completion*
