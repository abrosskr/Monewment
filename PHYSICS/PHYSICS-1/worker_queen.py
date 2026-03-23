import asyncio
from core.queen import QueenGovernor
from domain.physics_monitor import PhysicsMonitor

async def main():
    governor = QueenGovernor()
    monitor = PhysicsMonitor(governor)
    
    try:
        await asyncio.gather(
            governor.execute_strategic_policy(),
            monitor.run()
        )
    except KeyboardInterrupt:
        governor.logger.info("Universal Queen shutting down...")
    except Exception as e:
        governor.logger.critical(f"FATAL: {e}")
        governor.honorable_seppuku("Logic breakdown")

if __name__ == "__main__":
    asyncio.run(main())
