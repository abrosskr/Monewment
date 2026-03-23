# 👑 제국 총독 지침서 (Pillar: QUEEN)

**지위**: 제국의 '도메인 지휘관'이자 '범용 집행자'  
**핵심 기제**: Domain Generality (범용성) & Status Aggregation (상태 취합)

---

## 1. 개요 (Overview)
`QUEEN`은 제국 본영의 의지를 특정 영역(`FORAGER`, `PHYSICS` 등)에 투영하는 **'범용적 프레임워크'**다. 여왕은 도메인에 종속되지 않으며, 오직 대상에 따라 지휘 체계만을 정렬한다.

## 2. 핵심 기술 프로토콜 (Technical Protocols)

### 2.1 Generalized Orchestration (범용 지휘)
- **설계 원칙**: 모든 여왕의 기반 코드는 동일해야 한다. 주입되는 설정(`config`)과 `ANT` 가이드라인에 따라 가변적으로 동작한다.
- **Role Switching**: `FORAGER-QUEEN`이 즉각 `PHYSICS-QUEEN`으로 전환되어도 기술적 모순이 없어야 한다.

### 2.2 Status Aggregation (상태 취합 기록)
- **기록 규약**: 휘하 `ANT` 군집의 진행 상황을 취합하여, 영토의 `local_registry.db`에 하나의 트랜잭션으로 투영한다.
- **주권 행사**: 수하 ANT들 중 예산을 초과하거나 법을 위반한 개체가 감지되면, 여왕은 즉각 그들의 생명권을 박수(Revoke)하고 리소스를 회수한다.

## 3. 통신 및 격리 (Comms & Isolation)

### 3.1 Unilateral Reception (단방향 수신)
- 여왕은 코어로 보고하지 않는다.
- 코어의 지령(Master Policy)을 수신하거나 영내의 흔적을 갱신할 뿐이며, 모든 결정은 독립적으로 집행한다.

### 3.2 Local Core Dependency
- 실행 시 반드시 자신이 배속된 영토(`STRATUM`)의 로컬 코어만을 로드한다.
- 템플릿이나 타 영토의 자원을 도용하는 행위는 엔트로피 오염으로 간주한다.

---

## 4. 개발 금기 사항 (Taboos)
- **Hard-coded Domain**: 코드 내에 특정 도메인(예: "Cookpad", "BAEMIN")을 하드코딩하지 마십시오. 모든 도메인은 설정값으로 주입되어야 합니다.
- **Direct Push to Core**: 코어 서버의 API를 빈번히 호출하여 통계를 밀어 넣지 마십시오. 흔적을 남기면 코어가 집계할 것입니다.
- **Zombie Neglect**: 죽은 ANT를 방치하지 마십시오. 72시간 수기 제한을 엄격히 적용하여 무덤(Purge)으로 보내십시오.

**총독은 전장(Domain)을 가리지 않으며, 오직 제국의 승리만을 위해 존재한다.**
