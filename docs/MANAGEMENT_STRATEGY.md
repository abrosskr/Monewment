# Monewment: Management & Resource Strategy

## 1. Governance Hierarchy (관리 계층 구조)

Monewment 플랫폼은 **"Top-Down 확장"**과 **"Bottom-Up 승인"**이 공존하는 구조로 운영됩니다.

### Tier 1: Super Admin (Monewment)
- **대상:** 최상위 운영자
- **권한:**
    - **통합 클러스터 관리:** K8s 클러스터 리소스를 물리적으로 할당 및 회수.
    - **Organization 생성/승인:** 외부 기업(법인/브랜드)의 입점을 최종 승인.
    - **Top-Down 프로젝트 생성:** 특정 테넌트(예: PCroom, RND)를 동일 레벨의 프로젝트로 직접 배포.
    - **글로벌 가격 통제:** 전체 서비스의 Base Rate 결정.

### Tier 2: Project/Org Admin (Brand/Team)
- **대상:** 입점 기업 및 개별 팀 관리자
- **권한:**
    - **프로젝트 내부 자원 관리:** 할당된 쿼타(Quota) 내에서 VM 생성 및 삭제.
    - **멤버 권한 관리:** 팀원(Member) 초대 및 접근 제어.
    - **프로젝트별 빌링 리포트:** 자신들이 사용한 자원에 대한 정산 정보 확인.

---

## 2. Resource Allocation Strategy (스펙 할당 전략)

가상 공간의 가치는 할당된 **"컴퓨팅 파워"**에 의해 결정됩니다.

### [Strategy A] Tiered Resource Profiles (등급제 할당)
사용자/프로젝트 등급에 따라 미리 정의된 하드웨어 조합(Flavor)을 할당합니다.
| 등급 | vCPU | RAM | GPU | 용도 |
| :--- | :--- | :--- | :--- | :--- |
| **Basic** | 2 | 4GB | - | 일반 사무, 웹 브라우징 |
| **Standard** | 4 | 16GB | RTX 4070 | 일반 게이밍 (PCroom용) |
| **Pro** | 8 | 32GB | RTX 4090 | 고사양 R&D, AI 모델링 |
| **Ultra** | 16 | 128GB | A100/H100 | 거대 언어 모델(LLM) 학습 |

### [Strategy B] Hard-Cap Quotas (원천 차단)
- Super Admin이 Organization 단위로 **최대 할당 자원(Hard Limit)**을 설정합니다.
- 예: "PCroom 브랜드는 총 vCPU 100개, RAM 500GB를 초과할 수 없음."

### [Strategy C] Dynamic AI Model Logic
- 하드웨어 스펙 외에도 **"어떤 AI 모델이 올라가 있느냐"**에 따라 부가 가치가 달라집니다.
- 관리자 대시보드에서는 하드웨어(Flavor) 요금 + AI 모델(Surcharge) 요금을 실시간으로 합산하여 관리합니다.

---

## 3. Dashboard Integration Plan (대시보드 반영 계획)

### Super Admin View (Top-Level)
- [ ] **Organization/Project Tree:** Monewment 아래에 연결된 모든 테넌트를 트리 형태로 시각화.
- [ ] **Project Extension Button:** 클릭 한 번으로 새 프로젝트 공간(Namespace)을 클러스터에 확장.
- [ ] **Approval Queue:** 사용자가 요청한 가입/확장 요청 리스트 및 승인 버튼.

### Project Admin View (Tenant-Level)
- [ ] **Quota Dash:** 현재 사용 중인 자원 vs 잔여 할당량 그래프.
- [ ] **Internal User Logs:** 팀원들의 활동 및 자원 사용 내역 추적.
