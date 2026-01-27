# app/services/digital_twin_service.py
from typing import List, Dict, Any
from app.models.fis_protocol import FisFile, ActionType, MachineCommand

class DigitalTwinService:
    """
    [The Validator]
    Simulates the cooking process in memory to verify .fis data quality.
    Ensures "Physical Consistency" before selling data to Samsung/LG.
    """

    @staticmethod
    def validate_protocol(fis_data: FisFile) -> Dict[str, Any]:
        """
        Interprets the FIS file and checks for physical violations.
        """
        issues = []
        timeline = sorted(fis_data.timeline, key=lambda x: x.sequence_no)
        
        current_temp = 25.0 # Room Temp
        total_time = 0
        
        for cmd in timeline:
            # 1. Sequence Check
            if cmd.sequence_no < 0:
                issues.append(f"Cmd {cmd.id}: Negative sequence number.")
                
            # 2. Physics Check (Thermal Simulation)
            if cmd.action == ActionType.HEAT:
                target_temp = cmd.params.get("temp", 0)
                duration = cmd.params.get("duration", 0)
                
                # Simple check: Is temp achievable?
                if target_temp > 300:
                    issues.append(f"Cmd {cmd.id}: Target temp {target_temp}C exceeds safe limit (300C).")
                
                # Update simulation state
                current_temp = target_temp 
                total_time += duration
                
            # 3. Viscosity Check (Stirring)
            if cmd.action == ActionType.STIR:
                rpm = cmd.params.get("speed", 0)
                # If we knew the viscosity of the container content, we could check if RPM is too high (Splash risk)
                # For now, just a placeholder logic
                pass

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "simulated_metrics": {
                "final_temp": current_temp,
                "total_duration_sec": total_time
            }
        }

    @staticmethod
    def generate_mock_fis(recipe_name: str) -> FisFile:
        """
        Generates a sample FIS file for demonstration.
        """
        from app.models.fis_protocol import FisMetadata, PhysicalProperties, ChemicalVector, PhysicalState
        
        # Mock Data for "Perfect Boiled Egg"
        return FisFile(
            metadata=FisMetadata(recipe_id=f"RECIPE_{recipe_name.upper()}_001"),
            ingredients={
                "Water": PhysicalProperties(state=PhysicalState.LIQUID, specific_heat=4.18, viscosity_cp=1.0),
                "Egg": PhysicalProperties(state=PhysicalState.SOLID, specific_heat=3.1, viscosity_cp=None)
            },
            taste_profile=ChemicalVector(salt=0.0, sugar=0.0, acid=0.0),
            timeline=[
                MachineCommand(id="CMD_01", sequence_no=1, action=ActionType.DISPENSE, target="Pump_Water", params={"amount_ml": 500}),
                MachineCommand(id="CMD_02", sequence_no=2, action=ActionType.HEAT, target="Induction_A", params={"temp": 100, "duration": 300}), # Boil
                MachineCommand(id="CMD_03", sequence_no=3, action=ActionType.NOTIFY, target="Human", params={"msg": "Insert Egg"}),
                MachineCommand(id="CMD_04", sequence_no=4, action=ActionType.WAIT, target="System", params={"duration": 420}) # 7 mins
            ]
        )
