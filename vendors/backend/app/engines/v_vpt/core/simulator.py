from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.fis_physics import FisPhysics, PhysicsReactor
from app.engines.v_vpt.core.sensor_mocker import VPTSensorMocker, SensorNoiseConfig

class TimelineEvent(BaseModel):
    time_s: float
    action: str # "SET_POWER", "ADD_INGREDIENT", "CHANGE_AMBIENT"
    value: Any

class VPTScenario(BaseModel):
    name: str
    hardware_id: str
    initial_ingredients: Dict[str, float]
    timeline: List[TimelineEvent]
    max_duration_s: float = 3600

class VPTSimulator:
    """
    [VPT Core Engine]
    Orchestrates complex time-series scenarios.
    Useful for 'What-if' safety analysis and long-duration stability tests.
    """
    
    def __init__(self, scenario: VPTScenario, noise_config: Optional[SensorNoiseConfig] = None):
        self.scenario = scenario
        self.noise_config = noise_config or SensorNoiseConfig()
        self.reactor = PhysicsReactor(ingredients=scenario.initial_ingredients)
        self.current_power = 0.0
        self.history: List[Dict[str, Any]] = []

    def run(self, dt: float = 1.0):
        print(f"🚀 Starting VPT Scenario: {self.scenario.name}")
        
        elapsed = 0.0
        while elapsed < self.scenario.max_duration_s:
            # 1. Check Timeline for events
            for event in self.scenario.timeline:
                if abs(event.time_s - elapsed) < (dt / 2):
                    self._handle_event(event)

            # 2. Step Physics
            self.reactor = FisPhysics.step_simulation(self.reactor, dt, power_watts=self.current_power)
            
            # 3. Capture 'Dirty' Sensor Data (for feedback tests)
            sensor_data = VPTSensorMocker.mock_reactor_state(
                self.reactor.model_dump(), 
                self.noise_config, 
                elapsed
            )

            # 4. Record State
            record = {
                "time": elapsed,
                "true_temp": self.reactor.current_temp,
                "sensor_temp": sensor_data["current_temp"],
                "risk_level": self.reactor.tsr.risk_level,
                "mass": self.reactor.total_mass_g
            }
            self.history.append(record)

            if self.reactor.tsr.risk_level == "SHUTDOWN":
                print(f"🛑 [VPT] Emergency Shutdown at {elapsed}s")
                break
                
            elapsed += dt
        
        print(f"🏁 VPT Scenario '{self.scenario.name}' Finished.")
        return self.history

    def _handle_event(self, event: TimelineEvent):
        if event.action == "SET_POWER":
            self.current_power = event.value
            print(f"   [EVENT] {event.time_s}s: Power set to {event.value}W")
        elif event.action == "ADD_INGREDIENT":
            name, mass, temp = event.value["name"], event.value["mass"], event.value.get("temp", 23.0)
            self.reactor = FisPhysics.add_ingredient(self.reactor, name, mass, temp)
            print(f"   [EVENT] {event.time_s}s: Added {mass}g {name}")
        elif event.action == "CHANGE_AMBIENT":
            self.reactor.cal.env_overrides["TEMP"] = event.value
            print(f"   [EVENT] {event.time_s}s: Ambient Temp set to {event.value}C")
