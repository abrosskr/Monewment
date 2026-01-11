
# 프로젝트 과금 시스템 사용 가이드 (CCTV)

## 1. 개요
이 기능은 Monewment의 최종 사용자(프로젝트 오너)에게 제공되는 **과금 및 미터링 시스템**을 시뮬레이션합니다. 클라우드 서비스(AWS, Azure 등)의 대시보드처럼, 가상머신(VM)과 AI 모델 사용량에 따라 비용이 실시간으로 누적되는 과정을 시각적으로 보여줍니다.

> **주의:** 이 시스템은 Monewment 내 프로젝트들의 **가상 비용**을 추적합니다. 사용자가 현재 Antigravity AI를 사용하면서 발생하는 실제 토큰 비용과는 무관합니다.

## 2. 구성 요소
1.  **과금 모델 (Billing Models):** `vm_usage`(사용 이력), `subscription_plans`(요금제) 등 데이터베이스 테이블.
2.  **미터링 서비스 (Metering Service):** VM 실행/종료 시 시간을 기록하고 비용을 계산하는 백엔드 로직.
3.  **CCTV 모니터:** 실시간으로 업데이트되는 마크다운 대시보드 파일 (`docs/LIVE_USAGE.md`).

## 3. 사용 방법

### 1단계: CCTV 모니터 켜기
터미널에서 아래 명령어를 실행하여 백그라운드 감시 시스템을 시작합니다.
(이미 실행 중이라면 건너뛰세요.)

```powershell
python scripts/usage_cctv.py
```

이 터미널은 켜둔 상태로 유지하세요. 2초마다 데이터베이스를 조회하여 현황판을 갱신합니다.

### 2단계: 대시보드 보기
VSCode에서 `docs/LIVE_USAGE.md` 파일을 엽니다.
**미리보기(Preview) 패널**을 엽니다 (단축키: `Ctrl+K` 누른 후 `V`).

**확인 가능한 정보:**
- 현재 가동 중인 VM 숫자
- 전체 누적 매출
- 프로젝트별 예산 및 남은 크레딧 (🔴/🟢 상태 표시)
- AI 엔진별(GPT-4, Claude 등) 사용량 통계

### 3단계: 사용량 발생시키기 (시뮬레이션)
수치 변화를 보기 위해서는 실제로 VM을 생성하거나 사용하는 동작이 필요합니다.

**방법 A: 검증 스크립트 실행 (API 서버 필요)**
API 서버(`start_monewment.ps1`)가 켜져 있다면, 별도 터미널에서 다음을 실행하세요:
```powershell
python scripts/verify_metering.py
```

**방법 B: 파이썬 코드로 직접 주입**
개발 중이라면 `MeteringService`를 직접 호출하여 테스트할 수 있습니다:

```python
from src.database import SessionLocal
from src.services.metering import MeteringService

db = SessionLocal()
service = MeteringService(db)

# 세션 시작 (예: VM 1번이 GPT-4 모델 사용 시작)
session = service.start_session(vm_id=1, ai_model_id=1)

# ... 시간 경과 ...

# 세션 종료 (비용 정산)
service.end_session(vm_id=1)
```

## 4. 문제 해결
- **CCTV가 멈췄어요:** `usage_cctv.py`가 실행 중인 터미널이 닫혔는지 확인하세요. 에러가 발생했다면 `python scripts/fix_db_schema.py`를 실행하여 DB 구조를 최신화해보세요.
- **데이터가 안 보여요:** 초기 데이터가 없다면 `python scripts/init_metering_db.py`를 실행하여 요금제 정보를 생성하세요.
