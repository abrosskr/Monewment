# [Project Specification] DeepSync × DeepVault × DeepRender Integrated Architecture

**: Web3 기반의 제로 트러스트 보안 및 분산 렌더링을 지원하는 국가급 AI 컴퓨팅 인프라**
> **Current Version:** v2.1 (Port Standards Added)
> **Last Updated:** 2026-01-14

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


## 6. Phase 6: DeepVault & DeepRender Core (Completed)
> **Execution Period:** 2026-01-07  
> **Status:** ✅ Fully Implemented and Verified

본 단계에서는 분산 저장소(DeepVault)와 분산 렌더링(DeepRender)을 위한 핵심 로직과 네트워크 프로토콜을 완성했습니다.

### A. DeepVault: Zero-Trust Distributed Storage
1.  **Erasure Coding (Sharding)**
    *   **Reed-Solomon Algorithm**: 원본 파일을 `N`개의 데이터 조각 + `M`개의 패리티 조각으로 분할하여, 노드 이탈 시에도 복구 가능한 수학적 안전장치 구현.
    *   **Client-Side Shredder**: 클라이언트 단에서 `Encrypt` -> `Split` 과정을 수행하여, 서버에는 절대 원본이 저장되지 않도록 설계.
    *   **Map Manager**: 파일 조각(Shard)들의 분산 위치를 추적하는 메타데이터 관리 시스템 구축 (`/api/v1/vault/*`).

2.  **Self-Healing Network**
    *   **Queen Watchdog**: Redis 기반으로 샤드를 보관 중인 개미(Nodes)의 상태를 주기적으로 감시.
    *   **Repair Agent**: 노드 이탈 감지 시, 남아있는 조각들을 모아 소실된 조각을 수학적으로 재구성(Reconstruction)하고 새로운 노드에 재배포하는 자동 복구 로직 구현.

### B. DeepRender: Distributed Rendering Pipeline
1.  **Blender Engine Integration**
    *   Python 스크립트가 로컬에 설치된 `blender.exe`를 감지하고, `-b` (Background) 옵션으로 렌더링을 제어하는 `BlenderOps` 래퍼 구현.
    *   **Task Executor**: 퀸으로부터 할당받은 프레임 번호에 맞춰 `.blend` 파일을 로드하고 렌더링을 수행하는 자동화 파이프라인 완성.

2.  **Asset Management**
    *   렌더링에 필요한 대용량 자산 파일(텍스처, 모델)을 효율적으로 다운로드하고 관리하는 `VaultDownloader` 연동.

---

## 7. Phase 8 & 9: Operations & Packaging (Completed)
> **Execution Period:** 2026-01-07  
> **Status:** ✅ Fully Implemented and Verified

상용화를 위한 패키징 및 운영 자동화 시스템을 구축했습니다.

### A. Client Packaging (Phase 9)
*   **System Tray Integration**: `pystray`를 활용하여 윈도우 작업 표시줄 트레이에 상주하며, 백그라운드 작업을 제어하는 UX 구현.
*   **PyInstaller Build**: Python 코드를 단일 실행 파일(`.exe`)로 컴파일하여, 일반 사용자도 쉽게 설치/실행할 수 있도록 패키징 파이프라인 구축.

### B. Real-World Integration (Phase 8)
*   **Asset Injection**: 실제 3D 프로젝트 파일(`cube.blend` 예시)을 활용하여, 파이프라인의 처음부터 끝까지(Dispatch -> Render -> Result Upload) 실제 렌더링 사이클이 작동함을 검증.

---

## 8. Phase 10: Client GUI Dashboard Implementation (Completed)
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


## 9. Phase 11: Commercialization Hardening (Completed)
> **Execution Period:** 2026-01-08  
> **Status:** ✅ Fully Implemented and Verified

상용 서비스 런칭을 위한 필수 3대 요소(보안/운영/네트워크)를 보강했습니다.

