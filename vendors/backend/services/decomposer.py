import logging
from typing import Dict, List
from app.database import SessionLocal
from app.models.assets import SourceIngestion, IngredientAsset, CultureAsset, MethodAsset, BehaviorAsset
from app.services.normalization_engine import NormalizationEngine
from app.services.metrics_engine import MetricsEngine

logger = logging.getLogger(__name__)

class Decomposer:
    """
    [Refinery Step 2: Decomposer]
    Splits raw Ingestion data into Domain-Pure Atomic Assets.
    Now supports BEHAVIOR domain for Food Data Factory MS Scores.
    """

    @classmethod
    def process_source(cls, source_id: int):
        db = SessionLocal()
        try:
            source = db.query(SourceIngestion).get(source_id)
            if not source: return
            
            raw = source.raw_data
            
            # 1. Decompose INGREDIENT Domain
            cls._decompose_ingredients(db, source.id, raw.get('ingredients', []))
            
            # 2. Decompose CULTURE Domain
            cls._decompose_culture(db, source.id, raw.get('url', ''), raw.get('name', ''))
            
            # 3. Decompose RECIPE_TEXT (Method) Domain
            cls._decompose_methods(db, source.id, raw.get('steps', []))

            # 4. Decompose BEHAVIOR Domain (New Phase 8)
            if 'engagement' in raw:
                cls._decompose_behavior(db, source.id, raw['engagement'])
            
            db.commit()
            logger.info(f"💠 Source {source_id} Decomposed into Atomic Domains (including Behavior).")
        except Exception as e:
            logger.error(f"❌ Decomposition Error: {e}")
            db.rollback()
        finally:
            db.close()

    @classmethod
    def _decompose_behavior(cls, db, src_id, engagement: Dict):
        """
        Extracts behavioral truth and calculates the initial MS (Taste Score).
        """
        ms = MetricsEngine.evaluate_behavioral_truth(engagement)
        
        asset = BehaviorAsset(
            source_id=src_id,
            view_count=engagement.get('views', 0),
            like_count=engagement.get('likes', 0),
            comment_count=engagement.get('comments', 0),
            positive_sentiment_ratio=engagement.get('sentiment_score', 0.5),
            subscriber_view_ratio=engagement.get('scv', 0.1),
            ms_score=ms
        )
        db.add(asset)

    @classmethod
    def _decompose_ingredients(cls, db, src_id, raw_ings: List[str]):
        for ring in raw_ings:
            pim = NormalizationEngine.parse_to_pim(ring)
            if pim.main_category == "Unknown":
                purity = "C" # Cultural Assumption
            else:
                purity = "B" # Multi-recipe Consensus
                
            asset = IngredientAsset(
                source_id=src_id,
                purity_grade=purity,
                name=pim.main_category,
                category=pim.main_category,
                mass_g=pim.mass_g
            )
            db.add(asset)

    @classmethod
    def _decompose_culture(cls, db, src_id, url, name):
        # Placeholder for specialized TasteDNA/Culture logic
        # For now, simple mapping based on source origin
        # Purity Grade C: Cultural Assumption
        cuisine = "GLOBAL"
        if ".jp" in url: cuisine = "JAPANESE"
        elif ".kr" in url: cuisine = "KOREA"
        
        asset = CultureAsset(
            source_id=src_id,
            purity_grade="C",
            cuisine_type=cuisine,
            identity_markers=[name]
        )
        db.add(asset)

    @classmethod
    def _decompose_methods(cls, db, src_id, steps: List[str]):
        # Extraction of Cooking Verbs (Primitive Methods)
        # Purity Grade C: Cultural Assumption (from text)
        verbs = ["PREHEAT", "SEAR", "BRAISE", "STIR_FRY", "BOIL", "SIMMER"]
        
        order = 1
        for step in steps:
            step_upper = step.upper()
            found_verbs = [v for v in verbs if v in step_upper]
            for v in found_verbs:
                asset = MethodAsset(
                    source_id=src_id,
                    purity_grade="C",
                    verb=v,
                    sequence_order=order
                )
                db.add(asset)
                order += 1
