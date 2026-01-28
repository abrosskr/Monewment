<#
.SYNOPSIS
    MONEWMENT VESS (Virtual Environment Stability System) Controller
    
.DESCRIPTION
    The Enforcement Arm of the Control Plane.
    Manages Environment Integrity, Locking, and Healing.
    
.PARAMETER Command
    check   - Runs the Doctor (Read-only)
    lock    - Generates Manifest from current state (Admin only)
    heal    - Reinstalls environment to match Manifest (Destructive)
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("check", "lock", "heal")]
    [string]$Command
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$VenvPython = "$Root\.venv\Scripts\python.exe"

# Ensure venv exists
if (-not (Test-Path $VenvPython)) {
    Write-Host "❌ FATAL: Virtual Environment missing at $Root\.venv" -ForegroundColor Red
    exit 1
}

function Run-Check {
    Write-Host "🔍 [VESS] Running Integrity Check..." -ForegroundColor Cyan
    & $VenvPython "$ScriptDir\vess_doctor.py"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ [VESS] Integrity Verified. System Verified." -ForegroundColor Green
    } else {
        Write-Host "❌ [VESS] DRIFT DETECTED. EXECUTION BLOCKED." -ForegroundColor Red
        exit 1
    }
}

function Run-Lock {
    Write-Host "🔒 [VESS] Authorizing Environment Lock..." -ForegroundColor Yellow
    & $VenvPython "$ScriptDir\vess_lock.py"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ [VESS] New Law Established." -ForegroundColor Green
    } else {
        Write-Host "❌ [VESS] Lock Failed." -ForegroundColor Red
        exit 1
    }
}

function Run-Heal {
    Write-Host "🚑 [VESS] Initiating Self-Healing Protocol..." -ForegroundColor Magenta
    # Logic: Pip install from manifest... 
    # For now, we reuse requirements.txt reliability, but strictly we should use manifest.
    # To implement strict manifest heal:
    # 1. Read manifest in python
    # 2. Generate implicit requirements.txt
    # 3. Pip install
    
    # Placeholder for Phase 4 step "Heal" detailed implementation
    Write-Host "⚠️  Heal logic not yet fully implemented. Using standard pip sync." -ForegroundColor Yellow
    & $VenvPython -m pip install -r "$Root\requirements.txt"
    Run-Check
}

# Dispatch
switch ($Command) {
    "check" { Run-Check }
    "lock"  { Run-Lock }
    "heal"  { Run-Heal }
}
