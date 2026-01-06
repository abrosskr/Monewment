"""
Monewment 고급 문서 생성 시스템 v4.0
완전한 프로젝트 문서를 자동으로 생성합니다.
"""

import os
import sys
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.db_schema_generator import generate_db_schema_docs
from generators.api_docs_generator import generate_api_docs
from generators.architecture_generator import generate_architecture_docs
from generators.deployment_generator import generate_deployment_docs
from generators.user_manual_generator import generate_user_manual

def main():
    """메인 문서 생성 오케스트레이터"""
    print("=" * 80)
    print("🚀 Monewment 고급 문서 생성 시스템 v4.0")
    print("=" * 80)
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(root_dir, "docs")
    auto_gen_dir = os.path.join(docs_dir, "auto_generated")
    
    # 디렉토리 생성
    os.makedirs(auto_gen_dir, exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "deployment"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "user_guide"), exist_ok=True)
    
    results = {}
    
    # 1. DB 스키마 문서 생성
    print("\n📊 [1/5] DB 스키마 문서 생성 중...")
    try:
        db_result = generate_db_schema_docs(root_dir, auto_gen_dir)
        results['db_schema'] = db_result
        print(f"✅ 완료: {db_result['file']}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        results['db_schema'] = {'error': str(e)}
    
    # 2. API 문서 생성
    print("\n📡 [2/5] API 레퍼런스 문서 생성 중...")
    try:
        api_result = generate_api_docs(root_dir, auto_gen_dir)
        results['api_docs'] = api_result
        print(f"✅ 완료: {api_result['file']}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        results['api_docs'] = {'error': str(e)}
    
    # 3. 아키텍처 문서 생성
    print("\n🏗️  [3/5] 아키텍처 문서 생성 중...")
    try:
        arch_result = generate_architecture_docs(root_dir, auto_gen_dir)
        results['architecture'] = arch_result
        print(f"✅ 완료: {arch_result['file']}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        results['architecture'] = {'error': str(e)}
    
    # 4. 배포 가이드 생성
    print("\n🚢 [4/5] 배포 가이드 생성 중...")
    try:
        deploy_result = generate_deployment_docs(root_dir, os.path.join(docs_dir, "deployment"))
        results['deployment'] = deploy_result
        print(f"✅ 완료: {deploy_result['file']}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        results['deployment'] = {'error': str(e)}
    
    # 5. 사용자 매뉴얼 생성
    print("\n📖 [5/5] 사용자 매뉴얼 생성 중...")
    try:
        manual_result = generate_user_manual(root_dir, os.path.join(docs_dir, "user_guide"))
        results['user_manual'] = manual_result
        print(f"✅ 완료: {manual_result['file']}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        results['user_manual'] = {'error': str(e)}
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("📋 문서 생성 완료 요약")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if 'error' not in r)
    total_count = len(results)
    
    print(f"✅ 성공: {success_count}/{total_count}")
    
    for doc_type, result in results.items():
        if 'error' in result:
            print(f"  ❌ {doc_type}: {result['error']}")
        else:
            print(f"  ✅ {doc_type}: {result.get('file', 'N/A')}")
    
    print("\n🎉 모든 문서 생성 작업 완료!")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()
