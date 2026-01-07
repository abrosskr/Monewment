import asyncio
from src.dependencies import get_db
from src.models import User
from src.database import AsyncSessionLocal
from sqlalchemy import select

async def create_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "test@monewment.com"))
        user = result.scalars().first()
        
        if not user:
            print("Creating test user...")
            user = User(
                email="test@monewment.com",
                hashed_password="hashed_secret",
                api_key="test_key_123", # <--- Key for test
                role="ADMIN"
            )
            db.add(user)
        else:
            print("Updating test user key...")
            user.api_key = "test_key_123"
            
        await db.commit()
        print("✅ User Ready: test_key_123")

if __name__ == "__main__":
    asyncio.run(create_user())
