import os
import sys
import hashlib
import shutil
import logging
import asyncio
import aiohttp
import subprocess
from typing import Optional, Dict

logger = logging.getLogger("AntUpdater")

class AntUpdater:
    def __init__(self, current_version: str, server_url: str):
        self.current_version = current_version
        self.server_url = server_url
        self.base_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # For dev mode (not frozen), base_dir might be different, but strict OTA usually applies to Frozen EXE.
        
        self.exe_path = sys.executable if getattr(sys, 'frozen', False) else None
        
    async def check_for_updates(self) -> Optional[Dict]:
        """
        Polls the server for version info.
        Returns update_data dict if new version available, else None.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/client/version") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        remote_version = data.get("version")
                        if self._is_newer(remote_version):
                            logger.info(f"🆕 New version found: {remote_version} (Current: {self.current_version})")
                            return data
        except Exception as e:
            logger.warning(f"Update check failed: {e}")
            
        return None

    async def perform_update(self, update_data: Dict) -> bool:
        """
        Orchestrates the Fail-Safe Update Flow.
        CHECK -> DOWNLOAD -> VERIFY -> BACKUP -> SWAP -> RESTART
        """
        if not self.exe_path:
            logger.error("❌ Cannot update in non-frozen (script) mode.")
            return False

        logger.info("🚀 Starting Robust Update Sequence...")
        
        url = update_data.get("download_url")
        expected_hash = update_data.get("hash")
        
        tmp_path = self.exe_path + ".tmp"
        bak_path = self.exe_path + ".bak"
        
        # 1. DOWNLOAD
        if not await self._download_file(url, tmp_path):
            return False
            
        # 2. VERIFY
        if expected_hash and not self._verify_hash(tmp_path, expected_hash):
            logger.error("❌ Hash Mismatch! Possible Man-in-the-Middle or Corruption.")
            os.remove(tmp_path)
            return False
            
        # 3. BACKUP & SWAP (Atomic-ish)
        try:
            if os.path.exists(bak_path):
                os.remove(bak_path)
            
            logger.info("💾 Creating Backup...")
            os.rename(self.exe_path, bak_path)
            
            logger.info("🔄 Swapping Binaries...")
            os.rename(tmp_path, self.exe_path)
            
            # 4. RESTART
            logger.info("🔄 Restarting Application...")
            subprocess.Popen([self.exe_path, "--post-update"])
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ Update Failed during Swap: {e}")
            # ROLLBACK
            logger.warning("⏪ Rolling back changes...")
            if os.path.exists(bak_path) and not os.path.exists(self.exe_path):
                os.rename(bak_path, self.exe_path)
            elif os.path.exists(bak_path) and os.path.exists(self.exe_path):
                 # Swap failed halfway? Restore backup active
                 os.remove(self.exe_path)
                 os.rename(bak_path, self.exe_path)
            return False

    async def _download_file(self, url: str, target_path: str) -> bool:
        logger.info(f"⬇️ Downloading update from {url}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(target_path, 'wb') as f:
                            while True:
                                chunk = await resp.content.read(4096)
                                if not chunk: break
                                f.write(chunk)
                        return True
                    else:
                        logger.error(f"Download failed: HTTP {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False

    def _verify_hash(self, file_path: str, expected_hash: str) -> bool:
        logger.info("🛡️ Verifying Integrity...")
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data: break
                sha256.update(data)
        
        calculated_hash = sha256.hexdigest()
        if hasattr(expected_hash, 'lower'):
             match = calculated_hash.lower() == expected_hash.lower()
        else:
             match = calculated_hash == expected_hash
             
        if not match:
            logger.error(f"Hash Mismatch! Expected: {expected_hash}, Got: {calculated_hash}")
            
        return match

    def _is_newer(self, remote_ver: str) -> bool:
        # Simple SemVer check
        try:
            def to_int(v): return [int(x) for x in v.split('.')]
            return to_int(remote_ver) > to_int(self.current_version)
        except:
            return False
