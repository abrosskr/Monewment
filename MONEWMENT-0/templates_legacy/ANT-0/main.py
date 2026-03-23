import asyncio
import httpx
import logging
from core.ant_governance import AntLifeCycle, ensure_alive

# Configure logging to see the governance in action
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("origin_ant")

# 1. Initialize the ANT Lifecycle manager
ant = AntLifeCycle(
    ant_id="ORIGIN-ARTIST-01",
    stratum_id="badd8a15-5e63-4d24-81fd-489e8973cb85", # Default dev stratum
    api_url="http://127.0.0.1:8800/v1"
)

# 2. Define a protected AI Task using the decorator
@ensure_alive(ant)
async def generate_expensive_art():
    """Simulates a high-cost GPU/API operation."""
    # Increment cost before the operation
    ant.accumulated_cost += 0.75 
    logger.info(f"Generating Imperial Art... [Accumulated Cost: ${ant.accumulated_cost:.2f}]")
    
    # Simulate work
    await asyncio.sleep(2)
    logger.info("Art generation complete.")

async def main():
    logger.info("Imperial ANT Origin Template Booting...")
    
    async with httpx.AsyncClient() as client:
        while ant.is_alive:
            try:
                # First, check pulse (Governance/Heartbeat)
                await ant.pulse(client)
                
                # Execute protected task
                # If accumulated_cost hits the limit ($5.00), pulse will set is_alive=False
                # and ensure_alive will prevent the next execution.
                await generate_expensive_art()
                
                await asyncio.sleep(1)
            except RuntimeError as e:
                logger.warning(f"Control Panel: {e}")
                break
            except Exception as e:
                logger.error(f"External Error: {e}")
                await asyncio.sleep(5)

    logger.info("System Halted. Final status: DEAD.")

if __name__ == "__main__":
    asyncio.run(main())
