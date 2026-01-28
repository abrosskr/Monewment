import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import engine
from src.models import Base, ProjectCommit, FileBlob, CommitFile, ProjectHead, VCSRollbackEvent, VCSAuditLog

async def recreate_vcs():
    print("🗑️ Dropping existing VCS tables...")
    async with engine.begin() as conn:
        # Drop in order of dependencies
        for table in [VCSAuditLog, VCSRollbackEvent, CommitFile, ProjectHead, ProjectCommit, FileBlob]:
            await conn.run_sync(table.__table__.drop, checkfirst=True)
        
        print("🚀 Recreating VCS tables with full schema...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ VCS Tables recreated successfully.")

if __name__ == "__main__":
    asyncio.run(recreate_vcs())
