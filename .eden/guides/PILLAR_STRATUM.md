# 🏔️ 실행 영토 지침서 (Pillar: STRATUM)

**지위**: 제국의 '물리적 토대'이자 '임시 자산소'  
**핵심 기제**: Absolute Isolation (완전 격리) & Impermanence (비영원성)

---

## 1. 개요 (Overview)
`STRATUM`은 제국이 특정 목적을 위해 점유한 물리적/논리적 공간이다. 이곳은 언제든 소각될 수 있는 **'휘발성 영토'**임을 명심하라.

## 2. 핵심 기술 프로토콜 (Technical Protocols)

### 2.1 Territory Isolation (영토 격리)
- **물리적 격리**: 영토는 자신만의 `core/` 라이브러리를 보유하며, 부모 템플릿의 경로를 절대 참조하지 않는다.
- **데이터 격리**: `schema_stratum_{name}` 스키마를 사용하여 타 영토와의 조인을 원천 차단한다.
- **포트 격리**: 8800 포트의 코어 API와 통신하되, 오직 자산 PULL과 소유권 확인(Fencing)만을 위해 사용한다.

### 2.2 Local Registry (영내 흔적 보존)
- **저장소**: 영토 루트에 `local_registry.db` (SQLite)를 유지한다.
- **기록 의무**: 영토 내에서 구동되는 모든 `QUEEN`, `ANT`, `AREUM`은 30초마다 자신의 상태를 이 DB에 직접 기록(Overwrite)해야 한다.
- **내용**: `status`, `session_cost`, `fencing_token`, `last_active_at`.

## 3. 무결성 및 폐쇄 (Integrity & Disposal)

### 3.1 Atomic Birth (원자적 탄생)
- 영토는 부분적으로 존재할 수 없다. 
- 파일 복제, DB 생성, 초기 공무원 ANT 기동 중 하나라도 실패하면 해당 영토의 탄생은 무효화되며 즉각 삭제된다.

### 3.2 Disposal Protocol (초토화 프로토콜)
- 영토 폐쇄 명령 수신 시, 영내의 모든 프로세스는 5초 이내에 자결(Seppuku)하고 모든 임시 데이터를 소거한다.
- 미이행 시 본영의 **물리적 집행관(Imperial Sentinel)**에 의해 강제 소거된다.

---

## 4. 개발 금기 사항 (Taboos)
- **Path Hijack**: `sys.path.append("MONEWMENT-0")`는 반역죄에 해당한다.
- **Shared Connection**: 타 영토와 커넥션 풀을 공유하여 한쪽의 장애가 제정 임계점을 넘지 않게 하라.
- **Upward Ping**: 중앙 코어에 자신의 존재를 알리기 위해 핑을 쏘지 마라. 흔적을 남기면 코어가 정찰할 것이다.

**영토의 에이전트는 독립적으로 수행하되, 그림자 속에 흔적을 남겨라.**
