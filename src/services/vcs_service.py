import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import ProjectCommit, FileBlob, CommitFile

class VCSService:
    @staticmethod
    def calculate_hash(content: str) -> str:
        """Calculate SHA-256 hash for blobs or commits."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def commit(self, db: AsyncSession, project_id: int, author_id: int, message: str, files: List[Dict[str, str]]) -> str:
        """
        Create a new commit snapshot for a project.
        Files should be a list of {'path': str, 'content': str}
        """
        # 1. Deduplicate and Save Blobs
        blob_mappings = {}
        for file_data in files:
            content = file_data['content']
            path = file_data['path']
            b_hash = self.calculate_hash(content)
            
            # Check if blob exists
            blob = await db.get(FileBlob, b_hash)
            if not blob:
                blob = FileBlob(blob_hash=b_hash, content=content, size_bytes=len(content.encode('utf-8')))
                db.add(blob)
            
            blob_mappings[path] = b_hash

        # 2. Get Parent Commit (latest one)
        stmt = select(ProjectCommit).where(ProjectCommit.project_id == project_id).order_by(ProjectCommit.created_at.desc()).limit(1)
        result = await db.execute(stmt)
        parent = result.scalar_one_or_none()
        parent_hash = parent.commit_hash if parent else None

        # 3. Generate Commit Hash
        # Chain depends on parent hash + current state (sorted files) + metadata
        state_str = json.dumps(sorted(list(blob_mappings.items())), sort_keys=True)
        meta_str = f"{parent_hash}|{author_id}|{datetime.utcnow().isoformat()}|{message}"
        commit_raw = f"{state_str}|{meta_str}"
        c_hash = self.calculate_hash(commit_raw)

        # 4. Create Commit Record
        new_commit = ProjectCommit(
            project_id=project_id,
            commit_hash=c_hash,
            parent_hash=parent_hash,
            message=message,
            author_id=author_id
        )
        db.add(new_commit)

        # 5. Map Files to Commit
        for path, b_hash in blob_mappings.items():
            commit_file = CommitFile(
                commit_hash=c_hash,
                blob_hash=b_hash,
                file_path=path
            )
            db.add(commit_file)

        await db.commit()
        return c_hash

    async def get_history(self, db: AsyncSession, project_id: int) -> List[Dict]:
        """Fetch commit history for a project."""
        stmt = select(ProjectCommit).where(ProjectCommit.project_id == project_id).order_by(ProjectCommit.created_at.desc())
        result = await db.execute(stmt)
        commits = result.scalars().all()
        
        return [
            {
                "hash": c.commit_hash,
                "parent": c.parent_hash,
                "message": c.message,
                "author_id": c.author_id,
                "created_at": c.created_at.isoformat()
            } for c in commits
        ]

    async def get_commit_content(self, db: AsyncSession, commit_hash: str) -> List[Dict]:
        """Fetch all file paths and contents for a specific commit."""
        stmt = select(CommitFile).where(CommitFile.commit_hash == commit_hash)
        result = await db.execute(stmt)
        files = result.scalars().all()
        
        output = []
        for f in files:
            blob = await db.get(FileBlob, f.blob_hash)
            output.append({
                "path": f.file_path,
                "content": blob.content if blob else None,
                "hash": f.blob_hash
            })
        return output

vcs_service = VCSService()
