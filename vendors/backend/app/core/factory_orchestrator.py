import logging
import json
from typing import List, Dict
from app.database import SessionLocal
from app.models.assets import SourceIngestion, BehaviorAsset
from app.scrapers.youtube_scraper import YouTubeScraper
from app.services.metrics_engine import MetricsEngine
from app.services.clustering_engine import ClusteringEngine
from app.services.decomposer import Decomposer

logger = logging.getLogger(__name__)

class FactoryOrchestrator:
    """
    [The Global Food Data Factory]
    High-fidelity ingestion pipeline unifying social signals and recipe atoms.
    """

    def __init__(self):
        self.yt_scraper = YouTubeScraper()
        self.cluster_engine = ClusteringEngine()
        self.db = SessionLocal()

    def produce_from_channels(self, channel_ids: List[str]):
        """
        Main production loop for the Factory.
        """
        print(f"🏭 Starting Food Data Factory Production (Channels: {len(channel_ids)})")
        
        for cid in channel_ids:
            # 1. Sequential Channel Learning
            video_payloads = self.yt_scraper.learn_channel(cid)
            
            for payload in video_payloads:
                # 2. Semantic Clustering (Step 3: Finding Archetypes)
                embedding = self.cluster_engine.get_embedding(payload['name'])
                menu_type = self.cluster_engine.identify_menu_cluster(payload['name'])
                
                # Mock Cluster Center for rank calculation
                mock_center = self.cluster_engine.get_embedding(menu_type)
                cf_score = self.cluster_engine.find_cluster_rank(embedding, mock_center)
                
                # 3. Calculate MS Score (Step 4: Valuation)
                engagement = payload['engagement']
                engagement['cf'] = cf_score
                engagement['rr'] = 0.8 # Placeholder for reproducibility
                
                # 4. Step 1: Ingestion Sealing (Idempotency Check)
                exists = self.db.query(SourceIngestion).filter(SourceIngestion.url == payload['url']).first()
                if exists:
                    print(f"   ⏩ [Skip] Already Ingested: {payload['name']}")
                    continue

                source = SourceIngestion(
                    url=payload['url'],
                    raw_data={
                        "name": payload['name'],
                        "url": payload['url'],
                        "ingredients": payload['recipe']['ingredients'],
                        "steps": payload['recipe']['steps'],
                        "engagement": engagement # Attached for Decomposer
                    }
                )
                self.db.add(source)
                self.db.commit()
                
                print(f"   📦 Industry Asset Ingested: {payload['name']} (MS: {engagement.get('ms', 'TBD')})")
                
                # 5. Step 2 & 4: Atomic Decomposition
                Decomposer.process_source(source.id)

        self.db.close()
        print("✅ Factory Production Run Complete.")

if __name__ == "__main__":
    factory = FactoryOrchestrator()
    factory.produce_from_channels(["CH_PAIK_COOK", "CH_GORDON_RAMSAY"])
