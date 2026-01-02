# [설정] 터미널 인코딩 강제 고정 (스크립트 실행 시 리셋 방지)
chcp 65001 > $null
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 파일 경로: test_api.ps1
Write-Host "🔍 [System Check] 인프라 연결 상태 점검..." -ForegroundColor Cyan

# 1. 백엔드 연결 확인 (Port 8000)
try {
    # 127.0.0.1 대신 localhost를 사용하여 시도
    $backend = Invoke-RestMethod -Uri "http://127.0.0.1:8000/docs" -Method Get -ErrorAction Stop
    Write-Host "✅ [Backend] 연결 성공 (Port 8000)" -ForegroundColor Green
}
catch {
    Write-Host "❌ [Backend] 연결 실패 (Port 8000) - K8s 포드 상태를 확인하세요." -ForegroundColor Red
}

# 2. DB 포트 확인 (Port 5432)
$dbCheck = Test-NetConnection -ComputerName 127.0.0.1 -Port 5432 -InformationLevel Quiet
if ($dbCheck) {
    Write-Host "✅ [Database] 포트 감지됨 (Port 5432)" -ForegroundColor Green
}
else {
    Write-Host "❌ [Database] 포트 닫힘 (Port 5432)" -ForegroundColor Red
}

# 3. MCP 워커 확인 (Port 8080)
try {
    $mcp = Invoke-RestMethod -Uri "http://127.0.0.1:8080/" -Method Get -ErrorAction SilentlyContinue
    Write-Host "✅ [MCP Worker] 포트 응답 확인 (Port 8080)" -ForegroundColor Green
}
catch {
    if ($_.Exception.Status -eq 'ConnectFailure') {
        Write-Host "❌ [MCP Worker] 연결 실패 (Port 8080)" -ForegroundColor Red
    }
    else {
        Write-Host "✅ [MCP Worker] 포트 열림 (Port 8080)" -ForegroundColor Green
    }
}

Write-Host "-------------------------------------------"
Write-Host "🎉 점검 완료. 3개가 모두 초록색이면 업무를 시작하세요." -ForegroundColor Cyan