# app/routers/graph.py
from fastapi import APIRouter, HTTPException, Query
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Flavor Knowledge Graph"])

@router.on_event("startup")
async def load_graph():
    # Load demo data on startup
    GraphService.initialize_demo_data()

@router.get("/search")
def search_in_context(q: str = Query(..., description="Ingredient or Dish name (e.g., Pork)")):
    """
    [Contextual Search]
    Finds not just the node, but its connections (Dishes, Pairings, Substitutes).
    """
    result = GraphService.search_context(q)
    return result

@router.get("/visualize")
def get_graph_data():
    """
    Returns the full graph in D3.js node-link format for frontend visualization.
    """
    return GraphService.get_full_graph()

@router.get("/stats")
def get_insight_stats():
    """
    Returns real statistics from the V-Discovery knowledge base.
    """
    return GraphService.get_real_stats()
