# 🛡️ Clean-Monewment0.ps1 — 제국 코어 정제 스크립트
# [V51.5 Pure-Core Directive]

$ErrorActionPreference = "Continue"

Write-Host "`n[🧹 CLEAN] MONEWMENT-0 코어 정제 작업을 시작합니다..." -ForegroundColor Cyan

# 1. queens/ 폴더 활성 데이터 제거
$QueensPath = "$PSScriptRoot\MONEWMENT-0\queens"
if (Test-Path $QueensPath) {
    Write-Host "[!] Removing polluted data in: $QueensPath" -ForegroundColor Yellow
    Remove-Item -Path $QueensPath -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -Path $QueensPath -ItemType Directory -Force | Out-Null
    Write-Host "[OK] Queens directory sanitized." -ForegroundColor Green
}

# 2. 루트에 산재한 검증용 파이썬 스크립트 제거
$ScriptsToClean = @(
    "final_verify.py",
    "final_verify_v2.py",
    "final_verify_v3.py",
    "test_pipeline_500.py",
    "check_dashboard_data.py"
)

foreach ($script in $ScriptsToClean) {
    $path = "$PSScriptRoot\MONEWMENT-0\$script"
    if (Test-Path $path) {
        Write-Host "[!] Removing legacy script: $script" -ForegroundColor Yellow
        Remove-Item -Path $path -Force
    }
}

# 3. .env 파일 정체성 오염 확인 (가이드 제공)
Write-Host "[!] Note: Please ensure STRATUM_ID and STRATUM_NAME are removed from MONEWMENT-0/.env manually." -ForegroundColor Gray

Write-Host "[🏁 DONE] 제국 코어 정제 완료. 시스템 엔트로피가 감소했습니다.`n" -ForegroundColor Green
