import logging
import math
import random
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCTSCookingEngine:
    """
    [Grand Fortification: High Performance]
    Monte Carlo Tree Search for finding optimal cooking paths.
    Includes Pruning and Early Stopping to manage complexity explosion.
    """

    def __init__(self, chemistry_sim):
        self.chem_sim = chemistry_sim
        self.max_depth = 10
        self.simulations_per_node = 50
        self.exploration_weight = 1.414 # Standard UCT

    def explore_optimal_path(self, initial_state: str, ingredients: List[str]) -> List[Dict]:
        """
        Explores the action space to find the path with highest flavor/safety ROI.
        """
        logger.info(f"🧠 MCTS Exploration Started for {initial_state}...")
        
        # Root node represents initial state
        root = {"state": initial_state, "path": [], "visits": 0, "value": 0.0, "children": []}
        
        # 1. Parallelizable Simulation Loop
        for _ in range(500): # Total budgets
            self._simulate(root)
            
        # 2. Extract best path
        best_path = self._extract_best_path(root)
        logger.info(f"✅ MCTS Exploration Complete. Best path depth: {len(best_path)}")
        return best_path

    def _simulate(self, node: Dict):
        """Standard MCTS Simulation: Selection -> Expansion -> Simulation -> Backprop."""
        # Selection & Expansion
        if not node["children"] and node["visits"] > 0:
            self._expand(node)
        
        if node["children"]:
            child = self._select_uct(node)
            self._simulate(child)
        else:
            # Simulation (Rollout) with Pruning
            reward = self._rollout(node)
            # Backpropagation
            self._backprop(node, reward)

    def _expand(self, node: Dict):
        # Action space: Temperature steps [100, 120, 140, 160, 180, 200, 220]
        # [Pruning]: Filter out actions that breach safety early
        actions = [100, 140, 180, 220] 
        for heat in actions:
            # Predict if this heat is immediately fatal (Early Pruning)
            if heat > 210 and node["state"] == "ROOM_TEMP":
                continue # Prune likely carbonization paths
            
            new_node = {
                "heat": heat,
                "path": node["path"] + [{"temp": heat, "duration": 30}],
                "visits": 0,
                "value": 0.0,
                "children": []
            }
            node["children"].append(new_node)

    def _rollout(self, node: Dict) -> float:
        """Lightweight simulation to end of depth."""
        temp_profile = [p["temp"] for p in node["path"]]
        # Predict chemical outcome
        results = self.chem_sim.simulate_reactions(temp_profile, time_step=1.0)
        
        # [Early Stopping]: If safety risk is too high, return negative infinity
        if results["edibility"] == "REJECTED":
            return -100.0
            
        return results["metrics"]["flavor"] * 10 - results["metrics"]["safety_risk"]

    def _select_uct(self, node: Dict) -> Dict:
        log_total = math.log(node["visits"])
        return max(node["children"], key=lambda c: (c["value"] / (c["visits"] or 1)) + 
                   self.exploration_weight * math.sqrt(log_total / (c["visits"] or 1)))

    def _backprop(self, node: Dict, reward: float):
        node["visits"] += 1
        node["value"] += reward

    def _extract_best_path(self, root: Dict) -> List[Dict]:
        path = []
        curr = root
        while curr["children"]:
            curr = max(curr["children"], key=lambda c: c["visits"])
            path.append({"temp": curr["heat"], "duration": 30})
        return path
