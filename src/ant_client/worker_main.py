import asyncio
import logging
import os
import signal
import sys
from src.core.ant_security import AntSecurity
from src.ant_client.core.connection import ConnectionManager
from src.ant_client.core.executor import JobExecutor

# Configure Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s [ANT] %(message)s')
logger = logging.getLogger("AntWorker")

async def main():
    logger.info("🐜 Ant Client Worker Started.")
    
    # Configuration (In real app, load from config/env)
    server_url = os.getenv("QUEEN_SERVER_URL", "ws://localhost:8000")
    client_id = os.getenv("ANT_CLIENT_ID", "ant-001")
    
    # Security Init
    security = AntSecurity(key_bytes=b'0'*32) # Placeholder Key
    
    # Connection Manager
    conn = ConnectionManager(server_url, client_id, security)
    executor = JobExecutor(client_id)
    conn.set_executor(executor)
    
    # Start Connection in background
    conn_task = asyncio.create_task(conn.connect())
    
    # Message Handler (Simulated for this phase as websocket recv loop is in connection.py)
    # Ideally ConnectionManager should have a callback/queue for messages.
    # For now, let's just keep heartbeat.
    # TODO: Implement message receiving call back in Connection Manager
    
    # Heartbeat Loop
    try:
        while True:
            await asyncio.sleep(5)
            if conn.is_connected:
                # In real impl, status would change if processing
                await conn.send_heartbeat(status="ONLINE")
    except asyncio.CancelledError:
        logger.info("Worker stopping...")
        await conn.close()
        conn_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
