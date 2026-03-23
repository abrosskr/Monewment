import asyncio
import httpx
import os

# [V51.5] API-based Orchestration Trigger
CORE_API_URL = "http://127.0.0.1:8800/v1"
GATEWAY_TOKEN = os.getenv("GATEWAY_TOKEN", "mon_gw_ch4ng3m3_bef0re_pr0d")

async def trigger_orchestra_once():
    print(f"[*] Sending Intelligence Orchestration signal to Core ({CORE_API_URL})...")
    headers = {
        "X-Queen-Token": GATEWAY_TOKEN,
        "X-Alias": "ORCHESTRA"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{CORE_API_URL}/pipeline/orchestrate?limit=20", headers=headers)
            r.raise_for_status()
            data = r.json()
            if data.get("status") == "orchestrated":
                print(f"[SUCCESS] Orchestrated {data.get('count')} reports into Learning Queue.")
            else:
                print(f"[IDLE] No pending reports in areum_reports.")
    except Exception as e:
        print(f"[FAILURE] Orchestration signal failed: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_orchestra_once())