### A. Network Hardening (NAT Traversal)
*   **Problem**: PC방의 Symmetric NAT 환경에서 P2P 직접 연결 불가 (Connection Lost).
*   **Solution**: **Hybrid Transport System** 구축.
    *   **Direct UDP**: 1차 시도 (고속).
    *   **Relay Fallback**: 실패 시 Queen Server를 통한 WebSocket 중계 (100% 연결 보장).
    *   **Verification**: A->Queen->B 릴레이 메시지 전송 성공 확인.

### B. Security Hardening (Trojan Block)
*   **Problem**: 악성 스크립트가 심어진 `.blend` 파일로 인한 렌더러 PC 해킹/채굴 위험.
*   **Solution**: **Blender Secure Execution** 강제화.
    *   `--disable-autoexec` 플래그 강제 주입 및 `-y` (Auto Run) 옵션 원천 차단.
    *   업로드 시 파일 매직 헤더(`BLENDER`) 검증으로 위변조 파일 필터링.

### C. Operations Hardening (Fail-Safe OTA)
*   **Problem**: 업데이트 도중 전원/네트워크 차단 시 클라이언트 영구 벽돌(Zombie)화.
*   **Solution**: **Atomic Swap & Rollback Updater** 개발.
    *   **Transaction**: `Check` -> `Download` -> `Verify(Hash)` -> `Backup` -> `Swap`.
    *   **Rollback**: 부팅 실패 또는 Swap 오류 시 즉시 백업본(`v1.0.bak`)으로 자동 복구.


## 10. CI/CD & Git Synchronization Protocol (Stability Hardening)
> **Status:** ✅ Protocol Established and Hardened (2026-01-08)

개발 환경과 배포(CI) 환경 간의 격차를 해소하고, "가짜 초록불(Silent Failure)"을 원천 차단하기 위한 기술 규격입니다.

### A. CI Core Infrastructure (GitHub Actions Req.)
*   **Mandatory Services**: 
    *   `PostgreSQL`: 데이터베이스 스키마 문서 생성을 위한 정적 메타데이터 소스로 사용.
    *   `Redis`: FastAPI 앱 초기화 시 소켓 및 캐시 매니저 연결을 위해 필수.
*   **Environment Variables**: CI 단계에서 `Settings` 클래스 로딩 실패를 막기 위해 Dummy 변수(`SECRET_KEY`, `POSTGRES_*`, `REDIS_URL`) 주입 필수.

### B. Dependency Integrity Control
*   **Requirements Standard**: `src/` 모듈(특히 `security.py`)에서 임포트하는 모든 라이브러리(`passlib`, `python-jose`, `bcrypt` 등)는 반드시 `requirements.txt`에 명시되어야 함.
*   **Strict Exit Code**: 자동화 스크립트(`generate_docs_v4.py` 등)는 내부 에러 발생 시 반드시 `sys.exit(1)`을 호출하여 CI 파이프라인을 중단시켜야 함.

### C. Git Synchronization & Hygiene
*   **Pycache Lock**: `__pycache__` 파이썬 컴파일 파일이 Git 인덱스에 포함되지 않도록 `.gitignore` 최신화 및 추적 강제 제거.
*   **Bot Conflict Resolution**: CI Bot의 자동 커밋과 로컬 작업이 충돌할 경우, `git pull --rebase`를 통한 선형 히스토리 관리를 표준으로 채택.
*   **Commit Tagging**: `[skip ci]` 태그를 활용하여 자동 생성 커밋으로 인한 무한 루프 방지.


---
**[End of Hardening Phase]**  
Next Target: **Phase 14 (Profit & Scale - Real-time Dashboard & Smart Scheduler)**

---

## 11. PixelGrid Phase 4: Advanced Cell Controls & Media Support (Completed)
> **Execution Period:** 2026-01-08  
> **Status:** ✅ Fully Implemented and Verified

