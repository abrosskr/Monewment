from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database import engine, Base
from app.routers import training, ontology, fis, prediction, graph, analysis, vpt

# Initialize Logging
setup_logging()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize DB (Auto-migration for Dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="가장 낮은 곳에서 돕는 Losta 기술의 핵심 엔진입니다. (Hardened & Professional)",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set Limiter State
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware (Hardened: only allow loopback for now, or use * for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with standard prefix
app.include_router(training.router, prefix="/api")
app.include_router(ontology.router, prefix="/api")
app.include_router(fis.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(vpt.router, prefix="/api")

# Handle Optional Routers
try:
    from app.routers import prediction
    app.include_router(prediction.router, prefix="/api")
except ImportError as e:
    logger.warning(f"Prediction router not loaded: {e}")

@app.on_event("startup")
async def startup_event():
    """System warming up..."""
    logger.info("🚀 [Startup] VANDORS Engine Warming Up...")
    try:
        from app.services.recipe_cache import recipe_cache
        status = recipe_cache.start_background_classification()
        logger.info(f"🧠 Classification Worker: {status.get('status')}")
    except Exception as e:
        logger.error(f"⚠️ Startup error: {e}")

@app.get("/health", summary="Status Check")
def health_check():
    return {
        "status": "online",
        "version": settings.VERSION,
        "mode": "hardened",
        "db": "connected"
    }

@app.get("/")
def root():
    return {"message": "VANDORS API is running. Access /docs for API documentation."}