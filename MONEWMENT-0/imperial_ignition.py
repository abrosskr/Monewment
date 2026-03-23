import argparse
import subprocess
import sys
import os
from pathlib import Path

# ==============================================================================
# # imperial_ignition.py — THE MASTER ORCHESTRATOR (V51.5)
# ==============================================================================
# Role: MONEWMENT-0 시스템의 통합 시동 및 최적화(Refine)를 관리함.
#       헌법 v4.1 및 V51.5 요새화 표준을 준수하는지 점검하고 교정함.
# ==============================================================================

def run_script(script_path: str, args: list = None):
    """지정된 스크립트를 현재 Python 인터프리터로 실행"""
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    print(f"\n[IGNITION] Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[IGNITION] ERROR: Script {script_path} failed with exit code {e.returncode}")
        return False

def mode_refine():
    print("=== [V51.5] IMPERIAL SYSTEM REFINEMENT SEQUENCE START ===")
    
    # 1. 제국 환경 정화 (이단적 API 키 소거)
    print("\n--- Phase 1: Environmental Sanctification ---")
    run_script("scripts/imperial_sanitizer.py")
    
    # 2. 영토 구조 정렬 (Pillar/Stratum 위치 검증 및 동기화)
    print("\n--- Phase 2: Structural Realignment ---")
    run_script("scripts/template_realignment.py")
    
    # 3. 인프라 치안 영토 복구 (schema_system 프로비저닝)
    print("\n--- Phase 3: Infrastructure Restoration ---")
    run_script("scripts/trigger_provision_system.py")
    
    # 4. 최종 무결성 검증 (Kill-Switch & Connectivity)
    print("\n--- Phase 4: Integrity Verification ---")
    run_script("scripts/verify_kill_switch.py")
    
    print("\n=== [V51.5] REFINEMENT SEQUENCE COMPLETE. GLORY TO MONEWMENT. ===")

def mode_start(port: str = None):
    print("=== [V51.5] IMPERIAL IGNITION SEQUENCE START ===")
    
    # 시동 전 자가 점검 (Refine 호출 가능성 고려)
    # 여기서는 서버 시작(start.py)을 호출함
    args = []
    if port:
        args.extend(["--port", port])
    
    run_script("start.py", args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MONEWMENT Imperial Ignition Engine")
    parser.add_argument("--mode", choices=["start", "refine"], required=True, help="Ignition mode: start or refine")
    parser.add_argument("--port", help="Port for the server (start mode only)")
    
    args = parser.parse_args()
    
    # CWD를 MONEWMENT-0로 고정 (내부 스크립트 경로 상대성 유지)
    os.chdir(Path(__file__).resolve().parent)
    
    if args.mode == "refine":
        mode_refine()
    elif args.mode == "start":
        mode_start(args.port)
