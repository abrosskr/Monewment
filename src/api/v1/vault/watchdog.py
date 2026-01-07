from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import VaultFile, VaultShard
from src.core.redis_client import RedisManager
from src.core.socket_manager import SocketManager
import json
import asyncio
import structlog

logger = structlog.get_logger()

class VaultWatchdog:
    # N=10, M=4. Total 14.
    # We warn if < 12.
    SAFE_THRESHOLD = 12
    RECOVERY_MINIMUM = 10
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = RedisManager.get_instance().get_client()
        self.socket_mgr = SocketManager.get_instance()

    async def scan_and_repair(self):
        """
        Scans all files and checks shard availability.
        Triggers repair if needed.
        """
        logger.info("🔎 Watchdog Scan Started...")
        
        # 1. Get Online Ants
        if not self.redis:
            logger.error("Redis not connected")
            return
            
        keys = await self.redis.keys("ant:heartbeat:*")
        online_ants = {k.decode().split(":")[-1] for k in keys}
        logger.info(f"Active Ants: {len(online_ants)}")
        
        # 2. Scan Files
        # For MVP, scan all. In Prod, paginated.
        result = await self.db.execute(select(VaultFile).where(VaultFile.status == "AVAILABLE"))
        files = result.scalars().all()
        
        repair_count = 0
        
        for f in files:
            needed_repair = await self.check_file(f, online_ants)
            if needed_repair:
                repair_count += 1
                
        logger.info(f"Scan Complete. Triggered Repair for {repair_count} files.")
        return {"scanned": len(files), "repaired": repair_count}

    async def check_file(self, f: VaultFile, online_ants: set) -> bool:
        # Get Shards
        result = await self.db.execute(select(VaultShard).where(VaultShard.file_id == f.id))
        shards = result.scalars().all()
        
        # Count available shards (unique indices)
        # We need N unique shards to recover.
        # Actually we need 10 unique INDICES.
        # DeepVault sharding: shards 0..13.
        
        available_indices = set()
        
        for s in shards:
            stored_at = json.loads(s.stored_at) # List of ant_ids
            # If ANY of the hosts is online, this index is available
            is_avail = False
            for ant_id in stored_at:
                if ant_id in online_ants:
                    is_avail = True
                    break
            
            if is_avail:
                available_indices.add(s.shard_index)
                
        count = len(available_indices)
        
        if count < self.RECOVERY_MINIMUM:
             logger.critical("DATA_LOSS_IMMINENT", file_id=f.id, available=count, status="UNRECOVERABLE_MAYBE")
             # Should we try to salvage what we can?
             return False
             
        elif count < self.SAFE_THRESHOLD:
            logger.warning("REPAIR_NEEDED", file_id=f.id, available=count, threshold=self.SAFE_THRESHOLD)
            await self.trigger_repair(f, online_ants)
            return True
            
        return False

    async def trigger_repair(self, f: VaultFile, online_ants: set):
        # Pick a repair node
        # Must be online AND have a websocket connection
        repair_node = None
        
        # Simple Logic: First connected node
        for ant in online_ants:
            if self.socket_mgr.get_connection(ant):
                repair_node = ant
                break
                
        if not repair_node:
            logger.error("NO_REPAIR_NODE_AVAILABLE", file_id=f.id)
            return

        payload = {
            "type": "repair_job",
            "file_id": f.id,
            "filename": f.filename,
            "key_hex": f.encryption_key
        }
        
        sent = await self.socket_mgr.send_message(repair_node, json.dumps(payload))
        if sent:
            logger.info("REPAIR_DISPATCHED", file_id=f.id, worker=repair_node)
        else:
            logger.error("REPAIR_DISPATCH_FAILED", file_id=f.id, worker=repair_node)
