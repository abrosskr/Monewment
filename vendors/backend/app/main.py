from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import recommend, analyze
from app.routers import fis, graph, training, vpt
from app.config import settings

app = FastAPI(
    title="Vendors Intelligence Engine",
    description="The OS for Food Tech: Physics, Chemistry & Personalization API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(recommend.router, prefix="/v1/recommend", tags=["Recommendation"])
app.include_router(analyze.router, prefix="/v1/analyze", tags=["Analysis"])
app.include_router(fis.router, prefix="/v1/fis", tags=["FIS (Printer)"])
app.include_router(graph.router, prefix="/v1/graph", tags=["Flavor Graph"])
app.include_router(training.router, prefix="/v1/training", tags=["Training"])
app.include_router(vpt.router, prefix="/v1/vpt", tags=["VPT Simulation"])

# Hardened Async Tasks
from app.routers import task
app.include_router(task.router, prefix="/v1/tasks", tags=["Async Tasks (Secure)"])

# New Engines (Server-fication)
from app.api.v1.endpoints import product, logistics
app.include_router(product.router, prefix="/v1/product", tags=["PIM Engine"])
app.include_router(logistics.router, prefix="/v1/logistics", tags=["Logistics Engine"])

@app.get("/")
def root():
    return {
        "system": "Vendors Intelligence Engine",
        "status": "Online",
        "version": "1.0.0",
        "message": "The Brain is ready.",
        "modules": ["FIS", "VPT", "Graph", "Training", "Analysis"]
    }
