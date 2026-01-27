from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class TargetSource(str, Enum):
    CHEF = "chef"             # Recorded from human expert
    LITERATURE = "literature" # From Food Science paper
    SIMULATOR = "simulator"   # From Physics Engine
    ESTIMATE = "estimate"     # Rough guess

class PhysicalTarget(BaseModel):
    """
    The specific physical state we want to achieve.
    """
    target_temp_c: float = Field(..., description="Target Surface Temperature")
    min_maillard_index: Optional[float] = Field(None, description="Integrated Heat > 140C (0.0 - 1.0)")
    max_overshoot_temp: Optional[float] = Field(None, description="Safety limit for temp")
    
    # Metadata for Quality Control
    thermal_mass_g: Optional[float] = None
    
class FISProfile(BaseModel):
    """
    The 'Compiled Intent' of a cooking process.
    Acts as the Reference Signal for the Control Loop.
    """
    id: str
    name: str
    
    # The Physics Goal
    target: PhysicalTarget
    
    # Trust Metrics (Critical for AI Safety)
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Reliability of this target")
    source: TargetSource
    
    # Context
    description: Optional[str] = None
