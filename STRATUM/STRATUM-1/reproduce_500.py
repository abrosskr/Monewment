import httpx
import asyncio

async def test_mark_consumed():
    CORE = "http://127.0.0.1:8800"
    TOKEN = "mon_gw_ch4ng3m3_bef0re_pr0d"
    
    # 임의의 UUID 또는 이전에 실패했을 것으로 추정되는 ID
    payload = {
        "report_ids": ["e72ea2d1-6d80-4a05-85d4-da3ac7ac6ad2"] 
    }
    
    headers = {
        "X-Queen-Token": TOKEN,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"[TEST] Sending PATCH to {CORE}/v1/pipeline/cross_reports/mark_consumed")
        resp = await client.patch(
            f"{CORE}/v1/pipeline/cross_reports/mark_consumed",
            json=payload,
            headers=headers
        )
        print(f"[RESULT] Status: {resp.status_code}")
        print(f"[RESULT] Body: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_mark_consumed())
