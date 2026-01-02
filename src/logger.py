# src/logger.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger()
    if logger.handlers: return logger
    
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(message)s %(filename)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
    