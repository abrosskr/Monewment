# app/services/graph_service.py
import networkx as nx
from typing import List, Dict, Any
from app.models.graph import GraphNode, GraphEdge, NodeType, RelationType

class GraphService:
    """
    [Wide Data Engine]
    Manages the Food Knowledge Graph (FKG) in memory.
    Uses NetworkX for topology analysis and pathfinding.
    """
    
    # Singleton Instance Stub (for MVP)
    _graph = nx.DiGraph()

    @classmethod
    def initialize_demo_data(cls):
        """
        Loads a small demo dataset to prove the concept.
        In production, this would load from a vector DB or huge JSON.
        """
        cls._graph.clear()
        
        # 1. Defining Nodes (Ingredients & Dishes)
        nodes = [
            ("Pork", {"type": NodeType.INGREDIENT}),
            ("Kimchi", {"type": NodeType.INGREDIENT}),
            ("Tofu", {"type": NodeType.INGREDIENT}),
            ("Tuna", {"type": NodeType.INGREDIENT}),
            ("Spam", {"type": NodeType.INGREDIENT}),
            
            ("Kimchi_Jjigae", {"type": NodeType.DISH}),
            ("Tuna_Kimchi_Jjigae", {"type": NodeType.DISH}),
            ("Army_Stew", {"type": NodeType.DISH}), # Budae Jjigae
            
            ("Green_Onion", {"type": NodeType.INGREDIENT}),
            ("Chives", {"type": NodeType.INGREDIENT}), # 부추
            ("Seafood_Mix", {"type": NodeType.INGREDIENT}),
            ("Flour_Batter", {"type": NodeType.INGREDIENT}),
            ("Makgeolli", {"type": NodeType.INGREDIENT}), # 막걸리 (Beverage is technically ingredient here)
            
            ("Seafood_Pajeon", {"type": NodeType.DISH}),
            
            ("Savory", {"type": NodeType.TASTE}),
            ("Spicy", {"type": NodeType.TASTE}),
        ]
        
        cls._graph.add_nodes_from(nodes)
        
        # 2. Defining Edges (Relationships)
        edges = [
            # Dish Definitions
            ("Kimchi_Jjigae", "Pork", {"relation": RelationType.CONTAINS}),
            ("Kimchi_Jjigae", "Kimchi", {"relation": RelationType.CONTAINS}),
            ("Kimchi_Jjigae", "Tofu", {"relation": RelationType.CONTAINS}),
            
            ("Tuna_Kimchi_Jjigae", "Tuna", {"relation": RelationType.CONTAINS}),
            ("Tuna_Kimchi_Jjigae", "Kimchi", {"relation": RelationType.CONTAINS}),
            
            ("Army_Stew", "Spam", {"relation": RelationType.CONTAINS}),
            ("Army_Stew", "Kimchi", {"relation": RelationType.CONTAINS}),
            
            # Jeon (For Kairos Engine Demo)
            ("Seafood_Pajeon", "Green_Onion", {"relation": RelationType.CONTAINS}), # 쪽파
            ("Seafood_Pajeon", "Seafood_Mix", {"relation": RelationType.CONTAINS}),
            ("Seafood_Pajeon", "Flour_Batter", {"relation": RelationType.CONTAINS}),
            
            # Flavor Pairings (The "Context")
            ("Pork", "Kimchi", {"relation": RelationType.PAIRS_WITH, "weight": 0.9}),
            ("Tuna", "Kimchi", {"relation": RelationType.PAIRS_WITH, "weight": 0.85}),
            ("Spam", "Kimchi", {"relation": RelationType.PAIRS_WITH, "weight": 0.8}),
            ("Seafood_Pajeon", "Makgeolli", {"relation": RelationType.PAIRS_WITH, "weight": 0.95}), # 막걸리 Pairing

            # Substitutions (Similar Textures/Roles)
            ("Pork", "Tuna", {"relation": RelationType.SUBSTITUTES, "weight": 0.7}),
            ("Pork", "Spam", {"relation": RelationType.SUBSTITUTES, "weight": 0.6}),
            ("Green_Onion", "Chives", {"relation": RelationType.SUBSTITUTES, "weight": 0.8}), # 쪽파 -> 부추 대체
        ]
        
        for u, v, data in edges:
            cls._graph.add_edge(u, v, **data)
            
        print(f"🕸️ [GraphService] Initialized with {cls._graph.number_of_nodes()} nodes and {cls._graph.number_of_edges()} edges.")

    @classmethod
    def search_context(cls, query: str) -> Dict[str, Any]:
        """
        User Query: "Pork"
        Returns: { "related_dishes": [...], "pairings": [...] }
        """
        # Simple Exact Match for MVP
        # In real world, use Vector Embedding Search here.
        if query not in cls._graph:
            return {"status": "not_found", "message": f"Node '{query}' not found in Knowledge Graph."}
            
        # 1. Connected Dishes (Where is this used?)
        # Search for predecessors (Dishes that contain this Ingredient)
        related_dishes = []
        for neighbor in cls._graph.predecessors(query):
            rel = cls._graph.get_edge_data(neighbor, query).get("relation")
            if rel == RelationType.CONTAINS:
                related_dishes.append(neighbor)
                
        # 2. Good Pairings (What goes well with this?)
        pairings = []
        for neighbor in cls._graph.successors(query):
            rel = cls._graph.get_edge_data(query, neighbor).get("relation")
            if rel == RelationType.PAIRS_WITH:
                pairings.append(neighbor)
        # Also check bidirectional pairings (if defined as separate edges or checking predecessors)
        
        # 3. Substitutes (What can replace this?)
        substitutes = []
        for neighbor in cls._graph.successors(query):
            rel = cls._graph.get_edge_data(query, neighbor).get("relation")
            if rel == RelationType.SUBSTITUTES:
                substitutes.append(neighbor)

        return {
            "query": query,
            "type": cls._graph.nodes[query].get("type"),
            "context": {
                "used_in": related_dishes,
                "goes_well_with": pairings,
                "can_be_replaced_by": substitutes
            }
        }

    @classmethod
    def get_full_graph(cls):
        """Returns D3.js compatible format"""
        return nx.node_link_data(cls._graph)

    @classmethod
    def get_real_stats(cls) -> Dict[str, Any]:
        """
        Calculates real statistics from the data repository.
        Scans 'backend/data/fis_repo' for RECIPE_10K_*.json files.
        """
        import os
        import json
        
        # Path relative to execution context (usually backend/)
        # Adjust if necessary depending on where main.py runs
        # We assume main.py is in backend/app/../ or similar.
        # Ideally use absolute path or config.
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data", "fis_repo")
        
        stats = {
            "recipes": 0,
            "ingredients": 0,
            "sources": 0,
            "optScore": 98.2 # Keep this mocked/simulated for now
        }
        
        unique_ingredients = set()
        sources = set()
        
        try:
            if not os.path.exists(data_dir):
                print(f"[GraphService] Data directory not found: {data_dir}")
                return stats # Return empty stats if no dir

            files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
            stats["recipes"] = len(files)
            
            # Simple heuristic optimization: 
            # If > 1000 files, maybe sample? But 150 is fine to read all.
            for f in files:
                try:
                    # Identify source from filename prefix
                    if f.startswith("RECIPE_10K"):
                        sources.add("10000 Recipes")
                    else:
                        sources.add("Other")
                        
                    # Read ingredients
                    with open(os.path.join(data_dir, f), "r", encoding="utf-8") as json_file:
                        data = json.load(json_file)
                        if "ingredients" in data:
                            for ing_key in data["ingredients"].keys():
                                # Simple normalization: take text before first space or normalize
                                # The key is like "돼지목살 .... 500g"
                                # We want just "돼지목살"
                                ing_name = ing_key.split()[0].strip()
                                unique_ingredients.add(ing_name)
                except Exception as e:
                    continue
                    
            stats["ingredients"] = len(unique_ingredients)
            stats["sources"] = len(sources) or 1 # At least 1 if we have files
            
        except Exception as e:
            print(f"Error calculating stats: {e}")
            
        return stats
