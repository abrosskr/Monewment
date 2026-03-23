"""
spawn_areum.py — AREUM 자동 배포 스크립트
STRATUM 이 생성되면 이 스크립트로 AREUM-0 원형을 복제하고 설정을 주입합니다.

사용법:
  python spawn_areum.py --stratum-id <UUID> --queen-id <UUID> --name AREUM-1 --dest ./FORAGER/AREUM-1
  python spawn_areum.py --stratum-id <UUID> --queen-id <UUID> --name AREUM-2 --dest ./STRATUM-NOVEL/AREUM-2 --launch

옵션:
  --stratum-id    소속 영토 UUID (탄생 성사에 필요, 필수)
  --queen-id      함께 생성된 QUEEN UUID (필수)
  --name          이 AREUM 인스턴스의 이름 (기본값: AREUM-1)
  --dest          AREUM을 배포할 대상 폴더 경로 (필수)
  --core-host     제국 코어망 IP (기본값: 127.0.0.1)
  --core-port     제국 코어망 포트 (기본값: 8800)
  --model         사용할 Ollama 모델 (기본값: gemma3:4b)
  --launch        배포 후 즉시 worker_areum.py 실행
"""

import argparse
import shutil
import subprocess
import sys
import os
import json
import urllib.request
from pathlib import Path
import psutil
import re

def get_running_pids(dest_path: Path):
    """지정된 경로를 CWD로 하거나 worker_*.py를 실행 중인 프로세스 탐색"""
    pids = []
    try:
        dest_str = str(dest_path.resolve()).lower()
        for p in psutil.process_iter(['pid', 'name', 'cwd', 'cmdline']):
            try:
                # CWD가 대상 경로인 경우
                cwd = p.info.get('cwd')
                if cwd and str(Path(cwd).resolve()).lower() == dest_str:
                    pids.append(p.info['pid'])
                    continue
                
                # cmdline에 대상 경로가 포함된 경우 (worker_areum.py 등)
                cmd = p.info.get('cmdline')
                if cmd and any(dest_str in str(arg).lower() for arg in cmd):
                    pids.append(p.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return pids

def load_existing_id(dest: Path) -> tuple[str | None, str | None, str | None]:
    """기존 .env 에서 AREUM_NAME 과 STRATUM_ID/QUEEN_ID 등을 탐색 (재조명용)"""
    env_path = dest / ".env"
    if not env_path.exists():
        return None, None, None
    
    try:
        content = env_path.read_text("utf-8")
        name = re.search(r"AREUM_NAME=(.*)", content)
        s_id = re.search(r"STRATUM_ID=(.*)", content)
        a_id = re.search(r"AREUM_ID=(.*)", content)
        return (name.group(1).strip() if name else None, 
                s_id.group(1).strip() if s_id else None,
                a_id.group(1).strip() if a_id else None)
    except Exception:
        return None, None, None

def discover_parents(dest_path: Path) -> tuple[str | None, str | None]:
    """경로 기반 상위 STRATUM/QUEEN 정보 탐색 (.env 기반)"""
    # 1. 탐색 경로: 대상 폴더 상위, 현재 작업 디렉토리, 스크립트 상위 디렉토리
    search_dirs = [dest_path.parent, Path.cwd(), SCRIPT_DIR.parent]
    
    # 2. 형제 및 부모 디렉토리의 STRATUM 폴더 탐색
    for base in search_dirs:
        # STRATUM/STRATUM-1 형식과 STRATUM-1 형식을 모두 탐색
        candidates = list(base.glob("STRATUM-*")) + list(base.glob("STRATUM/STRATUM-*"))
        for p in candidates:
            env = p / ".env"
            if env.exists():
                content = env.read_text("utf-8")
                s_id = re.search(r"STRATUM_ID=(.*)", content)
                q_id = re.search(r"QUEEN_ID=(.*)", content)
                if s_id and q_id:
                    print(f"  [DISCOVERY] 상위 영토 감지: {p.name} (Stratum: {s_id.group(1)[:8]}...)")
                    return s_id.group(1).strip(), q_id.group(1).strip()
    return None, None

# ─── Layer 2: Zero-Entropy Spawn Validation ────────────────────────────────────
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from core.spawn_validator import validate_spawn_or_kill as _validate_spawn
    _HAS_VALIDATOR = True
except ImportError:
    _HAS_VALIDATOR = False

# ─── 경로 설정 ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent

# 제국 규약 제1장: 모든 원형 템플릿은 오직 MONEWMENT-0 내부에만 존재해야 한다.
TEMPLATE_CANDIDATES = [
    SCRIPT_DIR / "templates" / "AREUM-0",                         # 스크립트가 MONEWMENT-0 내부에 있을 때
    SCRIPT_DIR.parent / "MONEWMENT-0" / "templates" / "AREUM-0",  # 프로젝트 최상단 기준
]

def find_template() -> Path:
    for candidate in TEMPLATE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "AREUM-0 원형을 찾을 수 없습니다. MONEWMENT-0 또는 EDENVALE 경로를 확인하세요.\n"
        f"탐색 위치: {[str(c) for c in TEMPLATE_CANDIDATES]}"
    )

