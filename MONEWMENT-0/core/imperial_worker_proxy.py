import asyncio
import random
import logging
import os
import sys
import argparse
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.database import AsyncSessionLocal
from core.config import settings
from core.logger import logger

STRATUM_ID = "badd8a15-5e63-4d24-81fd-489e8973cb85"

async def register_self(ant_id: str, ant_class: str, status: str = "ACTIVE"):
    """Register the ANT in the imperial registry (database)."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("""
                INSERT INTO schema_registry.ants (ant_name, ant_type, status, stratum_id)
                VALUES (:name, :type, :status, :sid)
                ON CONFLICT (stratum_id, ant_name) DO UPDATE SET 
                    status = EXCLUDED.status, 
                    ant_type = EXCLUDED.ant_type
            """), {"name": ant_id, "type": ant_class, "status": status, "sid": STRATUM_ID})
            await session.commit()
            logger.info(f"[REGISTRY] {ant_id} registered as {status}")
    except Exception as e:
        logger.error(f"[REGISTRY] Failed to register {ant_id}: {e}")

async def run_worker(ant_class: str, ant_id: str):
    logger.info(f"[PERSONA] Loading persona for {ant_id} ({ant_class})...")
    
    # Self-registration
    await register_self(ant_id, ant_class, "ACTIVE")
    
    # Persona Mapping
    personas = {
        "GUARD": "The Sentinel - Integrity.",
        "CHRONOS": "The Archivist - Order, Patience.",
        "CCTV": "The Observer - Neutrality, Fact-only.",
        "MAP": "The Pathfinder - Exploration.",
        "ORCHESTRA": "The Conductor - Balance, Efficiency."
    }
    
    persona = personas.get(ant_class, "The Serf")
    logger.info(f"[VOW] {ant_id} is bound by: {persona}")
    
    # Task Loop Simulation
    task_count = 0
    while task_count < 10:
        logger.info(f"[{ant_id}] Performing task {task_count+1}/10...")
        await asyncio.sleep(random.uniform(2, 5)) # Simulate work
        task_count += 1
        
    logger.info(f"[{ant_id}] Task quota reached. Requesting self-termination.")
    await register_self(ant_id, ant_class, "DORMANT")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--class", dest="ant_class", required=True)
    parser.add_argument("--id", dest="ant_id", required=True)
    args = parser.parse_args()
    
    asyncio.run(run_worker(args.ant_class, args.ant_id))
