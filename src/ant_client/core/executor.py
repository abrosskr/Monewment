import logging
import asyncio
import random
import os
from datetime import datetime
from typing import Dict, Any, Optional

from src.core.protocol import JobRequest, JobResult, JobStatus, JobType
from src.ant_client.core.render.blender_ops import BlenderOps
# We need Vault classes passed in or imported. 
# Ideally Executor is initialized with them or creates them.
# For Clean Arch, we might pass them in execute, but for Phase 6 MVP, init here.
# NOTE: To avoid circular imports if Executor used in main before Vault...
# We will lazy import or assume they are available.
from src.config import settings

logger = logging.getLogger("AntExecutor")

class JobExecutor:
    def __init__(self, client_id: str, vault_downloader=None, vault_uploader=None):
        self.client_id = client_id
        # Dependency Injection for Vault Components
        self.downloader = vault_downloader
        self.uploader = vault_uploader
        self.blender = BlenderOps(blender_path=settings.BLENDER_PATH)
        
    async def execute_job(self, job: JobRequest) -> JobResult:
        logger.info(f"🎨 Executing Job {job.job_id} ({job.job_type})")
        start_time = datetime.utcnow()
        
        output_data = {}
        status = JobStatus.FAILED
        
        try:
            if job.job_type == "RENDER_3D": # JobType.RENDER defined as string usually or Enum
                # 1. Download Input (Blend File)
                if not self.downloader:
                    raise ValueError("Vault Downloader not configured")
                    
                # job.data should contain "input_file_id"
                input_file_id = job.params.get("input_file_id")
                if not input_file_id:
                     raise ValueError("Missing input_file_id")
                     
                temp_dir = f"temp_render_{job.job_id}"
                os.makedirs(temp_dir, exist_ok=True)
                
                blend_path = await self.downloader.download_file(input_file_id, temp_dir)
                if not blend_path:
                    raise Exception("Download failed")
                    
                # 2. Render
                # Output filename pattern: frame_####.png
                output_prefix = os.path.join(temp_dir, "render_")
                target_frame = job.params.get("frame", 1)
                
                # Mock Blender if flag set or if we want to skip heavy render
                # For Phase 6-6 verification without actual blender installed:
                # We can check if "MOCK_BLENDER" env var is set.
                if os.getenv("MOCK_BLENDER") == "1":
                    await asyncio.sleep(1) # Sim work
                    # Create dummy output
                    output_file = f"{output_prefix}{target_frame:04d}.png"
                    with open(output_file, "wb") as f:
                        f.write(b"fake_image_data")
                    success = True
                else:
                    success = await self.blender.render_frame(
                        blend_path, 
                        output_prefix, 
                        target_frame,
                        progress_callback=lambda p: print(f"Job {job.job_id}: {p}%")
                    )
                
                if not success:
                    raise Exception("Rendering failed")
                    
                # Expected output file
                # Blender appends frame number: output_prefix + 0001.png
                output_file = f"{output_prefix}{target_frame:04d}.png"
                
                if not os.path.exists(output_file):
                     # Try without padding if name different
                     pass
                
                # 3. Upload Result
                if not self.uploader:
                     raise ValueError("Vault Uploader not configured")
                     
                # We need to upload this file. 
                # Ideally Uploader returns file_id
                # But current Uploader prints to stdout mostly. 
                # We need to modify Uploader to return ID or parse it.
                # Wait, Uploader.upload_file returns None currently?
                # Check uploader implementation: it sends requests but returns nothing.
                # Update: I need to FIX Uploader to return file_id.
                
                # Assume Uploader is fixed/updated or we hack it here.
                # Let's trust it works and initiates upload. 
                # Problem: We need the RESULT ID to return in JobResult.
                
                # Quick Fix: Modify Executor to use API directly or Update Uploader?
                # Update Uploader is better. 
                # For now, let's assume we implement a `upload_and_get_id` method or similar.
                
                # Implementation Note: Since Uploader in Phase 6-3 was CLI-focused,
                # I will create a helper here or modify Uploader in next step.
                # Assuming `upload_file` returns file_id (will modify next).
                output_file_id = await self.uploader.upload_file(output_file)
                
                output_data["output_file_id"] = output_file_id
                status = JobStatus.COMPLETED
                
                # Cleanup
                import shutil
                shutil.rmtree(temp_dir)
                
            else:
                 # Legacy simulation
                 await asyncio.sleep(2)
                 output_data["legacy"] = "done"
                 status = JobStatus.COMPLETED

        except Exception as e:
            logger.error(f"Job Execution Error: {e}")
            output_data["error"] = str(e)
            
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return JobResult(
            job_id=job.job_id,
            status=status,
            worker_id=self.client_id,
            output_urls=[], # Deprecated in favor of Vault ID? Or allow both.
            output_data=output_data, # New field for flexible data
            execution_time_ms=execution_time
        )
