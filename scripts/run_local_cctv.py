import sys
import os
import time

# ========================================================
# 👁️ Monewment Local CCTV Runner (Path Fixed)
# ========================================================

if __name__ == "__main__":
    # 1. 내 위치(scripts)를 기준으로 프로젝트 루트(Monewment) 찾기
    current_file_path = os.path.abspath(__file__)
    scripts_dir = os.path.dirname(current_file_path)
    project_root = os.path.dirname(scripts_dir)
    
    # 2. 파이썬에게 프로젝트 루트 위치 알려주기 (src 모듈 인식용)
    if project_root not in sys.path:
        sys.path.append(project_root)

    print(f"🔧 CCTV 실행 위치: {current_file_path}")
    print(f"📂 프로젝트 루트: {project_root}")
    print("-" * 40)

    # 3. 감시 봇 호출
    try:
        from src.core.devtools.watcher import start_watching
        
        # 4. 루트 경로를 명시적으로 넘겨줌 (이 순간 초기 상태가 기록됨)
        start_watching(project_root)
        
    except ImportError as e:
        print(f"❌ 오류 발생: 모듈을 찾을 수 없습니다.\n{e}")
        print("팁: src 폴더가 프로젝트 루트에 있는지 확인해주세요.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")