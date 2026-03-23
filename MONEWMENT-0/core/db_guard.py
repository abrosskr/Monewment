# MONEWMENT-0/core/db_guard.py
import asyncio
import time
import json
import os
from pathlib import Path
from .logger import logger

class DBGuard:
    """
    [FORTIFICATION] Local Infrastructure Guard with Persistence.
    Prevents "Self-DDOS" by tracking local connection failures and enforcing exponential backoff
    even across process restarts using a state file.
    """
    _STATE_FILE = Path(os.getcwd()).resolve() / ".temp" / "db_guard_state.json"
    _MAX_BACKOFF = 300  # 5 minutes
    _BASE_BACKOFF = 2
    _CIRCUIT_THRESHOLD = 5 # Stricter threshold for total failures across restarts

    def __init__(self):
        # Ensure .temp directory exists
        self._STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._failure_count = 0
        self._last_failure_time = 0
        self._load_state()


    def _load_state(self):
        try:
            if self._STATE_FILE.exists():
                # Use a small wait/retry for file locking if multiple processes hit it
                with open(self._STATE_FILE, "r") as f:
                    state = json.load(f)
                    self._failure_count = state.get("failure_count", 0)
                    self._last_failure_time = state.get("last_failure_time", 0)
        except Exception:
            # Silently reset if corruption occurs
            self._reset_state()

    def _save_state(self):
        try:
            with open(self._STATE_FILE, "w") as f:
                json.dump({
                    "failure_count": self._failure_count,
                    "last_failure_time": self._last_failure_time
                }, f)
        except Exception as e:
            logger.error(f"[DB GUARD] Failed to save state: {e}")

    def _reset_state(self):
        self._failure_count = 0
        self._last_failure_time = 0

    async def check_and_wait(self):
        """Checks if a local circuit is tripped and waits if backoff is active."""
        self._load_state() 
        if self._failure_count == 0:
            return

        delay = min(self._BASE_BACKOFF ** self._failure_count, self._MAX_BACKOFF)
        time_since_failure = time.time() - self._last_failure_time
        
        if time_since_failure < delay:
            wait_time = delay - time_since_failure
            logger.warning(
                f"[DB GUARD] Local Circuit Active. Backing off for {wait_time:.1f}s "
                f"(Persistent Failures: {self._failure_count})"
            )
            await asyncio.sleep(wait_time)

    def report_failure(self, is_auth_error: bool = False):
        """Reports a connection failure."""
        self._load_state()
        self._failure_count += 1
        self._last_failure_time = int(time.time())
        self._save_state()

        
        if is_auth_error:
            logger.error("[DB GUARD] Authentication Error detected/propagated.")
            if self._failure_count >= self._CIRCUIT_THRESHOLD:
                logger.critical(f"[DB GUARD] LOCAL CIRCUIT TRIPPED: {self._failure_count} persistent failures.")

    def report_success(self):
        """Resets the failure counter."""
        self._load_state()
        if self._failure_count > 0:
            logger.info("[DB GUARD] Connection successful. Resetting persistent failure counter.")
            self._reset_state()
            self._save_state()

# Singleton instance for the module
db_guard = DBGuard()

db_guard = DBGuard()
