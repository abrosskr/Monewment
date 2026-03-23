"""
core/scheduler.py — Background GC Scheduler (API Contract v2.0)
Handles:
  - DORMANT decay: last_seen_at + 120s → DORMANT, +300s → DEAD
  - Max Lifetime: born_at + 72h → DEAD
  - DB Purge: DEAD + 30 days → DELETE (incl. idempotency_keys cleanup)
"""
import asyncio
from sqlalchemy import text
from .database import engine
from .logger import logger

_ENTITY_TABLES = [
    ("schema_registry.monewments", "monewment_id"),
    ("schema_registry.stratums",   "stratum_id"),
    ("schema_registry.queens",     "queen_id"),
    ("schema_registry.ants",       "ant_id"),
]


async def _run_dormant_decay() -> None:
    """[V49 TEMPORARY DISABLE] ACTIVE → DORMANT (120s), DORMANT → DEAD (300s additional)"""
    # logger.info("[GC] Dormant decay temporarily disabled for Ecosystem Health Check.")
    return
    
    async with engine.begin() as conn:
        for table, _ in _ENTITY_TABLES:
            # ACTIVE → DORMANT after 120s without ping
            r1 = await conn.execute(text(f"""
                UPDATE {table}
                SET status = 'DORMANT'
                WHERE status = 'ACTIVE'
                  AND last_seen_at < NOW() - INTERVAL '120 seconds'
                RETURNING 1
            """))
            dormant_count = r1.rowcount

            # DORMANT → DEAD after 300s additional
            r2 = await conn.execute(text(f"""
                UPDATE {table}
                SET status = 'DEAD', died_at = NOW(), death_reason = 'TIMEOUT'
                WHERE status = 'DORMANT'
                  AND last_seen_at < NOW() - INTERVAL '420 seconds'
                RETURNING 1
            """))
            dead_count = r2.rowcount

            if dormant_count or dead_count:
                logger.info(f"[GC] {table}: {dormant_count} DORMANT, {dead_count} auto-DEAD (timeout)")


async def _run_max_lifetime() -> None:
    """born_at + 72h → DEAD regardless of ping (Max Lifetime rule)"""
    async with engine.begin() as conn:
        for table, id_col in _ENTITY_TABLES:
            # [V51.5] Imperial Core Identity Protection
            # MONEWMENT-PRIMARY (ID: ...001) and any entity matching the core IDs are exempt.
            r = await conn.execute(text(f"""
                UPDATE {table}
                SET status = 'DEAD', died_at = NOW(), death_reason = 'MAX_LIFETIME'
                WHERE status IN ('ACTIVE', 'DORMANT')
                  AND born_at < NOW() - INTERVAL '72 hours'
                  AND {id_col} NOT IN (
                      '00000000-0000-0000-0000-000000000001', -- MONEWMENT-PRIMARY
                      'd8a9e0a0-0000-0000-0000-000000000000', -- IMPERIAL_CORE
                      'e5388cf9-4ce2-400e-8de1-f9e2a5bb18bd'  -- QUEEN-SFIS (Forager Commando)
                  )
                RETURNING 1
            """))
            if r.rowcount:
                logger.info(f"[GC] {table}: {r.rowcount} expired by max lifetime (72h)")


async def _run_inactivity_reaper() -> None:
    """[DECREE 12.1] last_seen_at + 72h -> DEAD (Inactivity Reaper)"""
    async with engine.begin() as conn:
        for table, id_col in _ENTITY_TABLES:
            if table not in ["schema_registry.queens", "schema_registry.ants"]:
                continue
                
            r = await conn.execute(text(f"""
                UPDATE {table}
                SET status = 'DEAD', died_at = NOW(), death_reason = 'INACTIVITY_TIMEOUT_72H'
                WHERE status NOT IN ('DEAD', 'BANNED')
                  AND last_seen_at < NOW() - INTERVAL '72 hours'
                  AND {id_col} NOT IN (
                      '00000000-0000-0000-0000-000000000001',
                      'd8a9e0a0-0000-0000-0000-000000000000',
                      'e5388cf9-4ce2-400e-8de1-f9e2a5bb18bd'
                  )
                RETURNING 1
            """))
            if r.rowcount:
                logger.info(f"[GC] {table}: {r.rowcount} reaped due to 72h inactivity")


