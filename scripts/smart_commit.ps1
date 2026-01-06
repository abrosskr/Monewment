# ========================================================
# 🚀 Monewment Smart Commit Script
# ========================================================
# 안정적인 Git 커밋/푸시를 위한 자동화 스크립트
# - 자동 pull --rebase
# - 재시도 로직 포함
# - 충돌 자동 해결 시도

param(
    [Parameter(Mandatory=$false)]
    [string]$Message = "chore: update"
)

$ErrorActionPreference = "Continue"
$root = "D:\projects\Monewment"
Set-Location $root

Write-Host "`n🚀 Monewment Smart Commit" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. 변경사항 확인 및 스테이징
Write-Host "`n📝 [1/4] Staging changes..." -ForegroundColor Yellow
git add -A

$status = git status --short
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "✅ No changes to commit" -ForegroundColor Green
    exit 0
}

Write-Host "Changes to commit:"
Write-Host $status -ForegroundColor Gray

# 2. 커밋
Write-Host "`n💾 [2/4] Committing changes..." -ForegroundColor Yellow
git commit -m "$Message"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Commit failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Committed successfully" -ForegroundColor Green

# 3. Pull with rebase (충돌 방지)
Write-Host "`n🔄 [3/4] Pulling latest changes..." -ForegroundColor Yellow
git pull origin feature/software-first-infra --rebase

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Pull failed - checking for conflicts..." -ForegroundColor Yellow
    
    # 충돌 확인
    $conflicts = git diff --name-only --diff-filter=U
    if ($conflicts) {
        Write-Host "❌ Merge conflicts detected:" -ForegroundColor Red
        Write-Host $conflicts -ForegroundColor Red
        Write-Host "`nPlease resolve conflicts manually and run:" -ForegroundColor Yellow
        Write-Host "  git rebase --continue" -ForegroundColor Cyan
        Write-Host "  git push origin feature/software-first-infra" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "✅ Pulled successfully" -ForegroundColor Green

# 4. Push (재시도 로직 포함)
Write-Host "`n📤 [4/4] Pushing changes..." -ForegroundColor Yellow

$maxRetries = 3
$retryCount = 0
$pushSuccess = $false

while ($retryCount -lt $maxRetries) {
    $attempt = $retryCount + 1
    Write-Host "  Attempt $attempt/$maxRetries..." -ForegroundColor Gray
    
    git push origin feature/software-first-infra 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        $pushSuccess = $true
        break
    }
    
    $retryCount++
    
    if ($retryCount -lt $maxRetries) {
        Write-Host "  ⚠️  Push failed, pulling again..." -ForegroundColor Yellow
        git pull origin feature/software-first-infra --rebase 2>&1 | Out-Null
        Start-Sleep -Seconds 2
    }
}

if ($pushSuccess) {
    Write-Host "`n✅ Successfully pushed to remote!" -ForegroundColor Green
    Write-Host "=" * 50
    Write-Host "🎉 All done!" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n❌ Push failed after $maxRetries attempts" -ForegroundColor Red
    Write-Host "=" * 50
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check your internet connection" -ForegroundColor Gray
    Write-Host "  2. Verify GitHub credentials" -ForegroundColor Gray
    Write-Host "  3. Try manually: git push origin feature/software-first-infra" -ForegroundColor Gray
    exit 1
}
