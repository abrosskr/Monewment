import asyncio
import pytest
import os
import shutil
from unittest.mock import MagicMock, AsyncMock
from src.ant_client.core.executor import JobExecutor
from src.core.protocol import JobRequest, JobType

@pytest.mark.asyncio
async def test_deep_render_pipeline():
    print("\n🎨 Starting DeepRender Pipeline Test...")
    
    # Setup
    os.environ["MOCK_BLENDER"] = "1"
    
    # Mocks
    mock_downloader = MagicMock()
    mock_downloader.download_file = AsyncMock(return_value="tests/temp_render_test/input.blend")
    
    mock_uploader = MagicMock()
    mock_uploader.upload_file = AsyncMock(return_value=777) # Mock Output File ID
    
    executor = JobExecutor("test_ant", vault_downloader=mock_downloader, vault_uploader=mock_uploader)
    
    # Create Dummy Input
    test_dir = "tests/temp_render_test"
    if not os.path.exists(test_dir): os.makedirs(test_dir)
    with open(os.path.join(test_dir, "input.blend"), "wb") as f:
        f.write(b"mock_blend_content")
        
    # Job Request
    job = JobRequest(
        job_id="job_123",
        project_id=1,
        job_type="RENDER_3D",
        params={"input_file_id": 101, "frame": 42},
        priority=1
    )
    
    # Execution
    print("▶️ Executing Render Job...")
    result = await executor.execute_job(job)
    
    # Assertions
    print(f"✅ Result Status: {result.status}")
    assert result.status == "COMPLETED"
    
    # 1. Verify Download
    mock_downloader.download_file.assert_called_with(101, f"temp_render_{job.job_id}")
    print("✅ Input File Downloaded.")
    
    # 2. Verify Output Generation (Mock verification logic inside Executor happened)
    # 3. Verify Upload (ID 777)
    # Check arguments: uploader.upload_file(expected_path)
    # Expected path: temp_render_job_123/render_0042.png
    expected_out = f"temp_render_{job.job_id}{os.sep}render_0042.png"
    mock_uploader.upload_file.assert_called_with(expected_out)
    print(f"✅ Output File Uploaded (ID: {result.output_data.get('output_file_id')})")
    
    assert result.output_data["output_file_id"] == 777
    
    # Cleanup
    if os.path.exists(test_dir): shutil.rmtree(test_dir)
    # Also Executor cleans up its temp dir.
    
    print("✅ DeepRender Pipeline Verified Successfully.")

if __name__ == "__main__":
    asyncio.run(test_deep_render_pipeline())
