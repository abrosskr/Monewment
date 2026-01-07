import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from src.core.redis_client import RedisManager
from src.core.protocol import JobRequest, JobType
from src.core.billing.profit_engine import HARDWARE_SPECS, GpuType

logger = logging.getLogger("DeepSyncScheduler")

class AntNodeInfo:
    def __init__(self, client_id: str, gpu_model: str, status: str, last_seen: datetime):
        self.client_id = client_id
        self.gpu_model = gpu_model
        self.status = status
        self.last_seen = last_seen
        
    @property
    def is_online(self) -> bool:
        # Consider offline if no heartbeat for 60 seconds
        return self.status == "ONLINE" and (datetime.utcnow() - self.last_seen) < timedelta(seconds=60)

class Scheduler:
    def __init__(self):
        pass

    async def _get_online_ants(self) -> List[AntNodeInfo]:
        """It scans Redis for available ants."""
        redis = RedisManager.get_instance().get_client()
        if not redis:
            return []
            
        # keys: ant:heartbeat:{client_id} -> timestamp (ISO)
        # We need a separate key for static info (specs) ideally.
        # For this prototype, we assume specs are stored in `ant:info:{client_id}` or similar.
        # Let's assume we store "status|gpu_model" in `ant:status:{client_id}` for simplicity in this phase.
        
        # Real-world: Use a Hash for each ant `ant:{client_id}` with fields `last_seen`, `gpu`, `status`.
        
        keys = await redis.keys("ant:info:*") # e.g. ant:info:client-123
        online_ants = []
        
        for key in keys:
            # Value JSON: {"status": "ONLINE", "gpu": "RTX_4090", "last_seen": "..."}
            data_raw = await redis.get(key)
            if data_raw:
                try:
                    data = json.loads(data_raw)
                    client_id = key.split(":")[-1]
                    
                    last_seen_str = data.get("last_seen")
                    last_seen = datetime.fromisoformat(last_seen_str) if last_seen_str else datetime.min
                    
                    ant = AntNodeInfo(
                        client_id=client_id,
                        gpu_model=data.get("gpu", "Unknown"),
                        status=data.get("status", "OFFLINE"),
                        last_seen=last_seen
                    )
                    
                    if ant.is_online:
                        online_ants.append(ant)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse ant info for {key}: {e}")
                    
        return online_ants

    async def schedule_job(self, job: JobRequest) -> Optional[str]:
        """
        Selects the best 'ONLINE' Ant Client for the job.
        Returns worker_id (client_id) or None if no suitable worker found.
        
        Strategy:
        1. Filter by Requirements (e.g. Min VRAM)
        2. Sort by 'Speed' (TFLOPS from HardwareSpecs) desc.
        """
        candidates = await self._get_online_ants()
        logger.info(f"Scheduling Job {job.job_id}: Found {len(candidates)} online ants.")
        
        valid_candidates = []
        required_vram = job.requirements.get("min_vram", 0)
        
        for ant in candidates:
            # 1. Check Specs
            # Convert string spec to Enum if possible
            try:
                # Ensure we match the Enum type used in HARDWARE_SPECS keys
                # We iterate to find matching string if direct lookup fails or use GpuType(ant.gpu_model)
                # Since GpuType is string enum, direct lookup might work, but robust way is:
                spec = HARDWARE_SPECS.get(ant.gpu_model)
                # If lookup by string fails but it's a valid enum name:
                if not spec:
                     spec = HARDWARE_SPECS.get(GpuType(ant.gpu_model))
            except ValueError:
                 logger.debug(f"Skipping {ant.client_id}: Unknown GPU Type {ant.gpu_model}")
                 continue
                 
            if not spec:
                logger.debug(f"Skipping {ant.client_id}: Unknown GPU Spec {ant.gpu_model}")
                continue
                
            if spec.vram_gb < required_vram:
                logger.debug(f"Skipping {ant.client_id}: Insufficient VRAM ({spec.vram_gb} < {required_vram})")
                continue
                
            valid_candidates.append((ant, spec))
            
        if not valid_candidates:
            logger.warning("No suitable candidates found.")
            return None
            
        # 2. Sort by Profitability (Commercial Grade)
        # Use ProfitEngine to calculate potential revenue/profit for this job duration (normalized to daily)
        # For scheduling locally, we can use "Revenue per hour" metric from ProfitEngine.
        # Higher profit/revenue potential = Better rank (if we want to maximize platform fee)
        # OR: Higher TFLOPS = Faster job = Happy User.
        
        # Let's verify requirement: "Profit Engine ... output Pydantic Model ... structure for Frontend"
        # The prompt implies Profit Engine is for "Settlement" and "Estimation".
        # For Scheduling, maximizing TFLOPS per Dollar is usually the goal for users.
        # But for the "Platform", maximizing "Utilization of best hardware" is key.
        # Let's combine: Sort by (TFLOPS * Profit_Metric).
        
        # Import inside method to avoid circular import if necessary, or at top if safe.
        from src.core.billing.profit_engine import ProfitEngine, ProfitCalculationRequest, GpuType
        
        scored_candidates = []
        for ant, spec in valid_candidates:
             # Calculate generic profit projection for this hardware
             # we need to cast the string model to Enum
             try:
                 g_type = GpuType(ant.gpu_model)
             except ValueError:
                 # Fallback or skip
                 g_type = GpuType.RTX_3060 # Default baseline
                 
             req = ProfitCalculationRequest(
                 gpu_type=g_type, 
                 electricity_cost_per_kwh=0.12, # Generic global avg
                 active_hours_per_day=24,
                 deep_sync_utilization=1.0, # Assuming this job is DeepSync
                 deep_render_utilization=0.0
             )
             
             try:
                 # Calculate Profit
                 profit_res = ProfitEngine.calculate_profit(req)
                 daily_profit = profit_res.daily_profit
             except Exception:
                 daily_profit = 0
             
             # Score = TFLOPS (Performance) + Normalization of Profit
             # We want high performance, but also want to prioritize nodes that are 'profitable' (efficient)
             score = spec.tflops + (float(daily_profit) * 0.1)
             scored_candidates.append((ant, score))
             
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        best_ant = scored_candidates[0][0]
        logger.info(f"Selected Best Ant: {best_ant.client_id} (Score: {scored_candidates[0][1]:.2f})")
        
        return best_ant.client_id
