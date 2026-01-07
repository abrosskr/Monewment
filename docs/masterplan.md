# [Project Specification] DeepSync × DeepVault × DeepRender Integrated Architecture

**: Web3 기반의 제로 트러스트 보안 및 분산 렌더링을 지원하는 국가급 AI 컴퓨팅 인프라**
> **Current Version:** v2.0 (DeepRender Expanded)  
> **Last Updated:** 2026-01-07  

---

## 1. 프로젝트 개요 (Executive Summary)

본 프로젝트는 유휴 컴퓨팅 자원을 활용하여 3가지 핵심 가치를 창출하는 통합 플랫폼 구축을 목표로 한다.

1. **DeepSync (GenAI):** LLM 기반의 고품질 합성 데이터(Synthetic Data) 생성. (✅ Core Implemented)
2. **DeepVault (Storage):** 생성된 데이터를 파편화(Sharding)하여 원본 없는 보안 저장소 구축. (🏗️ Planned)
3. **DeepRender (Rendering):** **(New)** 대용량 3D/영상 렌더링 작업을 프레임 단위로 분산 처리하여, 기존 렌더팜 대비 50% 비용 절감 및 10배 빠른 속도 구현. (🏗️ Planned)

이 시스템은 한국의 독보적인 고사양 PC방 인프라(RTX 30/40 시리즈)를 **'단일 슈퍼컴퓨터'**처럼 통합 제어하여, 글로벌 AI 및 콘텐츠 시장의 연산 수요를 흡수한다.

---

## 2. 시스템 아키텍처 (System Architecture)

전체 시스템은 중앙의 통제 서버(Queen)와 분산된 노드(Ants)로 구성되며, 렌더링 파이프라인 처리를 위한 전용 모듈이 추가된다.

### A. Queen Server (Control Tower)

* **역할:** 작업 스케줄링, 메타데이터 관리, 자산(Asset) 배포 트래커.
* **주요 기능:**
    * **Task Dispatcher:** AI 생성 및 렌더링 일감 배분 (우선순위 큐 관리). (✅ Implemented)
    * **Map Manager (Vault):** 데이터 조각 위치 정보 관리. (🏗️ Planned)
    * **Asset Tracker (Render):** **(New)** 대용량 렌더링 소스 파일(3D 모델, 텍스처)의 P2P 배포 현황 추적. (🏗️ Planned)
    * **Stitcher (Render):** **(New)** 개미들이 보낸 낱장 이미지(Frame)를 취합하여 최종 영상 파일로 병합(Encoding). (🏗️ Planned)

### B. Ant Client (Worker Node)

* **역할:** 실제 연산(생성/렌더링) 및 저장소 제공.
* **주요 모듈:**
    * **[Core 1] Generator (AI):** LLM 기반 데이터 생성. (✅ Implemented - Mock)
    * **[Core 2] Shredder (Vault):** 데이터 암호화 및 조각 분할. (🏗️ Planned)
    * **[Core 3] Renderer (Graphic):** **(New)** 할당받은 프레임에 대한 3D 렌더링 수행 (Blender/Maya/Unreal Engine 엔진 연동). (🏗️ Planned)
    * **[Core 4] P2P Syncer:** **(New)** 렌더링에 필요한 대용량 자산을 인접 노드로부터 고속 다운로드. (🏗️ Planned)

---

## 3. 핵심 기술 명세 (Core Technology Stack)

### ① DeepVault: 보안 저장 매커니즘
> **Logic:** `Generate` -> `Encrypt` -> `Split (Erasure Coding)` -> `Distribute`
* **Zero Trust Encryption:** `AES-256` 암호화 적용. (✅ Implemented)
* **Erasure Coding (Reed-Solomon):** 개의 데이터 조각 + 개의 패리티 조각 생성. 노드 이탈 시에도 100% 복구 보장.

### ② DeepSync: 분산 생성 매커니즘
> **Logic:** `Fetch Raw Data` -> `LLM Generation` -> `Quality Check`
* **Synthetic Data Engine:** PC방(High-Spec) 및 가정용(Low-Spec) 이원화 운영.
* **Cross-Validation:** 동일 작업을 3개 노드에 중복 할당하여 결과값 교차 검증.

