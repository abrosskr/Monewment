
import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import User
from src.core.security import verify_password, hash_password

async def debug_auth():
    async with AsyncSessionLocal() as db:
        email = "monewment@admin.com"
        password = "admin123"
        
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ User {email} NOT FOUND in DB.")
            return

        print(f"✅ User Found: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Hashed Password in DB: {user.hashed_password}")
        
        is_valid = verify_password(password, user.hashed_password)
        if is_valid:
            print(f"✅ Password '{password}' matches!")
        else:
            print(f"❌ Password verification FAILED.")
            # Debug: Try hashing again
            new_hash = hash_password(password)
            print(f"   New Hash of '{password}': {new_hash}")

if __name__ == "__main__":
    asyncio.run(debug_auth())
