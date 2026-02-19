import abc
import random
import time
import httpx
import logging
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import aiofiles

class BaseCrawler(abc.ABC):
    """
    [The Foundation - OMNI-CRAWLER Edition]
    Abstract Base Class for all scrapers.
    - Zero DB Dependency
    - Async Compatible (using HTTPX)
    - Local Buffer Persistence (via aiofiles)
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]

    def __init__(self, buffer_dir: Optional[Path] = None):
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
        self.buffer_dir = buffer_dir or Path("./data/buffer")
        self.buffer_dir.mkdir(parents=True, exist_ok=True)
        self._request_count = 0

    @abc.abstractmethod
    async def fetch_list(self, page: int) -> List[str]:
        """Extract URLs from a list page"""
        pass

    @abc.abstractmethod
    async def parse_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from detail page"""
        pass

    def _get_headers(self) -> Dict[str, str]:
        """Randomize Headers"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive"
        }

    async def _safe_request(self, url: str) -> Optional[httpx.Response]:
        """
        Common Request Logic with Retry & Backoff (Async/Non-blocking)
        """
        retries = 3
        for attempt in range(retries):
            try:
                # Polite Delay (Non-blocking)
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                response = await self.client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    return response
                elif response.status_code in [429, 503]:
                    wait = (attempt + 1) * 5
                    logger.warning(f"Rate Limited ({response.status_code}). Waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    logger.warning(f"Failed {url} with status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Request Error {url}: {e}")
                
        return None

    async def save_to_buffer(self, items: List[Dict], task_id: str):
        """
        [The Buffer]
        Persists data to Local JSON files instead of DB.
        Uses aiofiles for zero-blocking on high-load I/O.
        """
        if not items: return

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"harvest_{timestamp}_{task_id}.json"
        save_path = self.buffer_dir / filename
        
        try:
            async with aiofiles.open(save_path, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps({
                    "task_id": task_id,
                    "timestamp": timestamp,
                    "count": len(items),
                    "items": items
                }, ensure_ascii=False, indent=4))
            logger.info(f"💾 BUFFER SAVED (Async): {save_path} ({len(items)} items)")
        except Exception as e:
            logger.error(f"Failed to save buffer: {e}")

    async def run(self, task_id: str, count: int = 10, start_page: int = 1):
        """
        [The Flywheel]
        Executes the fetch-parse-save cycle asynchronously.
        """
        logger.info(f"🚀 Starting OMNI-CRAWLER Task {task_id} (Target: {count})")
        
        collected = 0
        page = start_page
        
        try:
            while collected < count:
                urls = await self.fetch_list(page)
                if not urls:
                    logger.warning("No more URLs found.")
                    break
                    
                batch_items = []
                for url in urls:
                    if collected >= count: break
                    
                    try:
                        data = await self.parse_detail(url)
                        if data:
                            data["task_id"] = task_id
                            data["collected_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                            batch_items.append(data)
                            collected += 1
                    except Exception as e:
                        logger.error(f"Failed to parse {url}: {e}")
                
                # Save Batch to Buffer
                if batch_items:
                    self.save_to_buffer(batch_items, task_id)
                
                page += 1
        finally:
            await self.client.aclose()
            
        logger.info(f"🏁 Task {task_id} Complete. Collected {collected} items.")

import asyncio # Needed for run logic
