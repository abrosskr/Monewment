from typing import List, Dict, Any
from app.engines.v_academy.core import VAcademyEngine
from app.services.learning.manager import LearningManager

class SmartCrawlerService:
    """
    [Smart Follower]
    Autonomous bot that scans registered channels (Youtube, Recipe Sites)
    for new cooking knowledge 24/7.
    """
    
    WATCH_LIST = [
        {"type": "youtube", "url": "https://www.youtube.com/@GordonRamsay"},
        {"type": "youtube", "url": "https://www.youtube.com/@Maangchi"},
        {"type": "10k_recipes", "url": "latest_beef_stew"}
    ]

    def __init__(self):
        self.academy = VAcademyEngine()
        self.manager = LearningManager(self.academy)

    async def run_cycle(self) -> Dict[str, int]:
        """
        Periodically called to fetch updates.
        """
        new_knowledge_count = 0
        
        for source in self.WATCH_LIST:
            # In real implementations, we would check 'last_updated' timestamps
            # to avoid re-learning old content.
            try:
                result = await self.manager.ingest(source["type"], source["url"])
                new_knowledge_count += result.get("absorbed_technique_count", 0)
            except Exception as e:
                print(f"Error crawling {source['url']}: {e}")
                
        return {"new_primitives": new_knowledge_count, "status": "Idle"}
