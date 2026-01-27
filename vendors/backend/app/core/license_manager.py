from typing import List, Dict

class LicenseManager:
    """
    [Tiered License Control]
    Manages access rights based on VANDORS subscription tiers.
    """
    
    TIERS = {
        "TIER_1": {"name": "Standard", "modules": ["PHYSICS_PID"], "limit_precision": "LOW"},
        "TIER_2": {"name": "Adaptive", "modules": ["PHYSICS_PID", "V_BRIDGE", "V_CALIBRATION"], "limit_precision": "HIGH"},
        "TIER_3": {"name": "Molecular", "modules": ["ALL"], "limit_precision": "MOLECULAR"}
    }
    
    def __init__(self, user_tier: str = "TIER_1"):
        self.tier = user_tier.upper()
        if self.tier not in self.TIERS:
            self.tier = "TIER_1"
            
    def can_access(self, module_name: str) -> bool:
        allowed = self.TIERS[self.tier]["modules"]
        if "ALL" in allowed: return True
        return module_name in allowed

    def get_parameter_precision(self) -> float:
        """
        Returns the simplified simulation step for this tier.
        Tier 3 gets fine-grained physics (0.1s), Tier 1 gets coarse (1.0s).
        """
        precision_map = {
            "TIER_1": 1.0,  # 1 second updates (Slow)
            "TIER_2": 0.5,  # 0.5 second updates
            "TIER_3": 0.1   # 0.1 second updates (Real-time Molecular)
        }
        return precision_map.get(self.tier, 1.0)
