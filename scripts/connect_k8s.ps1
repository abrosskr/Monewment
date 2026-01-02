# [설정] 터미널 인코딩 강제 고정 (한글 깨짐 및 메아리 방지)
chcp 65001 > $null
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# 파일 경로: scripts/connect_k8s.ps1
Write-Host "🔄 [Antigravity] 인프라 연결 초기화 중..." -ForegroundColor Cyan

# 1. 기존 프로세스 정리
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ 기존 연결 정리 완료."

# 2. 포트포워딩 함수 (원본 로직 유지)
function Start-Tunnel {
    param ($appName, $serviceNames, $podPrefix, $localPort, $remotePort)
    
    $targetSvc = $null
    foreach ($name in $serviceNames) {
        $svc = kubectl get svc $name -n vendors --ignore-not-found
        if ($svc) { $targetSvc = $name; break }
    }

    if ($targetSvc) {
        Write-Host "🚀 [$appName] 서비스($targetSvc) 연결 시도 ($localPort`:$remotePort)..." -ForegroundColor Yellow
        # [수정] 에러 유발 옵션 제거함. --address 0.0.0.0은 연결을 위해 유지.
        Start-Process -FilePath "kubectl" -ArgumentList "port-forward --address 0.0.0.0 svc/$targetSvc -n vendors $localPort`:$remotePort" -WindowStyle Hidden
        Write-Host "   ㄴ 완료: 서비스 모드로 실행됨." -ForegroundColor Green
        return
    }

    $podName = (kubectl get pods -n vendors --no-headers -o custom-columns=":metadata.name" | Select-String "^$podPrefix")
    if ($podName) {
        $podName = $podName.ToString().Trim()
        Write-Host "🚀 [$appName] 포드($podName) 직접 연결 시도 ($localPort`:$remotePort)..." -ForegroundColor Yellow
        # [수정] 에러 유발 옵션 제거함.
        Start-Process -FilePath "kubectl" -ArgumentList "port-forward --address 0.0.0.0 pod/$podName -n vendors $localPort`:$remotePort" -WindowStyle Hidden
        Write-Host "   ㄴ 완료: 포드 모드로 우회 연결됨." -ForegroundColor Green
    }
    else {
        Write-Host "❌ [$appName] 연결 실패: 리소스를 찾을 수 없습니다." -ForegroundColor Red
    }
}

# 3. 3대 핵심 인프라 연결
Start-Tunnel -appName "Backend" -serviceNames @("backend-service", "backend-cell") -podPrefix "backend-cell" -localPort 8000 -remotePort 8000
Start-Tunnel -appName "Database" -serviceNames @("db-service", "postgres-db") -podPrefix "postgres-db" -localPort 5432 -remotePort 5432
Start-Tunnel -appName "MCP_Worker" -serviceNames @("mcp-service", "mcp-server") -podPrefix "mcp-server" -localPort 8080 -remotePort 80

Write-Host "`n✨ 모든 터널링 명령이 실행되었습니다. (5초 후 안정화)" -ForegroundColor Cyan
Start-Sleep -Seconds 5