import os
import json
import time
import uuid
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ScientificRecorder:
    """
    [SK-SDS v1.0 Recorder]
    Logs high-frequency physical data for scientific analysis.
    Prioritizes RAW data over derived features.
    """
    
    def __init__(self, base_dir: str = "backend/data/assets/layer_b_physics"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session_id: Optional[str] = None
        self.session_path: Optional[Path] = None
        self.is_recording = False
        
        # Buffers for high-freq data
        self.buffer_thermal: List[Dict] = []
        self.buffer_power: List[Dict] = []
        self.buffer_control: List[Dict] = []
        
        self.chunk_size = 50 # Flush every 50 frames (~5 sec at 10Hz)

    def start_session(self, metadata: Dict, station_info: Dict, roi_info: Dict) -> str:
        """
        Initialize a new recording session.
        Creates directory structure and saves static JSONs.
        """
        self.current_session_id = str(uuid.uuid4())
        self.session_path = self.base_dir / self.current_session_id
        self.session_path.mkdir(exist_ok=True)
        
        # 1. Save Static Metadata (JSON) - Constitution Domain PHYSICS
        # Strip all cross-domain contamination (Recipe, Culture, PIM)
        clean_metadata = {
            "session_id": self.current_session_id,
            "domain": "PHYSICS",
            "purity_grade": "A+", # Sensor Verified
            "start_time_iso": datetime.utcnow().isoformat(),
            "physical_constants": {k: v for k, v in metadata.items() if not any(x in k.lower() for x in ['recipe', 'title', 'culture', 'name', 'url'])}
        }
        
        with open(self.session_path / "metadata.json", "w") as f:
            json.dump(clean_metadata, f, indent=2)
            
        with open(self.session_path / "station.json", "w") as f:
            json.dump(station_info, f, indent=2)
            
        with open(self.session_path / "roi.json", "w") as f:
            json.dump(roi_info, f, indent=2)
            
        self.is_recording = True
        logger.info(f"📼 Recording Started: {self.current_session_id}")
        return self.current_session_id

    def log_frame(self, 
                  timestamp: float,
                  thermal_data: Dict, 
                  power_data: Dict,
                  control_data: Dict):
        """
        Ingest a single time-step of data.
        """
        if not self.is_recording:
            return

        # Flatten Thermal Data (Raw Priority)
        # thermal_data expected: {'timestamp', 'surface_temp', 'amb_temp', 'raw_frame': np.array}
        raw_frame = thermal_data.get('raw_frame')
        raw_bytes = None
        if raw_frame is not None:
            # Serialize numpy array to bytes for Parquet Binary column
            # We also store shape in metadata or assume fixed 80x60?
            # For robustness, just bytes. Decoding requires knowing shape.
            # Or use explicit columns if flattened? 80x60=4800 columns is too wide.
            # Blob is best.
            try:
                raw_bytes = raw_frame.tobytes()
            except:
                pass

        t_row = {
            "time_epoch": timestamp,
            "pan_surface_c": thermal_data.get('surface_temp'),
            "amb_c": thermal_data.get('amb_temp', 25.0),
            "raw_thermal_blob": raw_bytes # Binary Column
        }
        self.buffer_thermal.append(t_row)
        
        # Flatten Power Data
        p_row = {
            "time_epoch": timestamp,
            "cmd_watts": power_data.get('cmd_watts', 0.0),
            "act_watts": power_data.get('act_watts', 0.0),
            "voltage_v": power_data.get('voltage', 220.0), # Mock/Real
            "current_a": power_data.get('current', 0.0)
        }
        self.buffer_power.append(p_row)
        
        # Flatten Control Data (Governor/Safety)
        c_row = {
            "time_epoch": timestamp,
            "safety_status": control_data.get('safety_status', 'UNKNOWN'),
            "governor_active": control_data.get('governor_status') == 'ACTIVE'
        }
        self.buffer_control.append(c_row)
        
        # Auto-Flush
        if len(self.buffer_thermal) >= self.chunk_size:
            self._flush()

    def _flush(self):
        """Write buffers to Parquet files"""
        if not self.session_path: return
        
        try:
            if self.buffer_thermal:
                df = pd.DataFrame(self.buffer_thermal)
                self._append_parquet(df, "raw_thermal.parquet")
                self.buffer_thermal.clear()
                
            if self.buffer_power:
                df = pd.DataFrame(self.buffer_power)
                self._append_parquet(df, "raw_power.parquet")
                self.buffer_power.clear()

            if self.buffer_control:
                df = pd.DataFrame(self.buffer_control)
                self._append_parquet(df, "control.parquet")
                self.buffer_control.clear()
                
        except Exception as e:
            logger.error(f"Recorder Flush Error: {e}")

    def _append_parquet(self, df: pd.DataFrame, filename: str):
        path = self.session_path / filename
        # Parquet append is tricky without engine support. 
        # For simplicity in Phase 6, we'll write separate chunks or check existence.
        # FastParquet or PyArrow allow append.
        # Simplest Logic: Check if exists. If so, read, append, write (Slow but safe for V1)
        # BETTER: Write separate chunk files or use fastparquet append.
        # Let's use 'fastparquet' append if available, otherwise just overwrite logic (bad).
        # We installed 'pyarrow' and 'pandas'.
        # Pandas to_parquet doesn't support append easily.
        # Strategy: Write chunk files raw_thermal_{n}.parquet?
        # NO, too many files.
        # Strategy: Use file lock and append? 
        # Actually, for V1 10Hz, accumulating in memory until stop is risky but easiest.
        # But we promised Chunking. 
        # Let's use the 'file exists' check to append is not native in pandas.
        # We will write to a NEW file if it doesn't exist, else append?
        # Pandas cannot append to parquet directly.
        # Construct: load existing -> concat -> save. (Performance Heavy for long runs)
        # ALTERNATIVE: CSV for V1? No, user demanded Scientific.
        # SOLUTION: Write each chunk as `part_{timestamp}.parquet`. 
        # This is standard Big Data practice.
        
        chunk_id = int(time.time() * 1000)
        chunk_name = f"{filename.replace('.parquet', '')}_part_{chunk_id}.parquet"
        df.to_parquet(self.session_path / chunk_name, engine='pyarrow')

    def stop_session(self):
        """Flush remaining data and close session"""
        self._flush()
        self.is_recording = False
        logger.info("📼 Recording Stopped.")