### ③ DeepRender: 분산 렌더링 파이프라인 (신규 추가)
> **Logic:** `Slice` -> `P2P Asset Sync` -> `Parallel Render` -> `Stitch`
* **Frame Slicing (The Slicer):**
    * 1TB 규모의 렌더링 요청을 **1 프레임 단위(1/60초)**의 초소형 작업으로 분해.
    * 예: 1시간 영상 → 216,000개의 개별 Task로 변환하여 21만 개의 노드에 동시 할당 가능.
* **Smart Asset Distribution (P2P Protocol):**
    * 수십 GB에 달하는 프로젝트 원본(Assets)을 중앙 서버에서 모두 전송하지 않음.
    * **BitTorrent 프로토콜**을 응용하여, 데이터를 먼저 받은 PC방 노드(Seeder)가 인접 노드(Leecher)에게 고속으로 전파. (LAN 환경 활용 극대화).
* **Redundant Rendering (중복 할당):**
    * 개미의 이탈(Log-off)에 대비하여, 동일한 프레임을 2개 이상의 노드에 동시 할당.
    * 가장 먼저 완료된 결과물만 채택하고 나머지는 Kill(중단) 처리하여 지연 시간(Latency) 최소화.
* **Secure Frame Rendering:**
    * 작업자는 전체 스토리나 맥락을 알 수 없는 '단일 프레임'만 처리하므로, 출시 전 영화 등의 콘텐츠 유출 원천 차단.

---

## 4. 단계별 개발 로드맵 (Phased Roadmap)

### Phase 1: MVP - "기반 기술 검증" (Today)
**목표:** AI 데이터 생성 및 렌더링 기초 로직 구현.
1. **Profit Simulator:** GPU 전력 대비 AI/렌더링 수익성 시뮬레이터 개발. (✅ Done)
2. **Generator (AI):** 뉴스 기반 Q&A 생성기 구현. (✅ Implemented as Mock)
3. **Mini-Renderer:** **(New)** 오픈소스 Blender를 활용하여 특정 프레임 1장을 렌더링하는 커맨드라인 도구 연동 테스트. (🏗️ Todo)

### Phase 2: Network - "연결과 배포" (Next Month)
**목표:** 대용량 파일의 효율적 전송 및 통신 프로토콜 완성.
1. **DeepVault Core:** 파일 분할/복구(Sharding) 로직 구현.
2. **P2P Asset Sync:** **(New)** `Libtorrent` 라이브러리를 활용한 자산 파일 공유 프로토타입 개발.
3. **Task Dispatcher:** AI 생성 작업과 렌더링 작업을 구분하여 할당하는 스케줄러 개발. (✅ Core Done, Needs Expansion)

### Phase 3: Platform - "통합 및 상용화" (Future)
**목표:** 검증 시스템 및 대시보드 오픈.
1. **Verifier System:** 결과물 품질 자동 검수 및 중복 제거.
2. **Stitching Server:** **(New)** 렌더링된 이미지를 영상(`mp4`, `mov`)으로 합치는 인코딩 서버 구축.
3. **Web Dashboard:** 사용자 기여도(포인트) 확인 및 렌더링 진행률 모니터링. (✅ Basic Dashboard Done)

---

## 5. 안티그래비티 작업 지시서 (Ready to Dev)

DeepRender(렌더링) 모듈이 포함된 **확장된 디렉토리 구조**입니다.

