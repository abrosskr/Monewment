import asyncio
import sys
import os

# Create a fake env for import
sys.path.append(os.path.join(os.getcwd()))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import User

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.api_key.isnot(None)))
        users = result.scalars().all()
        
        print(f"--- Found {len(users)} Users with API Keys ---")
        for u in users:
            masked_key = u.api_key[:4] + "***" + u.api_key[-4:] if len(u.api_key or "") > 8 else "***"
            print(f"User: {u.email} (ID: {u.id}) | Role: {u.role} | Key: {masked_key}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
