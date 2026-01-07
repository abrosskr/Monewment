import asyncio
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.ant_client.core.render.blender_ops import BlenderOps

class TestBlenderSecurity(unittest.IsolatedAsyncioTestCase):
    async def test_security_flags_present(self):
        """Verify --disable-autoexec is FORCED into the command."""
        ops = BlenderOps(blender_path="blender_mock")
        
        # Mock subprocess
        with patch('asyncio.create_subprocess_exec', new_callable=MagicMock) as mock_exec:
            # Setup mock return (process object)
            mock_process = MagicMock()
            mock_process.stdout.readline = asyncio.Future()
            mock_process.stdout.readline.set_result(b"") # EOF immediately
            mock_process.wait = asyncio.Future()
            mock_process.wait.set_result(None)
            mock_process.returncode = 0
            
            mock_exec.return_value = asyncio.Future()
            mock_exec.return_value.set_result(mock_process)
            
            # Run
            await ops.render_frame("malicious.blend", "out", 1)
            
            # Inspect Args
            # args[0] is executable, args[1:] are flags
            call_args = mock_exec.call_args[0]
            cmd = list(call_args)
            
            print(f"Captured Command: {cmd}")
            
            self.assertIn("--disable-autoexec", cmd, "CRITICAL: --disable-autoexec missing!")
            self.assertNotIn("-y", cmd, "CRITICAL: -y (Auto Exec) flag found!")
            
            # Additional checks
            self.assertIn("-b", cmd) # Background mode
            
if __name__ == '__main__':
    unittest.main()
