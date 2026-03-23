# [MANDATE: BLOODFLOW TEST COMMAND]
# 1. Inject Test Asset
Write-Host "--- [STEP 1: INJECTING TEST ASSET] ---" -ForegroundColor Cyan
python C:\monewment\BABEL\CORE\test_flow.py

# 2. Wait for BABEL-QUEEN (Loop 60s)
Write-Host "--- [STEP 2: WAITING FOR BABEL-QUEEN HARVEST...] ---" -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Verify Knowledge Triples
Write-Host "--- [STEP 3: VERIFYING BABEL KNOWLEDGE INCEPTION] ---" -ForegroundColor Green
python -c "import asyncio; from sqlalchemy import text; from core.database import engine; async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT * FROM schema_babel.knowledge_triples ORDER BY created_at DESC LIMIT 5'))
        print('--- [ BABEL KNOWLEDGE TRIPLES ] ---')
        for r in res.fetchall(): print(dict(r._mapping))
import os, sys; sys.path.append(r'C:\monewment\STRATUM\STRATUM-1'); asyncio.run(check())"
