import asyncio
import re
import subprocess
import os
import logging
from typing import Optional, Callable

logger = logging.getLogger("BlenderOps")

class BlenderOps:
    def __init__(self, blender_path: str = "blender"):
        self.blender_path = blender_path

    async def render_frame(
        self, 
        blend_file: str, 
        output_path: str,
        frame: int,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """
        Executes Blender in background to render a single frame.
        Parses stdout for progress.
        """
        
        # Command: blender -b file.blend --disable-autoexec -o output_path -f frame
        cmd = [
            self.blender_path,
            "-b", blend_file,
            "--disable-autoexec", # [Security] Disable script auto-execution
            "-o", output_path,
            "-f", str(frame)
        ]
        
        logger.info(f"🎨 Starting Render: {' '.join(cmd)}")
        
        try:
            # Create subprocess
            # On Windows, we can set priority class?
            creationflags = 0
            if os.name == 'nt':
                 # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                 creationflags = 0x00004000
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=creationflags
            )
            
            # Read stdout line by line
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                decoded_line = line.decode().strip()
                if not decoded_line:
                    continue
                    
                # Log parsing for progress
                # Example: "Fra:1 Mem:12.34M (0.00M, Peak 12.34M) | Time:00:01.23 | Remaining:00:00.00 | Mem:12.34M, Peak:12.34M | Scene, ViewLayer | Rendered 10/100 Tiles"
                # Simplistic Regex for "Rendered X/Y Tiles" or similar.
                # Blender output varies by engine (Cycles/Eevee).
                # Let's assume standard Cycles output or check for "Time:" which implies running.
                
                # Regex for "Time:..." usually acts as heartbeat
                if "Time:" in decoded_line:
                    # Try to extract progress if tiles are mentioned
                    # "Rendered 50/100 Tiles"
                    match = re.search(r"Rendered (\d+)/(\d+) Tiles", decoded_line)
                    if match and progress_callback:
                        current, total = map(int, match.groups())
                        percent = int((current / total) * 100)
                        progress_callback(percent)
                
                # Also log errors
                if "Error" in decoded_line:
                    logger.error(f"[Blender] {decoded_line}")
                    
            await process.wait()
            
            if process.returncode == 0:
                logger.info("✅ Render Complete")
                return True
            else:
                stderr = await process.stderr.read()
                logger.error(f"❌ Render Failed (Code {process.returncode}): {stderr.decode()}")
                return False
                
        except FileNotFoundError:
             logger.error("❌ Blender executable not found. Please add to PATH.")
             return False
        except Exception as e:
            logger.error(f"❌ Execution Error: {e}")
            return False
