# Vendors System Specification (V4: The Sentient Kitchen)

**문서 생성일**: 2026-01-27
**목적**: Monewment 시스템 통합 및 "Sentient Kitchen" 구현을 위한 전체 기술 명세 및 현황 공유

---

## 1. 시스템 개요 (System Identity)
**VENDORS**는 조리 과정을 **"물리적 벡터(Physics Vector)"**로 변환하여 이해하고 제어하는 **디지털 미각 엔진(Digital Taste Engine)**입니다.
- **Vision**: "요리는 감(Feeling)이 아니라 물리(Physics)다."
- **Core Tech**: **TSV (Thermal State Vector)** - 조리 상태를 5차원 벡터 `[T, V, A, I, t]`로 정의.
- **Goal**: 전 세계 모든 레시피를 물리적 실행 파일(`.FIS`)로 변환하여 로봇/스마트 키친에서 재현.

---

## 2. 핵심 아키텍처 (V4 Architecture)

### 2.1. The Brain: TSV Protocol
시스템은 요리를 영상(Video)이 아닌 **상태 벡터(State Vector)**로 인식합니다.
```python
TSV = [
    Temperature (T),    # 현재 에너지 (°C)
    Velocity (V),       # 변화 속도 (dT/dt) -> "지금 굽고 있는가, 식고 있는가?"
    Acceleration (A),   # 변화 가속도 (d2T/dt2) -> "재료가 투입되었는가? (이벤트)"
    Integral (I),       # 누적 열량 (∫T dt) -> "얼마나 익었는가? (Maillard)"
    Time (t)            # 상태 유지 시간 (Stability)
]
```

### 2.2. Infrastructure: Edge-Cloud Hybrid (Dual-Core)
무료 클라우드 리소스의 한계를 극복하고 실시간 성을 보장하기 위한 하이브리드 구조입니다.

| Layer | Component | Role | Tech Stack |
| :--- | :--- | :--- | :--- |
| **Edge (Local)** | **Intelligence** | 10Hz 센서 데이터 처리, 물리 엔진 구동, TSV 변환 | Python (FastAPI), Pandas, Scipy |
| **Cloud A (Lab)** | **Data Lake** | Raw 데이터 수집, 학습용 로그 저수지 (Supabase Project 1) | Supabase Storage, PostgreSQL |
| **Cloud B (Live)** | **Service** | 검증된 모델 배포, 사용자 서비스, 레시피 검색 (Supabase Project 2) | Supabase Auth, pgvector |

---

## 3. 주요 컴포넌트 현황 (Component Status)

### 3.1. Backend (`/backend`)
- **Drivers (`/drivers`)**:
    - `flir_ax8.py`: Modbus TCP 기반 10Hz 고속 열화상 데이터 폴링 (구현 완료).
    - `mock_sensors.py`: 개발용 가상 센서 시뮬레이터 (구현 완료).
- **Engines (`/engines`)**:
    - `state_vector_engine.py`: Raw Temperature -> TSV 변환 (Savitzky-Golay 필터 적용 완료).
    - `physics_estimator.py`: Maillard 반응, 점도(Viscosity) 변화 추정 (구현 완료).
    - `navigator.py`: (개발 예정) 목표 TSV와 현재 TSV의 오차($\Delta$)를 계산하여 제어 명령 생성.
- **Services (`/services`)**:
    - `pipeline_service.py`: 센서-엔진-API를 잇는 데이터 흐름 오케스트레이터 (구현 완료).
    - `global_collector.py`: 전 세계 레시피 사이트(Cookpad 등) 크롤링 및 정제 (구현 완료).

### 3.2. Data Protocol (`/data`)
- **.FIS (Food Inkjet System) Format**:
    - 조리 과정 전체를 기록한 시계열 데이터 포맷.
    - 구조: `Metadata` (레시피 정보) + `Frames` (초당 10개의 TSV 레코드).
- **Golden List**:
    - 수집 대상 핵심 사이트 선정 완료 (Marmiton, 10000recipe, BBC Good Food 등).

---

## 4. 통합 로드맵 (Integration Roadmap for Monewment)

### Phase 6: 관측의 시대 (The Era of Measurement)
**목표**: "데이터를 담을 그릇(Recorder)을 완성하고, 실제 요리(Egg/Steak)를 담는다."
1.  **Navigator 구현**: 오차 벡터($\Delta T, \Delta V$) 로직 완성.
2.  **Metrology Dashboard**: 
    - Monewment/vendors 프론트엔드에 `Phase Plane` ($T$ vs $\dot{T}$) 그래프 구현.
    - **통합 포인트**: Next.js에서 Python FastAPI의 WebSocket 엔드포인트로 접속.
3.  **Data Collection**:
    - 계란 후라이(민감도), 스테이크(열부하), 볶음밥(카오스) 3대 표준 요리 데이터 수집.

### Phase 7: 클라우드 이관 (Cloud Migration)
**목표**: "로컬의 지능과 클라우드의 기억을 연결한다."
1.  **Supabase 연동**:
    - `vendors-lab` (수집용) / `monewment-live` (서비스용) 프로젝트 생성.
    - Python 백엔드에 `Supabase Client` 탑재 (비동기 업로드).
2.  **Dual-Core 파이프라인**:
    - [Edge] 수집 -> [Lab] 저장 -> [AI] 학습 -> [Live] 배포 흐름 구축.

---

## 5. Monewment 개발자를 위한 가이드

**디렉토리 구조**:
```text
Monewment/vendors/
├── backend/            # [Python] 물리 엔진 & 드라이버 (이관 완료)
│   ├── main.py         # Entry Point
│   └── app/engines/    # Core Logic
├── app/                # [Next.js] 사용자 UI & 대시보드 (신규 생성)
└── lib/supabase.ts     # [TypsScript] 클라우드 연결
```

**실행 방법**:
1.  **Backend (Edge)**: `cd backend && python main.py` (포트 8000)
2.  **Frontend (Service)**: `npm run dev` (포트 3000)

이 명세서는 Vendors 서비스의 DNA입니다. Monewment 시스템은 이 문서를 기준으로 Vendors를 이해하고 확장해야 합니다.
