import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import engine
from src.models import Base

async def migrate_vcs():
    print("🚀 Starting VCS Schema Migration...")
    try:
        async with engine.begin() as conn:
            # create_all only creates tables that don't exist
            await conn.run_sync(Base.metadata.create_all)
        print("✅ VCS Tables (project_commits, file_blobs, commit_files) created successfully.")
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        # Print full traceback if needed
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_vcs())
