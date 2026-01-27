# app/services/recipe_cache.py
"""
Recipe Cache Service - 레시피 프리-캐시 시스템 with PostgreSQL
서버 시작 시 자동 수집을 제거하고 API 트리거 방식으로 변경 (안정성 확보)
"""
import threading
import time
import json
from datetime import datetime
from collections import deque
from typing import Optional, List, Dict

from sqlalchemy import desc, func
from ..database import SessionLocal
from ..models.recipe import ScrapedRecipe

class RecipeCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.cache: deque = deque(maxlen=100)
        self.used_urls: set = set()
        self._lock = threading.Lock()
        self._scraper = None
        self._classifier = None
        self._is_filling = False
        
        # NOTE: Do NOT start threads here. It blocks FastAPI startup if DB is locked.
        # Threads are started strictly via API endpoints or external workers.
        
        # Load initial data synchronously if needed, but safe to skip for now.
        # self._load_from_db()
        print("✅ [RecipeCache] Initialized (Lazy Loading Mode)")

    def _get_db(self):
        return SessionLocal()
    
    def _load_from_db(self):
        """DB에서 분류된 레시피 우선 로드"""
        db = self._get_db()
        try:
            # 분류된 레시피 우선, 그 다음 미분류
            # SQL: SELECT * FROM scraped_recipes WHERE used = FALSE ORDER BY classified DESC, collected_at DESC LIMIT 100
            recipes = db.query(ScrapedRecipe).filter(
                ScrapedRecipe.used == False
            ).order_by(
                desc(ScrapedRecipe.classified),
                desc(ScrapedRecipe.collected_at)
            ).limit(100).all()
            
            for row in recipes:
                recipe = {
                    "url": row.url,
                    "name": row.name,
                    "ingredients": row.ingredients,
                    "image": row.image,
                    "classification": row.classification
                }
                self.cache.append(recipe)
                if row.classified:
                    pass # Count stats if needed

            # Load used URLs
            used_recipes = db.query(ScrapedRecipe.url).filter(ScrapedRecipe.used == True).all()
            for r in used_recipes:
                self.used_urls.add(r.url)
                
            print(f"✅ [RecipeCache] Loaded {len(self.cache)} recipes from Postgres")
        except Exception as e:
            print(f"❌ [RecipeCache] DB load error: {e}")
        finally:
            db.close()
            
    def _save_to_db(self, recipe_data: Dict, classification: Dict = None):
        """레시피를 DB에 저장"""
        db = self._get_db()
        try:
            # Check exist
            exists = db.query(ScrapedRecipe).filter(ScrapedRecipe.url == recipe_data.get('url')).first()
            if exists:
                return

            new_recipe = ScrapedRecipe(
                url=recipe_data.get('url'),
                name=recipe_data.get('name'),
                ingredients=recipe_data.get('ingredients', []),
                image=recipe_data.get('image'),
                classification=classification,
                classified=True if classification else False
            )
            db.add(new_recipe)
            db.commit()
        except Exception as e:
            print(f"❌ [RecipeCache] DB save error: {e}")
            db.rollback()
        finally:
            db.close()

    def _update_classification_db(self, url: str, classification: Dict):
        """분류 결과 업데이트"""
        db = self._get_db()
        try:
            recipe = db.query(ScrapedRecipe).filter(ScrapedRecipe.url == url).first()
            if recipe:
                recipe.classification = classification
                recipe.classified = True
                db.commit()
        except Exception as e:
            print(f"❌ [RecipeCache] Update error: {e}")
            db.rollback()
        finally:
            db.close()

    def _mark_used_db(self, url: str):
        """레시피를 사용됨으로 표시"""
        db = self._get_db()
        try:
            recipe = db.query(ScrapedRecipe).filter(ScrapedRecipe.url == url).first()
            if recipe:
                recipe.used = True
                db.commit()
        except Exception as e:
            print(f"❌ [RecipeCache] Mark used error: {e}")
            db.rollback()
        finally:
            db.close()

    def _get_scraper(self):
        if self._scraper is None:
            from ..scrapers.recipe_10k import Recipe10kScraper
            self._scraper = Recipe10kScraper()
        return self._scraper
    
    def _get_classifier(self):
        if self._classifier is None:
            from .local_llm_classifier import LocalLLMClassifier
            self._classifier = LocalLLMClassifier()
        return self._classifier

    def get_recipe_with_classification(self) -> Optional[Dict]:
        """분류된 레시피 우선 반환 (즉시 응답)"""
        # 1. Memory check
        with self._lock:
            for recipe in self.cache:
                if recipe.get('classification'):
                    self.cache.remove(recipe)
                    self.used_urls.add(recipe['url'])
                    self._mark_used_db(recipe['url'])
                    return recipe
        
        # 2. DB Check (Direct)
        db = self._get_db()
        try:
            recipe = db.query(ScrapedRecipe).filter(
                ScrapedRecipe.used == False, 
                ScrapedRecipe.classified == True
            ).first()
            
            if recipe:
                data = {
                    "url": recipe.url,
                    "name": recipe.name,
                    "ingredients": recipe.ingredients,
                    "image": recipe.image,
                    "classification": recipe.classification
                }
                # Mark used
                recipe.used = True
                db.commit()
                self.used_urls.add(recipe.url)
                return data
        except Exception as e:
            print(f"❌ [RecipeCache] DB read error: {e}")
        finally:
            db.close()
        
        # 3. Fallback to unclassified
        return self.get_recipe()

    def get_recipe(self) -> Optional[Dict]:
        """분류 여부 상관없이 레시피 반환"""
        # 1. Memory
        with self._lock:
            if self.cache:
                recipe = self.cache.popleft()
                self.used_urls.add(recipe['url'])
                self._mark_used_db(recipe['url'])
                return recipe
                
        # 2. DB
        db = self._get_db()
        try:
            recipe = db.query(ScrapedRecipe).filter(ScrapedRecipe.used == False).first()
            if recipe:
                data = {
                    "url": recipe.url,
                    "name": recipe.name,
                    "ingredients": recipe.ingredients,
                    "image": recipe.image,
                    "classification": recipe.classification
                }
                recipe.used = True
                db.commit()
                self.used_urls.add(recipe.url)
                return data
        except Exception as e:
            print(f"❌ [RecipeCache] DB read error: {e}")
        finally:
            db.close()
            
        return None

    def get_cache_status(self) -> Dict:
        """캐시 상태 확인"""
        db = self._get_db()
        try:
            db_available = db.query(func.count(ScrapedRecipe.id)).filter(ScrapedRecipe.used == False).scalar()
            db_classified = db.query(func.count(ScrapedRecipe.id)).filter(ScrapedRecipe.used == False, ScrapedRecipe.classified == True).scalar()
            db_total = db.query(func.count(ScrapedRecipe.id)).scalar()
        except:
            db_available, db_classified, db_total = 0, 0, 0
        finally:
            db.close()

        memory_classified = sum(1 for r in self.cache if r.get('classification'))
        
        return {
            "memory_cache": len(self.cache),
            "memory_classified": memory_classified,
            "db_available": db_available,
            "db_classified": db_classified,
            "db_total": db_total,
            "used_count": len(self.used_urls),
            "is_filling": self._is_filling
        }

    # --------------------------------------------------------------------------
    # Manual / Background Task Triggers
    # --------------------------------------------------------------------------
    
    def prefill(self, count: int = 10):
        """수동 수집 실행 (동기 실행 주의)"""
        scraper = self._get_scraper()
        # Thread safety not guaranteed for scraper instance, but okay for sequential
        recipes = scraper.run_batch(count=count)
        
        with self._lock:
            for recipe in recipes:
                if recipe.get('url') not in self.used_urls:
                    self._save_to_db(recipe)
                    recipe['classification'] = None
                    self.cache.append(recipe)
        return {"added": len(recipes)}

    def start_background_classification(self):
        """분류 워커 수동 시작"""
        if self._is_filling: 
             return {"status": "already_running"}
             
        thread = threading.Thread(target=self._classification_loop, daemon=True)
        thread.start()
        return {"status": "started"}

    def _classification_loop(self):
        self._is_filling = True
        print("🧠 [Worker] Classification started")
        classifier = self._get_classifier()
        
        while True:
            db = self._get_db()
            try:
                # Get unclassified
                target = db.query(ScrapedRecipe).filter(
                    ScrapedRecipe.classified == False,
                    ScrapedRecipe.used == False
                ).first()
                
                if not target:
                    db.close()
                    time.sleep(10) # Wait for more data
                    continue
                    
                # Classify
                print(f"🧠 [Classifying] {target.name}...")
                classification = classifier.classify(target.name, target.ingredients)
                
                if classification:
                    target.classification = classification
                    target.classified = True
                    db.commit()
                    print(f"  ✅ Classified as: {classification.get('food_type_name')}")
                    
                    # [Intelligent Service] Add to Vector Memory
                    try:
                        from .memory_service import MemoryService
                        mem = MemoryService()
                        # Use Name + Ingredients string for embedding
                        text_for_embedding = f"{target.name} (Ingredients: {', '.join(target.ingredients)})"
                        mem.add_memory(text_for_embedding, classification)
                    except Exception as ve:
                         print(f"  ⚠️ Vector Indexing Failed: {ve}")
                else:
                    # Failed? Skip for now?
                    pass
                
                time.sleep(2) # Polite delay
                
            except Exception as e:
                print(f"❌ [Worker] Error: {e}")
                time.sleep(30)
            finally:
                db.close()
                

# Singleton instance
recipe_cache = RecipeCache()
