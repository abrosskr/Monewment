import asyncio
from sqlalchemy import text
from core.database import engine

async def map_idempotency():
    print("Mapping idempotency key for recilabeler...")
    async with engine.begin() as conn:
        # Key from identity.vow: QUEEN-IN-LABELLER-001
        # Queen ID for recilabeler: 9fa07853-416b-4aae-a72a-34ac2271efff
        await conn.execute(text("""
            INSERT INTO schema_registry.idempotency_keys (idempotency_key, entity_id, entity_type)
            VALUES ('QUEEN-IN-LABELLER-001', '9fa07853-416b-4aae-a72a-34ac2271efff', 'queen')
            ON CONFLICT (idempotency_key) DO NOTHING
        """))
        print("Idempotency key 'QUEEN-IN-LABELLER-001' mapped to recilabeler Queen.")

if __name__ == "__main__":
    asyncio.run(map_idempotency())
