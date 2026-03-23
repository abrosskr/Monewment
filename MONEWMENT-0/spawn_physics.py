"""
spawn_physics.py — PHYSICS 자동 배포 스크립트
STRATUM 이 생성되면 이 스크립트로 PHYSICS-0 원형을 복제하고 설정을 주입합니다.

사용법:
  python spawn_physics.py --stratum-id <UUID> --queen-id <UUID> --name PHYSICS-1 --dest ./MONITOR/PHYSICS-1
  python spawn_physics.py --stratum-id <UUID> --queen-id <UUID> --name PHYSICS-1 --dest ./MONITOR/PHYSICS-1 --launch

옵션:
  --stratum-id    소속 영토 UUID (필수)
  --queen-id      함께 생성된 QUEEN UUID (필수)
  --name          이 PHYSICS 인스턴스의 이름 (기본값: PHYSICS-1)
  --dest          PHYSICS를 배포할 대상 폴더 경로 (필수)
  --core-host     제국 코어망 IP (기본값: 127.0.0.1)
  --core-port     제국 코어망 포트 (기본값: 8800)
  --launch        배포 후 즉시 worker_queen.py 실행
  --domain-handler 도메인 핸들러 클래스 경로 (기본값: domain.physics_domain.PhysicsDomain)
"""

# [DNA Linker Protocol]
import sys, os
from pathlib import Path
def link_dna():
    p = Path(__file__).resolve().parent
    while p.parent != p:
        if (p / "MONEWMENT-0").exists():
            sys.path.insert(0, str(p / "MONEWMENT-0"))
            return
        p = p.parent
link_dna()