본 단계에서는 PixelGrid Editor의 기능을 대폭 확장하여 셀 크기 조정, ID 관리, 아웃라인 제어, 이미지 삽입 기능을 추가했습니다.

### A. 구현된 핵심 기능 (4가지)

1. **Cell Size Control (셀 크기 조정)**
   - `GridCell` 인터페이스에 `width`, `height` 필드 추가 (기본값: 80px)
   - Selection Editor에 Width/Height 입력 필드 추가
   - 셀별로 픽셀 단위 크기 제어 가능

2. **Cell ID Management (셀 ID 관리)**
   - 병합 시 자동 ID 생성: `m-{r}-{c}` 형식 (예: `m-2-3`)
   - Selection Editor에 Cell ID 입력 필드 추가
   - 사용자 정의 ID 수정 가능 (예: "header-logo", "nav-menu")
   - 프롬프트 생성 시 JSON 및 JSX에 ID 포함

3. **Outline Control (아웃라인 제어)**
   - Outline 데이터 구조: `enabled`, `width` (1-10px), `color`, `style` (solid/dashed/dotted)
   - Selection Editor에 Outline 섹션 추가 (ON/OFF 토글, Width 슬라이더, Color picker, Style 선택)
   - 셀별로 독립적인 테두리 스타일 적용 가능

4. **Image Support (이미지 삽입)**
   - Component Type에 'image' 추가
   - `imageUrl`, `imageAlt`, `imageFit` (cover/contain/fill) 필드 추가
   - Selection Editor에 Image Settings 섹션 추가 (URL 입력, Alt Text, Object Fit 선택)
   - 실제 이미지 렌더링 및 프롬프트 출력 지원

### B. UI/UX 개선

1. **Selection Editor 재구성**
   - 총 12개 섹션으로 확장: Cell ID, Component Type, Content, Dimensions, Font Settings, Color Palette, Outline, Image Settings, Global Padding, Content Alignment
   - Weight 버튼 스타일을 Component Type과 통일 (노란색 활성화)

2. **병합 셀 렌더링 수정**
   - 병합된 셀이 전체 영역을 차지하는 큰 박스로 확장되도록 수정
   - `gridRow`/`gridColumn` 단축 속성 사용 (`3 / 5` 형식)
   - 병합된 셀에는 `width: 100%; height: 100%` 적용하여 그리드 영역을 완전히 채움
   - 시작 셀을 제외한 나머지 병합된 셀들은 완전히 숨김 처리

### C. 기술적 변경 사항

**수정된 파일:**
- `gui/app/pixelgrid/editor/page.tsx`

**주요 변경 내용:**
1. GridCell 인터페이스 확장 (14개 새 필드)
2. editState 확장 (11개 새 필드)
3. updateEditStateFromCell 함수 업데이트
4. applyStyle 함수 확장 (Phase 4 필드 적용)
5. handleMerge 함수에 자동 ID 생성 로직 추가
6. Selection Editor UI 대폭 개편
7. renderComponent 함수에 'image' 타입 지원 추가
8. 그리드 렌더링에 width, height, outline 적용
9. generatePrompt 함수에 Phase 4 필드 포함

### D. 검증 결과

브라우저 테스트를 통해 모든 기능이 정상 작동함을 확인:
- ✅ 병합 셀이 전체 영역을 차지하는 큰 박스로 확장
- ✅ 병합된 셀 숨김 처리 (시작 셀만 표시)
- ✅ ID 간소화 (`m-n-n` 형식)
- ✅ Weight 스타일 통일 (노란색 활성화)
- ✅ Outline, Image, Dimensions 컨트롤 정상 작동

---
**[End of PixelGrid Phase 4]**  
Next Target: **PixelGrid Phase 5 (Advanced Features - Animation, Responsive Breakpoints, File Upload)**

---

## 12. Phase 4: Metering & Billing System (Integrated)
> **Execution Period:** 2026-01-11
> **Status:** ✅ Fully Implemented and Documented

