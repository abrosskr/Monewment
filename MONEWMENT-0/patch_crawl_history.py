import asyncio
from sqlalchemy import text
from core.database import engine

async def patch():
    async with engine.connect() as conn:
        print("Patching crawl_history ID default...")
        try:
            # PostgreSQL requires the extension for gen_random_uuid if not built-in (usually available in 13+)
            # We can also use uuid_generate_v4() if ossp-uuid is enabled, but gen_random_uuid is safer for modern PG.
            await conn.execute(text("ALTER TABLE public.crawl_history ALTER COLUMN id SET DEFAULT gen_random_uuid()::text"))
            await conn.commit()
            print("Successfully patched crawl_history.")
        except Exception as e:
            print(f"Error patching crawl_history: {e}")
            print("Attempting fallback with manual sequence or type change if needed...")

if __name__ == "__main__":
    asyncio.run(patch())
