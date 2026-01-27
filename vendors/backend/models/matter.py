from pydantic import BaseModel, Field
from typing import Optional, Dict

class FlavorProfile(BaseModel):
    """
    The Taste Fingerprint (Expanded)
    """
    acid: float = Field(0.0, ge=0.0, le=1.0)
    sugar: float = Field(0.0, ge=0.0, le=1.0)
    umami: float = Field(0.0, ge=0.0, le=1.0)
    bitter: float = Field(0.0, ge=0.0, le=1.0)
    salt: float = Field(0.0, ge=0.0, le=1.0)
    aroma: float = Field(0.0, ge=0.0, le=1.0, description="Volatile compound intensity")
    spiciness: float = Field(0.0, ge=0.0, le=1.0, description="Scoville heat scale normalized")

class PhysicalProperties(BaseModel):
    """
    Thermodynamic & Rheological Properties
    """
    water_activity: Optional[float] = Field(0.95, description="aw (0.0-1.0). Critical for microbial safety.")
    viscosity_cp: Optional[float] = Field(None, description="Centipoise at 20C")
    melting_point_c: Optional[float] = None
    boiling_point_c: Optional[float] = None
    fat_content_percent: float = Field(0.0, ge=0.0, le=100.0)
    protein_denaturation_temp_c: Optional[float] = Field(None, description="Temp where protein structure collapses")

class ReactionPotential(BaseModel):
    """
    How reactive is this matter?
    """
    maillard_score: float = Field(0.0, description="Potential for browning (Amino + Reducing Sugar)")
    caramelization_score: float = Field(0.0, description="Potential for sugar oxidation")
    fermentation_affinity: float = Field(0.0, description="Suitability for microbial growth")
    
import datetime

from enum import Enum

class TrustTier(str, Enum):
    A = "A_HUMAN_VERIFIED"  # Gold Standard
    B = "B_TEXT_EXPLICIT"   # Found directly in reliable text
    C = "C_LLM_INFERRED"    # AI Guess (Mid Risk)
    D = "D_HEURISTIC"       # Rule of thumb (High Risk)
    U = "U_UNKNOWN"         # No data

class SourceMetadata(BaseModel):
    source: str
    confidence: float
    tier: TrustTier
    timestamp: str

class IngredientModel(BaseModel):
    """
    FIS Matter Definition v2.1 (Tiered Trust)
    """
    id: str
    name: str
    brand: Optional[str] = "Generic"
    
    flavor: FlavorProfile
    physical: PhysicalProperties
    reaction: ReactionPotential
    
    # Provenance
    usda_id: Optional[str] = None
    trust_tier: TrustTier = TrustTier.U
    source_meta: Optional[Dict[str, SourceMetadata]] = Field(default_factory=dict)
    
    def set_trust(self, tier: TrustTier, source: str, confidence: float):
        self.trust_tier = tier
        if "global" not in self.source_meta:
             self.source_meta["global"] = SourceMetadata(
                 source=source, confidence=confidence, tier=tier, 
                 timestamp=str(datetime.datetime.now())
             )
