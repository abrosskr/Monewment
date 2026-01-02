# scripts/test_env.py
import os
import sys
import importlib

def check_structure():
    print("🔍 [1/3] 폴더 구조 확인 중...")
    # [수정됨] 'app' -> 'src'로 변경 (우리가 결정한 Flat 구조 반영)
    required_dirs = ['src', 'scripts', '.github/workflows']
    required_files = ['requirements.txt', '.gitignore', 'scripts/generate_docs.py']
    
    missing = []
    for d in required_dirs:
        if not os.path.exists(d): missing.append(d)
    for f in required_files:
        if not os.path.exists(f): missing.append(f)
        
    if missing:
        print(f"❌ 누락된 파일/폴더 발견: {missing}")
        return False
    print("✅ 폴더 구조 정상.")
    return True

def check_libraries():
    print("\n🔍 [2/3] 필수 라이브러리 설치 확인 중...")
    # [참고] src 구조여도 라이브러리 이름은 동일하므로 수정 없음
    libs = ['fastapi', 'sqlalchemy', 'asyncpg', 'pydantic', 'pydantic_settings']
    
    missing = []
    for lib in libs:
        try:
            importlib.import_module(lib)
        except ImportError:
            missing.append(lib)
            
    if missing:
        print(f"❌ 설치되지 않은 라이브러리: {missing}")
        print("💡 힌트: pip install -r requirements.txt 를 실행했나요?")
        return False
    print("✅ 라이브러리 정상.")
    return True

def run_auto_docs():
    print("\n🔍 [3/3] 자동 문서 생성기(Vendors 유산) 테스트...")
    try:
        # 같은 폴더에 있는 generate_docs를 import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from generate_docs import generate_tree
        
        # 루트 디렉토리 찾기
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(root_dir, "docs", "TEST_STRUCTURE.md")
        
        # docs 폴더 생성
        os.makedirs(os.path.join(root_dir, "docs"), exist_ok=True)
        
        # 실행
        generate_tree(root_dir, output_path)
        
        if os.path.exists(output_path):
            print(f"✅ 문서 생성 성공! 위치: {output_path}")
            # 테스트 파일은 삭제 (깔끔하게)
            os.remove(output_path) 
            return True
        else:
            print("❌ 문서 파일이 생성되지 않았습니다.")
            return False
    except Exception as e:
        print(f"❌ 스크립트 에러 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Monewment 환경 자가 진단 시작...\n" + "="*40)
    
    step1 = check_structure()
    step2 = check_libraries()
    step3 = run_auto_docs()
    
    print("="*40)
    if step1 and step2 and step3:
        print("🎉 모든 테스트 통과! Git에 푸시할 준비가 되었습니다.")
        sys.exit(0)
    else:
        print("💥 테스트 실패. 위 에러 내용을 확인하고 수정하세요.")
        sys.exit(1)