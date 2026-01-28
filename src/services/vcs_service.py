import hashlib
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models import ProjectCommit, FileBlob, CommitFile, ProjectHead, VCSAuditLog, VCSRollbackEvent

class VCSService:
    @staticmethod
    def calculate_hash(content: str) -> str:
        """Calculate SHA-256 hash for blobs or commits."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def _write_audit_log(self, db: AsyncSession, level: str, action: str, actor_id: int, resource_type: str, resource_id: str, message: str, details: Optional[Dict] = None):
        """Append-only Audit Log helper."""
        log = VCSAuditLog(
            level=level,
            action=action,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message,
            details=details
        )
        db.add(log)

    async def commit(self, db: AsyncSession, project_id: int, author_id: int, message: str, files: List[Dict[str, str]]) -> str:
        """
        Create a new commit snapshot with HEAD authority and Merkle integrity.
        """
        # 1. Deduplicate and Save Blobs
        blob_mappings = {}
        for file_data in files:
            content = file_data['content']
            path = file_data['path']
            b_hash = self.calculate_hash(content)
            
            blob = await db.get(FileBlob, b_hash)
            if not blob:
                blob = FileBlob(blob_hash=b_hash, content=content, size_bytes=len(content.encode('utf-8')))
                db.add(blob)
            
            blob_mappings[path] = b_hash

        # 2. Calculate Content Hash (Merkle Root of currently mapped files)
        sorted_items = sorted(list(blob_mappings.items()))
        content_hash = self.calculate_hash(json.dumps(sorted_items, sort_keys=True))

        # 3. Get Parent Commit and Project HEAD (Optimistic Locking)
        stmt = select(ProjectHead).where(ProjectHead.project_id == project_id)
        result = await db.execute(stmt)
        head = result.scalar_one_or_none()
        
        parent_hash = head.commit_hash if head else None
        
        # 4. Generate Commit Hash
        meta_str = f"{parent_hash}|{author_id}|{datetime.utcnow().isoformat()}|{message}"
        commit_raw = f"{content_hash}|{meta_str}"
        c_hash = self.calculate_hash(commit_raw)

        # 5. Create Commit Record
        new_commit = ProjectCommit(
            project_id=project_id,
            commit_hash=c_hash,
            parent_hash=parent_hash,
            content_hash=content_hash,
            message=message,
            author_id=author_id
        )
        db.add(new_commit)

        # 6. Map Files to Commit
        for path, b_hash in blob_mappings.items():
            commit_file = CommitFile(
                commit_hash=c_hash,
                blob_hash=b_hash,
                file_path=path
            )
            db.add(commit_file)

        # 7. Update Project HEAD with Optimistic Locking
        if head:
            # Atomic update with version check
            stmt = (
                update(ProjectHead)
                .where(ProjectHead.project_id == project_id)
                .where(ProjectHead.version_id == head.version_id)
                .values(commit_hash=c_hash, version_id=head.version_id + 1)
            )
            upd_res = await db.execute(stmt)
            if upd_res.rowcount == 0:
                raise Exception("Optimistic Locking Failure: Project HEAD was updated by another process.")
        else:
            new_head = ProjectHead(project_id=project_id, commit_hash=c_hash, version_id=1)
            db.add(new_head)

        # 8. Audit Plane Entry
        await self._write_audit_log(
            db=db, level="INFO", action="COMMIT", actor_id=author_id,
            resource_type="PROJECT", resource_id=str(project_id),
            message=f"Commit created: {c_hash}",
            details={"message": message, "file_count": len(files)}
        )

        await db.commit()
        return c_hash

    async def rollback(self, db: AsyncSession, project_id: int, executor_id: int, target_hash: str, project_root_path: str):
        """
        Atomic Restore Protocol: Stage -> Validate -> Switch -> Commit
        """
        # 1. Start Event Tracking
        event = VCSRollbackEvent(
            project_id=project_id,
            executor_id=executor_id,
            target_commit_hash=target_hash,
            status="STAGING"
        )
        db.add(event)
        await db.flush()

        try:
            # 2. Retrieve Commit Content
            files_to_restore = await self.get_commit_content(db, target_hash)
            if not files_to_restore:
                raise Exception(f"Commit {target_hash} not found or has no files.")

            # 3. Stage Phase
            staging_dir = os.path.join(project_root_path, ".vcs_staging", target_hash)
            if os.path.exists(staging_dir):
                shutil.rmtree(staging_dir)
            os.makedirs(staging_dir, exist_ok=True)

            for f in files_to_restore:
                full_path = os.path.join(staging_dir, f['path'])
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as fs:
                    fs.write(f['content'])

            # 4. Validate Phase
            event.status = "VALIDATED"
            for f in files_to_restore:
                full_path = os.path.join(staging_dir, f['path'])
                with open(full_path, 'r', encoding='utf-8') as fs:
                    restored_content = fs.read()
                if self.calculate_hash(restored_content) != f['hash']:
                    raise Exception(f"Integrity check failed for staged file: {f['path']}")

            # 5. Switch Phase (Atomic directory swap or surgical sync)
            # In a real high-integrity system, we'd use symlink swap. 
            # For local FS stability, we do surgical sync: delete all except staging, then move.
            for item in os.listdir(project_root_path):
                if item in [".vcs_staging", ".git", ".venv", "vess_manifest.json"]: # Skip management dirs
                    continue
                item_path = os.path.join(project_root_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

            for f in files_to_restore:
                src = os.path.join(staging_dir, f['path'])
                dst = os.path.join(project_root_path, f['path'])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)

            # Cleanup staging
            shutil.rmtree(os.path.join(project_root_path, ".vcs_staging"))

            # 6. Commit Phase (Authority Update)
            event.status = "COMMITTED"
            event.completed_at = datetime.utcnow()
            
            # Update HEAD Authority
            stmt = (
                update(ProjectHead)
                .where(ProjectHead.project_id == project_id)
                .values(commit_hash=target_hash, version_id=ProjectHead.version_id + 1)
            )
            await db.execute(stmt)

            await self._write_audit_log(
                db=db, level="WARN", action="ROLLBACK", actor_id=executor_id,
                resource_type="PROJECT", resource_id=str(project_id),
                message=f"System rolled back to {target_hash}"
            )
            
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            event.status = "FAILED"
            event.error_log = str(e)
            db.add(event)
            await db.commit()
            raise e

    async def get_history(self, db: AsyncSession, project_id: int) -> List[Dict]:
        """Fetch commit history for a project."""
        stmt = select(ProjectCommit).where(ProjectCommit.project_id == project_id).order_by(ProjectCommit.created_at.desc())
        result = await db.execute(stmt)
        commits = result.scalars().all()
        
        return [
            {
                "hash": c.commit_hash,
                "parent": c.parent_hash,
                "content_hash": c.content_hash,
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