Monewment 프로젝트의 사용자 과금 및 리소스 미터링 시스템을 구축했습니다.

### A. Core Billing Infrastructure
1.  **Database Schema Expansion**:
    *   `src/models.py`에 `SubscriptionPlan`, `ProjectSubscription`, `VMFlavor`, `AIModel`, `VMUsage` 등 7개 과금 관련 모델 통합.
    *   `scripts/init_metering_db.py`: 초기 데이터(요금제, AI 모델 테이블) 시딩 끊김 없는 자동화.
2.  **Metering Service Layer**:
    *   `src/services/metering.py`: VM 세션 시작/종료 시점의 정밀한 시간 기록 및 요금 계산 로직 구현 (HW 요금 + SW 할증).

### B. Live Usage Monitoring (CCTV)
1.  **Zero-UI Dashboard**:
    *   별도의 웹 프론트엔드 없이 `docs/LIVE_USAGE.md` 파일을 실시간 대시보드로 활용하는 창의적 모니터링 체계 구축.
    *   `scripts/usage_cctv.py`: 백그라운드 프로세스로 실행되어 DB 변동사항을 감지하고 마크다운 대시보드를 2초마다 갱신.
2.  **User Manual**:
    *   `docs/user_guide/METERING_MANUAL.md`: 미터링 시스템 활용법을 상세히 기술한 한글 매뉴얼 제공.

### C. Stability & Fixes
1.  **Schema Migration**: `scripts/fix_db_schema.py`를 통해 `projects` 테이블에 누락된 `status` 컬럼을 라이브 마이그레이션으로 추가.
2.  **Environment Stability**: Uvicorn 서버 구동에 필수적인 `slowapi` 의존성 누락 확인 및 설치 완료 (`ModuleNotFoundError` 해결).

---
**[End of Phase 4 Metering]**

---

## 13. Phase 5: Payment Gateway Integration & Burst Mode
> **Execution Period:** 2026-01-11
> **Status:** ✅ Fully Implemented and Verified

미터링 시스템 위에 실제 결제 및 예산 제어 로직을 통합했습니다.

### A. Hybrid Sizing Model ("Smart Hybrid")
1.  **Burst Mode Authorization**:
    *   `src/models.py`: `allow_burst` 플래그 추가 (DB Migration 완료).
    *   **Logic**: `MeteringService`에서 프로젝트의 크레딧 잔액을 확인하고, 초과 시 `allow_burst`가 켜져 있으면 오버드래프트로 VM 생성을 허용.
2.  **Safety Guardrails**:
    *   `ProjectBudget.usage_limit_hard_cap`에 도달하면 즉시 리소스 생성을 차단하여 "요금 폭탄" 방지.

### B. Payment System (Mock)
1.  **Infrastructure**:
    *   `payment_history` 테이블 신설 (감사 로그).
    *   `ProjectBudget.prepaid_credits` 컬럼 추가 (충전금 관리).
2.  **Billing API**:
    *   `POST /api/v1/billing/charge`: Stripe 결제 시뮬레이션 및 예산 자동 충전.
    *   `GET /api/v1/billing/balance/{id}`: 실시간 잔액 조회.

---
**[End of Phase 5 Payment]**
Next Target: **Phase 6 (DeepVault & DeepRender Core Implementation)**

---

## 14. Phase 6: Codebase Refactoring & Security Hardening
> **Execution Period:** 2026-01-13 ~ 2026-01-14
> **Status:** ✅ Fully Implemented

대규모 코드베이스 정리와 보안 강화 작업을 수행했습니다.

### A. Codebase Refactoring (main.py Modularization)

기존 ~1,000줄에 달하던 `src/main.py`를 역할별로 분리하여 유지보수성을 대폭 개선했습니다.

