# VESS (Virtual Environment Stability System) 마스터 가이드

## 1. 개요 (Overview)
**VESS**는 Monewment 시스템의 실행 환경을 정의하고, 감시하며, 강제하는 **"Control Plane의 환경 권위(Environment Authority)"** 구현체입니다.
개발자나 배포 환경마다 상이한 라이브러리 버전으로 인해 발생하는 "Works on my machine" 문제를 원천 차단하고, 시스템의 불변성(Immutability)을 보장합니다.

### 핵심 철학
1.  **Immutable Law**: 환경 정의(`vess_manifest.json`)는 법이며, 절대 타협하지 않습니다.
2.  **Zero Drift**: 정의된 상태와 1바이트라도 다르면 시스템 실행이 차단됩니다.
3.  **Self-healing**: 오염된 환경은 복구(`heal`)되지 않으면 폐기되어야 합니다.

---

## 2. 아키텍처 (Architecture)

### 2.1. The Law (법전)
- **파일**: `vess_manifest.json`
- **역할**: 허용된 Python 런타임 버전, 필수 라이브러리 및 버전, 무결성 해시를 정의한 불변의 원장입니다.
- **위치**: 프로젝트 Root

### 2.2. The Enforcer (집행기)
- **스크립트**: `scripts/vess_doctor.py`
- **역할**: 현재 런타임 환경을 스캔하고 법전과 대조하여 **Drift(변조)**를 탐지합니다.
- **결과**: `PASS` (정상) 또는 `FAIL` (실행 차단).

### 2.3. The Controller (관리기)
- **스크립트**: `scripts/vess.ps1`
- **역할**: 사용자가 VESS와 상호작용하는 CLI(Command Line Interface)입니다. `lock`, `check`, `heal` 명령을 수행합니다.

---

## 3. 사용법 (Usage Guide)

VESS 컨트롤러는 PowerShell 스크립트로 제공됩니다. 모든 명령은 프로젝트 루트에서 실행해야 합니다.

```powershell
./scripts/vess.ps1 [COMMAND]
```

### 3.1. 무결성 검사 (Check)
현재 환경이 Manifest와 일치하는지 검사합니다. 배포 파이프라인이나 서버 시작 전 필수적으로 실행됩니다.

```powershell
./scripts/vess.ps1 check
```
- **성공 시**: `✅ [VESS] Integrity Verified.`
- **실패 시**: `❌ [VESS] DRIFT DETECTED.` (상세 오류 출력 후 종료 코드 1 반환)

### 3.2. 환경 고정 (Lock)
**[주의]** 현재의 개발 환경을 새로운 "표준(Standard)"으로 승격시킵니다. 시스템이 안정화된 상태에서만 관리자가 실행해야 합니다.

```powershell
./scripts/vess.ps1 lock
```
- 실행 시 현재 설치된 모든 패키지(`pip freeze`)와 Python 버전을 캡처하여 `vess_manifest.json`을 덮어씁니다.
- **Phase 3 검증(테스트 통과)**이 선행되어야 합니다.

### 3.3. 자가 치유 (Heal)
환경이 오염되었거나(`Check FAIL`), 초기 세팅이 필요한 경우 실행합니다.

```powershell
./scripts/vess.ps1 heal
```
- Manifest에 정의된 환경으로 시스템을 강제 동기화합니다.
- 현재는 `pip install`을 수행하지만, 향후 구현에서는 가상환경 재생성(Re-creation)을 포함할 수 있습니다.

---

## 4. 정책 상세 (Policies)

### Python Runtime
- **표준 버전**: **Python 3.11.x** (LTS)
- 3.14 등 불안정한 최신 버전 사용은 엄격히 금지됩니다. Major.Minor 버전 불일치 시 `Doctor`가 실행을 거부합니다.

### Dependency Management
- 모든 의존성은 `Exact Version Pinning` (예: `numpy==1.26.4`)을 원칙으로 합니다.
- `requirements.txt`는 개발 편의를 위한 파일이며, 최종 권위는 `vess_manifest.json`이 가집니다.

---

## 5. 문제 해결 (Troubleshooting)

**Q: `vess check`가 실패합니다.**
A:
1. `vess_doctor.py`가 출력하는 에러 메시지를 확인하십시오 (예: `Version Drift`).
2. 의도치 않은 패키지 업데이트가 있었다면 `./scripts/vess.ps1 heal`을 실행하여 복구하십시오.
3. 의도한 변경이라면, 테스트를 통과시킨 후 `./scripts/vess.ps1 lock`으로 매니페스트를 갱신하십시오.

**Q: Manifest 파일이 없습니다.**
A: 시스템이 초기화되지 않았습니다. `./scripts/vess.ps1 lock`을 실행하여 현재 환경을 기준으로 초기 Manifest를 생성하십시오.
