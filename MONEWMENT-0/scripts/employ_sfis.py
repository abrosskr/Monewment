import asyncio
import httpx
import json

CORE_API_URL = "http://127.0.0.1:8800/v1/registry/birth"
GATEWAY_TOKEN = "mon_gw_ch4ng3m3_bef0re_pr0d"

async def employ_sfis():
    headers = {
        "X-Queen-Token": GATEWAY_TOKEN,
        "Content-Type": "application/json"
    }

    mon_id = "2136f144-fe60-4b6b-b533-fbe953617e55"
    edenvale_stratum_id = "a8527246-b140-42cf-b304-00f4587ee1f4"

    # 1. Register Stratum: sfis (Unique Pillar Territory)
    stratum_payload = {
        "entity_type": "stratum",
        "payload": {
            "stratum_name": "sfis",
            "purpose": "Strategic Flavor Intelligence Pillar",
            "schema_pg": "schema_stratum_sfis",
            "monewment_id": mon_id
        },
        "instance_path": "c:\\monewment\\sfis"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Birth Stratum
            res_s = await client.post(CORE_API_URL, json=stratum_payload, headers=headers)
            print(f"Stratum Birth Status: {res_s.status_code}")
            print(f"Stratum Birth Response: {res_s.text}")
            
            sfis_stratum_id = None
            if res_s.status_code == 200:
                sfis_stratum_id = res_s.json().get("entity_id")
            elif res_s.status_code == 409: # Already exists
                # Stratum might already exist from previous failed (but DB committed) attempt
                print("Stratum already exists. Checking for ID...")
                # We can try to get the ID via list if needed, or proceeds with None
            
            # 2. Register Queen: sfis-0 (Employed in EDENVALE + sfis)
            queen_payload = {
                "entity_type": "queen",
                "payload": {
                    "queen_name": "sfis-0",
                    "queen_type": "GENERAL",
                    "relationship_type": "INTERNAL",
                    "stratum_ids": [sfis_stratum_id, edenvale_stratum_id] if sfis_stratum_id else [edenvale_stratum_id],
                    "host_ip": "127.0.0.1"
                },
                "instance_path": "c:\\monewment\\sfis"
            }

            # Birth Queen
            res_q = await client.post(CORE_API_URL, json=queen_payload, headers=headers)
            print(f"Queen Birth Status: {res_q.status_code}")
            print(f"Queen Birth Response: {res_q.text}")
            
        except Exception as e:
            import traceback
            print(f"Error during employment: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(employ_sfis())
