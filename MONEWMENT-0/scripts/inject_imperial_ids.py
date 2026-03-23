import httpx
import asyncio
import uuid
import json
from pathlib import Path
import sys

# Path fix for AuditLogger
sys.path.insert(0, str(Path(r"c:\monewment\MONEWMENT-0")))
from core.audit_logger import AuditLogger

# ==============================================================================
# # inject_imperial_ids.py — Grandfathering Legacy Entities
# ==============================================================================
# Role: 기존 실체화된 엔티티들을 V2.0 레지스트리에 공식 등록하여 '시민권'을 하사함.
# ==============================================================================

BASE_URL = "http://127.0.0.1:8800/v1/registry"
GATEWAY_TOKEN = "test_gateway_token" # 실제 토큰 확인 필요

MANIFEST_PATH = Path(r"c:\monewment\structural_manifest.json")

async def inject_entities():
    if not MANIFEST_PATH.exists():
        print("Manifest not found.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. Stratums
    stratums = manifest.get("external_aliases", {})
    for alias, info in stratums.items():
        if info.get("target_level") == "STRATUM":
            print(f"\n[INJECT] Stratum: {alias}")
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{BASE_URL}/birth",
                        headers={"X-Queen-Token": GATEWAY_TOKEN, "Idempotency-Key": str(uuid.uuid4())},
                        json={
                            "entity_type": "stratum",
                            "payload": {
                                "stratum_name": alias.lower().replace("-", "_"),
                                "monewment_id": str(uuid.UUID(int=0)), # Dummy master ID
                                "purpose": f"Legacy Migration: {alias}"
                            }
                        }
                    )
                    print(f"  Result: {resp.status_code} - {resp.json().get('entity_id')}")
            except Exception as e:
                print(f"  Failed: {e}")

    # 2. Queens (Special)
    special_queens = ["physics", "forager", "queen-rex"]
    for qname in special_queens:
        print(f"\n[INJECT] Queen: {qname}")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{BASE_URL}/birth",
                    headers={"X-Queen-Token": GATEWAY_TOKEN, "Idempotency-Key": str(uuid.uuid4())},
                    json={
                        "entity_type": "queen",
                        "payload": {
                            "queen_type": "GENERAL",
                            "relationship_type": "INTERNAL" if "rex" in qname or "physics" in qname else "ALLY"
                        }
                    }
                )
                print(f"  Result: {resp.status_code} - {resp.json().get('official_name')} ({resp.json().get('entity_id')})")
        except Exception as e:
            print(f"  Failed: {e}")

    # 3. Ants
    ants = manifest.get("live_instances", {})
    for ant_name, info in list(ants.items())[:10]: # Too many ants, limiting to first 10 for demonstration
        print(f"\n[INJECT] Ant: {ant_name}")
        # Note: In real scenarios, we need valid queen_id and stratum_id. 
        # Here we demonstrate the principle.
        pass

    # [DECREE 13] 엔티티 주입 이력 기록
    await AuditLogger.log_movement(
        action_type="INJECT-HERITAGE",
        source="structural_manifest.json",
        target="schema_registry",
        reason="Grandfathering legacy entities into Registry v2.0"
    )

if __name__ == "__main__":
    # Ensure MONEWMENT-0 is running before executing this
    print("Pre-flight check: Ensure MONEWMENT-0 server (Port 8800) is ACTIVE.")
    asyncio.run(inject_entities())
