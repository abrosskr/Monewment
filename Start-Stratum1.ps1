# 🚀 Start-Stratum1.ps1 — STRATUM-1 제국 기동 스크립트
# [V51.5 Inheritance Architecture]

$ErrorActionPreference = "Stop"

Write-Host "`n[✨ IGNITION] STRATUM-1 제국 시스템을 기동합니다..." -ForegroundColor Cyan

# 1. PYTHONPATH 동적 주입 (MONEWMENT-0 하이픈 경로 문제 해결)
# $PSScriptRoot는 현재 스크립트가 위치한 c:\monewment를 가리킴
$CorePath = Join-Path $PSScriptRoot "MONEWMENT-0"
$StratumPath = Join-Path $PSScriptRoot "STRATUM\STRATUM-1"

if (!(Test-Path $CorePath)) {
    Write-Error "[FATAL] MONEWMENT-0 Core not found at $CorePath"
}

# 기존 PYTHONPATH에 코어 경로 추가
$env:PYTHONPATH = "$CorePath;$env:PYTHONPATH"
Write-Host "[OK] PYTHONPATH Injector: $CorePath" -ForegroundColor Green

# 2. STRATUM-1 폴더로 이동하여 uvicorn 실행
Set-Location -Path $StratumPath
Write-Host "[OK] Current Sector: $(Get-Location)" -ForegroundColor Green

# 3. uvicorn 기동 (Port 8800)
Write-Host "[🔥 FIRE] Starting Primary Dispatcher on Port 8800..." -ForegroundColor Yellow
uvicorn main:app --host 0.0.0.0 --port 8800 --reload
