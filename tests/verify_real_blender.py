import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.ant_client.core.render.blender_ops import BlenderOps

async def test_real_blender():
    print(f"🧪 Testing Real Blender Integration...")
    print(f"📂 Blender Path: {settings.BLENDER_PATH}")
    
    # 1. Check Blender Path
    if not os.path.exists(settings.BLENDER_PATH):
        print(f"❌ Blender Executable not found at {settings.BLENDER_PATH}")
        # Try to find it? No, just fail.
        return
        
    # 2. Setup Test Assets
    base_dir = settings.BASE_DIR
    cube_blend = os.path.join(base_dir, "cube.blend")
    output_dir = os.path.join(base_dir, "test_output")
    os.makedirs(output_dir, exist_ok=True)
    output_prefix = os.path.join(output_dir, "render_")
    
    # Ensure cube.blend exists (We tried strictly generating it before)
    # If not exists, we create a dummy just to see if Blender RUNS (even if it errors on file load)
    # But ideally we want successful render.
    if not os.path.exists(cube_blend):
        print("⚠️ cube.blend not found. Creating dummy file to test Process Launch...")
        with open(cube_blend, "wb") as f:
            f.write(b"FAKE_BLEND")
            
    # 3. Initialize Ops
    ops = BlenderOps(blender_path=settings.BLENDER_PATH)
    
    # 4. Run Render
    print("🚀 Invoking Blender...")
    try:
        # We render frame 1
        success = await ops.render_frame(
            blend_file=cube_blend,
            output_path=output_prefix,
            frame=1,
            progress_callback=lambda p: print(f"  > Progress: {p}%")
        )
        
        if success:
            print("✅ Blender Render Process Completed Successfully!")
            if os.path.exists(f"{output_prefix}0001.png"):
                print("✅ Output Image Verified!")
            else:
                print("⚠️ Output Image NOT found (Expected for Mock Blend file)")
        else:
            print("❌ Blender Process Returned Failure (Expected if Blend file is invalid)")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_blender())
