# Vendors Task List

- [x] **Phase 4: TSV 아키텍처 (핵심)**
    - [x] FLIR AX8 드라이버 (`drivers/flir_ax8.py`)
    - [x] Mock 센서 (`drivers/mock_sensors.py`)
    - [x] 상태 벡터 엔진 (`engines/state_vector_engine.py`)
    - [x] 물리 추정기 (`engines/physics_estimator.py`)

- [ ] **Phase 6: 궤적 계측 및 데이터 수집 (Metrology)**
    - [ ] Navigator (오차 벡터 로직 구현)
    - [ ] 계측 대시보드 (Real-time Phase Plane)
    - [ ] 데이터 레코더 (`.FIS` v2.0 TSV 포맷 정의)

- [ ] **Phase 7: 클라우드 인프라 (Dual-Core Strategy)**
    - [x] **전략 확정**: 2 Projects + 1 Edge (`strategy_supabase_hosting.md`)
    - [ ] **Monewment 통합**
        - [ ] `d:\projects\Monewment\vendors` 초기화
    - [ ] **Project A: The Lab (`vendors-brain`)**
        - [ ] DB 스키마: 수집/학습용 (Raw Data)
        - [ ] Scraper/Recorder 연결
    - [ ] **Project B: The Live (`monewment-live`)**
        - [ ] DB 스키마: 서비스용 (Golden Data)
        - [ ] User App 연결
