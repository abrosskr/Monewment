# [IMPERIAL COMMAND: BABEL REAL-WORLD IGNITION]
Write-Host "--- [INIT] MOVING TO IMPERIAL CORE ---" -ForegroundColor Cyan
Set-Location "C:\monewment\STRATUM\STRATUM-1"

# 1. Start BABEL-QUEEN Server in Background
Write-Host "--- [STEP 1] IGNITING BABEL-QUEEN SERVER (Background) ---" -ForegroundColor Yellow
Start-Process python -ArgumentList "C:\monewment\BABEL\CORE\main.py" -WindowStyle Hidden

# Wait for Server Birth
Start-Sleep -Seconds 5

# 2. Run Real-World Inception Engine
Write-Host "--- [STEP 2] LAUNCHING INCEPTION ENGINE (Real-World Data) ---" -ForegroundColor Green
python C:\monewment\BABEL\CORE\run_inception.py

# 3. Final Verification
Write-Host "--- [STEP 3] FINAL KNOWLEDGE HARVEST AUDIT ---" -ForegroundColor Green
python -c "import asyncio; from sqlalchemy import text; from core.database import engine; async def audit():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT count(*) FROM schema_babel.knowledge_triples'))
        print(f'>>> CURRENT BABEL KNOWLEDGE TRIPLES COUNT: {res.scalar()}')
import sys; sys.path.append(r'C:\monewment\STRATUM\STRATUM-1'); asyncio.run(audit())"

Write-Host "--- [COMPLETE] BABEL INCEPTION SEQUENCE FINISHED ---" -ForegroundColor Cyan
