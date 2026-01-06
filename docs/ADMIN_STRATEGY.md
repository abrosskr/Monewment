# Monewment: Admin Strategic Roadmap (v2.2+)

## 1. Access Guide
현재 개발 환경 기준으로 다음 주소를 통해 대시보드에 접속할 수 있습니다:
- **URL:** `http://localhost:3000/admin`
- **전제 조건:** 
    - 백엔드 서버(`8001`)가 실행 중이어야 함.
    - 프론트엔드(`3000`)가 실행 중이어야 함.
    - `verify_admin.py`를 통해 API 통신이 확인된 상태.

---

## 2. Admin Management Strategy (관리 전략)

단순 모니터링을 넘어, 상용화를 위해 추가적으로 관리해야 할 4가지 핵심 영역입니다.

### A. 거버넌스 및 사용자 관리 (Governance)
- **RBAC 실무 적용:** 현재 `OWNER` 권한 외에 `SUPPORT`, `ACCOUNTANT` 등 미세 권한 분리.
- **사용자 제재:** 비정상적 트래픽 발생 시 특정 프로젝트 혹은 사용자를 즉시 **차단(Suspension)** 하는 기능.
- **수동 크레딧 할당:** 이벤트나 보상 목적으로 사용자에게 크레딧을 수동으로 넣어주는 기능.

### B. 카탈로그 최적화 (Catalog Management)
- **Dynamic AI Model Provisioning:** 새로운 AI 모델(Llama 3.1, GPT-4o 등)이 출시될 때마다 코딩 없이 대시보드에서 즉시 추가.
- **Spot Instance 운영:** 유휴 자원이 많을 때 할인가를 적용하는 **Spot Pricing** 정책 관리.

### C. 강력한 보안 가드레일 (Advanced Guardrails)
- **Watchdog 정책 설정:** 프로젝트별로 "예산 소진 시 즉시 Kill"할지, "알림만 보낼지"에 대한 세부 정책 관리.
- **실시간 리소스 회수:** 사용하지 않고 켜져만 있는 VM(Idle VM)을 감지하여 관리자가 강제 종료.

### D. 재무 및 가시성 (Financial Intelligence)
- **매출 리포트:** 월간/주간 매출 추이 그래프 및 프로젝트별 매출 기여도 분석.
- **송장(Invoice) 발행:** 법인 사용자를 위한 자동 PDF 인보이스 생성 및 전송 관리.

---

## 3. Next Up: Admin Dash v1.1 주요 작업
- [ ] **사용자 리스트 뷰:** 모든 가입 유저 목록 및 상태 관리.
- [ ] **AI 모델 추가/삭제 UI:** 현재 하드웨어(Flavor)만 가능한 관리를 소프트웨어(AI Model)까지 확장.
- [ ] **수동 결제 승인:** Toss Payments 외에 무통장 입금 등을 처리하기 위한 관리자 승인 프로세스.