```text
DeepSync_Project/
│
├── queen_server/            # [서버] 중앙 통제실
│   ├── main.py              # FastAPI 진입점 (✅ Done)
│   ├── task_dispatcher.py   # 일감 배분 (AI/Render 구분) (✅ Basic Done)
│   ├── map_manager.py       # DeepVault 위치 기록 (🏗️ Todo)
│   ├── asset_tracker.py     # [Render] 자산 배포 현황 추적 (🏗️ Todo)
│   └── stitcher.py          # [Render] 결과물 병합 (FFmpeg 연동) (🏗️ Todo)
│
├── ant_client/              # [클라이언트] 사용자 PC용
│   ├── core_generator.py    # [DeepSync] AI 데이터 생성 (✅ Mock Optimized)
│   ├── core_vault.py        # [DeepVault] 암호화 및 샤딩 (🏗️ Todo)
│   ├── core_renderer.py     # [Render] 블렌더/엔진 연동 렌더링 (🏗️ Todo)
│   ├── p2p_syncer.py        # [Render] 자산 P2P 다운로드 (🏗️ Todo)
│   └── stealth_sensor.py    # 유휴 상태 감지 (✅ Watchdog Done)
│
├── common/                  # 공통 모듈
│   ├── crypto_utils.py      # AES-256 암호화 (✅ Done)
│   └── erasure_coding.py    # 데이터 분할/복구 (🏗️ Todo)
│
└── simulator/               # 수익성 분석기
    └── profit_calc.py       # [0단계] AI 및 렌더링 수익 계산 (✅ ProfitEngine Done)
```

---

## 6. Phase 10: Client GUI Dashboard Implementation (Completed)
> **Execution Period:** 2026-01-07  
> **Status:** ✅ Fully Implemented and Verified

본 단계에서는 실험적인 Python 3.14 환경에서의 호환성 문제(Binder Issue)를 극복하고, 상용 수준의 Native Client 경험을 제공하는 **GUI Dashboard**를 완성했습니다.

### A. Architectural Pivot: Edge App Mode
*   **Challenge**: 최신 Python 3.14와 `pythonnet`/`pywebview` 간의 C-Binding 호환성 문제로 인해 기존 방식의 웹뷰 구동 불가.
*   **Solution**: **Microsoft Edge App Mode** (`msedge.exe --app=...`)를 활용한 "Hybrid Native" 아키텍처 채택.
    *   **Frameless UI**: 주소창/탭 없는 깔끔한 독립 실행 창 제공.
    *   **Stability**: 브라우저 기반이므로 Python 런타임 충돌 원천 배제.
    *   **Optimization**: 기본 해상도 `1280x800`, 시작 시 자동 최대화(`--start-maximized`) 적용.

### B. Core Features Implemented
1.  **Network-Based Token Sync (Zero-IPC)**
    *   기존 로컬 IPC 방식을 대체하여, **Web Frontend -> Queen Server -> Python Worker** 흐름의 네트워크 동기화 구현.
    *   로그인 시 Queen이 Redis에 토큰을 캐싱하고, 소켓으로 연결된 Worker에게 즉시 푸시(`token_sync`)하여 보안성 및 연동성 강화.

2.  **Silent Auto-Login (Persistence)**
    *   **Cloud Persistence**: 사용자 토큰을 Queen의 Redis(`ant:token:{client_id}`)에 저장.
    *   **Silent Start**: 클라이언트 재실행 시 로그인 화면 없이 즉시 Tray 모드로 진입 및 백그라운드 채굴 시작.
    *   **Local UX**: 브라우저 `localStorage`를 활용하여 이메일 기억하기("Save ID") 기능 구현.

3.  **Responsive UI Implementation**
    *   **Hybrid Layout**: 데스크톱(Split View) 및 모바일/태블릿(Single Column Stack) 자동 전환.
    *   **Safe Scrolling**: 작은 창에서도 로그인 폼이 잘리지 않도록 동적 스크롤 적용.
    *   **Draggable Region**: CSS `-webkit-app-region: drag`를 사용하여 네이티브 앱처럼 창 이동 가능.

### C. Critical Fixes & Stability Hardening
1.  **Database Connection**:
    *   Docker 컨테이너 포트 `5433`과 로컬 환경 설정 `5432` 불일치 해결.
    *   `.env` 및 Uvicorn 설정을 `5433`으로 표준화.
2.  **IPv6 Networking Conflict**:
    *   Windows의 `localhost`가 IPv6(`::1`)로 우선 해석되어 백엔드 연결이 끊키는 현상 발견.
    *   Frontend API 호출을 `http://127.0.0.1:8000` (IPv4)로 강제하여 연결 신뢰성 100% 확보.
3.  **Error Handling**:
    *   단순 "Server Error" 알림을 **"상세 디버그 메시지(Stack Trace)"** 출력으로 개선하여 사용자 경험/유지보수성 향상.

---
