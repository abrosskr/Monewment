from ..core.celery_app import celery_app
from ..core.logging import logger
from ..services.extractor_service import ExtractorService
from ..services.fis_service import FisService
from ..database import SessionLocal
import time

@celery_app.task(name="app.tasks.worker_tasks.classify_recipe_task")
def classify_recipe_task(recipe_id: int):
    """
    Background task to classify a recipe and extract physics data.
    """
    from ..models.recipe import ScrapedRecipe
    db = SessionLocal()
    try:
        recipe = db.query(ScrapedRecipe).filter(ScrapedRecipe.id == recipe_id).first()
        if not recipe:
            logger.warning(f"Task skipped: Recipe {recipe_id} not found.")
            return False

        logger.info(f"🧠 [Celery] Classifying Recipe: {recipe.name}")
        
        # 1. Dependency-like Service Initialization
        # In a more advanced setup, we use a container or manually inject
        extractor = ExtractorService()
        
        # Perform classification (AI Call)
        # Note: In real production, we'd use a dedicated classifier service
        # but here we reuse the extractor logic for semantic grouping.
        extraction = extractor.extract_entities(f"{recipe.name} Ingredients: {', '.join(recipe.ingredients)}")
        
        if extraction:
            recipe.classification = extraction
            recipe.classified = True
            db.commit()
            logger.info(f"✅ [Celery] Finished classification for {recipe.name}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ [Celery] Task failed for recipe {recipe_id}: {e}")
        return False
    finally:
        db.close()

@celery_app.task(name="app.tasks.worker_tasks.bulk_data_processing")
def bulk_data_processing():
    """
    Periodic task to process unclassified records in bulk.
    """
    from ..models.recipe import ScrapedRecipe
    db = SessionLocal()
    try:
        unclassified = db.query(ScrapedRecipe).filter(ScrapedRecipe.classified == False).limit(10).all()
        for recipe in unclassified:
            classify_recipe_task.delay(recipe.id)
        return len(unclassified)
    finally:
        db.close()
