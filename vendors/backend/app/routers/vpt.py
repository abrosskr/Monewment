from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.engines.v_vpt.core.simulator import VPTSimulator, VPTScenario, TimelineEvent
from app.engines.v_academy.core import VAcademyEngine
from app.services.learning.manager import LearningManager
from app.engines.v_vision.inference import VVisualInference, VThermalProfiler
from app.core.security import get_api_key

router = APIRouter(prefix="/vpt", tags=["VPT"])

class YTLearnRequest(BaseModel):
    url: str

class SimulationRequest(BaseModel):
    scenario_name: str
    hardware_id: str
    ingredients: Dict[str, float]
    heating_method: str = "INDUCTION"
    chef_mode: bool = False
    youtube_url: Optional[str] = None

@router.post("/learn-link")
async def learn_youtube_link(request: YTLearnRequest, _ = Depends(get_api_key)):
    academy = VAcademyEngine()
    manager = LearningManager(academy)
    # Detect type or default to youtube
    source_type = "youtube" if "youtube.com" in request.url else "10k_recipes"
    result = await manager.ingest(source_type, request.url)
    return result

@router.post("/simulate")
async def run_vpt_simulation(request: SimulationRequest, _ = Depends(get_api_key)):
    # 1. Base Scenario
    timeline = [TimelineEvent(time_s=0.0, action="SET_POWER", value=1500)]
    
    # 2. Inject Chef Primitives if mode is enabled
    if request.chef_mode and request.youtube_url:
        academy = VAcademyEngine()
        manager = LearningManager(academy)
        kb = await manager.ingest("youtube", request.youtube_url)
        
        # Note: In a real system, we'd query the academy for the specific primitives 
        # that were just absorbed or are relevant to this dish.
        # For now, we simulate the hydration tech if primitives were found.
        if kb.get("absorbed_technique_count", 0) > 0:
             timeline = [
                TimelineEvent(time_s=0.0, action="SET_POWER", value=2000),
                TimelineEvent(time_s=60.0, action="ADD_INGREDIENT", value={"name": "water", "mass": 50.0}),
                TimelineEvent(time_s=120.0, action="ADD_INGREDIENT", value={"name": "water", "mass": 50.0})
            ]

    # 3. Vision-based parameter extraction (Simulated)
    # The system "sees" the meat to get thickness and marbling
    vision_data = VVisualInference.analyze_ingredient(None)

    scenario = VPTScenario(
        name=request.scenario_name,
        hardware_id=request.hardware_id,
        initial_ingredients=request.ingredients,
        timeline=timeline,
        max_duration_s=300
    )
    
    simulator = VPTSimulator(scenario)
    # AUTOMATION: Apply vision results to the physics reactor
    simulator.reactor.thickness_mm = vision_data["thickness_mm"]
    # Adjust fat content dynamically based on visual marbling
    simulator.reactor.cal.ingredient_offsets["beef"] = {"fat_content": vision_data["visual_fat_ratio"] - 0.15}
    simulator.reactor.heating_method = request.heating_method
    
    history = simulator.run(dt=1.0)
    return {
        "scenario": request.scenario_name,
        "history": history,
        "metrics": {
            "final_maillard": simulator.reactor.reaction_progress.get("MAILLARD", 0),
            "final_temp": simulator.reactor.current_temp,
            "risk_level": simulator.reactor.tsr.risk_level
        }
    }
