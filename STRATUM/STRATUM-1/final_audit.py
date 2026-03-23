import asyncio
from sqlalchemy import text
from core.database import engine

async def final_audit():
    try:
        async with engine.connect() as conn:
            print("=== [FINAL AUDIT] Imperial Registry Consolidated State ===")
            
            # 1. Stratums
            print("\n--- [STRATUMS] ---")
            q_s = text("SELECT stratum_id, stratum_name, status FROM schema_registry.stratums")
            rows = await conn.execute(q_s)
            for r in rows:
                print(f"S: {r.stratum_name} | {r.stratum_id} | {r.status}")

            # 2. Queens
            print("\n--- [QUEENS] ---")
            q_q = text("SELECT queen_id, queen_name, status FROM schema_registry.queens")
            rows = await conn.execute(q_q)
            for r in rows:
                print(f"Q: {r.queen_name} | {r.queen_id} | {r.status}")

            # 3. Areums
            print("\n--- [AREUMS] ---")
            q_a = text("SELECT areum_id, areum_name, status FROM schema_registry.areums")
            rows = await conn.execute(q_a)
            for r in rows:
                print(f"A: {r.areum_name} | {r.areum_id} | {r.status}")

            # 4. Ants
            print("\n--- [ANTS] ---")
            q_ant = text("SELECT ant_id, ant_name, ant_type, status FROM schema_registry.ants")
            rows = await conn.execute(q_ant)
            for r in rows:
                print(f"Ant: {r.ant_name} | {r.ant_id} | {r.ant_type} | {r.status}")

    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    asyncio.run(final_audit())
