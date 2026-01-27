from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSensorDriver(ABC):
    """
    Universal Interface for The Sentient Kitchen Sensors.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the hardware."""
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """
        Return the latest sensor data.
        Must include 'timestamp' and core metric.
        """
        pass

    @abstractmethod
    def close(self):
        """Cleanly close connection."""
        pass
    
    @property
    def is_connected(self) -> bool:
        return False
