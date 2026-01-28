import asyncio
import sys
import os
from pprint import pprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import AsyncSessionLocal
from src.services.vcs_service import vcs_service
from src.models import Project, User

async def test_vcs_flow():
    print("🧪 Starting VCS Functional Test Flow...")
    async with AsyncSessionLocal() as db:
        # 1. Ensure a test project and user exist
        # We assume project 1 and user 1 might exist or we create dummy logic
        # For safety in test, we just check if we can insert.
        
        project_id = 1
        author_id = 1
        
        print(f"📝 Step 1: Creating Commit 1 (Genesis)")
        files_v1 = [
            {"path": "hello.py", "content": "print('Hello Monewment')"},
            {"path": "config.json", "content": '{"version": "1.0"}'}
        ]
        
        hash_v1 = await vcs_service.commit(
            db=db,
            project_id=project_id,
            author_id=author_id,
            message="Initial Genesis Commit",
            files=files_v1
        )
        print(f"✅ Commit 1 Hash: {hash_v1}")

        print(f"\n📝 Step 2: Creating Commit 2 (Update)")
        files_v2 = [
            {"path": "hello.py", "content": "print('Hello Control Plane')"}, # Changed
            {"path": "config.json", "content": '{"version": "1.0"}'}, # Same (Deduplication check)
            {"path": "new_file.txt", "content": "Welcome to Phase 6"} # Added
        ]
        
        hash_v2 = await vcs_service.commit(
            db=db,
            project_id=project_id,
            author_id=author_id,
            message="Updated hello logic and added new file",
            files=files_v2
        )
        print(f"✅ Commit 2 Hash: {hash_v2}")

        print(f"\n🔍 Step 3: Verifying History for Project {project_id}")
        history = await vcs_service.get_history(db, project_id)
        pprint(history)
        
        assert len(history) >= 2
        assert history[0]["hash"] == hash_v2
        assert history[1]["hash"] == hash_v1
        print("✅ History Order Verified.")

        print(f"\n🔍 Step 4: Verifying Content of Commit 1")
        content_v1 = await vcs_service.get_commit_content(db, hash_v1)
        pprint(content_v1)
        assert len(content_v1) == 2
        
        print(f"\n🔍 Step 5: Verifying Deduplication (FileBlob)")
        # Check if config.json shares same blob hash in both commits
        blob_v1 = next(f["hash"] for f in content_v1 if f["path"] == "config.json")
        content_v2 = await vcs_service.get_commit_content(db, hash_v2)
        blob_v2 = next(f["hash"] for f in content_v2 if f["path"] == "config.json")
        
        print(f"Blob Hash (v1): {blob_v1}")
        print(f"Blob Hash (v2): {blob_v2}")
        assert blob_v1 == blob_v2
        print("✅ Deduplication (Blob Reuse) Verified.")

    print("\n✨ VCS Functional Test PASSED successfully.")

if __name__ == "__main__":
    asyncio.run(test_vcs_flow())
