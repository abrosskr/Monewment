from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum

class ActionType(str, Enum):
    # Thermal
    HEAT_SURFACE = "HEAT_SURFACE"   # Conduction (Pan)
    HEAT_AMBIENT = "HEAT_AMBIENT"   # Convection (Oven)
    HEAT_LIQUID  = "HEAT_LIQUID"    # Convection (Boil)
    COOL_RAPID   = "COOL_RAPID"     # Shock
    
    # Kinetic
    STIR         = "STIR"
    WHISK        = "WHISK"
    CUT          = "CUT"
    
    # Chemical
    REST         = "REST"           # Time for diffusion/reaction
    
    # Process
    WAIT         = "WAIT"
    DISPENSE     = "DISPENSE"
    NOTIFY       = "NOTIFY"
    
class PhysicalGoal(str, Enum):
    MAILLARD_ONSET = "MAILLARD_ONSET"    # Surface > 140C
    GELATINIZATION = "GELATINIZATION"    # Starch breakdown
    EMULSIFICATION = "EMULSIFICATION"    # Stable mix
    DENATURATION   = "DENATURATION"      # Protein cooked
    SAFETY_KILL    = "SAFETY_KILL"       # Pathogen kill

class MachineCommand(BaseModel):
    """
    The Executable Instruction for any Food Robot.
    Decoupled from specific hardware (e.g. "Heat to 160C", not "Turn Oven Knob to 5").
    """
    step_id: int
    action: ActionType
    target_ingredient_id: Optional[str] = None
    
    # Physics Parameters (The Core Value)
    temperature_c: Optional[float] = Field(None, description="Target temp in Celsius")
    duration_sec: Optional[int] = Field(None, description="Duration in seconds")
    humidity_percent: Optional[float] = Field(None, description="Target ambient humidity")
    rpm: Optional[int] = Field(None, description="Stirring speed")
    
    # The 'Why'
    goal: Optional[PhysicalGoal] = None
    
    def to_instruction_string(self) -> str:
        """
        Compiler output for debugging.
        """
        param_str = []
        if self.temperature_c: param_str.append(f"@{self.temperature_c}°C")
        if self.duration_sec: param_str.append(f"for {self.duration_sec}s")
        if self.rpm: param_str.append(f"at {self.rpm} RPM")
        
        return f"[{self.step_id}] {self.action.value} ({', '.join(param_str)}) -> Goal: {self.goal.value if self.goal else 'None'}"
