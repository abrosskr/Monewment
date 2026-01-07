import asyncio
import websockets
import json
import logging
from typing import Optional, Callable, Dict, Any, Awaitable
from src.core.ant_security import AntSecurity
from src.core.protocol import JobRequest, JobResult

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, server_url: str, client_id: str, security: AntSecurity):
        self.server_url = f"{server_url}/ws/ant/{client_id}"
        self.client_id = client_id
        self.security = security
        self.connection: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.should_reconnect = True
        self.executor = None # Set later
        
    def set_executor(self, executor):
        self.executor = executor
        
    async def connect(self):
        """Persistent connection loop with exponential backoff."""
        retry_delay = 1
        while self.should_reconnect:
            try:
                logger.info(f"Connecting to Queen Server: {self.server_url}")
                async with websockets.connect(self.server_url) as websocket:
                    self.connection = websocket
                    self.is_connected = True
                    logger.info("✅ Connected to Queen Server.")
                    retry_delay = 1 # Reset retry delay on success
                    
                    # Connection Loop
                    await self._listen()
                    
            except (ConnectionRefusedError, websockets.exceptions.ConnectionClosed):
                self.is_connected = False
                logger.warning(f"Connection lost. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60) # Max 60s backoff
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                await asyncio.sleep(5)

    async def _listen(self):
        """Listen for incoming messages (Jobs, Ack)."""
        try:
            async for message in self.connection:
                # Decrypt if needed (Assuming server replies in plain JSON for now, or encrypted)
                # For this stage, we assume server sends plain commands, client sends encrypted heartbeats
                # To be strict, we should decrypt incoming too if server encrypts.
                logger.debug(f"Received: {message}")
                
                try:
                    data = json.loads(message)
                    if data.get("type") == "job_request" and self.executor:
                        # Handle Job
                        req_data = data.get("data")
                        job_req = JobRequest(**req_data)
                        
                        # Execute in background (or await if blocking is okay for now)
                        # For simple architecture, we await. Ideally execute_job shouldn't block heartbeat.
                        # Since executor.execute_job is async, it yields.
                        asyncio.create_task(self._process_job(job_req))
                        
                except json.JSONDecodeError:
                    pass
                    
                # Relay Handling
                # We assume message is JSON. If it was decrypted above, 'data' is the dict.
                if isinstance(data, dict) and data.get("type") == "RELAY":
                    # { "type": "RELAY", "sender_id": "...", "payload": "..." }
                    sender_id = data.get("sender_id")
                    payload = data.get("payload")
                    if self.p2p_callback:
                         asyncio.create_task(self.p2p_callback(sender_id, payload))
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed.")
            raise

    async def _process_job(self, job: JobRequest):
        if not self.executor: return
        try:
            result = await self.executor.execute_job(job)
            await self._send_job_result(result)
        except Exception as e:
            logger.error(f"Job Execution Failed: {e}")
            
    async def _send_job_result(self, result: JobResult):
        if not self.is_connected: return
        payload = {
            "type": "job_result",
            "data": result.dict()
        }
        await self.connection.send(json.dumps(payload, default=str))

    async def send_heartbeat(self, status: str, active_job_id: Optional[str] = None):
        """Sends an encrypted heartbeat payload."""
        if not self.is_connected or not self.connection:
            return

        payload = {
            "type": "heartbeat",
            "client_id": self.client_id,
            "status": status, # ONLINE, WORKING, ERROR
            "active_job_id": active_job_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Encrypt payload
        try:
            encrypted_token = self.security.encrypt_payload(payload)
            await self.connection.send(encrypted_token)
            logger.debug("Heartbeat sent.")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    async def send_relay_packet(self, target_id: str, payload: str):
        """Sends a P2P packet via Queen Relay (Fallback)."""
        if not self.is_connected: return False
        
        msg = {
            "type": "RELAY",
            "target_id": target_id,
            "payload": payload
        }
        try:
            # We can encrypt this outer envelope or trust TLS. 
            # For Phase 13, check if we need e2e encryption of the inner payload (P2P encrypts it?)
            # Assuming P2P payload is opaque bytes (base64 encoded string).
            await self.connection.send(json.dumps(msg))
            return True
        except Exception as e:
            logger.error(f"Relay Send Error: {e}")
            return False

    async def close(self):
        self.should_reconnect = False
        if self.connection:
            await self.connection.close()

    # Callback for P2P Engine
    p2p_callback: Optional[Callable[[str, Any], Awaitable[None]]] = None
    
    def set_p2p_callback(self, callback):
        self.p2p_callback = callback

