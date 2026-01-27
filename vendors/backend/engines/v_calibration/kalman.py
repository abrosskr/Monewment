import numpy as np
from typing import Tuple

class VKalmanFilter:
    """
    [V-Kalman]
    Multi-variable State Observability Filter.
    Distinguishes between Sensor Noise, Thermal Inertia, and Power Inefficiency.
    """

    def __init__(self, 
                 initial_state: np.ndarray, 
                 initial_covariance: np.ndarray, 
                 process_noise: np.ndarray, 
                 measurement_noise: np.ndarray):
        self.x = initial_state           # State: [Temp, Efficiency]
        self.P = initial_covariance      # Uncertainty
        self.Q = process_noise           # Process noise (how much we trust our model)
        self.R = measurement_noise       # Measurement noise (how much we trust sensors)

    def predict(self, F: np.ndarray, B: np.ndarray, u: float):
        """
        x = F*x + B*u
        P = F*P*F^T + Q
        """
        self.x = np.dot(F, self.x) + (B * u).flatten()
        self.P = np.dot(F, np.dot(self.P, F.T)) + self.Q

    def update(self, z: float, H: np.ndarray):
        """
        K = P*H^T * (H*P*H^T + R)^-1
        x = x + K * (z - H*x)
        P = (I - K*H) * P
        """
        # Innovation
        y = z - np.dot(H, self.x)
        
        # Innovation covariance
        S = np.dot(H, np.dot(self.P, H.T)) + self.R
        
        # Kalman Gain
        K = np.dot(self.P, np.dot(H.T, np.linalg.inv(S)))
        
        # Update state and covariance
        self.x = self.x + np.dot(K, y)
        I = np.eye(self.P.shape[0])
        self.P = np.dot(I - np.dot(K, H), self.P)
        
        return self.x
