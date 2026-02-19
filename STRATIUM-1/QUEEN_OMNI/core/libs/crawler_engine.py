import httpx
import asyncio
import json
import logging
import random
import time
from typing import List, Dict, Optional, Any
from pathlib import Path
import aiofiles

logger = logging.getLogger("CrawlerEngine")

class CrawlerEngine:
    """
    [The Shared Heart]
    Common scraping logic shared via EDENVALE/core/libs/
    """
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def fetch_html(self, url: str) -> Optional[str]:
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # Polite Delay (Non-blocking)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            logger.error(f"Fetch Error {url}: {e}")
        return None

    @staticmethod
    async def persist_json(path: Path, data: Dict[str, Any]):
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info(f"💾 Persistent: {path.name}")
