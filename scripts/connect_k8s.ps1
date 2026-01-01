# 파일 경로: scripts/connect_k8s.ps1
# 역할: 기존 연결을 정리하고, 백엔드/DB/MCP 3가지 통신을 한 번에 뚫어줍니다.

Write-Host "🔄 [Antigravity] 인프라 연결 초기화 중..." -ForegroundColor Cyan

# 1. 기존의 좀비 프로세스(kubectl) 강제 종료
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ 기존 연결 정리 완료."

# 2. 백그라운드 작업(Job)으로 포트포워딩 실행 함수
function Start-Tunnel {
    param ($appName, $serviceNames, $podPrefix, $localPort, $remotePort)
    
    # A. 서비스(Service) 이름으로 먼저 시도
    $targetSvc = $null
    foreach ($name in $serviceNames) {
        $svc = kubectl get svc $name -n vendors --ignore-not-found
        if ($svc) { $targetSvc = $name; break }
    }

    if ($targetSvc) {
        Write-Host "🚀 [$appName] 서비스($targetSvc) 연결 시도 (Port $localPort)..." -ForegroundColor Yellow
        Start-Process -FilePath "kubectl" -ArgumentList "port-forward svc/$targetSvc -n vendors $localPort`:$remotePort" -WindowStyle Hidden
        Write-Host "   ㄴ 성공: 서비스 모드로 연결됨." -ForegroundColor Green
        return
    }

    # B. 서비스가 없으면 포드(Pod) 이름으로 비상 연결 (Fallback)
    Write-Host "⚠️ [$appName] 서비스를 찾을 수 없어 POD를 검색합니다..." -ForegroundColor DarkYellow
    $podName = (kubectl get pods -n vendors --no-headers -o custom-columns=":metadata.name" | Select-String "^$podPrefix")
    
    if ($podName) {
        $podName = $podName.ToString().Trim()
        Write-Host "🚀 [$appName] 포드($podName) 직접 연결 시도 (Port $localPort)..." -ForegroundColor Yellow
        Start-Process -FilePath "kubectl" -ArgumentList "port-forward pod/$podName -n vendors $localPort`:$remotePort" -WindowStyle Hidden
        Write-Host "   ㄴ 성공: 포드 모드로 우회 연결됨." -ForegroundColor Green
    }
    else {
        Write-Host "❌ [$appName] 연결 실패: 실행 중인 포드나 서비스를 찾을 수 없습니다." -ForegroundColor Red
    }
}

# 3. 3대 핵심 인프라 연결 실행
# (1) Backend (8000)
Start-Tunnel -appName "Backend" -serviceNames @("backend-cell", "backend-service") -podPrefix "backend-cell" -localPort 8000 -remotePort 80

# (2) Database (5432)
Start-Tunnel -appName "Database" -serviceNames @("db-service", "postgres-db") -podPrefix "postgres-db" -localPort 5432 -remotePort 5432

# (3) MCP Agent (8080) -> 이게 빠져서 에러가 났던 것임!
Start-Tunnel -appName "MCP_Worker" -serviceNames @("mcp-server", "mcp-service") -podPrefix "mcp-server" -localPort 8080 -remotePort 80

Write-Host "`n✨ 모든 터널링 명령이 백그라운드에서 실행되었습니다." -ForegroundColor Cyan
Write-Host "   (잠시 후 ./test_api.ps1 으로 연결 상태를 확인하세요)"