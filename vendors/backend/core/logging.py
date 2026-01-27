import logging
import sys
from .config import settings

def setup_logging():
    """
    Configure structured logging for the application.
    In a real production environment, this would use a JSON formatter.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("backend_standardized.log")
        ]
    )
    
    # Set levels for specialized loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

logger = logging.getLogger("vandors")
