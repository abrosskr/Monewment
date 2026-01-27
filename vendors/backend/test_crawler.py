import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.learning.crawler import SmartCrawlerService
from app.services.dataset_manager import DatasetManager

async def test_smart_pipeline():
    print("\n🕸️ Testing Smart Follower: Auto-Crawling and Dataset Reservoir")
    print("-" * 80)

    # 1. Initialize Bot
    crawler = SmartCrawlerService()
    
    # 2. Run a cycle
    print("   Action: Crawler checking watch-list...")
    report = await crawler.run_cycle()
    
    print(f"   [Report] New Primitives Absorbed: {report['new_primitives']}")
    
    # 3. Verify Persistence
    stats = DatasetManager.get_stats()
    print(f"   [Database] Total Labeled Entries: {stats['total_entries']}")
    
    assert report['new_primitives'] > 0
    assert stats['total_entries'] > 0
    
    print("\n   ✅ SUCCESS: VANDORS is now autonomously learning and building its own library.")

if __name__ == "__main__":
    asyncio.run(test_smart_pipeline())
