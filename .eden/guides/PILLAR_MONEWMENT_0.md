# 🛰️ 제국 본영 지침서 (Pillar: MONEWMENT-0)

**지위**: 제국의 '정신'이자 '절대 통제소'  
**핵심 기제**: Active Scout (능동 정찰) & Sovereign Creation (주권 창조)

---

## 1. 개요 (Overview)
`MONEWMENT-0`는 제국 전역의 설계도(Blueprint)이며, 모든 영토(`STRATUM`)의 기원이자 종착지다. 이곳은 실행되는 공간이 아니라 **'정의되는 공간'**이다.

## 2. 핵심 기술 프로토콜 (Technical Protocols)

### 2.1 Active Scout (능동 정찰)
- **정의**: 하위 개체의 상향식 보고를 불신하고, 코어가 직접 영토 내의 `local_registry.db`를 읽어 상태를 동기화하는 체계.
- **실행 주기**: 매 60초마다 모든 데이터베이스 스트림을 스캔.
- **동기화 대상**: 
    - `entity_id`별 `last_active_at` 갱신.
    - 누적 비용(`accumulated_cost`) 합산 및 예산 집행.
    - `fencing_token` 검증 및 무결성 체크.

### 2.2 Sovereign Creation (주권 창조)
- **절차**: `Provisioner.py`를 통해 새로운 영토를 소환할 때, 다음 3개 요소를 **단일 트랜잭션**으로 배치함.
    1. **Physical Files**: 코어 라이브러리와 공무원 ANT 소스 복제.
    2. **Logical Schema**: 영토 전용 데이터베이스 및 스키마 생성.
    3. **Legal Marker**: 해당 영토 전용 `IMPERIAL_CONSTITUTION.md` 주입.

## 3. 권한 및 집행권 (Authority & Force)

### 3.1 물리적 집행권 (Physical Kill)
- 코어는 정찰 중 '유전적 변이(Mutation)'나 '법 위반' 감지 시, 해당 영토의 모든 프로세스 트리를 **OS 레벨에서 즉각 소멸**시킨다.
- 집행 근거: `sys.path` 주입 시도, 코어 API 불법 점유, 예산 초과 등.

### 3.2 문서 주권 (Document Master)
- 모든 규약과 가이드는 `MONEWMENT-0/docs`에서만 수정 가능하다.
- 수정 즉시 하향식 동기화 엔진이 구동되어 전 제국의 문서를 최신화한다.

---

## 4. 개발 금기 사항 (Taboos)
- **Template Run**: 템플릿 폴더 내에서 직접 워커를 기동하거나 실험하지 마십시오.
- **Reporting Slave**: 하위 개체가 보고서를 가져다주길 기다리지 마십시오. 직접 흔적을 찾아 읽으십시오.
- **Logic Sharing**: 템플릿의 로직을 하위 개체와 동적으로 공유하지 마십시오. 오직 '복제된 파편'만 허용하십시오.

**모든 본영 에이전트는 이 규약을 자신의 DNA로 삼아 제국을 통치하라.**