**생성된 파일들:**
| 파일 | 역할 |
|------|------|
| `src/api/v1/endpoints/auth.py` | 회원가입, 로그인, JWT 발급 |
| `src/api/v1/endpoints/projects.py` | 프로젝트 엔진 생성, 폴더 구조 조회 |
| `src/api/v1/endpoints/services.py` | 설치 가능 서비스 목록, API 키 관리 |
| `src/api/v1/endpoints/chat.py` | AI 에이전트 대화 |
| `src/api/v1/endpoints/ant_socket.py` | Ant WebSocket 연결 처리 |
| `src/api/v1/admin/dashboard.py` | 관리자 통계, 계층 조회, 클러스터 관리 |
| `src/core/limiter.py` | Rate Limiter 인스턴스 (순환 참조 방지) |
| `src/core/background.py` | Write-Behind 백그라운드 태스크 |
| `src/schemas.py` | 기존 main.py 내 Pydantic 모델들 통합 |

**결과:** `main.py`는 이제 ~200줄로 간결해졌으며, FastAPI 앱 초기화와 라우터 등록만 담당합니다.

### B. API Key Security Hardening (SHA-256 Hashing)

API 키를 평문이 아닌 해시값으로 DB에 저장하도록 보안을 강화했습니다.

**구현 내용:**
1.  `src/core/security.py`:
    *   `generate_api_key()`: `sk_live_...` 형식의 안전한 랜덤 키 생성.
    *   `hash_api_key()`: SHA-256 해싱.
    *   `get_api_key_user()`: 요청된 키를 해싱 후 DB와 비교.
2.  `src/api/v1/endpoints/auth.py`:
    *   `POST /api/auth/api-key`: 새 API 키 발급 엔드포인트 추가. 발급된 키는 한 번만 보여지며, DB에는 해시값만 저장됨.

### C. Modular Email Service

하위 프로젝트에서 재사용 가능한 이메일 인증 API 모듈을 구축했습니다.

**구현 내용:**
1.  `src/core/email_utils.py`:
    *   `EmailUtils.validate_format()`: `email-validator` 패키지 활용.
    *   `EmailUtils.send_verification_email()`: Redis에 OTP 저장 + Mock 콘솔 출력 (SMTP 미설정 시).
    *   `EmailUtils.verify_code()`: Redis에서 OTP 검증.
2.  `src/api/v1/endpoints/email_service.py`:
    *   `POST /api/services/email/validate`: 이메일 형식 검증.
    *   `POST /api/services/email/send-verification`: 인증번호 발송 (Mock Mode 지원).
    *   `POST /api/services/email/verify-code`: 인증번호 검증.

### D. CI/CD Stability Fix

GitHub Actions 워크플로우가 보안 키 검증 로직 도입 이후 실패하던 문제를 해결했습니다.

**수정 내용:**
*   `.github/workflows/ci.yml`: `SECRET_KEY` (32자 이상) 및 `ANT_ENCRYPTION_KEY` (64자 Hex) 더미 값을 CI 환경 변수에 추가하여 `config.py` 검증을 통과하도록 함.

---
**[End of Phase 6 Refactoring]**
Next Target: **Phase 7 (Internationalization - i18n / Localization)**

---

## 15. Project Standards: Port Registry
> **Status:** 🛑 Immutable Convention (2026-01-14)

프로젝트 전체에서 사용되는 포트 규약을 정의합니다. 모든 개발 및 배포 환경은 이 규약을 엄격히 준수해야 합니다.

| Service | Port | Protocol | Usage |
| :--- | :--- | :--- | :--- |
| **Frontend** | `3000` | HTTP | Next.js Client |
| **Backend** | `8000` | HTTP | FastAPI Server |
| **PostgreSQL** | `5433` | TCP | Database (Host Access) |
| **Redis** | `6379` | TCP | Message Broker |

> 참조: [PORT_STRATEGY.md](file:///d:/projects/Monewment/docs/standards/PORT_STRATEGY.md)
