from typing import List, Dict, Any
from app.engines.v_bridge.core import PhysicalStateTarget

class VGuideEngine:
    """
    [V-Guide: The Human-Appliance Bridge]
    Converts physical goals into human-actionable or 
    analog machine guidance when direct IoT control is absent.
    """

    @classmethod
    def generate_instruction(cls, 
                              target: PhysicalStateTarget, 
                              current_temp: float,
                              machine_type: str = "ANALOG_GAS") -> str:
        """
        Translates 'Absolute Physics' into 'Perceptual Instruction'.
        """
        delta = target.surface_temp_target - current_temp
        
        if machine_type == "ANALOG_GAS":
            if delta > 30: return "가스레인지 불을 '강'으로 올리세요. 팬에서 연기가 살짝 나기 시작할 때까지 기다리세요."
            if delta < -5: return "불을 '약'으로 줄이거나 팬을 화구에서 잠시 떼어 열을 식히세요."
            return "현재 온도가 적절합니다. 불을 '중약불'로 유지하며 재료를 계속 저어주세요."
            
        elif machine_type == "HUMAN_CHEF":
            if target.target_reaction_intensity > 0.05:
                return "고기 조각의 가장자리가 갈색으로 변할 때까지 충분히 시어링하세요."
            return "재료의 수분이 날아가지 않도록 뚜껑을 덮고 기다리세요."
        
        return "표준 조리 지침을 따르세요."

    @classmethod
    def sense_check(cls, actual_temp: float, target_temp: float) -> str:
        """Warns the user if they are deviating too much from the physical path."""
        error = actual_temp - target_temp
        if error > 20: return "⚠️ 경고: 온도가 너무 높습니다! 탄맛이 날 수 있으니 즉시 불을 줄이세요."
        if error < -20: return "ℹ️ 안내: 온도가 너무 낮아 마이야르 반응이 일어나지 않고 있습니다. 화력을 높이세요."
        return "✅ 물리 경로를 잘 따르고 있습니다."
