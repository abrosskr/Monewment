import sys
import os
import asyncio
import time
import random

# Setup Path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.services.etl_service import EtlPipeline
from app.services.youtube_discovery import YouTubeDiscoveryService
from app.services.learning_service import LearningService
from app.services.ontology_learner import OntologyLearner
from app.services.vocabulary_builder import VocabularyBuilder
from app.engines.v_academy.core import VAcademyEngine

# Import legacy scraper from root
try:
    from collect_mass_data import collect_mass_data, load_scraper_state, save_scraper_state
except ImportError:
    # Fallback if not found (or if running from backend dir)
    print("⚠️ Warning: 'collect_mass_data.py' not found in path.")
    def collect_mass_data(count, start_page=1): 
        print(f"   [Mock] Scraping {count} recipes (File missing)")
        return start_page + 1
    def load_scraper_state(): return {"last_page": 1}
    def save_scraper_state(state): pass

async def run_daily_jobs():
    print("\n🌅 [VendorOS] Starting Daily Brain Expansion Routine")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. ETL Pipeline (Product Data)
        print("\n1️⃣  [Data] Running ETL Pipeline...")
        etl = EtlPipeline(db)
        etl.run()
        
        # 2. Recipe Crawler (10000 Recipes)
        print("\n2️⃣  [Crawler] Harvesting valid recipes from Web...")
        state = load_scraper_state()
        start_page = state.get("last_page", 1)
        print(f"   📍 Resuming from Page: {start_page}")
        
        # Scrape 100 new items per run as requested
        next_page = collect_mass_data(count=100, start_page=start_page)
        
        # Save new state
        state["last_page"] = next_page
        save_scraper_state(state)

        # 3. YouTube Discovery & Learning
        print("\n3️⃣  [Learning] Discovering new cooking videos...")
        discovery = YouTubeDiscoveryService()
        urls = discovery.discover_videos(count=3) # Target 3 videos per run
        
        if urls:
            academy = VAcademyEngine()
            learner = LearningService(academy, db_session=db)
            
            learning_summary = []
            
            for i, url in enumerate(urls):
                # Rate Limit Protection: Sleep 20-30s between videos for maximum stealth
                if i > 0:
                    wait_time = random.uniform(20, 30)
                    print(f"   ⏳ Cooling down for {wait_time:.1f}s to avoid YouTube 429...")
                    time.sleep(wait_time)

                print(f"   ▶️  Learning from: {url}")
                try:
                    result = await learner.learn_from_youtube(url, language="auto")
                    if 'detected_primitives' in result:
                        p_count = len(result['detected_primitives'])
                        print(f"      ✅ Learned {p_count} logic patterns.")
                        # Collect for final report
                        learning_summary.append({
                            "url": url,
                            "count": p_count,
                            "primitives": result['detected_primitives']
                        })
                except Exception as e:
                    print(f"      ❌ Failed to learn: {e}")
            
            # --- PRINT YOUTUBE LEARNING REPORT ---
            if learning_summary:
                print("\n📊 [YouTube Learning Report]")
                total_patterns = 0
                for item in learning_summary:
                    print(f"   - Video: {item['url']}")
                    for p in item['primitives']:
                        print(f"     📍 [{p['category']}] {p['name']}: {p['logic_pattern'][:50]}...")
                        total_patterns += 1
                print(f"   ⭐️ Total New Logic Patterns Absorbed: {total_patterns}")

        else:
            print("   ⚠️ No videos found or discovery disabled.")

        # 4. Ontology Evolution (Learning new attributes)
        print("\n4️⃣  [Evolution] Learning new terminology and expanding Ontology...")
        learner = OntologyLearner()
        learner.learn_new_patterns()

        # 5. Vocabulary Building (Knowledge Graph Expansion)
        print("\n5️⃣  [Vocabulary] Updating Brain Ontology...")
        builder = VocabularyBuilder(db)
        builder.build_vocabulary()

    except Exception as e:
        print(f"\n❌ critical: {e}")
    finally:
        db.close()
        print("\n" + "="*60)
        print("🌙 [VendorOS] Daily Routine Complete.")

if __name__ == "__main__":
    asyncio.run(run_daily_jobs())
