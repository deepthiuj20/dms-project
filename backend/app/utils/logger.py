"""
Logging configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from app.utils.config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with JSON formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Root logger
logger = setup_logger("dms")
