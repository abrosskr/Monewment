import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MetricsEngine:
    """
    [Food Data Factory: Step 4]
    The Valuation Engine for Food Intelligence assets.
    Calculates MS (Taste Score) based on behavior and content.
    """
    
    # Default Constitution Weights (Refinery v1.0)
    WEIGHTS = {
        "LR": 0.25,  # Like Ratio (Likes / Views)
        "SCV": 0.20, # Subscriber View Ratio
        "CPR": 0.15, # Comment Positive Ratio (Sentiment)
        "GR": 0.15,  # Growth Rate (View Speed)
        "CF": 0.15,  # Content Feature (Clustering Rank)
        "RR": 0.10   # Reproducibility Ratio (Repetition)
    }

    @classmethod
    def calculate_ms(cls, 
                     views: int, 
                     likes: int, 
                     comments: int, 
                     sentiment: float,
                     scv: float,
                     growth: float,
                     cluster_rank: float = 0.5,
                     reproducibility: float = 0.5) -> float:
        """
        Calculates the Taste Score (MS).
        All inputs should be normalized 0.0 to 1.0 where applicable.
        """
        try:
            # 1. Calculate Primitive Metrics
            lr = (likes / views) if views > 0 else 0.0
            # Normalize LR (Typical good LR is around 0.05)
            lr_norm = min(lr / 0.05, 1.0)
            
            # 2. Weighted Sum
            score = (
                cls.WEIGHTS["LR"] * lr_norm +
                cls.WEIGHTS["SCV"] * min(scv / 0.2, 1.0) +
                cls.WEIGHTS["CPR"] * sentiment + # Already normalized
                cls.WEIGHTS["GR"] * min(growth / 2.0, 1.0) +
                cls.WEIGHTS["CF"] * cluster_rank +
                cls.WEIGHTS["RR"] * reproducibility
            )
            
            return round(score, 4)
        except Exception as e:
            logger.error(f"MS Calculation Error: {e}")
            return 0.5 # Safe fallback

    @classmethod
    def evaluate_behavioral_truth(cls, metrics_dict: Dict) -> float:
        """
        Helper to calculate MS from a dict (e.g., from YouTubeScraper)
        """
        return cls.calculate_ms(
            views=metrics_dict.get('views', 0),
            likes=metrics_dict.get('likes', 0),
            comments=metrics_dict.get('comments', 0),
            sentiment=metrics_dict.get('sentiment_score', 0.5),
            scv=metrics_dict.get('scv', 0.1),
            growth=metrics_dict.get('gr', 1.0)
        )
