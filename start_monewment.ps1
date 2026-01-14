# 1. 절대 경로 고정 및 환경변수 설정
$root = Get-Location
$env:PYTHONPATH = $root
Write-Host "🏗️ [Monewment Hub] 통합 개발환경 가동..." -ForegroundColor Yellow

# 2. Docker 인프라 가동
Write-Host "📡 1. Docker DB 가동 중..." -ForegroundColor Cyan
docker-compose -f "$root/docker-compose.yml" --env-file "$root/.env" up -d

# 3. Frontend (npm) 위치 자동 추적 및 실행
Write-Host "🔍 Frontend(package.json) 위치 찾는 중..." -ForegroundColor Gray

# node_modules는 제외하고, package.json을 깊이 2단계까지 뒤져서 찾음
$npmFile = Get-ChildItem -Path $root -Filter "package.json" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "node_modules" } | Select-Object -First 1

if ($npmFile) {
    $npmDir = $npmFile.Directory.FullName
    Write-Host "🎨 2. Frontend 발견! ($npmDir) -> 새 창에서 실행..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WorkingDirectory "$npmDir"
}
else {
    Write-Host "⚠️ package.json을 찾을 수 없습니다. (폴더 구조 확인 필요)" -ForegroundColor Red
}

# 4. Backend (Uvicorn) 실행
Write-Host "🧠 3. Hub API 서버 가동 (Port: 8001)..." -ForegroundColor Cyan
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
}
uvicorn src.main:app --reload --port 8000