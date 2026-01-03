$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 1. 절대 경로 고정
$root = Get-Location
$env:PYTHONPATH = $root

Write-Host "🏗️ [Monewment Hub] 가동 시작..." -ForegroundColor Yellow

# 2. Docker 인프라 가동 (명시적 경로 지정)
Write-Host "📡 1. Docker DB 가동 중..." -ForegroundColor Cyan
docker-compose -f "$root/docker-compose.yml" --env-file "$root/.env" up -d

# 3. API 서버 가동 (Port 8001)
Write-Host "🧠 2. Hub API 서버 가동 (Port: 8001)..." -ForegroundColor Cyan
uvicorn src.main:app --reload --port 8001
