"""
start.py — STRATUM-1 Imperial Core 시동 스크립트
시작 전 .env 파일의 필수 키(CCTV_SECRET, GATEWAY_TOKEN)를 자동 생성하고
Uvicorn 으로 서버를 시작합니다.

사용법:
    python start.py
    python start.py --port 8800     (포트 오버라이드)
    python start.py --check-only    (시작 없이 환경 점검만)
"""
import secrets
import sys
import os
os.environ['TZ'] = 'Asia/Seoul'
import subprocess
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"
SERVER_PORT = 8800  # Standardized Imperial Core Port

# 필수 키 목록: (env_key, 설명, 자동생성 가능 여부)
REQUIRED_KEYS: list[tuple[str, str, bool]] = [
    ("SUPABASE_USER",     "Supabase 사용자명",       False),
    ("SUPABASE_PASSWORD", "Supabase 비밀번호",       False),
    ("SUPABASE_HOST",     "Supabase 호스트 주소",    False),
    ("CCTV_SECRET",       "CCTV 인증 비밀키",        True),   # 자동 생성
    ("GATEWAY_TOKEN",     "Gateway X-Queen-Token",   True),   # 자동 생성
]


def load_env() -> dict[str, str]:
    """현재 .env 를 파싱하여 dict 반환"""
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def save_key(key: str, value: str) -> None:
    """기존 .env 에 key=value 를 추가 (없는 경우에만)"""
    with open(ENV_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{key}={value}\n")
    print(f"  [AUTO] {key} 자동 생성 및 .env 에 저장됨.")


def preflight_check() -> bool:
    """
    시동 전 환경 점검.
    - 자동 생성 가능한 키는 생성
    - 수동 설정이 필요한 키가 빠져 있으면 False 반환
    """
    print("=" * 60)
    print("  STRATUM-1 Imperial Core Pre-Flight Environment Check")
    print("=" * 60)

    current_env = load_env()
    missing_manual: list[str] = []

    for key, desc, auto_gen in REQUIRED_KEYS:
        if key in current_env and current_env[key]:
            print(f"  [OK]   {key} ({desc})")
        elif auto_gen:
            new_val = secrets.token_urlsafe(32)
            save_key(key, new_val)
        else:
            print(f"  [FAIL] {key} ({desc}) - Please set this in .env manually.")
            missing_manual.append(key)

    if missing_manual:
        print()
        print("  !! Manual configuration required for:")
        for k in missing_manual:
            print(f"     {k}=<your_value>  → {ENV_FILE}")
        print()
        return False

    print()
    print("  OK: All environment variables verified.")
    print("=" * 60)
    return True


def start_server(port: int = SERVER_PORT) -> None:
    """Uvicorn 으로 STRATUM-1 Imperial Core 서버를 시작합니다."""
    stratum1_dir = Path(__file__).resolve().parent
    
    print(f"\n  [IGNITION] Starting STRATUM-1 Imperial Core on port {port}...")
    
    # [ARCHITECTURE] Standard environment
    current_env = os.environ.copy()

    os.chdir(stratum1_dir)  # main.py 가 있는 디렉터리로 이동
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--reload",
        "--reload-dir", str(stratum1_dir),
        "--no-access-log",
    ]

    subprocess.run(cmd, env=current_env, check=True)


if __name__ == "__main__":
    check_only = "--check-only" in sys.argv

    port = SERVER_PORT
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=")[1])
        elif arg == "--port":
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])

    if not preflight_check():
        print("  시동 중단. .env 를 설정한 후 다시 실행하세요.")
        sys.exit(1)

    if check_only:
        print("  --check-only 모드: 서버를 시작하지 않습니다.")
        sys.exit(0)

    start_server(port)
