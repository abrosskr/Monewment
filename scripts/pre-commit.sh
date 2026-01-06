#!/bin/sh
# Monewment CCTV Auto-Documentation Git Hook
# 이 파일을 .git/hooks/pre-commit 으로 복사하세요

echo "📝 [CCTV] 변경사항 감지 - 자동 문서 생성 시작..."

# Python 스크립트 실행
python scripts/generate_docs.py

# 생성 결과 확인
if [ $? -eq 0 ]; then
    # 생성된 문서가 있으면 자동으로 스테이징
    if [ -d "docs/auto_generated" ]; then
        git add docs/auto_generated/*.md
        git add docs/STRUCTURE.md 2>/dev/null || true
        echo "✅ [CCTV] 문서 업데이트 완료 및 커밋에 포함"
    else
        echo "⚠️ [CCTV] auto_generated 디렉토리가 없습니다"
    fi
else
    echo "❌ [CCTV] 문서 생성 실패 (커밋은 계속 진행됩니다)"
fi

# 커밋은 항상 진행 (문서 생성 실패해도 코드 커밋은 허용)
exit 0
