import asyncio
import logging
import time
from typing import Dict, Any, Optional

from app.perception.drivers.flir_ax8 import FlirAX8Driver
from app.perception.drivers.mock_sensors import MockProbeDriver, MockScaleDriver
from app.perception.state_engine import StateVectorEngine

from app.control.navigator import Navigator
from app.control.safety import SafetyEngine
from app.control.governor import ActuatorGovernor
from app.knowledge.recorder import ScientificRecorder
from app.models.pan import PanProfile 

from app.perception.physics import PhysicsEstimator
from app.models.fis import FISProfile

# [Grand Fortification] 요쇄화 서비스
from app.services.safety_kernel import EmergencyStopService
from app.services.sensor_calibration import DualSensorCalibrationService

logger = logging.getLogger(__name__)

class PipelineService:
    """
    [Orchestrator]
    Orchestrates the Perception -> Safety -> Control -> Governor pipeline.
    Phase 9: Adds Physics Estimation and FIS Target Comparison.
    """
    
    def __init__(self):
        # 1. Perception Layer
        self.ax8 = FlirAX8Driver()
        self.probe = MockProbeDriver()
        self.scale = MockScaleDriver()
        self.vector_engine = StateVectorEngine(window_size=15)
        self.physics_engine = PhysicsEstimator() # [Phase 9]
        
        # 2. Control & Safety Layer
        self.navigator = Navigator()
        self.safety = SafetyEngine()
        self.estop = EmergencyStopService()  # [Grand Fortification] 하드웨어 가드레일
        self.calibrator = DualSensorCalibrationService() # [Grand Fortification] 이중 센서 융합
        self.governor = ActuatorGovernor(max_power_watts=1500.0, max_slew_rate=150.0) 
        
        # 3. Knowledge/State
        self.recorder = ScientificRecorder(base_dir="sessions")
        self.is_running = False
        
        # HIL Control State
        self.mode = "MANUAL"
        self.manual_watts = 0.0
        
        # [Phase 9] FIS Target
        self.current_fis: Optional[FISProfile] = None
        
        self.latest_session: Dict[str, Any] = {}
        
        # Default Station
        self.current_station = PanProfile(
            id="DEFAULT", name="Cast Iron Mock", 
            thermal_mass=1000.0, heat_loss_coeff=5.0,
            diameter_cm=28.0
        )

    async def start(self):
        logger.info("🚀 Starting Sentient Kitchen Pipeline...")
        self.is_running = True
        
        # Connect Hardware
        self.ax8.connect()
        self.probe.connect()
        self.scale.connect()
        
        # Start Polling
        asyncio.create_task(self._poll_loop())

    async def stop(self):
        self.is_running = False
        # Resources cleaned in finally block of loop
        
    def start_recording(self, metadata: Dict):
        station_info = {
            "id": self.current_station.id,
            "name": self.current_station.name,
            "thermal_mass": self.current_station.thermal_mass
        }
        roi_info = {"mock_roi": "x100y100w50h50"}
        
        sid = self.recorder.start_session(metadata, station_info, roi_info)
        return sid

    def stop_recording(self):
        self.recorder.stop_session()

    def set_mode(self, mode: str):
        if mode in ["AUTO", "MANUAL", "CALIBRATION"]:
            self.mode = mode
            logger.info(f"Switched Control Mode to: {mode}")

    def set_manual_command(self, watts: float):
        self.manual_watts = watts

    def load_fis_profile(self, profile: FISProfile):
        """[Phase 9] Set the Physics Target."""
        self.current_fis = profile
        logger.info(f"🎯 FIS Target Loaded: {profile.name} (Source: {profile.source})")
        self.physics_engine.reset()

    async def run_calibration_sequence(self):
        """Executes Step Response Test."""
        if self.is_running and self.mode == "CALIBRATION":
            logger.warning("Calibration already running.")
            return

        logger.info("🧪 Starting Calibration Sequence...")
        original_mode = self.mode
        self.set_mode("CALIBRATION")
        
        try:
            logger.info("🧪 Phase 1: Tare (10s)")
            self.set_manual_command(0.0)
            await asyncio.sleep(10.0)
            
            logger.info("🧪 Phase 2: Heat Step (60s)")
            self.set_manual_command(800.0)
            await asyncio.sleep(60.0)
            
            logger.info("🧪 Phase 3: Relaxation (120s)")
            self.set_manual_command(0.0)
            await asyncio.sleep(120.0)
            
            logger.info("🧪 Phase 4: Impulse (15s)")
            self.set_manual_command(1500.0)
            await asyncio.sleep(15.0)
            
            logger.info("🧪 Calibration Complete.")
            
        except asyncio.CancelledError:
            logger.warning("🧪 Calibration Cancelled.")
            raise
        except Exception as e:
            logger.error(f"🧪 Calibration Failed: {e}")
        finally:
            self.set_manual_command(0.0)
            self.set_mode(original_mode)
            logger.info("🧪 Restored Control Mode.")

    async def _poll_loop(self):
        try:
            while self.is_running:
                start_t = time.time()
                
                # --- A. SENSE ---
                d_ax8 = self.ax8.read()
                d_probe = self.probe.read()
                
                # [Grand Fortification] Sensor Fusion & Calibration
                fused_temp, confidence = self.calibrator.validate_and_fuse(
                    d_ax8['surface_temp'], d_probe['probe_temp']
                )
                
                now = time.time()
                sensor_age = now - d_ax8['timestamp']
                
                # --- B. EXTRACT ---
                # Using Fused Temperature (High-confidence)
                tsv = self.vector_engine.process_reading(d_ax8['timestamp'], fused_temp)
                
                # [Phase 9] Physics & Gap
                phys_metrics = self.physics_engine.process(tsv)
                
                nav_target = {"velocity": 1.0, "temp": 100.0}
                physics_error = {}
                
                if self.current_fis:
                    nav_target = {
                        "temp": self.current_fis.target.target_temp_c,
                        "velocity": 1.0
                    }
                    t_gap = self.current_fis.target.target_temp_c - tsv['temp']
                    m_gap = 0.0
                    if self.current_fis.target.min_maillard_index:
                         m_gap = self.current_fis.target.min_maillard_index - phys_metrics['maillard_index']
                    
                    physics_error = {
                        "temp_error": round(t_gap, 2),
                        "maillard_remaining": round(m_gap, 4) if m_gap > 0 else 0
                    }

                # --- C. SAFETY ---
                # 1. Standard Safety Engine (Logic/Context)
                is_safe, safety_reason = self.safety.evaluate(tsv)
                
                # 2. Grand Fortification Safety Kernel (Physical ESTOP)
                # Primary protection against 엣지 케이스 및 Reward Hacking
                phys_state = "FROZEN" if (self.current_fis and "FROZEN" in self.current_fis.name) else "ROOM_TEMP"
                kc_safe = self.estop.check_constraints(
                    surface_temp=tsv['temp'], 
                    core_temp=d_probe['probe_temp'], 
                    state=phys_state
                )
                
                if not kc_safe:
                    logger.critical(f"🛑 CRITICAL SAFETY BREACH: {self.estop.last_fault_reason}")
                    is_safe = False
                    safety_reason = f"ESTOP: {self.estop.last_fault_reason}"

                if not is_safe: logger.warning(f"Safety Trigger: {safety_reason}")
                
                # --- D. PLAN ---
                nav_result = self.navigator.calculate_action(tsv, nav_target, self.current_station)
                ai_watts_request = nav_result.get("cmd_watts", 0.0)
                
                # --- E. DECIDE ---
                governor_input_watts = 0.0
                if self.mode == "MANUAL": governor_input_watts = self.manual_watts
                elif self.mode == "AUTO": governor_input_watts = ai_watts_request
                elif self.mode == "CALIBRATION": governor_input_watts = self.manual_watts
                
                # --- F. GOVERN ---
                final_watts = self.governor.govern(governor_input_watts, sensor_age, not is_safe)
                
                # --- H. RECORD ---
                thermal_data_raw = d_ax8 
                power_data_raw = {
                    "cmd_watts": ai_watts_request,
                    "act_watts": final_watts,
                    "voltage": 220.0, 
                    "current": final_watts / 220.0,
                    "control_source": self.mode
                }
                control_data_raw = {
                    "safety_status": "OK" if is_safe else safety_reason,
                    "estop_active": self.estop.is_healthy if hasattr(self.estop, 'is_healthy') else not self.estop.is_estop_active,
                    "sensor_confidence": confidence,
                    "governor_status": "ACTIVE",
                    "physics": phys_metrics,
                    "physics_error": physics_error
                }
                if self.current_fis:
                    control_data_raw['fis_target'] = self.current_fis.model_dump()
                
                self.recorder.log_frame(now, thermal_data_raw, power_data_raw, control_data_raw)
                
                # --- I. REPORT ---
                self.latest_session = {
                    "timestamp": now,
                    "tsv": tsv,
                    "control": power_data_raw,
                    "status": "ACTIVE" if is_safe else "SAFETY_LOCKOUT",
                    "mode": self.mode,
                    "physics": phys_metrics,
                    "error": physics_error
                }
                
                elapsed = time.time() - start_t
                sleep_time = max(0.001, 0.1 - elapsed)
                await asyncio.sleep(sleep_time)

        except Exception as e:
            logger.critical(f"🔥 PIPELINE CRASHED: {e}", exc_info=True)
        finally:
            logger.critical("🛑 EMERGENCY SHUTDOWN TRIGGERED...")
            self.is_running = False
            self.recorder.stop_session()
            self.ax8.close()
            self.probe.close()
            self.scale.close()
            logger.info("✅ System Halted Safely.")

    def get_current_state(self) -> Dict[str, Any]:
        return self.latest_session
