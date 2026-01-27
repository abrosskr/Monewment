# app/models/graph.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class NodeType(str, Enum):
    INGREDIENT = "Ingredient"
    DISH = "Dish"
    TASTE = "Taste"
    METHOD = "Method"

class RelationType(str, Enum):
    CONTAINS = "CONTAINS"       # Dish -> Ingredient
    PAIRS_WITH = "PAIRS_WITH"   # Ingredient <-> Ingredient (Flavor synergy)
    HAS_TASTE = "HAS_TASTE"     # Ingredient -> Taste
    SUBSTITUTES = "SUBSTITUTES" # Ingredient <-> Ingredient (Alternative)

class GraphNode(BaseModel):
    id: str = Field(..., description="Unique Identifier (e.g., 'Pork', 'Kimchi_Jjigae')")
    type: NodeType
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata (weight, chemical_vector, etc.)")

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: RelationType
    weight: float = 1.0 # Strength of relationship (0.0 ~ 1.0)

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
