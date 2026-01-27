# app/models/fis_protocol.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from enum import Enum

# Import Phase 4 High-Fidelity Models
from app.models.matter import PhysicalProperties, FlavorProfile
from app.models.machine_ir import MachineCommand, ActionType

# Backward Compatibility for Phase 3 AutoLabeler
class ChemicalVector(BaseModel):
    salt: float = 0.0
    sugar: float = 0.0
    acid: float = 0.0
    glutamate: float = 0.0
    capsaicin: float = 0.0
    lipid: float = 0.0

class PhysicalState(str, Enum):
    SOLID = "Solid"
    LIQUID = "Liquid"
    GAS = "Gas"
    plasma = "Plasma"

# 3. 📁 The File Format (.fis)
class FisMetadata(BaseModel):
    vsn: str = "2.0.0" # Version Step-up
    recipe_id: str
    author: str = "Vendors AI"
    target_device_profile: Optional[str] = "Universal_v2"
    source_url: Optional[str] = None
    name: Optional[str] = None
    data_quality: float = Field(1.0, description="Confidence Score")
    extra_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class FisFile(BaseModel):
    """
    The MP3 of Food (v2.0).
    Now powered by Matter Physics and Machine IR.
    """
    metadata: FisMetadata
    
    # Validation Mismatch Fix:
    # Compiler passes {name: PhysicalProperties}
    ingredients: Dict[str, PhysicalProperties] 
    
    taste_profile: FlavorProfile # Replaced ChemicalVector with FlavorProfile
    
    timeline: List[MachineCommand] # Replaced legacy Command with IR Command
