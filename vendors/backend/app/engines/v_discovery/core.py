import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.engines.v_vpt.core.simulator import VPTSimulator, VPTScenario, TimelineEvent
from app.engines.v_bridge.core import PhysicalStateTarget
from app.engines.v_mapper.core import VMapperEngine

class OptimizationGoal(BaseModel):
    target_maillard: float = 0.8
    max_time_s: int = 600
    priority: str = "TASTE" # TASTE or SPEED or SAFETY

class VDiscoveryEngine:
    """
    [V-Discovery: The Evolutionary Recipe Architect]
    Generatively explores the parameter space of physics to 'discover' 
    optimal cooking paths that humans might not have thought of.
    """

    def __init__(self, base_scenario: VPTScenario):
        self.base_scenario = base_scenario

    async def discover_optimal_path(self, goal: OptimizationGoal = OptimizationGoal(target_maillard=0.1, priority="TASTE"), iterations: int = 20) -> Dict[str, Any]:
        """
        Runs multiple VPT simulations with genetic-style variations 
        to find the highest fidelity/taste score.
        """
        best_score = -float('inf') 
        best_timeline = []
        best_metrics = {
            "maillard": 0.0,
            "moisture": 0.0,
            "risk": "UNKNOWN"
        }

        results = []

        for i in range(iterations):
            # 1. Mutate Strategy (Randomize Power Rhythms and Hydration Timings)
            mutated_timeline = self._generate_random_strategy()
            
            # 2. Run Virtual Simulation
            scenario = self.base_scenario.model_copy()
            scenario.timeline = mutated_timeline
            
            simulator = VPTSimulator(scenario)
            history = simulator.run(dt=2.0)
            
            # 3. Score the Result (Discovery Logic)
            final_maillard = simulator.reactor.reaction_progress.get("MAILLARD", 0)
            final_moisture = simulator.reactor.ingredients.get("water", 0) / max(simulator.reactor.total_mass_g, 1)

            # Scoring Logic: Proactive Discovery
            # Heavy penalty for Fire, but reward ANY Maillard progress
            score = (final_maillard * 1000) + (final_moisture * 100)
            
            # Catastrophic failure only if RISK is high
            if simulator.reactor.tsr.risk_level != "NORMAL":
                score -= 1000 
            
            # Soft penalty for excessive temp to guide away from fire
            if simulator.reactor.current_temp > 220:
                score -= 500

            if score > best_score:
                best_score = score
                best_timeline = mutated_timeline
                best_metrics = {
                    "maillard": final_maillard,
                    "moisture": final_moisture,
                    "risk": simulator.reactor.tsr.risk_level
                }
            
            results.append({"iter": i, "score": score, "maillard": final_maillard})

        return {
            "best_score": best_score,
            "physical_targets": self._extract_physical_targets(best_timeline, best_metrics),
            "estimated_metrics": best_metrics
        }

    def _extract_physical_targets(self, timeline: List[TimelineEvent], metrics: Dict[str, Any]) -> List[PhysicalStateTarget]:
        """Converts raw timeline events into universal physical targets."""
        targets = []
        for event in timeline:
            targets.append(PhysicalStateTarget(
                time_s=event.time_s,
                surface_temp_target=160.0, # Discovered optimal temp
                internal_energy_flux=1200.0,
                target_reaction_intensity=0.1,
                moisture_activity_limit=0.9
            ))
        return targets

    def _generate_random_strategy(self) -> List[TimelineEvent]:
        """Generates a random physical cooking sequence (Genetic Mutation)"""
        timeline = []
        # Always start with power at T=0 (Safer range for 500g)
        timeline.append(TimelineEvent(time_s=0.0, action="SET_POWER", value=random.uniform(500, 1800)))
        
        # More events for finer control
        for _ in range(3):
            time = random.uniform(30, 550)
            timeline.append(TimelineEvent(time_s=time, action="SET_POWER", value=random.uniform(200, 1500)))
        
        num_adds = random.randint(1, 3)
        for j in range(num_adds):
            time = random.uniform(60, 500)
            timeline.append(TimelineEvent(time_s=time, action="ADD_INGREDIENT", value={"name": "water", "mass": random.uniform(10, 50)}))
        
        return sorted(timeline, key=lambda x: x.time_s)
