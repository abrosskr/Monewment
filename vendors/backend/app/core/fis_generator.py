from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from app.models.assets import SourceIngestion, IngredientAsset, CultureAsset, MethodAsset, FoodPhysicsAsset
from app.models.fis_protocol import FisFile, FisMetadata
from app.models.matter import PhysicalProperties, FlavorProfile
from app.models.machine_ir import MachineCommand, ActionType, PhysicalGoal
import json

class FISGenerator:
    """
    [Refinery Step 5: Fusion Engine]
    Synthesizes Temporary Products From Atomic Domain Atoms.
    """
    
    # Constitution: Culinary Verbs (Language) -> Physical Primitives (Physics)
    VERB_MAP = {
        "PREHEAT": ActionType.HEAT_SURFACE,
        "SEAR": ActionType.HEAT_SURFACE,
        "BOIL": ActionType.HEAT_LIQUID,
        "STIR_FRY": ActionType.HEAT_SURFACE,
        "SIMMER": ActionType.HEAT_LIQUID,
        "WAIT": ActionType.WAIT
    }

    @classmethod
    def synthesize_from_source(cls, db: Session, source_id: int, physics_session_id: Optional[str] = None, client_profile: str = "GENERIC") -> FisFile:
        source = db.query(SourceIngestion).get(source_id)
        if not source: return None
        
        ingredients = db.query(IngredientAsset).filter(IngredientAsset.source_id == source_id).all()
        methods = db.query(MethodAsset).filter(MethodAsset.source_id == source_id).order_by(MethodAsset.sequence_order).all()
        
        physics = None
        if physics_session_id:
            physics = db.query(FoodPhysicsAsset).filter(FoodPhysicsAsset.session_id == physics_session_id).first()

        metadata = FisMetadata(
            recipe_id=f"FUSION_{source_id}_{client_profile}",
            name=source.raw_data.get('name', 'Unknown'),
            source_url=source.url,
            extra_info={"client": client_profile}
        )

        fis_ingredients = {}
        for ing in ingredients:
             # Law 1: Absolute Isolation (Clean physical properties)
             fis_ingredients[ing.name] = PhysicalProperties()

        # Fusion: Mapping Language (Methods) to Physics (Timeline)
        timeline = []
        if physics:
            # Law 2: Sensors outrank text (Physics-driven)
            timeline = cls._extract_control_timeline(physics)
        else:
            # Step 5: Contracted Synthesis (Mapping text to machine IR)
            for i, m in enumerate(methods):
                action = cls.VERB_MAP.get(m.verb.upper(), ActionType.WAIT)
                cmd = MachineCommand(
                    step_id=i + 1,
                    action=action,
                    duration_sec=60 if m.verb == "SEAR" else 300, # Expert Assumption
                    goal=PhysicalGoal.MAILLARD_ONSET if m.verb == "SEAR" else None
                )
                timeline.append(cmd)

        return FisFile(
            metadata=metadata,
            ingredients=fis_ingredients,
            taste_profile=FlavorProfile(),
            timeline=timeline
        )

    @classmethod
    def _extract_control_timeline(cls, physics_asset: FoodPhysicsAsset) -> List[MachineCommand]:
        return [
            MachineCommand(step_id=1, action=ActionType.HEAT_SURFACE, temperature_c=160.0, goal=PhysicalGoal.MAILLARD_ONSET)
        ]
