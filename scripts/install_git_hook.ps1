# Monewment CCTV Git Hook 설치 스크립트
# PowerShell에서 실행하세요

Write-Host "🔧 Monewment CCTV Git Hook 설치 중..." -ForegroundColor Cyan

$hookSource = "scripts\pre-commit.sh"
$hookDest = ".git\hooks\pre-commit"

# 소스 파일 확인
if (-not (Test-Path $hookSource)) {
    Write-Host "❌ 오류: $hookSource 파일을 찾을 수 없습니다" -ForegroundColor Red
    exit 1
}

# 기존 hook 백업
if (Test-Path $hookDest) {
    $backupPath = "$hookDest.backup"
    Write-Host "⚠️  기존 pre-commit hook을 백업합니다: $backupPath" -ForegroundColor Yellow
    Copy-Item $hookDest $backupPath -Force
}

# Hook 복사
Copy-Item $hookSource $hookDest -Force

# 실행 권한 부여 (Git Bash에서 실행 가능하도록)
Write-Host "✅ Git Hook 설치 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "📌 이제 git commit 시 자동으로 문서가 생성됩니다." -ForegroundColor Green
Write-Host "   테스트: git commit -m 'test: hook verification'" -ForegroundColor Gray
