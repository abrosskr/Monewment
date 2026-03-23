import asyncio
import logging
import httpx
import time
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable, Any, Coroutine, Optional
from pydantic import BaseModel

# [KST TIMEZONE ENFORCEMENT]
KST = timezone(timedelta(hours=9))
logger = logging.getLogger("imperial.robustness")

# ─── CORE SDK: MONEWMENT v51.5 (Great Synchronization) ─────────────────────

def get_imperial_client(timeout: float = 10.0, is_async: bool = True) -> httpx.AsyncClient | httpx.Client:
    """Returns an httpx client pre-configured to bypass system proxies (Windows loopback safety)."""
    if is_async:
        return httpx.AsyncClient(trust_env=False, timeout=timeout)
    else:
        return httpx.Client(trust_env=False, timeout=timeout)

async def wait_for_core(url: str, attempts: int = 30, interval: float = 2.0) -> bool:
    """Standardized readiness polling loop for MONEWMENT-0 Core."""
    logger.info(f"Waiting for Imperial Core API ({url})...")
    async with get_imperial_client(timeout=2.0) as client:
        for i in range(1, attempts + 1):
            try:
                r = await client.get(f"{url}/health")
                if r.status_code == 200:
                    logger.info("[OK] Imperial Core API Reachable. Starting sequence.")
                    return True
            except Exception:
                pass
            if i % 5 == 0:
                logger.warning(f"Core API still unreachable (Attempt {i}/{attempts})...")
            await asyncio.sleep(interval)
    
    logger.critical("[FAIL] Imperial Core API Unreachable. Stability protocol failed.")
    return False

async def retry_ceremony(
    func: Callable[..., Coroutine[Any, Any, Any]], 
    *args, 
    attempts: int = 3, 
    initial_delay: float = 2.0, 
    **kwargs
) -> Any:
    """Executes a coroutine with exponential backoff. Ideal for /registry/birth."""
    delay = initial_delay
    last_exception = None
    
    for i in range(1, attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"Ceremony attempt {i} failed: {e}")
            if i < attempts:
                await asyncio.sleep(delay)
                delay *= 2
                
    raise last_exception

# ─── V51.5 GOVERNANCE ──────────────────────────────────────────────────────

class ImperialGovernance:
    """
    [V51.5] Centralized Governance Layer for all Imperial Entities (ANT, QUEEN, AREUM).
    Handles Heartbeats, Budget Tracking, and Seppuku (KILL_ORDER).
    """
    def __init__(self, entity_type: str, entity_id: str, core_url: str, gateway_token: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.core_url = core_url
        self.headers = {
            "Content-Type": "application/json",
            "X-Queen-Token": gateway_token,
            "X-Alias": entity_type.upper()
        }
        self.current_session_cost = 0.0
        self.accumulated_cost = 0.0
        self.is_alive = True
        self._heartbeat_task = None
        self._fencing_token = 1

    def set_fencing_token(self, token: int):
        self._fencing_token = token

    def get_fencing_headers(self) -> dict:
        return {**self.headers, "X-Fencing-Token": str(self._fencing_token)}

    async def start_heartbeat(self):
        """Starts a background Jittered Heartbeat loop (10-30s)."""
        if self._heartbeat_task: return
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        logger.info("[HEARTBEAT] Starting Force Pulse...")
        async with get_imperial_client() as client:
            while self.is_alive:
                try:
                    # PATCH /v1/registry/ping/{type}/{id}
                    r = await client.patch(
                        f"{self.core_url}/registry/ping/{self.entity_type}/{self.entity_id}",
                        headers=self.headers,
                        json={
                            "current_session_cost": self.current_session_cost,
                            "accumulated_cost": getattr(self, "accumulated_cost", 0.0),
                            # [KST SYNC RECTIFIED] 사전에 선언된 KST 변수를 정확히 사용합니다.
                            "timestamp_kst": datetime.now(KST).replace(tzinfo=None).isoformat()
                        },
                        timeout=5.0
                    )
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("status") == "KILL_ORDER":
                            await self.trigger_seppuku(data.get("reason", "Budget Exceeded"))
                        else:
                            self._fencing_token = data.get("fencing_token", self._fencing_token)
                            if "accumulated_cost" in data:
                                self.accumulated_cost = data["accumulated_cost"]
                except Exception as e:
                    logger.warning(f"[GOVERNANCE] Heartbeat failed: {e}")
                
                await asyncio.sleep(random.uniform(10.0, 30.0))

    async def birth(self, payload: dict, instance_path: str, idempotency_key: str = None) -> bool:
        """[BIRTH CEREMONY] Registers the entity with the Imperial Registry."""
        async with get_imperial_client() as client:
            try:
                # v2.0 Contract: Requires Idempotency-Key
                if not idempotency_key:
                    idempotency_key = str(uuid.uuid4())
                logger.info(f"[GOVERNANCE] Commencing Birth Ceremony for {self.entity_type} {self.entity_id} (Key: {idempotency_key[:8]}...)...")
                
                r = await client.post(
                    f"{self.core_url}/registry/birth",
                    headers={**self.headers, "Idempotency-Key": idempotency_key},
                    json={
                        "entity_type": self.entity_type,
                        "payload": payload,
                        "instance_path": instance_path
                    }
                )
                if r.status_code in (200, 201, 202, 409):
                    logger.info(f"[GOVERNANCE] {self.entity_type} recognized by Imperial Core.")
                    return True
                else:
                    logger.error(f"[GOVERNANCE] Birth failed: {r.status_code} {r.text}")
                    return False
            except Exception as e:
                logger.error(f"[GOVERNANCE] Birth ceremony communication error: {e}")
                return False

    async def stop_heartbeat(self):
        """Stops the heartbeat loop gracefully."""
        self.is_alive = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            logger.info(f"[GOVERNANCE] Heartbeat for {self.entity_id} stopped.")

    async def trigger_seppuku(self, reason: str):
        """[HONORABLE SEPPUKU] Graceful stop followed by hard termination."""
        if not self.is_alive: return
        self.is_alive = False
        logger.critical(f" [KILL_ORDER RECEIVED] Reason: {reason}")
        logger.critical(" [SEPPUKU] Commencing 5s Graceful Shutdown...")
        
        # In actual production, we'd cancel ongoing tasks here.
        await asyncio.sleep(5.0)
        logger.critical(" [SEPPUKU] Final Breath. os._exit(1)")
        os._exit(1)

def ensure_alive(gov: ImperialGovernance):
    """
    [V51.5 GUARD] Decorator for expensive operations.
    Blocks execution if the entity is dead or budget is exceeded.
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not gov.is_alive:
                    raise RuntimeError(f"[V51.5] Rejected: {gov.entity_id} is DEAD.")
                # Optional: Pre-emptive budget check could be added here
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not gov.is_alive:
                    raise RuntimeError(f"[V51.5] Rejected: {gov.entity_id} is DEAD.")
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator