from pydantic import BaseModel, Field
from typing import Optional
import datetime

class PanProfile(BaseModel):
    """
    [Hardware Identity]
    Physical properties of the cooking vessel.
    Derived from System Identification (Step Response).
    """
    id: str = Field(..., description="Unique ID (e.g., 'Lodge_CastIron_10in')")
    name: str
    
    # 1. Physical Dimensions (Static)
    diameter_cm: float
    material_type: str = "Unknown" # e.g. "CastIron", "Aluminum", "Steel"
    
    # 2. Thermal Properties (Dynamic / Identified)
    thermal_mass: float = Field(..., description="Heat Capacity (J/K). Determines heating speed.")
    heat_loss_coeff: float = Field(..., description="Dissipation (W/K). Determines cooling speed.")
    
    # 3. Meta
    calibration_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    confidence_score: float = 1.0

    class Config:
        from_attributes = True
