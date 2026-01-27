import time
import logging
from collections import deque
from typing import Dict, Any, Optional
import numpy as np

# PyModbus imports
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    ModbusTcpClient = None

from app.perception.drivers.base_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

class FlirAX8Driver(BaseSensorDriver):
    """
    Driver for FLIR AX8 Thermal Camera via Modbus TCP.
    
    [CRC Protocol Implementation]
    This driver not only reads temperature but calculates the 
    Cooking Response Coefficient (CRC = dT/dt) internally.
    """
    
    # Default Registers (Based on research, customizable)
    # 400 series usually maps to Holding Registers. 
    # PyModbus address 0 maps to 40001.
    # If Spot 1 is 402019, address is 2018 (0-based) ?? 
    # Usually manuals say "Modbus Address" vs "Register Number".
    # Let's assume user configures this. Defaulting to a common area or Mocking if fail.
    
    def __init__(self, ip_address: str = "192.168.0.168", port: int = 502, spot_register: int = 2018):
        self.ip_address = ip_address
        self.port = port
        self.spot_register = spot_register
        self.client: Optional[ModbusTcpClient] = None
        self._connected = False
        
        # CRC Calculation State
        self.window_size = 5 # 0.5 sec at 10Hz
        self.history = deque(maxlen=self.window_size)
        self.last_crc = 0.0
        
        # Mock Mode (Safety Fallback)
        self.mock_mode = False

    def connect(self) -> bool:
        if ModbusTcpClient is None:
            logger.warning("pymodbus not installed. Falling back to Mock Mode.")
            self.mock_mode = True
            return True
            
        try:
            self.client = ModbusTcpClient(self.ip_address, port=self.port, timeout=1.0)
            if self.client.connect():
                self._connected = True
                logger.info(f"✅ FLIR AX8 Connected at {self.ip_address}")
                return True
            else:
                logger.warning(f"⚠️ Failed to connect to FLIR AX8 at {self.ip_address}. Using Mock Mode.")
                self.mock_mode = True
                return False
        except Exception as e:
            logger.error(f"❌ Connection Error: {e}")
            self.mock_mode = True
            return False

    def read(self) -> Dict[str, Any]:
        """
        Returns:
            {
                "timestamp": float,
                "surface_temp": float (Celsius),
                "crc": float (deg/sec),
                "status": "OK" | "ERROR"
            }
        """
        now = time.time()
        temp = 0.0
        
        if self.mock_mode or not self._connected:
            # Simulate slight noise around 25C (Room Temp)
            # or rising if we want to test CRC
            base_temp = 25.0 + np.random.normal(0, 0.1)
            temp = base_temp
            # Mock Raw Frame (80x60)
            # Center hotspot if high temp?
            raw_frame = np.full((60, 80), base_temp, dtype=np.float32)
            # Add some noise
            raw_frame += np.random.normal(0, 0.05, (60, 80)).astype(np.float32)
        else:
            try:
                # Read Holding Register (Function Code 3)
                rr = self.client.read_holding_registers(self.spot_register, 1)
                if not rr.isError():
                    raw = rr.registers[0]
                    temp = raw / 10.0 # Prototyping assumption
                else:
                    logger.warning("Modbus Read Error")
            except Exception as e:
                logger.error(f"Modbus IO Error: {e}")
                self._connected = False
            
            # TODO: Implement Block Read or RTSP for Real Raw Frame
            raw_frame = None 
        
        # Calculate CRC (dT/dt)
        crc = self._calculate_crc(now, temp)
        
        return {
            "timestamp": now,
            "surface_temp": round(temp, 2),
            "crc": round(crc, 4),
            "status": "MOCK" if self.mock_mode else "LIVE",
            "raw_frame": raw_frame
        }

    def _calculate_crc(self, now: float, temp: float) -> float:
        """
        Computes derivative with noise filtering (Simple Moving Average).
        """
        self.history.append((now, temp))
        
        if len(self.history) < 2:
            return 0.0
            
        # Linear Regression Slope for better stability than simple diff
        times = np.array([x[0] for x in self.history])
        temps = np.array([x[1] for x in self.history])
        
        # Min-max normalize time to avoid huge numbers? No, just delta.
        # Simple finite difference of the average? 
        # Best: Slope of best fit line
        try:
            slope, _ = np.polyfit(times, temps, 1)
            return slope
        except:
            return 0.0

    def close(self):
        if self.client:
            self.client.close()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected or self.mock_mode
