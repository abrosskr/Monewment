import os
import sys
import logging
import httpx
import threading
import asyncio
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("ant.governance")

def ensure_alive(ant_instance: Any):
    """
    Decorator to ensure the ANT is still alive before executing any task.
    Usage: @ensure_alive(ant)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not getattr(ant_instance, "is_alive", True):
                logger.error(f"[TERMINATED] Refusing to execute {func.__name__}. ANT is DEAD.")
                raise RuntimeError(f"Honorable Seppuku already performed. Task {func.__name__} aborted.")
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not getattr(ant_instance, "is_alive", True):
                logger.error(f"[TERMINATED] Refusing to execute {func.__name__}. ANT is DEAD.")
                raise RuntimeError(f"Honorable Seppuku already performed. Task {func.__name__} aborted.")
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator

class AntLifeCycle:
    """
    Universal Imperial Governance Protocol for all ANT types (Forager, Artist, Analyst).
    Handles heartbeat pings, budget enforcement, and emergency self-termination.
    """
    def __init__(self, ant_id: str, stratum_id: str, api_url: str):
        self.ant_id = ant_id
        self.stratum_id = stratum_id
        self.api_url = api_url
        self.is_alive = True
        self.accumulated_cost = 0.0
        self.network_fail_count = 0
        self._kill_timer = None

    async def pulse(self, client: httpx.AsyncClient):
        """Standardized heartbeat pulse to report status and costs."""
        if not self.is_alive:
            return

        payload = {
            "current_session_cost": self.accumulated_cost,
            "note": "Imperial Origin Template Pulse"
        }
        
        headers = {
            "X-Alias": "ANT",
            "X-Stratum-ID": self.stratum_id
        }

        try:
            resp = await client.patch(
                f"{self.api_url}/registry/ping/ant/{self.ant_id}",
                json=payload,
                headers=headers
            )
            
            # Reset network monitoring on success
            self.network_fail_count = 0

            # 1. Budget Death (Status 200, KILL_ORDER in body)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "KILL_ORDER":
                    self.perform_seppuku(f"Budget Exceeded: {data.get('reason')}")
                    return

            # 2. Identity Death (Status 409 Conflict)
            if resp.status_code == 409:
                self.perform_seppuku("Identity Collision (Zombie Detected)")
                return

            resp.raise_for_status()

        except httpx.RequestError as e:
            self.network_fail_count += 1
            if self.network_fail_count >= 6:
                self.perform_seppuku("Network Isolation (6 failures)")

    def perform_seppuku(self, reason: str):
        """The 'Honorable Seppuku' - Safe self-termination sequence."""
        if not self.is_alive:
            return
            
        self.is_alive = False
        logger.critical(f"!!! [HONORABLE SEPPUKU] Reason: {reason} !!!")
        logger.info("Glory to the Empire. Terminating process in 5.0 seconds...")
        
        # Hard kill timer in case of hangs
        self._kill_timer = threading.Timer(5.0, lambda: os._exit(1))
        self._kill_timer.daemon = True
        self._kill_timer.start()
