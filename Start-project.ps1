# ========================================================
# 🚀 Monewment 통합 런처 (SaaS Edition)
# ========================================================
$root = "D:\projects\Monewment"
Set-Location $root

Clear-Host
Write-Host "🏭 Monewment SaaS 시스템 가동 (with UI Factory)" -ForegroundColor Cyan

# 1. 프로세스 정리 (기존 서버 종료)
Stop-Process -Name "node", "python", "uvicorn" -Force -ErrorAction SilentlyContinue

# 2. [Client] UI Factory 감시자 가동
Write-Host "   [1/3] UI Factory 클라이언트(주문 접수) 가동..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; python scripts/ui_factory.py"

# 3. [Server] 백엔드 API 서버 가동
Write-Host "   [2/3] 백엔드 API 서버(생성 엔진) 가동..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; python -m uvicorn src.main:app --reload --port 8001"

# 4. [Frontend] GUI 가동
Write-Host "   [3/3] 프론트엔드 가동..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/gui'; npm run dev"

Write-Host "
✅ 시스템이 재가동되었습니다!" -ForegroundColor Green