def inject_env(dest: Path, args: argparse.Namespace, gateway_token: str):
    """.env 에 인스턴스 정보 주입 (Bulletproof Overlay)"""
    target_env = dest / ".env"
    env_vars = {}
    
    # 1. 기존 값 로드
    if target_env.exists():
        try:
            for line in target_env.read_text("utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
        except Exception as e:
            print(f"  [WARN] 기존 .env 파싱 실패 (초기화 진행): {e}")

    # 2. 필수 값 강제 주입/갱신
    env_vars["CORE_HOST"] = str(args.core_host)
    env_vars["CORE_PORT"] = str(args.core_port)
    env_vars["PORT_CORE_API"] = str(args.core_port)
    env_vars["GATEWAY_TOKEN"] = str(gateway_token)
    env_vars["STRATUM_ID"] = str(args.stratum_id)
    env_vars["QUEEN_ID"] = str(args.queen_id)
    env_vars["AREUM_NAME"] = str(args.name)
    env_vars["AREUM_ID"] = str(args.areum_id)
    env_vars["OLLAMA_MODEL"] = str(args.model)

    # 3. 저장
    with open(target_env, "w", encoding="utf-8") as f:
        f.write("# AREUM 인스턴스 환경 설정\n")
        for k, v in sorted(env_vars.items()):
            f.write(f"{k}={v}\n")
    
    print(f"  [OK] .env 주입 완료 → {target_env}")

def inject_yaml(dest: Path, args: argparse.Namespace):
    """config/areum.yaml 에 인스턴스 정보 주입 (Regex 기반 Overlay)"""
    yaml_path = dest / "config" / "areum.yaml"
    if not yaml_path.exists():
        return

    content = yaml_path.read_text("utf-8")
    replacements = {
        "areum_name": args.name,
        "stratum_id": args.stratum_id,
        "queen_id":   args.queen_id,
        "host":       args.core_host,
        "port":       args.core_port,
        "model":      args.model,
    }
    
    for key, val in replacements.items():
        # simple yaml key: val replacement
        pattern = rf"{key}:\s*.*"
        if isinstance(val, int):
            new_line = f"{key}: {val}"
        else:
            new_line = f'{key}: "{val}"'
        content = re.sub(pattern, new_line, content)

    yaml_path.write_text(content, "utf-8")
    print(f"  [OK] areum.yaml 주입 완료 → {yaml_path}")

def _read_local_gov_token(script_dir: Path) -> str:
    search = [
        script_dir / ".env",
        script_dir.parent / "MONEWMENT-0" / ".env",
    ]
    for p in search:
        if not p.exists():
            continue
        for line in p.read_text("utf-8").splitlines():
            if line.startswith("LOCAL_GOV_TOKEN="):
                return line.split("=", 1)[1].strip()
    return "mon_local_gov_token_default"


def _validate_spawn_integrity(args, entity_id: str, dest: Path, token: str):
    """Layer 2: Spawn Integrity Validator 연동 (Partial-Spawn 엔트로피 자동 방지)"""
    if not _HAS_VALIDATOR:
        print("  [WARN] spawn_validator 모듈 미제돔 - 검증 스킵")
        return
    local_gov_token = _read_local_gov_token(SCRIPT_DIR)
    ok = _validate_spawn(
        gateway_base=f"http://{args.core_host}:{args.core_port}/v1/registry",
        entity_type="areum",
        entity_id=entity_id,
        instance_path=dest,
        expected_files=[".env", "worker_areum.py"],
        local_gov_token=local_gov_token,
        gateway_token=token,
    )
    if ok:
        print("  [INTEGRITY] Spawn Validator: 무결성 확인 - 정상")
    else:
        print("  [INTEGRITY] Spawn Validator: Partial-Spawn 탐지! DB 사망 처리 완료.")
        sys.exit(1)

def read_gateway_token(core_host: str, core_port: int) -> str:
    """제국 코어망의 .env 에서 GATEWAY_TOKEN 을 자동 탐색"""
    search_paths = [
        SCRIPT_DIR / ".env",
        SCRIPT_DIR.parent / "EDENVALE" / ".env",
        SCRIPT_DIR.parent / "MONEWMENT-0" / ".env",
    ]
    for env_path in search_paths:
        if not env_path.exists():
            continue
        for line in env_path.read_text("utf-8").splitlines():
            if line.startswith("GATEWAY_TOKEN="):
                token = line.split("=", 1)[1].strip()
                if token:
                    print(f"  [AUTO] GATEWAY_TOKEN 탐지: {env_path.parent.name}/.env")
                    return token
    print("  [WARN] GATEWAY_TOKEN 자동 탐지 실패. .env에 직접 입력하세요.")
    return "FILL_ME_IN"

import uuid
def sanctify_id(oid: str, label: str) -> str:
    """[SPAWNER UUID SANCTIFICATION] Mandate v3.0"""
    try:
        uuid.UUID(oid)
        return oid
    except ValueError:
        print(f"  [ERROR] 불결한 식별자 감지 ({label}): {oid}")
        print(f"  [DECREE] 유효한 UUIDv4 형식을 사용하십시오.")
        sys.exit(1)

def spawn_areum(args: argparse.Namespace):
    dest = Path(args.dest).resolve()
    print("=" * 60)
    print(f"  [START] AREUM 배포 대기: {dest}")
    
    # 0. Discovery (부모 영토 탐색)
    if args.stratum_id == "UNKNOWN" or args.queen_id == "UNKNOWN":
        d_stratum, d_queen = discover_parents(dest)
        if d_stratum:
            args.stratum_id = d_stratum
            args.queen_id = d_queen
        else:
            print("  [ERROR] 상위 영토(STRATUM) 정보를 찾을 수 없습니다. --stratum-id 를 명시하세요.")
            sys.exit(1)

    # UUID Sanctification
    args.stratum_id = sanctify_id(args.stratum_id, "STRATUM_ID")
    args.queen_id = sanctify_id(args.queen_id, "QUEEN_ID")

    print(f"  STRATUM → {args.stratum_id}")
    print(f"  QUEEN   → {args.queen_id}")
    print("=" * 60)

    # 0. 로컬 식별자 결정 (Decoupling: No upward birth call)
    dest = Path(args.dest).resolve()
    existing_name, existing_stratum, existing_areum_id = load_existing_id(dest)
    
    if existing_areum_id:
        entity_id = existing_areum_id
        print(f"  [REUSE] 기존 AREUM_ID를 계승합니다: {entity_id}")
    else:
        entity_id = str(uuid.uuid4())
        print(f"  [NEW] 새 로컬 식별자 확정 (UUID: {entity_id})")

    official_name = getattr(args, 'name', None) or existing_name or f"AREUM-{entity_id[:4].upper()}"
    args.name = official_name
    args.areum_id = entity_id

    # 1. 원형 탐색
    template = find_template()
    print(f"  [OK] 원형 발견: {template}")

    # 2. 복제
    dest = Path(args.dest).resolve()
    running_pids = get_running_pids(dest)
    
    if running_pids:
        print(f"  [ALIVE] 대상 영토에 이미 활성 프로세스가 존재합니다: PID {running_pids}")
        if not args.force:
            print("  [ERROR] 프로세스가 실행 중이므로 배포를 진행할 수 없습니다. (PermissionError 방지)")
            print("  [TIP] 먼저 프로세스를 종료하거나 --force 옵션을 사용하세요.")
            sys.exit(1)
        else:
            print(f"  [FORCE] 활성 프로세스 강제 종료 시도 (PID: {running_pids})...")
            for pid in running_pids:
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                except Exception as e:
                    print(f"  [WARN] 종료 실패 (PID {pid}): {e}")

    # [DEPLOYMENT LOGIC]
    mode = "y"
    if dest.exists():
        if not args.force:
            print(f"  [ALREADY EXISTS] 대상 영토가 이미 존재합니다. (설정 자동 갱신 및 기동)")
            mode = "s"
        else:
            print(f"  [FORCE] 기존 영토를 정화(삭제)하고 재배포합니다.")
            import time
            for _ in range(5): 
                try:
                    shutil.rmtree(dest)
                    break
                except PermissionError:
                    time.sleep(1)
                except Exception: break
            mode = "y"
    else:
        mode = "y"

    # [HEALING] 물리적 무결성 보완 (Idempotent Healing)
    core_src = SCRIPT_DIR / "core"
    core_dest = dest / "core"
    
    if mode == "s":
        print(f"  [HEAL] core 라이브러리 상태 확인 및 동기화...")
        try:
            shutil.copytree(core_src, core_dest, dirs_exist_ok=True)
        except PermissionError:
            print(f"  [ALIVE] 영토 파일이 시스템에 의해 잠겨 있습니다. 동기화를 건너뜁니다.")
        except Exception as e:
            print(f"  [WARN] 동기화 중 오류 발생 (무시하고 진행): {e}")
    elif mode == "y":
        print(f"  [DNA] 원형 복제 중...")
        shutil.copytree(template, dest, ignore=shutil.ignore_patterns("__pycache__", ".env"))
        shutil.copytree(core_src, core_dest, dirs_exist_ok=True)

    # 3. GATEWAY_TOKEN 탐색
    token = read_gateway_token(args.core_host, args.core_port)

    # 4. 설정 주입
    # args.name이 없으므로, getattr 오류 방지를 위해 런타임 주입된 official_name을 명시적으로 전달
    setattr(args, 'name', dest.name) if not hasattr(args, 'name') else None 
    inject_env(dest, args, token)
    inject_yaml(dest, args)

    # [Layer 2] Spawn Integrity Validation
    _validate_spawn_integrity(args, entity_id, dest, token)

    print()
    print(f"  [OK] {getattr(args, 'name', 'AREUM')} 배포 완료!")
    print(f"  실행: cd {dest} && python worker_areum.py")
    print("=" * 60)

    # 5. --launch 플래그 시 즉시 실행
    if args.launch:
        print(f"\n  [LAUNCH] --launch 감지: {getattr(args, 'name', 'AREUM')} 즉시 기동...")
        os.chdir(dest)
        subprocess.run([sys.executable, "worker_areum.py"])


def main():
    parser = argparse.ArgumentParser(
        description="AREUM-0 원형을 지정 위치에 복제하고 인스턴스를 배포합니다."
    )
    parser.add_argument("--stratum-id",  default="UNKNOWN", help="소속 영토 UUID (미지정 시 자동 탐색)")
    parser.add_argument("--queen-id",    default="UNKNOWN", help="동반 QUEEN UUID (미지정 시 자동 탐색)")
    parser.add_argument("--is-ally",     action="store_true", help="외부 연합망(ALLY) 소속 AREUM 여부")
    parser.add_argument("--dest",        required=True,  help="배포 대상 폴더 경로")
    parser.add_argument("--core-host",   default="127.0.0.1", help="코어망 IP")
    parser.add_argument("--core-port",   default=8800, type=int, help="코어망 포트 (기본값: 8800)")
    parser.add_argument("--model",       default="gemma3:4b", help="Ollama 모델 (기본값: gemma3:4b)")
    parser.add_argument("--name",        help="AREUM 인스턴스 명칭 (기본값: 자동 생성)")
    parser.add_argument("--launch",      action="store_true",  help="배포 후 즉시 워커 실행")
    parser.add_argument("--force",       action="store_true",  help="기존 디렉토리가 있을 경우 묻지 않고 덮어씁니다.")

    args = parser.parse_args()
    spawn_areum(args)

if __name__ == "__main__":
    main()