async def _run_db_purge() -> None:
    """DEAD + 30 days → hard DELETE"""
    async with engine.begin() as conn:
        for table, _ in _ENTITY_TABLES:
            r = await conn.execute(text(f"""
                DELETE FROM {table}
                WHERE status = 'DEAD'
                  AND died_at < NOW() - INTERVAL '30 days'
                RETURNING 1
            """))
            if r.rowcount:
                logger.info(f"[GC] {table}: {r.rowcount} records purged (DEAD > 30 days)")

        # Idempotency-Key 72h 만료 정리
        r2 = await conn.execute(text("""
            DELETE FROM schema_registry.idempotency_keys
            WHERE created_at < NOW() - INTERVAL '72 hours'
            RETURNING 1
        """))
        if r2.rowcount:
            logger.info(f"[GC] idempotency_keys: {r2.rowcount} expired keys purged")


async def _run_bloodstream_purification() -> None:
    """
    [DECREE 12.1] Centralized Bloodstream Purification.
    Scans all stratums and purges raw_data/storage_path for AREUM_DONE assets.
    """
    async with engine.begin() as conn:
        # 1. Get all active stratums
        result = await conn.execute(text("SELECT stratum_name FROM schema_registry.stratums WHERE status = 'ACTIVE'"))
        stratums = [r[0] for r in result.fetchall()]

    for s_name in stratums:
        schema = f"schema_stratum_{s_name}"
        try:
            async with engine.begin() as conn:
                # Purge raw_data where areum_processed_at is older than 48 hours
                # We set raw_data to NULL to keep the metadata but free the space.
                # Storage deletion would require storage client integration in scheduler too.
                # For now, we focus on DB space (Schema Expansion Prevention).
                purge_query = text(f"""
                    UPDATE {schema}.assets
                    SET raw_data = NULL
                    WHERE (raw_data IS NOT NULL OR storage_path IS NOT NULL)
                      AND areum_processed_at < NOW() - INTERVAL '48 hours'
                    RETURNING 1
                """)
                r = await conn.execute(purge_query)
                if r.rowcount:
                    logger.info(f"[GC] {schema}: {r.rowcount} assets purified (raw_data cleared)")
        except Exception as e:
            # Schema might not exist yet or table structure different
            logger.debug(f"[GC] Bloodstream purification skipped for {schema}: {e}")


async def _dispatch_pipeline_workers() -> None:
    """
    [PHASE 8] Imperial Asset Dispatcher.
    Monitors the data bloodstream and triggers/logs the need for processing.
    """
    try:
        async with engine.begin() as conn:
            # 1. Check for Pending Assets (AREUM trigger)
            result = await conn.execute(text("SELECT stratum_name FROM schema_registry.stratums WHERE status = 'ACTIVE'"))
            stratums = [r[0] for r in result.fetchall()]
            
            total_pending = 0
            for s_name in stratums:
                schema = f"schema_stratum_{s_name}"
                try:
                    count_r = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.assets WHERE ai_summary IS NULL"))
                    p_count = count_r.scalar() or 0
                    if p_count > 0:
                        logger.info(f"[DISPATCH] {schema}: {p_count} assets pending for AREUM-IN.")
                        total_pending += p_count
                except Exception:
                    continue

            # 2. Check for Unconsumed Reports (PHYSICS trigger)
            rex_r = await conn.execute(text("""
                SELECT COUNT(*) FROM schema_pipeline.cross_reports 
                WHERE rex_consumed = FALSE AND rex_processing = FALSE
            """))
            unconsumed = rex_r.scalar() or 0
            if unconsumed > 0:
                logger.info(f"[DISPATCH] {unconsumed} cross-reports pending for PHYSICS/REX.")

    except Exception as e:
        logger.error(f"[DISPATCH] pipeline_dispatcher error: {e}")


async def run_gc_loop() -> None:
    """
    백그라운드 GC 루프.
    main.py lifespan 에서 asyncio.create_task(run_gc_loop()) 으로 시작.
    """
    logger.info("[GC] Scheduler started.")
    while True:
        try:
            await _run_dormant_decay()
        except Exception as e:
            logger.error(f"[GC] dormant_decay error: {e}")
        try:
            await _run_max_lifetime()
        except Exception as e:
            logger.error(f"[GC] max_lifetime error: {e}")
            
        try:
            await _run_inactivity_reaper()
        except Exception as e:
            logger.error(f"[GC] inactivity_reaper error: {e}")

        # Purge는 더 드물게: 1시간마다
        for _ in range(120):          # 120 * 30s = 3600s = 1h
            await asyncio.sleep(30)
            try:
                await _run_dormant_decay()
            except Exception as e:
                logger.error(f"[GC] dormant_decay error: {e}")

        try:
            await _run_db_purge()
        except Exception as e:
            logger.error(f"[GC] db_purge error: {e}")

        try:
            await _run_bloodstream_purification()
        except Exception as e:
            logger.error(f"[GC] bloodstream_purification error: {e}")

        try:
            await _dispatch_pipeline_workers()
        except Exception as e:
            logger.error(f"[GC] pipeline_dispatcher error: {e}")
