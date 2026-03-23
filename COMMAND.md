# ═══════════════════════════════════════════════════════════════
#   MONEWMENT — CORE COMMAND REFERENCE (V51.5 MODERNIZED)
#   Centralized Dispatcher: STRATUM-1 | Master DNA: MONEWMENT-0
# ═══════════════════════════════════════════════════════════════

# 💡 필수: 모든 명령어 실행 전 PYTHONPATH 설정 (MONEWMENT-0 Core 참조 준수)
# Windows: set PYTHONPATH=C:\monewment\MONEWMENT-0;%PYTHONPATH%
# PowerShell: $env:PYTHONPATH="C:\monewment\MONEWMENT-0;$env:PYTHONPATH"

# ─── [1] COMMAND & CONTROL: STRATUM-1 제국 본영 ────────────────
# 위치: c:/monewment/STRATUM/STRATUM-1/

# [PRIMARY ENTRY POINT] 메인 디스패처 서버 시동 (Port 8800)
# 주의: MONEWMENT-0/main.py를 직접 실행하지 마십시오.
cd c:/monewment/STRATUM/STRATUM-1; python start.py

# 통합 지휘 및 자가 복구 가동 (Panopticon Sentinel)
cd c:/monewment/STRATUM/STRATUM-1; python panopticon_sentinel.py

# ─── [2] INTELLIGENCE: REX 지능 증류 엔진 (Singleton) ────────
# 위치: c:/monewment/REX/CORE/

# 유일 지능 엔진 시동 (Singleton REX)
cd c:/monewment/REX/CORE; python main.py

# ─── [3] SPAWNING: 워커 소환 및 배포 (Consolidated IDs) ────────
# 위치: c:/monewment/MONEWMENT-0/
# STRATUM_ID: 3bb565af-e01a-49b8-af27-049e6a642f2d
# QUEEN_ID:   ba537759-f607-4eda-841c-eeba65a5147b

### 1. AREUM Analyst Deployment (ANALYSIS)
- **명령어**: `python spawn_areum.py --dest <PATH> [--name <NAME>] [--launch]`
- **특징**: 이제 `--stratum-id`와 `--queen-id`를 생략할 수 있으며, 스포너가 주변 환경에서 부모 영토 정보를 자동으로 탐색(Discovery)합니다.
- **예시**: `python spawn_areum.py --dest ../AREUM/AREUM-1 --launch`

### 2. PHYSICS Monitor Deployment (MONITORING)
- **명령어**: `python spawn_physics.py --dest <PATH> [--name <NAME>] [--launch]`
- **특징**: AREUM과 마찬가지로 부모 식별자를 자동으로 탐색합니다. 기존 폴더가 있을 경우 자동으로 구성을 동기화하고 DNA 정합성을 유지하며 기동합니다.
- **예시**: `python spawn_physics.py --dest ../PHYSICS/PHYSICS-1 --launch`

# ─── [4] MAINTENANCE: 제국 정비 및 유령 제거 ────────────────
# 위치: c:/monewment/

# 유령 및 좀비 프로세스/DB 레코드 정리
cd c:/monewment; python purge_ghosts.py

# 제국 통합 대시보드 및 브로드캐스트
cd c:/monewment/MONEWMENT-0; python imperial_dashboard.py
cd c:/monewment/MONEWMENT-0; python broadcast_update.py

# ─── [!] 필수 확인 규약 ──────────────────────────────────────
# 1. 모든 수평 통신(Push)은 금등됨. 워커는 자신의 local_registry.db에 기록.
# 2. 본영(STRATUM-1)의 Scout mission이 60초 주기로 데이터를 수집함.
# ═══════════════════════════════════════════════════════════════



taskkill /F /IM python.exe /T


cd C:\monewment\STRATUM\STRATUM-1
python .\start.py


cd C:\monewment\REX\CORE
python .\main.py

cd C:\monewment\AREUM\AREUM-1
python .\worker_areum.py


cd C:\monewment\PHYSICS\PHYSICS-1
python .\worker_physics.py


바벨 확인 
cd C:\monewment\BABEL\CORE
python .\main.py


cd C:\monewment\BABEL\CORE
python .\run_inception.py

cd C:\monewment\STRATUM\STRATUM-1



cd C:\monewment\DASHBOARD\CORE
python .\main.py