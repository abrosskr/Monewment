import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

logger = logging.getLogger(__name__)

class LocalRelay:
    """
    Relays data from Local Vendors DB to the core network.
    Used when Supabase only has lightweight indexes.
    """
    def __init__(self):
        # Local DB URL - assuming same host
        self.local_url = "postgresql+asyncpg://forager:forager@localhost:5432/forager"
        self.engine = create_async_engine(self.local_url)

    async def fetch_raw_recipe(self, local_id: str):
        """Fetches raw HTML/content from local raw_archive."""
        try:
            async with self.engine.connect() as conn:
                res = await conn.execute(text("""
                    SELECT url, raw_html_gz, cleaned_text 
                    FROM public.raw_archive 
                    WHERE id = CAST(:l_id AS uuid)
                """), {"l_id": local_id})
                row = res.fetchone()
                if row:
                    return {
                        "url": row[0],
                        "raw_html_gz": row[1],
                        "cleaned_text": row[2],
                        "relay_source": "LOCAL_VENDORS_NODE"
                    }
                return None
        except Exception as e:
            logger.error(f"[LOCAL RELAY] Failed to fetch {local_id}: {e}")
            return None
        finally:
            # We don't dispose the engine here as it's a singleton-like usage.
            pass

# Instance
relay = LocalRelay()
