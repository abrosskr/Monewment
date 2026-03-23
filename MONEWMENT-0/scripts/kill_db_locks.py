import asyncio
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import engine

async def kill_locks():
    print("Checking for active queries and locks...")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT pid, state, query FROM pg_stat_activity WHERE state != 'idle' AND pid != pg_backend_pid()"))
        for row in res.fetchall():
            print(f"Active PID: {row.pid}, State: {row.state}, Query: {row.query[:100]}")
            # Terminate connections holding locks or just long-running ones
            if row.pid:
                print(f" terminating {row.pid}")
                await conn.execute(text(f"SELECT pg_terminate_backend({row.pid})"))
        await conn.commit()
    print("Done")

if __name__ == "__main__":
    asyncio.run(kill_locks())
