from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_api_key
from app.core.logging import logger
from app.scrapers.baemin import get_scraper
from app.services.vision import vision_service
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

router = APIRouter(
    prefix="/predict",
    tags=["prediction"],
    dependencies=[Depends(get_api_key)]
)

class UrlRequest(BaseModel):
    url: str

@router.post("/baemin", summary="배민 메뉴 원가 예측 (BIPS)")
async def predict_baemin_margin(request: UrlRequest):
    """
    1. Scraper: URL 방문 -> 스크린샷 캡처
    2. Vision: 스크린샷 분석 -> 식자재 리스트 추출
    3. (Future) Calculator: 식자재 리스트 -> 원가 계산
    """
    scraper = get_scraper()
    
    logger.info(f"🚀 [BIPS] Scraping URL: {request.url}")
    try:
        # Step 1: Scrape (Run synchronous Selenium in thread pool to avoid blocking event loop)
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, scraper.scrape_menu, request.url)
        
        logger.info(f"📸 Screenshot captured. Title: {data['title']}")
        
        # Step 2: Vision Analysis
        logger.info("🧠 Sending to Gemini Vision...")
        ingredients_data = vision_service.analyze_menu_image(
            data['screenshot'], 
            context=data['title']
        )
        
        return {
            "status": "success",
            "page_title": data['title'],
            "predictions": ingredients_data
        }
        
    except Exception as e:
        logger.error(f"❌ Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