import argparse
import shutil
import subprocess
import urllib.request
import psutil
import re
import uuid

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
                # cmdline에 대상 경로가 포함된 경우
                cmd = p.info.get('cmdline')
                if cmd and any(dest_str in str(arg).lower() for arg in cmd):
                    pids.append(p.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return pids

def load_existing_id(dest: Path) -> tuple[str | None, str | None]:
    """기존 .env 에서 PHYSICS_NAME 과 QUEEN_ID 등을 탐색"""
    env_path = dest / ".env"
    if not env_path.exists():
        return None, None
    try:
        content = env_path.read_text("utf-8")
        name = re.search(r"PHYSICS_NAME=(.*)", content)
        q_id = re.search(r"QUEEN_ID=(.*)", content)
        return (name.group(1).strip() if name else None, 
                q_id.group(1).strip() if q_id else None)
    except Exception:
        return None, None

def discover_parents(dest_path: Path) -> tuple[str | None, str | None]:
    """경로 기반 상위 STRATUM/QUEEN 정보 탐색 (가장 정확한 .env 기반)"""
    # 1. 탐색 경로: 현재 작업 디렉토리, 스크립트 위치, 제국 루트
    search_dirs = [Path.cwd(), SCRIPT_DIR, IMPERIAL_ANCHOR, SCRIPT_DIR.parent]
    
    # 2. 형제 및 부모 디렉토리의 STRATUM 폴더 탐색
    for base in search_dirs:
        # STRATUM 폴더 내부의 STRATUM-* 또는 루트의 STRATUM-* 탐색
        candidates = list(base.glob("STRATUM-*")) + list(base.glob("STRATUM/STRATUM-*"))
        for p in candidates:
            if not p.is_dir(): continue
            env = p / ".env"
            if env.exists():
                content = env.read_text("utf-8")
                s_id = re.search(r"STRATUM_ID=(.*)", content)
                q_id = re.search(r"QUEEN_ID=(.*)", content)
                if s_id and q_id:
                    print(f"  [DISCOVERY] 상위 영토 감지: {p.name} (Stratum: {s_id.group(1)[:8]}...)")
                    return s_id.group(1).strip(), q_id.group(1).strip()
    return None, None

# --- Dynamic Path Discovery (Termination of Rigidity) ---
IMPERIAL_ANCHOR = Path(__file__).resolve().parent
# If spawn_physics.py is in MONEWMENT-0, anchor is parent.
if (IMPERIAL_ANCHOR / "MONEWMENT-0").exists():
    pass
else:
    # Try to find it upwards
    p = IMPERIAL_ANCHOR
    while p.parent != p:
        if (p / "MONEWMENT-0").exists():
            IMPERIAL_ANCHOR = p
            break
        p = p.parent

# ─── Layer 2: Spawn Validation ──────────────────────────────────────────────────
try:
    from core.path_discovery import discover_imperial_anchor, sanitize_and_inject_path
    IMPERIAL_ANCHOR = discover_imperial_anchor()
    sanitize_and_inject_path()
    from core.spawn_validator import validate_spawn_or_kill as _validate_spawn
    _HAS_VALIDATOR = True
except ImportError:
    _HAS_VALIDATOR = False
    IMPERIAL_ANCHOR = Path(__file__).resolve().parent

# ─── 경로 설정 ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent

TEMPLATE_CANDIDATES = [
    IMPERIAL_ANCHOR / "templates" / "PHYSICS-0",
    IMPERIAL_ANCHOR / "MONEWMENT-0" / "templates" / "PHYSICS-0",
]

def find_template() -> Path:
    for candidate in TEMPLATE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("PHYSICS-0 원형을 찾을 수 없습니다.")

def inject_env(dest: Path, args: argparse.Namespace, gateway_token: str):
    """.env 에 인스턴스 정보 주입 (Bulletproof Overlay)"""
    target_env = dest / ".env"
    env_vars = {}
    
    if target_env.exists():
        try:
            for line in target_env.read_text("utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
        except Exception:
            pass

    # 필수 값 강제 주입
    env_vars["CORE_HOST"] = str(args.core_host)
    env_vars["PORT_CORE_API"] = str(args.core_port)
    env_vars["GATEWAY_TOKEN"] = str(gateway_token)
    env_vars["STRATUM_ID"] = str(args.stratum_id)
    env_vars["QUEEN_ID"] = str(args.queen_id)
    env_vars["PHYSICS_NAME"] = str(args.name)
    env_vars["PHYSICS_ID"] = str(args.physics_id)
    env_vars["DOMAIN_HANDLER"] = str(args.domain_handler)
    env_vars["LOCAL_REGISTRY_PATH"] = "local_registry.db"
    
    # 기본값 보전 (없을 때만 추가)
    if "POLL_INTERVAL_SEC" not in env_vars: env_vars["POLL_INTERVAL_SEC"] = "60"
    if "BATCH_SIZE" not in env_vars: env_vars["BATCH_SIZE"] = "20"

    with open(target_env, "w", encoding="utf-8") as f:
        f.write("# PHYSICS 인스턴스 환경 설정\n")
        for k, v in sorted(env_vars.items()):
            f.write(f"{k}={v}\n")
    
    print(f"  [OK] .env 주입 완료 → {target_env}")

def _read_local_gov_token(script_dir: Path) -> str:
    search = [script_dir / ".env", script_dir.parent / "MONEWMENT-0" / ".env"]
    for p in search:
        if not p.exists(): continue
        for line in p.read_text("utf-8").splitlines():
            if line.startswith("LOCAL_GOV_TOKEN="):
                return line.split("=", 1)[1].strip()
    return "mon_local_gov_token_default"

def read_gateway_token() -> str:
    search_paths = [IMPERIAL_ANCHOR / ".env", IMPERIAL_ANCHOR / "MONEWMENT-0" / ".env"]
    for env_path in search_paths:
        if not env_path.exists(): continue
        for line in env_path.read_text("utf-8").splitlines():
            if line.startswith("GATEWAY_TOKEN="):
                return line.split("=", 1)[1].strip()
    return "FILL_ME_IN"

def sanctify_id(oid: str, label: str) -> str:
    """[SPAWNER UUID SANCTIFICATION] Mandate v3.0"""
    try:
        uuid.UUID(oid)
        return oid
    except ValueError:
        print(f"  [ERROR] 불결한 식별자 감지 ({label}): {oid}")
        print(f"  [DECREE] 유효한 UUIDv4 형식을 사용하십시오.")
        sys.exit(1)

def spawn_physics(args: argparse.Namespace):
    # 0. Discovery (부모 영토 탐색 - Sanctification 완료 전 임시 ID 허용)
    dest = Path(args.dest).resolve()
    print("=" * 60)
    print(f"  [START] PHYSICS 배포 대기: {dest}")

    if args.stratum_id == "UNKNOWN" or args.queen_id == "UNKNOWN":
        d_stratum, d_queen = discover_parents(dest)
        if d_stratum:
            args.stratum_id = d_stratum
            args.queen_id = d_queen
        else:
            print("  [ERROR] 상위 영토(STRATUM) 정보를 찾을 수 없습니다. --stratum-id 를 명시하세요.")
            sys.exit(1)

    # [SANCTIFICATION] Discovery 이후 최종 UUID 유효성 검증
    args.stratum_id = sanctify_id(args.stratum_id, "STRATUM_ID")
    args.queen_id = sanctify_id(args.queen_id, "QUEEN_ID")

    print(f"  STRATUM → {args.stratum_id}")
    print(f"  QUEEN   → {args.queen_id}")
    print("=" * 60)

    # 1. 로컬 식별자 결정 (Persistence Check)
    existing_name, existing_queen = load_existing_id(dest)
    
    # [V51.5] PHYSICS_ID 추출 (기존 .env 에서)
    existing_physics_id = None
    if (dest / ".env").exists():
        env_content = (dest / ".env").read_text("utf-8")
        match = re.search(r"PHYSICS_ID=(.*)", env_content)
        if match:
            existing_physics_id = match.group(1).strip()

    if existing_physics_id:
        entity_id = existing_physics_id
        print(f"  [REUSE] 기존 PHYSICS_ID를 계승합니다: {entity_id}")
    else:
        entity_id = str(uuid.uuid4())
        print(f"  [NEW] 새 로컬 식별자 확정 (UUID: {entity_id})")

    official_name = args.name or existing_name or f"PHYSICS-{entity_id[:4].upper()}"
    args.name = official_name
    args.physics_id = entity_id

    # 2. 원형 탐색
    template = find_template()
    print(f"  [OK] 원형 발견: {template}")

    # 3. 프로세스 체크 및 복제
    running_pids = get_running_pids(dest)
    if running_pids:
        print(f"  [ALIVE] 대상 영토에 이미 활성 프로세스가 존재합니다: PID {running_pids}")
        if not args.force:
            print("  [ERROR] 프로세스가 실행 중이므로 배포를 진행할 수 없습니다. (PermissionError 방지)")
            sys.exit(1)
        else:
            print(f"  [FORCE] 활성 프로세스 강제 종료 시도...")
            for pid in running_pids:
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                except Exception: pass

    # 배포 모드 결정
    mode = "y" # New
    if dest.exists():
        if not args.force:
            print(f"  [ALREADY EXISTS] 대상 영토가 이미 존재합니다. (설정 자동 갱신 및 기동)")
            mode = "s"
        else:
            print(f"  [FORCE] 기존 영토를 정화하고 재배포합니다.")
            shutil.rmtree(dest, ignore_errors=True)
            mode = "y"

    # [HEALING / REPLICATION]
    core_src = IMPERIAL_ANCHOR / "core"
    core_dest = dest / "core"

    if mode == "y":
        print(f"  [DNA] 원형 복제 중...")
        shutil.copytree(template, dest, ignore=shutil.ignore_patterns("__pycache__", ".env"), dirs_exist_ok=True)
        shutil.copytree(core_src, core_dest, dirs_exist_ok=True)
    else: # 's' 모드
        print(f"  [HEAL] core 라이브러리 상태 확인 및 동기화...")
        try:
            shutil.copytree(core_src, core_dest, dirs_exist_ok=True)
        except Exception as e:
            print(f"  [WARN] 동기화 중 일부 파일 잠김 (건너뜀): {e}")

    # 4. 설정 주입
    token = read_gateway_token()
    inject_env(dest, args, token)

    # 5. 검증 (Layer 2)
    if _HAS_VALIDATOR:
        local_gov_token = _read_local_gov_token(SCRIPT_DIR)
        ok = _validate_spawn(
            gateway_base=f"http://{args.core_host}:{args.core_port}/v1/registry",
            entity_type="ant",
            entity_id=entity_id,
            instance_path=dest,
            expected_files=[".env", "worker_physics.py"],
            local_gov_token=local_gov_token,
            gateway_token=token,
        )
        if ok:
            print("  [INTEGRITY] Spawn Validator: 무결성 확인 - 정상")
        else:
            print("  [INTEGRITY] Spawn Validator: 무결성 검증 실패!")
            sys.exit(1)

    print()
    print(f"  [OK] {args.name} 배포 완료!")
    print(f"  실행: cd {dest} && python worker_physics.py")
    print("=" * 60)

    if args.launch:
        print(f"\n  [LAUNCH] --launch 감지: {args.name} 즉시 기동...")
        os.chdir(dest)
        subprocess.run([sys.executable, "worker_physics.py"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PHYSICS-0 원형 배포")
    parser.add_argument("--stratum-id",  default="UNKNOWN", help="소속 영토 UUID (미지정 시 자동 탐색)")
    parser.add_argument("--queen-id",    default="UNKNOWN", help="동반 QUEEN UUID (미지정 시 자동 탐색)")
    parser.add_argument("--name",        default="PHYSICS-1")
    parser.add_argument("--dest",        required=True)
    parser.add_argument("--core-host",   default="127.0.0.1")
    parser.add_argument("--core-port",   default=8800, type=int)
    parser.add_argument("--domain-handler", default="domain.physics_domain.PhysicsDomain")
    parser.add_argument("--launch",      action="store_true")
    parser.add_argument("--force",       action="store_true")

    args = parser.parse_args()
    spawn_physics(args)
