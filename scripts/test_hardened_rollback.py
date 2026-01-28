import asyncio
import os
import sys
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import engine
from src.dependencies import get_db
from src.services.vcs_service import vcs_service
from src.models import Project, User, ProjectHead, VCSRollbackEvent, VCSAuditLog
from sqlalchemy import select

async def test_hardened_rollback():
    print("🧪 Starting Hardened VCS Rollback Verification...")
    
    async for db in get_db():
        # 1. Setup Dummy Project
        project_name = "rollback_test_project"
        project_path = os.path.abspath(f"projects/{project_name}")
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path, exist_ok=True)
        
        # Check if project exists in DB
        result = await db.execute(select(Project).where(Project.name == project_name))
        project = result.scalar_one_or_none()
        if not project:
            project = Project(name=project_name)
            db.add(project)
            await db.flush()
        
        # 2. First Commit (V1)
        files_v1 = [
            {"path": "main.py", "content": "print('Hello V1')"},
            {"path": "config.json", "content": '{"version": 1}'}
        ]
        print("📝 Creating Commit V1...")
        h1 = await vcs_service.commit(db, project.id, 1, "Initial Commit V1", files_v1)
        print(f"✅ V1 Hash: {h1}")
        
        # 3. Second Commit (V2)
        files_v2 = [
            {"path": "main.py", "content": "print('Hello V2')"},
            {"path": "extra.txt", "content": "New file in V2"}
        ]
        print("📝 Creating Commit V2...")
        h2 = await vcs_service.commit(db, project.id, 1, "Update V2", files_v2)
        print(f"✅ V2 Hash: {h2}")
        
        # 4. Perform Rollback to V1
        print(f"🚑 Initiating Rollback to V1 ({h1})...")
        success = await vcs_service.rollback(db, project.id, 1, h1, project_path)
        
        if success:
            print("✨ Rollback SUCCESS.")
        else:
            print("❌ Rollback FAILED.")
            return

        # 5. Verification
        print("🔍 Verifying physical files...")
        assert os.path.exists(os.path.join(project_path, "main.py"))
        with open(os.path.join(project_path, "main.py"), 'r') as f:
            content = f.read()
            assert content == "print('Hello V1')"
            print("  - main.py restored correctly.")
            
        assert os.path.exists(os.path.join(project_path, "config.json"))
        print("  - config.json restored (was deleted in V2).")
        
        assert not os.path.exists(os.path.join(project_path, "extra.txt"))
        print("  - extra.txt removed (was added in V2).")
        
        print("🔍 Verifying HEAD Authority...")
        result = await db.execute(select(ProjectHead).where(ProjectHead.project_id == project.id))
        head = result.scalar_one()
        assert head.commit_hash == h1
        print(f"  - HEAD points to {h1}.")
        
        print("🔍 Verifying Audit Trail...")
        result = await db.execute(select(VCSRollbackEvent).filter_by(project_id=project.id).order_by(VCSRollbackEvent.created_at.desc()))
        event = result.scalars().first()
        assert event.status == "COMMITTED"
        print(f"  - RollbackEvent status: {event.status}")
        
        result = await db.execute(select(VCSAuditLog).filter_by(action="ROLLBACK").order_by(VCSAuditLog.created_at.desc()))
        log = result.scalars().first()
        print(f"  - AuditLog: {log.message}")
        
        print("\n🏆 Verification COMPLETE. High-Integrity VCS Authority is operational.")
        break # async for get_db is a generator, we only need one session

if __name__ == "__main__":
    asyncio.run(test_hardened_rollback())
