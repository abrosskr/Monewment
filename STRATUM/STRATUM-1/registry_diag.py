import asyncio
import httpx
import uuid
import os

# Manual Sacrament Simulation
BASE_URL = "http://127.0.0.1:8800/v1/registry/birth"
TOKEN = "mon_gw_ch4ng3m3_bef0re_pr0d"
STRATUM_ID = "badd8a15-5e63-4d24-81fd-489e8973cb85"
QUEEN_ID = "e5388cf9-4ce2-400e-8de1-f9e2a5bb18bd"

async def test_sacrament():
    payload = {
        "entity_type": "ant",
        "payload": {
            "ant_name": "DIAGNOSTIC-ANT",
            "queen_id": QUEEN_ID,
            "stratum_id": STRATUM_ID,
            "ant_type": "AREUM_PARSER",
            "target_url": None
        }
    }
    headers = {
        "X-Queen-Token": TOKEN,
        "Idempotency-Key": str(uuid.uuid4()),
        "Content-Type": "application/json"
    }
    
    print(f"[*] Testing Birth Sacrament at {BASE_URL}...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(BASE_URL, json=payload, headers=headers)
            print(f"[STATUS] {resp.status_code}")
            print(f"[BODY] {resp.text}")
    except Exception as e:
        print(f"[ERR] {e}")

if __name__ == "__main__":
    asyncio.run(test_sacrament())
